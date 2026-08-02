# FlightGuard — Radeon-native fail-closed embodied-flight claim auditor

## 60-second Judge Path

From the competition repository root, enter the FlightGuard submission and run the evidence-only smoke check (Python standard library plus the project's existing OpenCV runtime; no GPU, simulator, training, or network access):

~~~bash
cd submissions/track3-flightguard && python3 scripts/judge_smoke.py
~~~

Expected result:

~~~text
FlightGuard judge smoke: PASS
frozen evidence 7/7 | claim checks PASS | auditor files 2/2 | demo files 4/4 | workflow assets 4/4
60-second path 1/5 | Genesis workflow video 2100/2100 | Genesis clip 500/500
60-second path 2/5 | one-Radeon fixed-r5 intra-device scaling 16.027013647337444x
60-second path 3/5 | synthetic 4-case auditor: 1 ACCEPT / 3 REJECT | TP=1 TN=3 FP=0 FN=0 | max=37.38 us
60-second path 4/5 | Genesis draft PR #3159 is open, draft, unmerged, and software-only
60-second path 5/5 | v4 scientific FAIL | v5 incremental claim rejected | v6 observer rejected with 12/12 exact-Cal fallback
~~~

This is the shortest review path through the submitted result:

1. **Genesis workflow video:** start with the 2,100-frame reviewer video and its bound 500-frame simulator replay.
2. **Radeon scaling ACCEPT:** the fixed r5 nominal workload processed 2,227,200 measured transitions and reached 16.027013647337444× intra-device speedup from 32 to 512 environments on one Radeon.
3. **Frozen synthetic auditor:** generic field constraints classify the four frozen cases as 1 ACCEPT / 3 REJECT with TP=1, TN=3, FP=0, FN=0 and a measured maximum decision latency of 37.38 µs.
4. **Upstream boundary:** Genesis draft PR #3159 is open, draft, unmerged, and software-only.
5. **Scientific boundary:** v4 remains a scientific FAIL, v5 adds no incremental capability, and v6 admits 0/12 lanes and returns exact-Cal fallback.

The smoke check verifies evidence already committed under submission/evidence/; it does not rerun the scientific campaigns. Continue with the [technical report](docs/technical-report.md), deterministic figures in submission/figures/, or the static demo command below.

## Primary reviewer video

The primary reviewer artifact is `submission/flightguard-genesis-workflow-demo.mp4`: 1280×720, 10 fps, 2,100 frames, 210.0 seconds, reported codec `FMP4`, no audio, 18,873,354 bytes, SHA-256 `37924b5e3ef81a122c2ef5a76edb40ed9db0fd38aba2dbb08fb153b8b1fb0ba0`.

Its 00:30–01:20 interval is a 50-second real Genesis truth-controller visual replay rendered directly from simulator state. The bound source clip is `submission/genesis-nominal-visual-replay.mp4`: fixed seed 5001, one simulation step per frame, terminal step 476, 24 padded frames, 500 total frames, SHA-256 `adc0ea528b611e55dca006d220c30ef935f32448f6b935b7b6c1a33cd9d9fbce`. The segment is simulation-only, visual-only, and metric-ineligible. It demonstrates the review workflow and nominal simulated motion; it does not demonstrate fault recovery, physical-flight performance, safety, sim-to-real transfer, or upstream contribution.

`submission/flightguard-faultfork-demo.mp4` remains the retained frozen-evidence explainer. It is no longer the primary reviewer video.

FlightGuard is a **simulation-only** embodied-flight evidence pipeline for AMD Track 3. It does not present another estimator as a winner. It turns a candidate flight claim into a sequence of frozen inputs, Radeon-native replays, preregistered gates, and machine-readable accept/reject evidence. When a mechanism cannot beat its calibrated fallback, the pipeline records the failure and stops expansion.

The current evidence contains three honest outcomes:

- **v4 scientific FAIL:** the patch recovered 11/36 fault episodes versus 0/36 for ActionOnly, but RawStrapdown and CalibratedStrapdown reached 33/36 and 32/36. Failure reduction versus ActionOnly was 30.56%, below the 50% gate.
- **v5 development PASS, award-ineligible:** Patch and CalibratedStrapdown both reached 10/12 fault successes and 12/12 nominal successes. Their 19 post-onset operational fields were raw-bit exact, so incremental capability was 0.
- **v6 scientific FAIL at checkpoint 30:** all 12 lanes had rank 8 and normalized sigma ratios from 0.019169591096042157 to 0.0321526465925691, but 0/12 passed split-half stability, 0/12 passed either RMSE ≤ 0.90×Cal gate, and only 3/12 passed each q95 gate. All 12 lanes therefore used exact-Cal fallback. Checkpoints 31 and 32 were not audited after the preregistered stop rule fired.
- **Radeon throughput evidence PASS:** the fixed r5 nominal deployed simulation pipeline processed 2,227,200 measured transitions on one Radeon. Mean throughput rose from 4,632.582556654058 transitions/s at 32 environments to 74,246.46385791198 at 512 environments: 16.027013647337444× speedup and 1.0016883529585903 parallel efficiency.

The frozen constraint auditor then evaluated those four already-frozen cases without simulator or GPU work. It returned 1 ACCEPT and 3 REJECT with TP=1, TN=3, FP=0, FN=0, accuracy=1.0, false-accept count 0, and maximum decision latency 37.38 µs. Accuracy 1.0 applies only to this frozen four-case synthetic corpus; it is not a robot-capability, safety, or general-accuracy claim.

This is the product: a claim auditor that keeps an unfavorable result intact while showing the measured compute path separately from candidate science.

## What it does

1. Freezes the legacy protocol, seed bank, observer configuration, and three 800-step sensor-error banks.
2. Captures exact native and estimator-delivered traces on one AMD Radeon GPU through PyTorch ROCm.
3. Replays the registered raw-to-delivered transform on Radeon and requires recurrence, disabled no-op, and enabled kill-magnitude checks to pass.
4. Fits a frozen eight-state pose-increment observer on steps 0–199, performs zero-update holdout on steps 200–299, and freezes at step 300.
5. Applies rank, conditioning, split-half, Δv, rotation, and q95 gates lane by lane.
6. Returns the calibrated baseline by exact identity whenever a lane is rejected, then stops the candidate when the checkpoint gate fails.

```text
frozen inputs
    │
    ▼
single-Radeon capture ──► raw-bit recurrence / no-op / kill checks
    │                                      │
    ▼                                      ▼
frozen observer fit                 fail closed on corruption
    │
    ▼
holdout qualification ──► admitted observer OR exact-Cal fallback
    │
    ▼
checkpoint gate ──► continue OR stop and preserve the negative result
```

## AMD Radeon and ROCm use

- Device reported by the run: `AMD Radeon Graphics`.
- Execution was restricted to one visible Radeon GPU and serialized behind the FlightGuard GPU lock.
- Genesis capture and the sensor-transform recurrence replay used the PyTorch HIP/ROCm path.
- Three checkpoint captures completed before scientific audit. Checkpoint 30 then failed the observability gate; the stop rule prevented checkpoint 31/32 audit and any downstream performance scout.
- The frozen Radeon scaling run covers only the fixed r5 nominal deployed simulation pipeline: 32/128/256/512 environments reached 4,632.582556654058 / 18,354.411592309174 / 36,383.01129648785 / 74,246.46385791198 transitions/s.
- Across those four workloads, GPU-use means were 77.3544% / 76.2593% / 77.0864% / 78.4684%; observed GPU use reached 86%, maximum VRAM was 962,785,280 bytes, and maximum throughput CV was 0.0033317633931520337.
- `scripts/benchmark_causal_falsifier_scaling_amd.py` remains a retained utility without a submitted scaling claim. `scripts/benchmark_radeon_formal_pipeline_amd.py` produced the frozen throughput evidence above; that evidence does not establish scientific superiority.

## Reproduce the submission figures

The packaged evidence is byte-for-byte copied from the frozen run summaries. The figure builder uses only the Python standard library and rejects unknown input hashes.

```bash
python3 scripts/build_award_figures.py \
  --v4 submission/evidence/v4-summary.json \
  --v5 submission/evidence/v5-summary.json \
  --v6 submission/evidence/v6-checkpoint-30.json \
  --scaling submission/evidence/radeon-formal-scaling.json \
  --output-dir /tmp/flightguard-figures
```

For the interactive static demo:

```bash
python3 -m http.server 8000 --directory demo/faultfork
```

Open `http://127.0.0.1:8000`. The flight motion is schematic. The archived fault-stratum explorer is explicitly non-claim evidence; it cannot alter the frozen v4/v5/v6 matrix or exported certificate.

## Frozen evidence

| Artifact | SHA-256 | Meaning |
|---|---|---|
| `submission/evidence/v4-summary.json` | `4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b` | v4 preregistered scientific FAIL |
| `submission/evidence/v5-summary.json` | `d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034` | v5 development-only, award-ineligible scout |
| `submission/evidence/v6-checkpoint-30.json` | `905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678` | v6 checkpoint-30 observability FAIL |
| `submission/evidence/v6-audit-receipt.json` | `521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1` | command, return code, and output binding for v6 audit |
| `submission/evidence/capture-terminal.json` | `923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be` | three completed Radeon capture jobs |
| `submission/evidence/radeon-formal-scaling.json` | `98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072` | fixed-pipeline one-Radeon throughput evidence |
| `scripts/evaluate_frozen_claim_constraints.py` | `33c58e5ecf3c861ff931421c488fbdbb3293f47cbb9edd7164d27f025931abe9` | generic frozen-field constraint evaluator |
| `tests/test_evaluate_frozen_claim_constraints.py` | `73160247493eb0ce5148c3c5d313f7798d6d08ee1b9bd4ea9504743536d9e49e` | decision isolation and fail-closed tests |
| `submission/evidence/frozen-claim-auditor-benchmark.json` | `ccbf38ef7aa36571c3f2433d5f4e9d54b1dd1de7cc2e8f93f2291ccc816f83f7` | frozen four-case synthetic benchmark result |

Original run paths are recorded inside the JSON artifacts. The submission copies do not replace or modify the run lineage.

Rerun the same four frozen decisions with one command; the latency samples are measured anew, so the rerun JSON is not expected to have the frozen result SHA:

```bash
python3 scripts/evaluate_frozen_claim_constraints.py \
  --expected-source-sha256 33c58e5ecf3c861ff931421c488fbdbb3293f47cbb9edd7164d27f025931abe9 \
  --output /tmp/frozen-claim-auditor-benchmark.json
```

## Results at a glance

| Campaign | Integrity result | Capability result | Claim status |
|---|---|---|---|
| v4 causal IMU repair | Raw evidence and registered banks matched | Patch 11/36; ActionOnly 0/36; Raw 33/36; Cal 32/36 | Scientific FAIL; no repair claim |
| v5 residual-q95 quarantine | 19 post-onset operational fields Patch↔Cal raw-bit exact | Patch 10/12 = Cal 10/12; nominal both 12/12 | Development PASS; incremental capability 0; award-ineligible |
| v6 frozen observer, cp30 | Recurrence, no-op, kill, rank, and sigma checks passed | 0/12 admitted; 12/12 exact-Cal fallback | Scientific FAIL; candidate stopped |
| Radeon scaling | Fixed r5 nominal deployed pipeline; one Radeon; 2,227,200 transitions | 4,632.58 → 74,246.46 transitions/s from 32 → 512 envs | Performance acceptance achieved; throughput evidence only |
| Frozen synthetic constraint audit | Four immutable artifact hashes; generic eq/ge/le constraints | 1 ACCEPT / 3 REJECT; TP=1, TN=3, FP=0, FN=0; max 37.38 µs | Accuracy 1.0 only on this four-case corpus |

Generated evidence views are in `submission/figures/`:

- `gate-matrix.svg`
- `v4-v5-fault-success.svg`
- `v6-lane-qualification.svg`
- `radeon-scaling.svg`
- `summary.csv`
- `summary.json`

## Upstream contribution

[Genesis draft PR #3159](https://github.com/Genesis-Embodied-AI/genesis-world/pull/3159) is a separate, software-only upstream contribution at commit `09b3e04132a15d6c842835829e277c9cbff4cce3`. Its scope is limited to aligning the AMD Docker default from PyTorch 2.6 to AMD's official PyTorch 2.8 image and adding a static regression test. The PR is open, draft, and unmerged, and it is not counted as robot-capability evidence. The 9.4 GB image was not pulled or built, so this submission makes no claim of container runtime success, acceptance, or merge.

## Claim boundary and limitations

- Simulation-only; no physical flight validation.
- One T265 development event informed the recorded availability pattern.
- “Causal” refers only to the ROS bag record-time availability proxy used by the paired simulation protocol.
- No sim-to-real, safety, certification, real-flight repair, population-generalization, or formal-superiority claim.
- v5 cannot support an incremental mechanism claim because Patch and Cal are operationally raw-bit exact after onset.
- v6 cannot support an observer claim because checkpoint 30 admitted no lanes; checkpoints 31 and 32 were intentionally not audited.
- The upstream PR is open, draft, and unmerged; it is software-only evidence and does not alter any v4/v5/v6 scientific verdict or support a robot-capability claim.
- The throughput result applies only to the fixed r5 nominal deployed simulation pipeline on one Radeon; it does not repair or override the v4/v5/v6 mechanism verdicts.
- The synthetic auditor result covers exactly four frozen cases; its accuracy is not a general benchmark and supports no robot-capability or safety claim.
- `submission/flightguard-genesis-workflow-demo.mp4` is the primary 210-second reviewer video. Its embedded Genesis segment is a simulation-only, visual-only, metric-ineligible nominal replay; it carries no fault-recovery, safety, sim-to-real, real-flight, or upstream claim.
- `submission/flightguard-faultfork-demo.mp4` remains a retained captioned evidence rendering, not physical-flight footage. It is 1280×720, 10 fps, 2,100 frames, 210.0 seconds, codec request `mp4v` / reported `FMP4`, no audio, 19,375,892 bytes, SHA-256 `fc76e7b051c392274ca98627cc2c125727c7661a9545f67875a9593afc592c64`.

## Repository map

- `src/flightguard/`: observer and causal IMU components.
- `scripts/`: Radeon/Genesis capture, evaluation, deterministic figure generation, and captioned-video rendering entry points.
- `tools/`: frozen-input, queue, and evidence builders.
- `demo/faultfork/`: static evidence-first demo with preserved flight animation.
- `docs/technical-report.md`: compact Track 3 technical report.
- `submission/video-script.md`: 210-second English narration and screen-action timeline.
- `submission/flightguard-genesis-workflow-demo.mp4`: primary verified 210-second reviewer video.
- `submission/genesis-nominal-visual-replay.mp4`: bound 50-second Genesis truth-controller visual replay used at 00:30–01:20.
- `submission/flightguard-faultfork-demo.mp4`: retained 210-second captioned frozen-evidence explainer.
- `submission/evidence/`: immutable evidence copies.
- `submission/figures/`: deterministic figures and machine-readable summaries, including Radeon throughput.

