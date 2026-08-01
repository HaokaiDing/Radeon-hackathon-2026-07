#!/usr/bin/env python3
"""Render a captioned FlightGuard submission video from frozen JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np

WIDTH = 1280
HEIGHT = 720
DEFAULT_FPS = 10.0
DEFAULT_DURATION = 210.0
FOURCC = "mp4v"
FONT = cv2.FONT_HERSHEY_SIMPLEX

EXPECTED_SHA256 = {
    "v4": "4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b",
    "v5": "d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034",
    "v6": "905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678",
    "scaling": "98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072",
}

BG = (23, 19, 15)
PANEL = (42, 34, 27)
PANEL_ALT = (52, 43, 34)
INK = (245, 241, 235)
MUTED = (185, 174, 160)
BLUE = (245, 165, 89)
GREEN = (141, 214, 88)
RED = (107, 107, 255)
AMBER = (96, 189, 246)
LINE = (78, 66, 55)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_verified(role: str, path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    expected = EXPECTED_SHA256[role]
    if digest != expected:
        raise ValueError(f"{role} SHA-256 mismatch: expected {expected}, got {digest}")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise TypeError(f"{role} JSON root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def evidence_values(
    v4: dict[str, Any],
    v5: dict[str, Any],
    v6: dict[str, Any],
    scaling: dict[str, Any],
) -> dict[str, Any]:
    require(v4["status"] == "FAIL", "v4 status drift")
    v4_counts = {
        arm: int(v4["metrics"][arm]["fault"]["mission_success_count"])
        for arm in ("CausalIMUPatch", "ActionOnly", "RawStrapdown", "CalibratedStrapdown")
    }
    require(list(v4_counts.values()) == [11, 0, 33, 32], "v4 counts drift")
    v4_reduction = float(v4["capability_effect"]["patch_vs_action_only_failure_reduction_fraction"])

    require(v5["status"] == "PASS" and v5["award_evidence_eligible"] is False, "v5 status drift")
    v5_fault = {
        arm: int(v5["metrics"][arm]["fault"]["mission_success_count"])
        for arm in ("CausalIMUPatch", "ActionOnly", "CalibratedStrapdown")
    }
    v5_nominal = {
        arm: int(v5["metrics"][arm]["nominal"]["mission_success_count"])
        for arm in ("CausalIMUPatch", "CalibratedStrapdown")
    }
    traces = v5["integrity"]["fault_paired_patch_calibrated_trace"]
    trace_fields = [len(traces[str(checkpoint)]["fields"]) for checkpoint in (30, 31, 32)]
    require(v5_fault == {"CausalIMUPatch": 10, "ActionOnly": 0, "CalibratedStrapdown": 10}, "v5 counts drift")
    require(v5_nominal == {"CausalIMUPatch": 12, "CalibratedStrapdown": 12}, "v5 nominal drift")
    require(trace_fields == [19, 19, 19], "v5 trace field drift")

    require(v6["status"] == "FAIL" and v6["checkpoint_seed"] == 30, "v6 status drift")
    recurrence = v6["raw_to_delivered_sensor_recurrence"]
    recurrence_pass = all(
        bool(recurrence[key])
        for key in (
            "replayed_delivered_force_raw_bit_exact",
            "replayed_delivered_gyro_raw_bit_exact",
            "disabled_no_op_force_raw_bit_exact",
            "disabled_no_op_gyro_raw_bit_exact",
            "enabled_kill_gate_changes_force",
            "enabled_kill_gate_changes_gyro",
        )
    )
    lanes = v6["lanes"]
    lane_counts = {
        "rank8": sum(int(lane["full_fit_certificate"]["numerical_rank"] == 8) for lane in lanes),
        "sigma": sum(float(lane["full_fit_certificate"]["normalized_sigma_ratio"]) >= 1e-3 for lane in lanes),
        "split": sum(bool(lane["split_half_stability"]["passed"]) for lane in lanes),
        "dv_rmse": sum(bool(lane["holdout_qualification"]["delta_velocity_error_mps"]["rmse_passed_by_core"]) for lane in lanes),
        "rot_rmse": sum(bool(lane["holdout_qualification"]["rotation_geodesic_error_rad"]["rmse_passed_by_core"]) for lane in lanes),
        "dv_q95": sum(bool(lane["holdout_qualification"]["delta_velocity_error_mps"]["q95_passed_by_core"]) for lane in lanes),
        "rot_q95": sum(bool(lane["holdout_qualification"]["rotation_geodesic_error_rad"]["q95_passed_by_core"]) for lane in lanes),
    }
    sigma_values = [float(lane["full_fit_certificate"]["normalized_sigma_ratio"]) for lane in lanes]
    require(v6["admitted_lane_count"] == 0 and len(lanes) == 12, "v6 admission drift")
    require(lane_counts == {"rank8": 12, "sigma": 12, "split": 0, "dv_rmse": 0, "rot_rmse": 0, "dv_q95": 3, "rot_q95": 3}, "v6 lane gates drift")

    require(scaling["status"] == "PASS" and scaling["simulation_only"] is True, "scaling status drift")
    scale = scaling["scaling"]
    require(scale["status"] == "PASS" and scale["performance_acceptance"]["achieved"] is True, "scaling acceptance drift")
    scale_rows = []
    for row in scale["env_summaries"]:
        monitor = row["measured_gpu_monitor"]
        scale_rows.append(
            {
                "env_count": int(row["env_count"]),
                "throughput": float(row["mean_transitions_per_s"]),
                "gpu_mean": float(monitor["gpu_use_percent_mean"]),
                "gpu_max": float(monitor["gpu_use_percent_max"]),
                "vram_max": int(monitor["vram_used_bytes_max"]),
                "cv": float(row["coefficient_of_variation"]),
                "speedup": float(row["speedup_vs_32_envs"]),
                "efficiency": float(row["parallel_efficiency_vs_32_envs"]),
                "measured_transitions": int(row["measured_transitions"]),
            }
        )
    require([row["env_count"] for row in scale_rows] == [32, 128, 256, 512], "scaling env order drift")
    require(sum(row["measured_transitions"] for row in scale_rows) == 2_227_200, "scaling transition count drift")

    return {
        "v4_counts": v4_counts,
        "v4_reduction": v4_reduction,
        "v5_fault": v5_fault,
        "v5_nominal": v5_nominal,
        "v5_fields": trace_fields[0],
        "v6_recurrence": recurrence_pass,
        "v6_lanes": lane_counts,
        "v6_sigma": (min(sigma_values), max(sigma_values)),
        "scaling": scale_rows,
        "total_transitions": int(scale["total_measured_transitions"]),
    }


def put_text(
    image: np.ndarray,
    text: str,
    x: int,
    y: int,
    *,
    scale: float = 0.65,
    color: tuple[int, int, int] = INK,
    thickness: int = 1,
) -> None:
    cv2.putText(image, text, (x, y), FONT, scale, color, thickness, cv2.LINE_AA)


def wrap_lines(text: str, max_width: int, scale: float, thickness: int = 1) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        width = cv2.getTextSize(candidate, FONT, scale, thickness)[0][0]
        if current and width > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def put_wrapped(
    image: np.ndarray,
    text: str,
    x: int,
    y: int,
    max_width: int,
    *,
    scale: float = 0.65,
    color: tuple[int, int, int] = INK,
    thickness: int = 1,
    line_height: int = 30,
) -> int:
    lines = wrap_lines(text, max_width, scale, thickness)
    for index, line in enumerate(lines):
        put_text(image, line, x, y + index * line_height, scale=scale, color=color, thickness=thickness)
    return y + len(lines) * line_height


def base_slide(section: str, title: str, subtitle: str) -> np.ndarray:
    image = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)
    for row in range(HEIGHT):
        shade = int(12 * row / HEIGHT)
        image[row, :, :] = np.clip(np.array(BG) + shade, 0, 255)
    cv2.rectangle(image, (0, 0), (WIDTH, 7), BLUE, -1)
    cv2.rectangle(image, (42, 32), (102, 92), BLUE, -1)
    put_text(image, "F/F", 53, 72, scale=0.75, color=BG, thickness=2)
    put_text(image, section.upper(), 126, 54, scale=0.48, color=BLUE, thickness=2)
    put_wrapped(image, title, 126, 94, 1080, scale=1.12, color=INK, thickness=2, line_height=52)
    put_wrapped(image, subtitle, 126, 174, 1040, scale=0.58, color=MUTED, line_height=28)
    return image


def panel(image: np.ndarray, x: int, y: int, w: int, h: int, title: str, value: str, color: tuple[int, int, int]) -> None:
    cv2.rectangle(image, (x, y), (x + w, y + h), PANEL, -1)
    cv2.rectangle(image, (x, y), (x + 6, y + h), color, -1)
    put_text(image, title.upper(), x + 24, y + 30, scale=0.43, color=MUTED, thickness=1)
    put_wrapped(image, value, x + 24, y + 66, w - 44, scale=0.62, color=INK, thickness=2, line_height=29)


def draw_title(values: dict[str, Any]) -> np.ndarray:
    image = base_slide(
        "AMD Track 3 / simulation-only",
        "FlightGuard / FaultFork",
        "A Radeon-native, fail-closed embodied-flight claim auditor.",
    )
    put_wrapped(image, "The product is the audit: freeze evidence, run the device path, enforce gates, and preserve the negative result.", 126, 285, 990, scale=0.72, color=INK, thickness=2, line_height=36)
    panel(image, 126, 405, 300, 105, "Candidate mechanisms", "v4 / v5 / v6", BLUE)
    panel(image, 452, 405, 300, 105, "Scientific outcome", "No mechanism claim", RED)
    panel(image, 778, 405, 300, 105, "Compute evidence", "One AMD Radeon", GREEN)
    return image


def draw_pipeline(values: dict[str, Any]) -> np.ndarray:
    image = base_slide(
        "01 / evidence pipeline",
        "Fail closed before making a claim",
        "Frozen inputs and a serial Radeon run feed explicit integrity and science gates.",
    )
    labels = ["Frozen JSON", "Radeon capture", "Recur / no-op / kill", "Observer gates", "Exact-Cal fallback"]
    x_values = [74, 310, 546, 782, 1018]
    for index, (x, label) in enumerate(zip(x_values, labels, strict=True)):
        cv2.rectangle(image, (x, 290), (x + 184, 390), PANEL, -1)
        cv2.rectangle(image, (x, 290), (x + 184, 296), BLUE if index < 3 else (RED if index == 3 else AMBER), -1)
        put_wrapped(image, label, x + 16, 334, 152, scale=0.53, color=INK, thickness=2, line_height=25)
        if index < len(labels) - 1:
            cv2.arrowedLine(image, (x + 190, 340), (x_values[index + 1] - 10, 340), LINE, 2, cv2.LINE_AA, tipLength=0.3)
    put_wrapped(image, "If provenance or recurrence fails, interpretation stops. If scientific qualification fails, the candidate returns the calibrated baseline and expansion stops.", 126, 470, 1020, scale=0.66, color=MUTED, thickness=1, line_height=33)
    return image


def draw_v4(values: dict[str, Any]) -> np.ndarray:
    c = values["v4_counts"]
    image = base_slide("02 / v4", "Causal IMU repair: scientific FAIL", "A better result than ActionOnly was not enough to establish superiority.")
    entries = [
        ("PATCH", c["CausalIMUPatch"], BLUE),
        ("ACTION ONLY", c["ActionOnly"], AMBER),
        ("RAW", c["RawStrapdown"], GREEN),
        ("CAL", c["CalibratedStrapdown"], GREEN),
    ]
    max_success = 36
    for index, (label, count, color) in enumerate(entries):
        y = 275 + index * 62
        put_text(image, label, 126, y + 25, scale=0.5, color=MUTED, thickness=2)
        cv2.rectangle(image, (300, y), (1080, y + 34), PANEL, -1)
        if count:
            cv2.rectangle(image, (300, y), (300 + int(780 * count / max_success), y + 34), color, -1)
        put_text(image, f"{count} / 36", 318, y + 24, scale=0.55, color=INK, thickness=2)
    put_text(image, f"Failure reduction vs ActionOnly: {100 * values['v4_reduction']:.2f}% < 50% gate", 126, 566, scale=0.66, color=RED, thickness=2)
    put_text(image, "Verdict retained: SCIENTIFIC FAIL", 126, 612, scale=0.78, color=RED, thickness=2)
    return image


def draw_v5(values: dict[str, Any]) -> np.ndarray:
    f = values["v5_fault"]
    n = values["v5_nominal"]
    image = base_slide("03 / v5", "Residual-q95 quarantine: award-ineligible", "The development gates passed, but Patch and Cal were operationally identical after onset.")
    panel(image, 126, 286, 300, 120, "Fault success", f"Patch {f['CausalIMUPatch']}/12 = Cal {f['CalibratedStrapdown']}/12", BLUE)
    panel(image, 452, 286, 300, 120, "Nominal success", f"Patch {n['CausalIMUPatch']}/12 = Cal {n['CalibratedStrapdown']}/12", GREEN)
    panel(image, 778, 286, 300, 120, "ActionOnly fault", f"{f['ActionOnly']} / 12", AMBER)
    panel(image, 126, 440, 952, 105, "Raw-bit evidence", f"{values['v5_fields']} post-onset operational fields were exact for Patch and Cal.", GREEN)
    put_text(image, "Incremental capability: 0", 126, 607, scale=0.82, color=RED, thickness=2)
    return image


def draw_v6(values: dict[str, Any]) -> np.ndarray:
    counts = values["v6_lanes"]
    sigma_min, sigma_max = values["v6_sigma"]
    image = base_slide("04 / v6 checkpoint 30", "Frozen 8-state observer: scientific FAIL", "The Radeon recurrence gate passed. The observer qualification gate did not.")
    labels = [
        ("Recurrence / no-op / kill", 12 if values["v6_recurrence"] else 0, GREEN),
        ("Rank 8", counts["rank8"], GREEN),
        ("Sigma >= 1e-3", counts["sigma"], GREEN),
        ("Split-half stable", counts["split"], RED),
        ("dV RMSE <= 0.90xCal", counts["dv_rmse"], RED),
        ("Rotation RMSE <= 0.90xCal", counts["rot_rmse"], RED),
        ("dV q95 <= Cal", counts["dv_q95"], AMBER),
        ("Rotation q95 <= Cal", counts["rot_q95"], AMBER),
    ]
    for index, (label, count, color) in enumerate(labels):
        col = index % 2
        row = index // 2
        x = 126 + col * 496
        y = 252 + row * 79
        panel(image, x, y, 468, 62, label, f"{count} / 12", color)
    put_text(image, f"Sigma range: {sigma_min:.17g} - {sigma_max:.17g}", 126, 594, scale=0.55, color=MUTED, thickness=1)
    put_text(image, "0 admitted / 12 exact-Cal fallback / checkpoints 31-32 not audited", 126, 638, scale=0.67, color=RED, thickness=2)
    return image


def draw_scaling(values: dict[str, Any]) -> np.ndarray:
    rows = values["scaling"]
    image = base_slide("05 / Radeon throughput", "Measured scaling on one AMD Radeon", "Fixed r5 nominal deployed simulation pipeline; throughput evidence only.")
    chart_x, chart_y, chart_w, chart_h = 150, 260, 990, 270
    maximum = max(row["throughput"] for row in rows)
    cv2.line(image, (chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h), LINE, 2)
    bar_w = 150
    gap = (chart_w - len(rows) * bar_w) // (len(rows) + 1)
    for index, row in enumerate(rows):
        x = chart_x + gap + index * (bar_w + gap)
        height = int(chart_h * row["throughput"] / maximum)
        y = chart_y + chart_h - height
        cv2.rectangle(image, (x, y), (x + bar_w, chart_y + chart_h), BLUE, -1)
        put_text(image, f"{row['throughput']:,.1f}", x + 6, y - 12, scale=0.47, color=INK, thickness=2)
        put_text(image, f"{row['env_count']} envs", x + 30, chart_y + chart_h + 28, scale=0.48, color=INK, thickness=2)
        put_text(image, f"GPU {row['gpu_mean']:.4f}%", x + 8, chart_y + chart_h + 53, scale=0.39, color=MUTED, thickness=1)
    last = rows[-1]
    put_text(image, f"512/32 speedup {last['speedup']:.15f}x   |   parallel efficiency {last['efficiency']:.15f}", 126, 620, scale=0.54, color=GREEN, thickness=2)
    put_text(image, f"{values['total_transitions']:,} measured transitions   |   max CV {max(row['cv'] for row in rows):.16f}   |   VRAM max {max(row['vram_max'] for row in rows):,} B", 126, 658, scale=0.46, color=MUTED, thickness=1)
    return image


def draw_boundary(values: dict[str, Any]) -> np.ndarray:
    image = base_slide("06 / claim boundary and reproduction", "What the evidence establishes", "A reproducible Radeon pipeline and three honest stop decisions - not a flight-performance claim.")
    claims = [
        "Simulation-only; fixed r5 nominal deployed pipeline on one Radeon.",
        "Single T265 development event; causal only to the ROS bag record-time availability proxy.",
        "No scientific superiority, sim-to-real, safety, certification, or real-flight repair claim.",
        "No candidate mechanism claim was established by v4, v5, or v6.",
    ]
    y = 270
    for claim in claims:
        cv2.circle(image, (142, y - 7), 6, BLUE if "No candidate" not in claim else RED, -1)
        y = put_wrapped(image, claim, 166, y, 950, scale=0.61, color=INK, thickness=1, line_height=31) + 18
    put_text(image, "Evidence: submission/evidence/", 126, 535, scale=0.55, color=GREEN, thickness=2)
    put_text(image, "Figures: submission/figures/", 126, 570, scale=0.55, color=GREEN, thickness=2)
    put_text(image, "Reproduce: README.md and docs/technical-report.md", 126, 605, scale=0.55, color=GREEN, thickness=2)
    put_text(image, "Radeon scaling SHA-256: 98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072", 126, 650, scale=0.38, color=MUTED, thickness=1)
    return image


def add_caption(image: np.ndarray, caption: str, elapsed: float, duration: float, local_fraction: float) -> np.ndarray:
    frame = image.copy()
    cv2.rectangle(frame, (0, 664), (WIDTH, HEIGHT), (14, 12, 10), -1)
    put_wrapped(frame, caption, 56, 692, 1080, scale=0.46, color=INK, thickness=1, line_height=22)
    put_text(frame, f"{elapsed:06.1f}s / {duration:06.1f}s", 1090, 700, scale=0.38, color=MUTED, thickness=1)
    cv2.rectangle(frame, (0, 714), (WIDTH, 719), PANEL_ALT, -1)
    cv2.rectangle(frame, (0, 714), (int(WIDTH * elapsed / duration), 719), BLUE, -1)
    dot_x = 55 + int(1100 * max(0.0, min(1.0, local_fraction)))
    cv2.circle(frame, (dot_x, 646), 7, BLUE, -1)
    return frame


def render_video(values: dict[str, Any], output: Path, fps: float, duration: float) -> dict[str, Any]:
    require(180.0 <= duration <= 300.0, "duration must be between 180 and 300 seconds")
    require(1.0 <= fps <= 30.0, "fps out of range")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_name(f".{output.name}.part.mp4")
    if part.exists():
        raise FileExistsError(f"refusing to overwrite {part}")

    segments: list[tuple[float, float, Callable[[dict[str, Any]], np.ndarray], str]] = [
        (0.0, 18.0, draw_title, "FlightGuard audits embodied-flight claims on Radeon and preserves negative evidence."),
        (18.0, 48.0, draw_pipeline, "Frozen inputs feed a serial Radeon capture, integrity checks, scientific gates, and exact fallback."),
        (48.0, 80.0, draw_v4, "V4 improved over ActionOnly but missed the failure-reduction gate and trailed Raw and Cal."),
        (80.0, 110.0, draw_v5, "V5 tied Cal and was raw-bit exact after onset, so incremental capability was zero."),
        (110.0, 150.0, draw_v6, "V6 passed recurrence, rank, and conditioning, then admitted zero lanes at checkpoint 30."),
        (150.0, 185.0, draw_scaling, "One Radeon processed the fixed r5 nominal deployed pipeline with measured near-linear environment scaling."),
        (185.0, duration, draw_boundary, "The submission claims a reproducible audit pipeline, not scientific superiority or real-flight safety."),
    ]
    require(abs(segments[-1][1] - duration) < 1e-9, "segment duration mismatch")
    slides = [builder(values) for _, _, builder, _ in segments]
    writer = cv2.VideoWriter(str(part), cv2.VideoWriter_fourcc(*FOURCC), fps, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("cv2 VideoWriter failed to open mp4v output")
    frame_count = int(round(duration * fps))
    try:
        for frame_index in range(frame_count):
            elapsed = frame_index / fps
            segment_index = next(
                index
                for index, (start, end, _builder, _caption) in enumerate(segments)
                if start <= elapsed < end
            )
            start, end, _builder, caption = segments[segment_index]
            local = (elapsed - start) / max(end - start, 1e-9)
            frame = add_caption(slides[segment_index], caption, elapsed, duration, local)
            fade = min(1.0, local / 0.04, (1.0 - local) / 0.04)
            if fade < 1.0:
                frame = cv2.addWeighted(frame, max(0.0, fade), np.zeros_like(frame), 1.0 - max(0.0, fade), 0.0)
            writer.write(frame)
    finally:
        writer.release()

    capture = cv2.VideoCapture(str(part))
    if not capture.isOpened():
        raise RuntimeError("rendered video cannot be opened")
    actual_fps = float(capture.get(cv2.CAP_PROP_FPS))
    actual_frames = int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
    actual_width = int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    actual_height = int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    actual_fourcc_value = int(round(capture.get(cv2.CAP_PROP_FOURCC)))
    actual_fourcc = "".join(chr((actual_fourcc_value >> (8 * index)) & 0xFF) for index in range(4))
    capture.release()
    actual_duration = actual_frames / actual_fps
    require(actual_width == WIDTH and actual_height == HEIGHT, "rendered dimensions mismatch")
    require(abs(actual_fps - fps) < 0.01, "rendered fps mismatch")
    require(actual_frames == frame_count, "rendered frame count mismatch")
    require(180.0 <= actual_duration <= 300.0, "rendered duration outside submission range")
    os.replace(part, output)
    raw = output.read_bytes()
    return {
        "path": str(output.resolve()),
        "codec_requested": FOURCC,
        "codec_reported": actual_fourcc,
        "width": actual_width,
        "height": actual_height,
        "fps": actual_fps,
        "frame_count": actual_frames,
        "duration_seconds": actual_duration,
        "size_bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "audio": False,
        "captioned": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v4", required=True, type=Path)
    parser.add_argument("--v5", required=True, type=Path)
    parser.add_argument("--v6", required=True, type=Path)
    parser.add_argument("--scaling", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    args = parser.parse_args()

    values = evidence_values(
        load_verified("v4", args.v4),
        load_verified("v5", args.v5),
        load_verified("v6", args.v6),
        load_verified("scaling", args.scaling),
    )
    report = render_video(values, args.output, args.fps, args.duration)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
