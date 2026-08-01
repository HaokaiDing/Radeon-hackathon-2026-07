# FlightGuard Track 3 Technical Report

## Project information

- **Project:** FlightGuard
- **Submission framing:** Radeon-native fail-closed embodied-flight claim auditor
- **Track:** Track 3 — Physical AI Challenge
- **Execution scope:** Genesis simulation on one AMD Radeon GPU through PyTorch ROCm
- **Evidence scope:** simulation-only; single T265 development event; causal only relative to a ROS bag record-time availability proxy

## Project overview

Embodied-AI demos often report the best downstream score while hiding whether a proposed mechanism is identifiable, stable, or even different from its fallback. FlightGuard packages the opposite behavior: frozen inputs, matched simulation histories, device-native recurrence checks, preregistered scientific gates, exact fallback, and an auditable stop decision.

The current submission does not claim a new flight estimator. It demonstrates an evidence pipeline that rejected three increasingly constrained mechanisms without rewriting the result.

## Motivation and application

Flight stacks combine simulators, sensor transforms, estimators, controllers, and accelerators. A friendly aggregate can arise from an implementation mismatch, an always-on fallback, or an unidentifiable latent state. FlightGuard targets robotics teams that need to know whether a proposed change adds capability before investing in hardware testing.

The practical output is a compact decision package: frozen summaries, exact hashes, deterministic figures, a static demo, and explicit claim exclusions. It supports review, experiment triage, and reproducibility; it is not a safety case.

## Technical architecture

The v6 candidate is a frozen eight-state observer with state order `[b_ax, b_ay, b_az, b_gx, b_gy, b_gz, delta_roll, delta_pitch]`. It consumes native IMU samples plus record-time VIO pose increments. The schedule is fixed:

- fit on steps 0–199;
- holdout on steps 200–299 with zero parameter updates;
- freeze at step 300;
- use exact calibrated fallback on any rejected lane.

Each run is bound to a frozen legacy protocol, seed bank, configuration, and checkpoint-specific 800-step sensor-error bank. The capture queue executes checkpoints serially on one Radeon. Before observer metrics are trusted, the evaluator repeats the raw-to-delivered transform on Radeon and checks:

1. delivered force and gyro recurrence by raw bits;
2. disabled-transform no-op by raw bits;
3. enabled-transform kill magnitude for both force and gyro.

The lane gate then requires rank 8, normalized sigma ratio ≥ 1e-3, split-half stability, Δv RMSE ≤ 0.90×Cal, rotation RMSE ≤ 0.90×Cal, and both q95 ratios ≤ 1.0. A checkpoint needs at least 9/12 admitted lanes; the three-checkpoint aggregate would need at least 30/36.

## AMD hardware and software use

The frozen capture terminal records three completed jobs on `AMD Radeon Graphics`. Execution used a single visible GPU and a serial queue. Genesis generated the capture traces through the PyTorch HIP/ROCm path. The corrected recurrence evaluator also replays the sensor transform on Radeon, avoiding two observed CPU/Radeon half-bin rounding differences while retaining raw-bit checks.

A separate frozen scaling run measured the fixed r5 nominal deployed simulation pipeline on one Radeon. It processed 2,227,200 measured transitions across 32, 128, 256, and 512 environments. This is throughput and utilization evidence only; it does not change the v4/v5/v6 scientific verdicts.

## Innovation

The contribution is the integration of scientific falsification with an accelerator-native embodied simulation pipeline:

- device-native recurrence before scientific interpretation;
- no-op and kill-magnitude self-tests before an expensive run;
- lane-level identifiability and holdout gates;
- exact-Cal fallback rather than silent candidate substitution;
- a mandatory stop rule that preserves negative evidence;
- deterministic evidence rendering directly from verified JSON.

This changes the deliverable from “a mechanism that appears to work” to “a reviewable statement of what the mechanism did and did not establish.”

## Evaluation and exact results

### v4 — causal IMU repair

Across 36 fault episodes per arm, CausalIMUPatch succeeded 11 times, ActionOnly 0, RawStrapdown 33, and CalibratedStrapdown 32. Patch failure reduction versus ActionOnly was 30.56%, below the preregistered 50% gate, and Patch was worse than Raw and Cal on required metrics. Verdict: **scientific FAIL**.

### v5 — residual-q95 quarantine scout

Across 12 fault episodes per arm, Patch succeeded 10 times, ActionOnly 0, and Cal 10. Patch and Cal both succeeded on 12/12 nominal episodes. Nineteen post-onset operational fields were raw-bit exact for Patch and Cal at each checkpoint. The development gates passed, but incremental capability was 0. Verdict: **development PASS, award-ineligible**.

### v6 — frozen observer observability audit

Checkpoint 30 contained 12 lanes. Recurrence, no-op, and kill checks passed. Every lane had numerical rank 8; normalized sigma ratios ranged from 0.019169591096042157 to 0.0321526465925691. The remaining gates failed:

- split-half stability: 0/12;
- Δv RMSE ≤ 0.90×Cal: 0/12;
- rotation RMSE ≤ 0.90×Cal: 0/12;
- Δv q95 ≤ Cal: 3/12;
- rotation q95 ≤ Cal: 3/12.

No lane was admitted and all 12 used exact-Cal fallback. Verdict: **scientific FAIL; stop candidate A**. Checkpoints 31 and 32 were not audited after the checkpoint-30 stop condition.

### Radeon scaling — fixed r5 nominal deployed pipeline

The frozen one-Radeon run achieved the following mean throughput:

| Environments | Mean transitions/s | GPU-use mean | CV |
|---:|---:|---:|---:|
| 32 | 4,632.582556654058 | 77.3544% | 0.003122105834443068 |
| 128 | 18,354.411592309174 | 76.2593% | 0.0009916172953886402 |
| 256 | 36,383.01129648785 | 77.0864% | 0.002506217057283922 |
| 512 | 74,246.46385791198 | 78.4684% | 0.0033317633931520337 |

The 512/32 speedup was 16.027013647337444× and parallel efficiency was 1.0016883529585903. GPU use reached 86%; maximum observed VRAM was 962,785,280 bytes. The preregistered throughput acceptance was achieved. These numbers describe only the simulation workload and one Radeon, not candidate-mechanism superiority.

## Reproducibility and evidence

The submission evidence directory contains byte-identical copies of the frozen summaries:

| File | SHA-256 |
|---|---|
| `submission/evidence/v4-summary.json` | `4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b` |
| `submission/evidence/v5-summary.json` | `d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034` |
| `submission/evidence/v6-checkpoint-30.json` | `905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678` |
| `submission/evidence/v6-audit-receipt.json` | `521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1` |
| `submission/evidence/capture-terminal.json` | `923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be` |
| `submission/evidence/radeon-formal-scaling.json` | `98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072` |

`scripts/build_award_figures.py` verifies the v4/v5/v6/scaling hashes, derives every plotted value from those JSON payloads, and writes deterministic SVG, CSV, and JSON outputs. The static demo foregrounds the three-case gate matrix and the separate Radeon throughput evidence; its animation and archived fault map remain explicitly illustrative.

`scripts/render_submission_video.py` reads the same four frozen JSON files and produced `submission/flightguard-faultfork-demo.mp4`: 1280×720, 10 fps, 2,100 frames, 210.0 seconds, requested codec `mp4v`, reported codec `FMP4`, captioned with no audio, size 19,375,892 bytes, SHA-256 `fc76e7b051c392274ca98627cc2c125727c7661a9545f67875a9593afc592c64`. It is a generated evidence explainer, not real-flight footage.

## Limitations and claim boundary

- Simulation-only; no hardware-in-the-loop or physical-flight validation.
- One T265 development event; no population-generalization claim.
- Causal only relative to ROS bag record-time availability, not global causality.
- No sim-to-real, real-flight repair, safety, certification, or formal-superiority claim.
- No upstream contribution claim.
- Radeon scaling is limited to the fixed r5 nominal deployed pipeline on one GPU; it is not estimator or repair superiority.
- The MP4 is a captioned simulation-evidence rendering with no audio, not a real-flight recording.

The negative v6 result is a result: under the frozen gate, the observer did not earn deployment beyond the calibrated baseline.

