#!/usr/bin/env python3
"""Evidence-only 60-second judge path for the FlightGuard submission."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import cv2
except ImportError:
    cv2 = None

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "submission" / "evidence"

EXPECTED_SHA256 = {
    "verified-flight-envelope-aggregate.json": "c7ca6e460e967c3070736d8120bd918a3c489f1e7d62a3ae933ab631af827f58",
    "radeon-formal-scaling.json": "98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072",
    "v4-summary.json": "4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b",
    "v5-summary.json": "d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034",
    "v6-checkpoint-30.json": "905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678",
    "v6-audit-receipt.json": "521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1",
    "capture-terminal.json": "923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be",
    "frozen-claim-auditor-benchmark.json": "ccbf38ef7aa36571c3f2433d5f4e9d54b1dd1de7cc2e8f93f2291ccc816f83f7",
}

RAW_METRICS_SHA256 = {
    "training-collector/seed303-metrics.json": "aaa5e1e4654aec24b907527eb5334338a50f328c679eace8208b87f650e36959",
    "training-collector/seed304-metrics.json": "61b70eead81696608a75436db23f59be9f01a25f65d09af9bc81a6d489010b54",
    "training-collector/seed305-metrics.json": "24cadca684b1de7f069f4ffb3767502396c1f38031f35e606157fc7874395955",
    "heldout-three-gate-mission/seed303-metrics.json": "7d30a032a032b3d757a77afbe8ed60aa97c61e54f557ef2ba242251b14f14238",
    "heldout-three-gate-mission/seed304-metrics.json": "c3408cbb720df48690783888e6335b6350c265ad4af8526d72486250aa2204a8",
    "heldout-three-gate-mission/seed305-metrics.json": "e546809527d28df7b25fa82ad2d552de170672c871fee6aed132889f38d8d63e",
}
RAW_METRICS = EVIDENCE / "raw-metrics"

WORKFLOW_ASSETS = (
    (
        "submission/flightguard-nominal-envelope-demo-v2.mp4",
        "a5f13ea90ed64468299e925721607c2a2e896efc33fc99213f50cb0fa50799fd",
        17_428_715,
        (2_100, 1_280, 720, 10.0),
    ),
    (
        "submission/genesis-nominal-visual-replay.mp4",
        "adc0ea528b611e55dca006d220c30ef935f32448f6b935b7b6c1a33cd9d9fbce",
        3_717_464,
        (500, 1_280, 720, 10.0),
    ),
)

STATIC_FILES = (
    "docs/technical-report.md",
    "submission/video-script.md",
    "demo/faultfork/index.html",
    "demo/faultfork/app.js",
    "demo/faultfork/styles.css",
)
RENDERER_ASSET = (
    "scripts/render_submission_video.py",
    "a0a17d91e15c92f8541da594c7c2ca04b97ce7c5326f61b08436798caace35cd",
    26_993,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path.relative_to(ROOT)}")
    return value


def equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_video(
    errors: list[str],
    relative: str,
    expected_sha: str,
    expected_size: int,
    expected_meta: tuple[int, int, int, float],
) -> int:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing workflow asset: {relative}")
        return 0
    equal(errors, f"size {relative}", path.stat().st_size, expected_size)
    equal(errors, f"SHA {relative}", sha256(path), expected_sha)
    if cv2 is None:
        errors.append(f"OpenCV unavailable for video metadata: {relative}")
        return 0
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            errors.append(f"cannot open workflow video: {relative}")
            return 0
        actual = (
            int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT))),
            int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH))),
            int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))),
            float(capture.get(cv2.CAP_PROP_FPS)),
        )
    finally:
        capture.release()
    equal(errors, f"video frames/size {relative}", actual[:3], expected_meta[:3])
    if abs(actual[3] - expected_meta[3]) > 1e-6:
        errors.append(f"video fps {relative}: expected {expected_meta[3]}, got {actual[3]}")
    return actual[0]


def main() -> int:
    errors: list[str] = []
    documents: dict[str, dict[str, Any]] = {}

    for name, expected_sha in EXPECTED_SHA256.items():
        path = EVIDENCE / name
        if not path.is_file():
            errors.append(f"missing evidence: submission/evidence/{name}")
            continue
        actual_sha = sha256(path)
        if actual_sha != expected_sha:
            errors.append(f"SHA mismatch: {name} expected {expected_sha}, got {actual_sha}")
            continue
        try:
            documents[name] = load_object(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid JSON: {name}: {exc}")

    raw_documents: dict[str, dict[str, Any]] = {}
    for relative, expected_sha in RAW_METRICS_SHA256.items():
        path = RAW_METRICS / relative
        if not path.is_file():
            errors.append(f"missing raw metric: submission/evidence/raw-metrics/{relative}")
            continue
        actual_sha = sha256(path)
        if actual_sha != expected_sha:
            errors.append(f"raw metric SHA mismatch: {relative} expected {expected_sha}, got {actual_sha}")
            continue
        try:
            raw_documents[relative] = load_object(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid raw metric JSON: {relative}: {exc}")

    if len(documents) == len(EXPECTED_SHA256):
        envelope = documents["verified-flight-envelope-aggregate.json"]
        equal(errors, "envelope simulation-only", envelope.get("simulation_only"), True)
        equal(errors, "envelope existing-metrics-only", envelope.get("generated_from_existing_metrics_only"), True)
        equal(errors, "envelope source commit", envelope.get("source_commit"), "5f56f9ca3bd236f752844d2e3518276d9f494d8c")

        mission = envelope["heldout_three_gate_mission"]["aggregate"]
        equal(errors, "paired heldout course contexts", mission.get("paired_course_contexts"), 384)
        equal(errors, "method episodes", mission.get("method_episodes"), 1_152)
        equal(errors, "mission all finite", mission.get("all_fields_finite"), True)
        equal(errors, "mission one Radeon", mission.get("all_runs_one_visible_radeon"), True)
        equal(errors, "mission source statuses", mission.get("all_source_status_pass"), True)
        equal(errors, "mission saturation field present", mission.get("motor_saturation_recorded_in_source_metrics"), False)
        equal(errors, "mass min/max", (mission.get("mass_scale_min"), mission.get("mass_scale_max")), (0.8004579544067383, 1.1993319988250732))
        equal(errors, "thrust min/max", (mission.get("thrust_scale_min"), mission.get("thrust_scale_max")), (0.8060941696166992, 1.1986122131347656))
        equal(errors, "wind max", mission.get("wind_acceleration_norm_max_mps2"), 0.5982784032821655)
        equal(errors, "delay min/max", (mission.get("action_delay_steps_min"), mission.get("action_delay_steps_max")), (0, 6))
        equal(errors, "dropout-minus-mean-terminal", mission.get("dropout_minus_mean_terminal_step_by_seed"), [534.2578125, 532.53125, 532.6953125])

        for method in ("constant_velocity", "hold_last", "learned"):
            result = mission["per_method"][method]
            equal(errors, f"{method} evaluated envs", result.get("evaluated_envs"), 384)
            equal(errors, f"{method} mission successes", result.get("mission_success_count"), 384)
            equal(errors, f"{method} gate passes", result.get("gate_passes_total"), 1_152)
            for field in ("mission_failure_count", "strike_count", "terminal_failure_count", "unfinished_count"):
                equal(errors, f"{method} {field}", result.get(field), 0)

        claim = envelope["claim_boundary"]
        for key in (
            "continuous_envelope_guarantee_claim",
            "dropout_recovery_claim",
            "learned_superiority_claim",
            "real_flight_claim",
            "safety_or_certification_claim",
            "sim_to_real_claim",
        ):
            equal(errors, f"claim boundary {key}", claim.get(key), False)

        collector = envelope["training_distribution_collector"]["aggregate"]
        if len(raw_documents) == len(RAW_METRICS_SHA256):
            mission_raw = [
                raw_documents[f"heldout-three-gate-mission/seed{seed}-metrics.json"]
                for seed in (303, 304, 305)
            ]
            collector_raw = [
                raw_documents[f"training-collector/seed{seed}-metrics.json"]
                for seed in (303, 304, 305)
            ]

            raw_paired_contexts = sum(int(item["pairs"]) for item in mission_raw)
            raw_method_episodes = sum(int(item["total_envs"]) for item in mission_raw)
            equal(errors, "raw paired heldout course contexts", raw_paired_contexts, 384)
            equal(errors, "raw method episodes", raw_method_episodes, 1_152)
            equal(errors, "raw mission statuses", [item["status"] for item in mission_raw], ["PASS"] * 3)
            equal(errors, "raw mission visible GPU count", [item["visible_gpu_count"] for item in mission_raw], [1, 1, 1])
            equal(errors, "raw mission GPU names", [item["gpu_name"] for item in mission_raw], ["AMD Radeon Graphics"] * 3)
            equal(
                errors,
                "raw mission integrity",
                [item["integrity"]["checks"]["all_tracked_tensors_finite"] for item in mission_raw],
                [True, True, True],
            )
            for item in mission_raw:
                for method_name, finite_fields in item["integrity"]["finite_by_method"].items():
                    equal(
                        errors,
                        f"raw mission finite fields seed {item['seed']} {method_name}",
                        all(finite_fields.values()),
                        True,
                    )
            for method in ("constant_velocity", "hold_last", "learned"):
                method_rows = [item["methods"][method] for item in mission_raw]
                success = sum(int(row["mission_success_count"]) for row in method_rows)
                gates = sum(int(row["gate_passes_total"]) for row in method_rows)
                equal(errors, f"raw {method} mission successes", success, 384)
                equal(errors, f"raw {method} gate passes", gates, 1_152)
                for field in ("mission_failure_count", "strike_count", "terminal_failure_count", "unfinished_count"):
                    equal(
                        errors,
                        f"raw {method} {field}",
                        sum(int(row[field]) for row in method_rows),
                        0,
                    )
                equal(
                    errors,
                    f"raw/aggregate {method} mission successes",
                    success,
                    mission["per_method"][method]["mission_success_count"],
                )
                equal(
                    errors,
                    f"raw/aggregate {method} gate passes",
                    gates,
                    mission["per_method"][method]["gate_passes_total"],
                )

            raw_survivors = [int(item["collector"]["survivor_count"]) for item in collector_raw]
            equal(errors, "raw collector survivors by seed", raw_survivors, [63, 62, 61])
            equal(errors, "raw collector survivors total", sum(raw_survivors), 186)
            equal(
                errors,
                "raw collector visible GPU count",
                [item["single_gpu_proof"]["visible_gpu_count"] for item in collector_raw],
                [1, 1, 1],
            )
            equal(
                errors,
                "raw collector GPU names",
                [item["single_gpu_proof"]["gpu_name"] for item in collector_raw],
                ["AMD Radeon Graphics"] * 3,
            )
            for item in collector_raw:
                seed = item["args"]["seed"]
                equal(errors, f"raw collector status seed {seed}", item["status"], "PASS")
                equal(
                    errors,
                    f"raw collector finite seed {seed}",
                    all(field["all"] for field in item["collector"]["finite"].values()),
                    True,
                )
                equal(
                    errors,
                    f"raw collector applied saturation seed {seed}",
                    item["collector"]["motor_saturation"]["applied_action"]["max_per_env_fraction"],
                    0.0,
                )
            equal(errors, "raw/aggregate paired contexts", raw_paired_contexts, mission["paired_course_contexts"])
            equal(errors, "raw/aggregate method episodes", raw_method_episodes, mission["method_episodes"])
            equal(errors, "raw/aggregate collector survivors", sum(raw_survivors), collector["survivors"])

        equal(errors, "collector environments", collector.get("environments"), 192)
        equal(errors, "collector survivors", collector.get("survivors"), 186)
        equal(errors, "collector survivor fraction", collector.get("survivor_fraction"), 0.96875)
        equal(errors, "collector all finite", collector.get("all_fields_finite"), True)
        equal(errors, "collector one Radeon", collector.get("all_runs_one_visible_radeon"), True)
        equal(errors, "collector applied saturation", collector.get("max_applied_action_per_env_saturation_fraction"), 0.0)

        scaling = documents["radeon-formal-scaling.json"]["scaling"]
        summaries = scaling["env_summaries"]
        equal(errors, "scaling status", scaling.get("status"), "PASS")
        equal(errors, "scaling transitions", scaling.get("total_measured_transitions"), 2_227_200)
        equal(errors, "scaling env counts", [item["env_count"] for item in summaries], [32, 128, 256, 512])
        equal(errors, "scaling throughput", [item["mean_transitions_per_s"] for item in summaries], [4632.582556654058, 18354.411592309174, 36383.01129648785, 74246.46385791198])
        equal(errors, "scaling speedup", summaries[-1]["speedup_vs_32_envs"], 16.027013647337444)
        equal(errors, "scaling efficiency", summaries[-1]["parallel_efficiency_vs_32_envs"], 1.0016883529585903)

        v4 = documents["v4-summary.json"]
        equal(errors, "v4 status", v4.get("status"), "FAIL")
        equal(errors, "v4 Patch/Action/Raw/Cal", [v4["metrics"][arm]["fault"]["mission_success_count"] for arm in ("CausalIMUPatch", "ActionOnly", "RawStrapdown", "CalibratedStrapdown")], [11, 0, 33, 32])

        v5 = documents["v5-summary.json"]
        equal(errors, "v5 formal eligibility", v5.get("formal_claim_eligible"), False)
        equal(errors, "v5 award eligibility", v5.get("award_evidence_eligible"), False)

        v6 = documents["v6-checkpoint-30.json"]
        lanes = v6.get("lanes", [])
        equal(errors, "v6 status", v6.get("status"), "FAIL")
        equal(errors, "v6 admitted lanes", v6.get("admitted_lane_count"), 0)
        equal(errors, "v6 exact-Cal fallback", sum(all(lane["fallback_integrity_checks"].values()) for lane in lanes), 12)

        terminal = documents["capture-terminal.json"]
        equal(errors, "capture status", terminal.get("status"), "complete")
        equal(errors, "capture jobs", [job.get("name") for job in terminal.get("completed_jobs", [])], ["capture-checkpoint-30", "capture-checkpoint-31", "capture-checkpoint-32"])

        auditor = documents["frozen-claim-auditor-benchmark.json"]
        equal(errors, "auditor status", auditor.get("status"), "PASS")
        equal(errors, "auditor confusion", [auditor["confusion"][key] for key in ("true_positive", "true_negative", "false_positive", "false_negative")], [1, 3, 0, 0])

    for relative in STATIC_FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty submission file: {relative}")

    renderer_relative, renderer_sha, renderer_size = RENDERER_ASSET
    renderer_path = ROOT / renderer_relative
    if not renderer_path.is_file():
        errors.append(f"missing renderer: {renderer_relative}")
    else:
        equal(errors, "renderer size", renderer_path.stat().st_size, renderer_size)
        equal(errors, "renderer SHA", sha256(renderer_path), renderer_sha)

    video_frames: dict[str, int] = {}
    for relative, expected_sha, expected_size, expected_meta in WORKFLOW_ASSETS:
        video_frames[relative] = check_video(errors, relative, expected_sha, expected_size, expected_meta)

    if errors:
        print("FlightGuard judge smoke: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("FlightGuard judge smoke: PASS")
    print("raw metrics 6/6 | aggregate SHA c7ca6e460e967c3070736d8120bd918a3c489f1e7d62a3ae933ab631af827f58")
    print("nominal envelope | 384 paired contexts | 1152 method episodes | every method 384/384")
    print("mission integrity | 0 strikes | 0 mission/terminal failures | 0 unfinished | all finite")
    print("collector | 186/192 survivors | all tracked fields finite | applied saturation max 0.0")
    print("sampled ranges | mass 0.80046-1.19933 | thrust 0.80609-1.19861 | wind 0-0.59828 m/s^2 | delay 0-6")
    print("Radeon | 2,227,200 transitions | 4,632.58 -> 74,246.46 transitions/s | 16.027013647337444x")
    print(f"workflow assets | reviewer video {video_frames['submission/flightguard-nominal-envelope-demo-v2.mp4']}/2100 | Genesis clip {video_frames['submission/genesis-nominal-visual-replay.mp4']}/500")
    print("boundaries | simulation-only | sampled, not continuous | method replicas tie | no dropout-recovery claim")
    print("retained lineage | v4 FAIL | v5 award-ineligible | v6 0/12 admitted with exact-Cal fallback")
    return 0


if __name__ == "__main__":
    sys.exit(main())
