# FlightGuard Track 3 Technical Report

## Project information

- **Project:** FlightGuard
- **Submission framing:** Radeon-Native Sampled Nominal Flight Envelope Verifier
- **Track:** Track 3 — Physical AI Challenge
- **Execution scope:** Genesis simulation on one AMD Radeon GPU through PyTorch ROCm
- **Evidence scope:** sampled nominal simulation evidence; no physical-flight, sim-to-real, safety, certification, or continuous-envelope claim

## Team member and contribution

- **Haokai Ding** — system design, implementation, experiments, evaluation, demo, and report.

## Datasets and evaluation inputs

FlightGuard uses procedural Genesis contexts rather than a learned training dataset. The nominal-envelope inputs are deterministic domain-randomized samples from seeds 303, 304, and 305. That heldout suite covers 384 paired three-gate course contexts; three registered method replicas produce 1,152 method episodes, and the training-distribution collector covers another 192 environments. A separate frozen Challenge Arena uses three preregistered seeds for 384 paired primary-adversarial contexts plus 192 paired retention-heldout contexts.

Across the heldout samples, observed mass scale spans 0.80046–1.19933, thrust scale 0.80609–1.19861, wind-acceleration norm 0–0.59828 m/s², and action delay 0–6 steps. These are observed sampled ranges, not a continuous hyper-rectangle guarantee or formal envelope certificate.

The nominal-envelope aggregate is frozen at `submission/evidence/verified-flight-envelope-aggregate.json`, SHA-256 `c7ca6e460e967c3070736d8120bd918a3c489f1e7d62a3ae933ab631af827f58`. The Challenge Arena aggregate is frozen at `submission/evidence/challenge-arena/challenge-arena-summary.json`, SHA-256 `91b18677fa9fcb5f05acead2aa3fb4324188b44173ea85fda75c67e2dcb129ee`. Each binds its source paths and hashes. Historical v4/v5/v6 sensor-fault artifacts remain as secondary falsification lineage.

## Project overview

FlightGuard is a Radeon-native application for reproducibly qualifying a simulated quadrotor controller over sampled off-nominal conditions. It generates deterministic mass, thrust, wind, delay, and gate-course contexts; runs three-gate missions in Genesis through PyTorch ROCm; checks mission and tensor-integrity outcomes; and exports hash-bound evidence that can be verified without rerunning the simulator.

The nominal-envelope result is positive: over 384 paired heldout course contexts, each registered replica completed 384/384 missions with zero strikes, terminal failures, or unfinished episodes. The Challenge Arena adds an intervention result: on the same paired contexts, changing only vertical controller gains raises primary-adversarial mission success from 194/384 to 371/384 and retention-heldout success from 121/192 to 192/192, with zero nominal-only wins. A separate training-distribution collector retained 186/192 environments with every tracked field finite and zero applied-action saturation.

## Motivation and application

Robotics teams need an inexpensive way to determine whether a controller remains usable across a defined sample of vehicle and environment variation before committing to hardware tests. FlightGuard turns that question into a repeatable Radeon simulation workload and a compact evidence package.

The target users are embodied-AI researchers and flight-control developers. The practical outputs are sampled nominal qualification, a paired before/after controller challenge, per-seed source metrics, one-Radeon performance measurements, deterministic figures, reviewer videos, and explicit exclusions. FlightGuard supports experiment triage and controller qualification in simulation; it is not a safety case.

## Technical architecture

The primary workflow has five stages:

1. Deterministically sample training-distribution and heldout domain parameters.
2. Run the Genesis quadrotor with the `robust_z` controller on one visible Radeon GPU.
3. Evaluate a three-gate course for three registered method replicas over seeds 303–305.
4. Check completion, strikes, terminal failures, unfinished episodes, field finiteness, and collector action saturation.
5. Freeze the source bindings and aggregate metrics for evidence-only verification.

The registered replicas `constant_velocity`, `hold_last`, and `learned` tie exactly in the nominal-envelope data. Therefore that branch supports the shared `robust_z` controller plus domain-randomized evaluator, not learned-method superiority. The Challenge Arena is a separate paired controller comparison: nominal PD (`kp_z=2.5`, `kd_z=2.0`) versus `robust_z` (`kp_z=8.0`, `kd_z=3.6`) with identical paired initial state, gates, domain parameters, and random streams.

The repository also contains a secondary falsification pipeline for v4/v5/v6 estimator candidates. It uses frozen protocols, no-op and kill-magnitude self-tests, lane-level observability gates, and exact calibrated fallback. Those candidates did not pass their scientific gates and are retained as limitations rather than used as the primary application claim.

## AMD hardware and software use

Every source mission and collector run reports exactly one visible `AMD Radeon Graphics`. Genesis executes the batched simulation through the PyTorch HIP/ROCm path. GPU jobs were serialized, and the frozen source metrics retain device identity, seed, domain profile, and integrity results.

A separate fixed-workload scaling run measured 2,227,200 transitions at 32, 128, 256, and 512 environments on one Radeon. Mean throughput increased from 4,632.582556654058 to 74,246.46385791198 transitions/s: 16.027013647337444× speedup and 1.0016883529585903 parallel efficiency. Maximum observed VRAM was 962,785,280 bytes.

## Innovation

FlightGuard combines four elements that are usually presented separately:

- a deterministic Physical-AI domain-randomization suite;
- a paired before/after controller challenge with exact no-op and kill-magnitude self-tests;
- a Radeon-native Genesis execution path with measured batched scaling;
- hash-bound, evidence-only review of mission and integrity outcomes.

The application value is the complete loop: sampled condition generation → Radeon simulation → mission qualification → frozen evidence. The retained v4/v5/v6 failures add a second contribution: the same project records when an attractive estimator mechanism does not earn a claim.

## Evaluation and exact results

### Challenge Arena — paired controller intervention

The Challenge Arena was frozen before the formal seeds were run. Each pair shares initial state, gate geometry, mass/thrust/wind/delay parameters, and random streams; only `kp_z` and `kd_z` change. The bit-exact no-op passes. A zero-action kill control achieves 0/8 successes and 10.506417 m maximum paired-active position divergence, confirming intervention sensitivity.

| Suite | Pairs | Nominal PD | `robust_z` | Delta | Nominal-only wins |
|---|---:|---:|---:|---:|---:|
| Primary adversarial | 384 | 194/384 (50.5208%) | 371/384 (96.6146%) | +177 (+46.0938 pp) | 0 |
| Retention heldout | 192 | 121/192 (63.0208%) | 192/192 (100%) | +71 (+36.9792 pp) | 0 |

Primary failures fall from 190 to 13 (93.1579% reduction), strikes from 178 to 13, and terminal failures from 190 to 13. Per-seed success deltas are +57, +58, and +62; all three are positive. All traces are finite and paired, every formal source reports one visible `AMD Radeon Graphics`, and maximum applied-action saturation is 0.0 for both arms. All 14 preregistered summary gates pass.

The 7-second side-by-side Genesis replay selects one deterministic frozen raw pair after aggregation by sorting `(seed, pair_index)`: seed 144856705, pair 0. Nominal collides at step 167 with 0/3 gates; `robust_z` completes 3/3 at step 479 without a strike. The clip is a visual replay of a raw metric pair; aggregate claims come from all 384 primary and 192 retention pairs.

### Nominal-envelope result — sampled heldout three-gate missions

Across 384 paired heldout course contexts and 1,152 method episodes:

- `constant_velocity`: 384/384 mission successes, 1,152 gate passes;
- `hold_last`: 384/384 mission successes, 1,152 gate passes;
- `learned`: 384/384 mission successes, 1,152 gate passes;
- all three: 0 strikes, 0 mission failures, 0 terminal failures, and 0 unfinished episodes;
- all tracked mission fields finite;
- every source run used exactly one visible Radeon GPU.

The methods tie exactly, so no learned-superiority claim is made. The configured one-step dropout starts at step 999, more than 532 steps after each seed's reported mean terminal step. Because the source does not expose maximum per-episode terminal step, this does not establish dropout recovery or prove every episode ended before step 999.

### Primary result — training-distribution collector

The collector retained 63/64, 62/64, and 61/64 environments for seeds 303, 304, and 305: 186/192 = 96.875%. Position, velocity, quaternion, angular velocity, issued action, and applied action were finite in every source run. Maximum per-environment applied-action saturation fraction was 0.0.

The heldout mission metrics contain no saturation field, so the saturation result is limited to the collector.

### Radeon scaling — fixed r5 deployed pipeline

| Environments | Mean transitions/s | GPU-use mean | CV |
|---:|---:|---:|---:|
| 32 | 4,632.582556654058 | 77.3544% | 0.003122105834443068 |
| 128 | 18,354.411592309174 | 76.2593% | 0.0009916172953886402 |
| 256 | 36,383.01129648785 | 77.0864% | 0.002506217057283922 |
| 512 | 74,246.46385791198 | 78.4684% | 0.0033317633931520337 |

The 512/32 speedup was 16.027013647337444×; parallel efficiency was 1.0016883529585903; GPU use reached 86%; maximum observed VRAM was 962,785,280 bytes. These measurements cover this fixed simulation workload on one Radeon.

### Retained falsification lineage

#### v4 — causal IMU repair

Across 36 fault episodes per arm, CausalIMUPatch succeeded 11 times, ActionOnly 0, RawStrapdown 33, and CalibratedStrapdown 32. Patch failure reduction versus ActionOnly was 30.56%, below the preregistered 50% gate. Verdict: **scientific FAIL**.

#### v5 — residual-q95 quarantine scout

Across 12 fault episodes per arm, Patch and Cal each succeeded 10 times under fault and 12/12 nominal. Nineteen post-onset operational fields were raw-bit exact. Verdict: **development PASS, award-ineligible; incremental capability 0**.

#### v6 — frozen observer observability audit

Checkpoint 30 contained 12 lanes. Every lane had numerical rank 8, but 0/12 passed split-half stability, 0/12 passed either RMSE ≤ 0.90×Cal gate, and only 3/12 passed each q95 gate. No lane was admitted; all 12 used exact-Cal fallback. Checkpoints 31 and 32 were not audited after the stop rule. Verdict: **scientific FAIL**.

### Frozen four-case claim audit

A generic constraint evaluator verified the four historical frozen artifacts and produced 1 ACCEPT / 3 REJECT with TP=1, TN=3, FP=0, FN=0 and maximum decision latency 37.38 µs. This is a four-case synthetic evidence check, not a robot-capability or general-accuracy result.

## Upstream contribution

A separate software-only contribution is available as [Genesis PR #3159](https://github.com/Genesis-Embodied-AI/genesis-world/pull/3159) at commit `09b3e04132a15d6c842835829e277c9cbff4cce3`. Its scope is the AMD Docker alignment from PyTorch 2.6 to AMD's official PyTorch 2.8 image plus a static regression test. The PR remains open, ready for review, and unmerged. The 9.4 GB image was not pulled or built; no container runtime success, acceptance, or merge is claimed. This software contribution is not counted as robot capability and does not change the v4/v5/v6 scientific verdicts.

## Reproducibility and evidence

The submission contains frozen, hash-bound evidence:

| File | SHA-256 |
|---|---|
| `submission/evidence/challenge-arena/challenge-arena-summary.json` | `91b18677fa9fcb5f05acead2aa3fb4324188b44173ea85fda75c67e2dcb129ee` |
| `submission/evidence/challenge-arena/challenge-arena-raw-json-v1.tar.gz` | `21647f791444aed708da5e056f17af98258fbc7605bb46acb4a148c0f6a6811b` |
| `submission/evidence/verified-flight-envelope-aggregate.json` | `c7ca6e460e967c3070736d8120bd918a3c489f1e7d62a3ae933ab631af827f58` |
| `submission/evidence/raw-metrics/training-collector/seed303-metrics.json` | `aaa5e1e4654aec24b907527eb5334338a50f328c679eace8208b87f650e36959` |
| `submission/evidence/raw-metrics/training-collector/seed304-metrics.json` | `61b70eead81696608a75436db23f59be9f01a25f65d09af9bc81a6d489010b54` |
| `submission/evidence/raw-metrics/training-collector/seed305-metrics.json` | `24cadca684b1de7f069f4ffb3767502396c1f38031f35e606157fc7874395955` |
| `submission/evidence/raw-metrics/heldout-three-gate-mission/seed303-metrics.json` | `7d30a032a032b3d757a77afbe8ed60aa97c61e54f557ef2ba242251b14f14238` |
| `submission/evidence/raw-metrics/heldout-three-gate-mission/seed304-metrics.json` | `c3408cbb720df48690783888e6335b6350c265ad4af8526d72486250aa2204a8` |
| `submission/evidence/raw-metrics/heldout-three-gate-mission/seed305-metrics.json` | `e546809527d28df7b25fa82ad2d552de170672c871fee6aed132889f38d8d63e` |
| `submission/evidence/radeon-formal-scaling.json` | `98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072` |
| `submission/evidence/v4-summary.json` | `4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b` |
| `submission/evidence/v5-summary.json` | `d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034` |
| `submission/evidence/v6-checkpoint-30.json` | `905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678` |
| `submission/evidence/v6-audit-receipt.json` | `521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1` |
| `submission/evidence/capture-terminal.json` | `923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be` |
| `submission/evidence/frozen-claim-auditor-benchmark.json` | `ccbf38ef7aa36571c3f2433d5f4e9d54b1dd1de7cc2e8f93f2291ccc816f83f7` |

Run `python3 scripts/judge_smoke.py` from the submission directory for a standard-library/OpenCV evidence check. The command does not rerun simulation or use the network. It reads the 94,002-byte deterministic Challenge Arena archive in memory, verifies its exact eight-member inventory, checks each decompressed original JSON SHA, and validates the submitted aggregate assertions.

The recommended first visual is `submission/flightguard-challenge-arena-v1.mp4`: 140 frames, 1280×720, 20 fps, 7.0 seconds, 2,146,360 bytes, SHA-256 `aabdea74a53e07ba0b77b52cab68a5fd5f5ed03e68b81aa3647ef36d49dd5b65`. It is an exact Genesis replay of the summary-bound frozen pair. The full reviewer video remains `submission/flightguard-nominal-envelope-demo-v2.mp4`: 2,100 frames, 1280×720, 10 fps, 210.0 seconds, 17,428,715 bytes, SHA-256 `a5f13ea90ed64468299e925721607c2a2e896efc33fc99213f50cb0fa50799fd`.

## Limitations and claim boundary

- Simulation-only; no hardware-in-the-loop or physical-flight validation.
- Results cover 384 sampled heldout contexts, not a continuous hyper-rectangle or formally certified flight envelope.
- No sim-to-real, real-flight repair, safety, certification, or population-generalization claim.
- The three registered method replicas tie exactly; no learned-method superiority claim.
- Dropout starts at step 999, more than 532 steps after each reported seed mean terminal step. The evidence does not establish dropout recovery or prove every episode ended before dropout.
- Heldout mission metrics contain no saturation field; only the collector supports a saturation result.
- Radeon scaling applies to the fixed r5 workload on one GPU; it is not a cross-device benchmark or estimator-superiority result.
- Challenge Arena compares two frozen controllers within this project; it is not a SOTA comparison or a continuous-envelope claim.
- v4 and v6 are scientific failures; v5 is award-ineligible with zero incremental capability.
- The four-case claim-auditor accuracy is limited to its immutable synthetic corpus.
- The fixed-seed 5001 nominal clip is visual-only and metric-ineligible. The Challenge Arena clip is bound to one frozen raw pair, but aggregate claims still come from all paired JSON evidence.

The defensible conclusion is a Radeon-native sampled flight-verification workflow with a reproducible paired controller improvement, strong one-GPU scaling, and hash-bound evidence. It remains simulation-only and is not a physical-flight safety, SOTA, sim-to-real, or certified-envelope claim.
