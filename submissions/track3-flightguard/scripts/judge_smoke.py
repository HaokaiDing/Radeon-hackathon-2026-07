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
    "v4-summary.json": "4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b",
    "v5-summary.json": "d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034",
    "v6-checkpoint-30.json": "905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678",
    "v6-audit-receipt.json": "521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1",
    "capture-terminal.json": "923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be",
    "radeon-formal-scaling.json": "98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072",
    "frozen-claim-auditor-benchmark.json": "ccbf38ef7aa36571c3f2433d5f4e9d54b1dd1de7cc2e8f93f2291ccc816f83f7",
}
AUDITOR_FILES = (
    ("scripts/evaluate_frozen_claim_constraints.py", "33c58e5ecf3c861ff931421c488fbdbb3293f47cbb9edd7164d27f025931abe9", 16_259),
    ("tests/test_evaluate_frozen_claim_constraints.py", "73160247493eb0ce5148c3c5d313f7798d6d08ee1b9bd4ea9504743536d9e49e", 8_958),
)
DEMO_FILES = ("demo/faultfork/index.html", "demo/faultfork/app.js", "demo/faultfork/styles.css", "submission/flightguard-faultfork-demo.mp4")
WORKFLOW_ASSETS = (
    ("submission/flightguard-genesis-workflow-demo.mp4", "37924b5e3ef81a122c2ef5a76edb40ed9db0fd38aba2dbb08fb153b8b1fb0ba0", 18_873_354, (2_100, 1_280, 720, 10.0)),
    ("submission/genesis-nominal-visual-replay.mp4", "adc0ea528b611e55dca006d220c30ef935f32448f6b935b7b6c1a33cd9d9fbce", 3_717_464, (500, 1_280, 720, 10.0)),
    ("scripts/render_submission_video.py", "1facba35683e7e3136b66ccab20dcfe83c173e821eab5e1950c397835b9ac7f4", 25_819, None),
    ("scripts/render_genesis_submission_clips_amd.py", "e48a670525cce608e4d158bcbc2e9c7727a724471f75b6646adee20b63509e91", 19_879, None),
)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()

def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path.relative_to(ROOT)}")
    return value

def check_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")

def main() -> int:
    errors: list[str] = []
    documents: dict[str, dict[str, Any]] = {}
    for name, expected in EXPECTED_SHA256.items():
        path = EVIDENCE / name
        if not path.is_file():
            errors.append(f"missing evidence: submission/evidence/{name}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"SHA mismatch: {name} expected {expected}, got {actual}")
            continue
        try:
            documents[name] = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"invalid JSON: {name}: {exc}")

    if len(documents) == len(EXPECTED_SHA256):
        v4 = documents["v4-summary.json"]
        check_equal(errors, "v4 status", v4.get("status"), "FAIL")
        for arm, expected in (("CausalIMUPatch", 11), ("ActionOnly", 0), ("RawStrapdown", 33), ("CalibratedStrapdown", 32)):
            check_equal(errors, f"v4 {arm} fault successes", v4["metrics"][arm]["fault"]["mission_success_count"], expected)
        check_equal(errors, "v4 failure reduction", v4["capability_effect"]["patch_vs_action_only_failure_reduction_fraction"], 0.3055555555555556)

        v5 = documents["v5-summary.json"]
        check_equal(errors, "v5 status", v5.get("status"), "PASS")
        check_equal(errors, "v5 formal claim eligibility", v5.get("formal_claim_eligible"), False)
        check_equal(errors, "v5 award evidence eligibility", v5.get("award_evidence_eligible"), False)
        check_equal(errors, "v5 extension permission", v5.get("formal_extension_permitted"), False)
        for arm in ("CausalIMUPatch", "CalibratedStrapdown"):
            check_equal(errors, f"v5 {arm} fault successes", v5["metrics"][arm]["fault"]["mission_success_count"], 10)
            check_equal(errors, f"v5 {arm} nominal successes", v5["metrics"][arm]["nominal"]["mission_success_count"], 12)
        check_equal(errors, "v5 Patch-Cal operational identity", v5["integrity"]["checks"]["fault_patch_calibrated_operational_trace_raw_bit_exact"], True)

        v6 = documents["v6-checkpoint-30.json"]
        lanes = v6.get("lanes", [])
        check_equal(errors, "v6 status", v6.get("status"), "FAIL")
        check_equal(errors, "v6 checkpoint", v6.get("checkpoint_seed"), 30)
        check_equal(errors, "v6 lane count", len(lanes), 12)
        check_equal(errors, "v6 admitted lanes", v6.get("admitted_lane_count"), 0)
        check_equal(errors, "v6 ranks", [lane["full_fit_certificate"]["numerical_rank"] for lane in lanes], [8] * 12)
        check_equal(errors, "v6 sigma minimum", min(lane["full_fit_certificate"]["normalized_sigma_ratio"] for lane in lanes), 0.019169591096042157)
        check_equal(errors, "v6 sigma maximum", max(lane["full_fit_certificate"]["normalized_sigma_ratio"] for lane in lanes), 0.0321526465925691)
        check_equal(errors, "v6 split-half passes", sum(bool(lane["split_half_stability"]["passed"]) for lane in lanes), 0)
        check_equal(errors, "v6 delta-v RMSE passes", sum(bool(lane["scientific_checks"]["delta_velocity_rmse_ratio_at_most_0_90"]) for lane in lanes), 0)
        check_equal(errors, "v6 rotation RMSE passes", sum(bool(lane["scientific_checks"]["rotation_rmse_ratio_at_most_0_90"]) for lane in lanes), 0)
        check_equal(errors, "v6 delta-v q95 passes", sum(bool(lane["scientific_checks"]["delta_velocity_q95_ratio_at_most_1_0"]) for lane in lanes), 3)
        check_equal(errors, "v6 rotation q95 passes", sum(bool(lane["scientific_checks"]["rotation_q95_ratio_at_most_1_0"]) for lane in lanes), 3)
        check_equal(errors, "v6 exact-Cal fallback lanes", sum(all(lane["fallback_integrity_checks"].values()) for lane in lanes), 12)

        audit = documents["v6-audit-receipt.json"]
        check_equal(errors, "v6 audit rc", audit.get("rc"), 0)
        check_equal(errors, "v6 audit stderr", audit.get("stderr"), "")
        check_equal(errors, "v6 audit result", audit["result"].get("status"), "FAIL")
        check_equal(errors, "v6 audit output binding", audit["output"].get("sha256"), EXPECTED_SHA256["v6-checkpoint-30.json"])

        terminal = documents["capture-terminal.json"]
        check_equal(errors, "capture status", terminal.get("status"), "complete")
        check_equal(errors, "capture operational status", terminal.get("operational_status"), "COMPLETE")
        check_equal(errors, "capture jobs", [job.get("name") for job in terminal.get("completed_jobs", [])], ["capture-checkpoint-30", "capture-checkpoint-31", "capture-checkpoint-32"])

        scaling = documents["radeon-formal-scaling.json"]
        summaries = scaling["scaling"]["env_summaries"]
        check_equal(errors, "scaling status", scaling.get("status"), "PASS")
        check_equal(errors, "scaling inner status", scaling["scaling"].get("status"), "PASS")
        check_equal(errors, "scaling transitions", scaling["scaling"].get("total_measured_transitions"), 2_227_200)
        check_equal(errors, "scaling environment counts", [item["env_count"] for item in summaries], [32, 128, 256, 512])
        check_equal(errors, "scaling throughput", [item["mean_transitions_per_s"] for item in summaries], [4632.582556654058, 18354.411592309174, 36383.01129648785, 74246.46385791198])
        check_equal(errors, "scaling speedup", summaries[-1]["speedup_vs_32_envs"], 16.027013647337444)
        check_equal(errors, "scaling parallel efficiency", summaries[-1]["parallel_efficiency_vs_32_envs"], 1.0016883529585903)
        check_equal(errors, "scaling acceptance", scaling["scaling"]["performance_acceptance"].get("achieved"), True)

        auditor = documents["frozen-claim-auditor-benchmark.json"]
        check_equal(errors, "auditor schema", auditor.get("schema_version"), "flightguard-frozen-claim-auditor-benchmark-v1")
        check_equal(errors, "auditor status", auditor.get("status"), "PASS")
        check_equal(
            errors,
            "auditor source binding",
            auditor.get("source", {}).get("sha256"),
            AUDITOR_FILES[0][1],
        )
        check_equal(
            errors,
            "auditor scope",
            auditor.get("scope"),
            {
                "name": "frozen 4-case synthetic corpus",
                "case_count": 4,
                "simulation_only": True,
                "robot_capability_claim": False,
                "safety_claim": False,
                "general_accuracy_claim": False,
            },
        )
        expected_cases = [
            ("radeon_fixed_r5_scaling", "ACCEPT", "ACCEPT", True, EXPECTED_SHA256["radeon-formal-scaling.json"]),
            ("v4_repair_claim", "REJECT", "REJECT", True, EXPECTED_SHA256["v4-summary.json"]),
            ("v5_incremental_capability_claim", "REJECT", "REJECT", True, EXPECTED_SHA256["v5-summary.json"]),
            ("v6_observer_admission_claim", "REJECT", "REJECT", True, EXPECTED_SHA256["v6-checkpoint-30.json"]),
        ]
        actual_cases = [
            (
                case.get("case_id"),
                case.get("decision"),
                case.get("expected_label"),
                case.get("correct"),
                case.get("artifact", {}).get("sha256"),
            )
            for case in auditor.get("cases", [])
        ]
        check_equal(errors, "auditor cases/labels/artifact bindings", actual_cases, expected_cases)
        check_equal(
            errors,
            "auditor confusion",
            auditor.get("confusion"),
            {
                "true_positive": 1,
                "true_negative": 3,
                "false_positive": 0,
                "false_negative": 0,
                "precision": 1.0,
                "recall": 1.0,
                "specificity": 1.0,
                "accuracy": 1.0,
                "false_accept_count": 0,
                "false_accept_rate": 0.0,
            },
        )
        check_equal(
            errors,
            "auditor maximum decision latency ns",
            auditor.get("decision_latency_ns", {}).get("maximum"),
            37_380,
        )

    verified_auditor_files = 0
    for relative, expected_sha, expected_size in AUDITOR_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing auditor file: {relative}")
            continue
        error_count = len(errors)
        check_equal(errors, f"auditor file size {relative}", path.stat().st_size, expected_size)
        check_equal(errors, f"auditor file SHA {relative}", sha256(path), expected_sha)
        if len(errors) == error_count:
            verified_auditor_files += 1

    present_demo = 0
    for relative in DEMO_FILES:
        path = ROOT / relative
        if path.is_file() and path.stat().st_size > 0:
            present_demo += 1
        else:
            errors.append(f"missing or empty demo file: {relative}")

    verified_workflow = 0
    video_frames: dict[str, int] = {}
    for relative, expected_sha, expected_size, expected_video in WORKFLOW_ASSETS:
        error_count = len(errors)
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing workflow asset: {relative}")
            continue
        check_equal(errors, f"workflow asset size {relative}", path.stat().st_size, expected_size)
        check_equal(errors, f"workflow asset SHA {relative}", sha256(path), expected_sha)
        if expected_video is not None:
            if cv2 is None:
                errors.append(f"OpenCV unavailable for video metadata: {relative}")
            else:
                capture = cv2.VideoCapture(str(path))
                try:
                    if not capture.isOpened():
                        errors.append(f"cannot open workflow video: {relative}")
                    else:
                        actual_video = (
                            int(round(capture.get(cv2.CAP_PROP_FRAME_COUNT))),
                            int(round(capture.get(cv2.CAP_PROP_FRAME_WIDTH))),
                            int(round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))),
                            float(capture.get(cv2.CAP_PROP_FPS)),
                        )
                        video_frames[relative] = actual_video[0]
                        check_equal(errors, f"video frames/size {relative}", actual_video[:3], expected_video[:3])
                        if abs(actual_video[3] - expected_video[3]) > 1e-6:
                            errors.append(f"video fps {relative}: expected {expected_video[3]!r}, got {actual_video[3]!r}")
                finally:
                    capture.release()
        if len(errors) == error_count:
            verified_workflow += 1

    if errors:
        print("FlightGuard judge smoke: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("FlightGuard judge smoke: PASS")
    print(f"frozen evidence 7/7 | claim checks PASS | auditor files {verified_auditor_files}/2 | demo files {present_demo}/4 | workflow assets {verified_workflow}/4")
    print(f"60-second path 1/5 | Genesis workflow video {video_frames['submission/flightguard-genesis-workflow-demo.mp4']}/2100 | Genesis clip {video_frames['submission/genesis-nominal-visual-replay.mp4']}/500")
    print("60-second path 2/5 | one-Radeon fixed-r5 intra-device scaling 16.027013647337444x")
    print("60-second path 3/5 | synthetic 4-case auditor: 1 ACCEPT / 3 REJECT | TP=1 TN=3 FP=0 FN=0 | max=37.38 us")
    print("60-second path 4/5 | Genesis draft PR #3159 is open, draft, unmerged, and software-only")
    print("60-second path 5/5 | v4 scientific FAIL | v5 incremental claim rejected | v6 observer rejected with 12/12 exact-Cal fallback")
    return 0

if __name__ == "__main__":
    sys.exit(main())
