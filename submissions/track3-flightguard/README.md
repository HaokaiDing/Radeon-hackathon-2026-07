# FlightGuard — Sampled Flight-Controller Qualification on AMD Radeon

**Team:** 做实验摸鱼呢

**Participant:** Haokai Ding (solo)

> **AMD Track 3 · simulation-only.** FlightGuard runs matched quadrotor missions in Genesis through PyTorch ROCm on one AMD Radeon GPU. It helps robotics teams find controller failures, compare a targeted change, and review the result before hardware testing.

## 60-second judge path

From the competition repository root:

```bash
cd submissions/track3-flightguard
python3 scripts/judge_smoke.py
```

Expected headline:

```text
FlightGuard judge smoke: PASS
nominal envelope | 384 paired contexts | 1152 method episodes | every method 384/384
collector | 186/192 survivors | all tracked fields finite | applied saturation max 0.0
challenge arena | primary 194/384 -> 371/384 (+46.1 pp) | retention 121/192 -> 192/192 | 0 regressions
Radeon | 2,227,200 transitions | 16.027013647337444x scaling
```

This CPU-only check reads the submitted metrics, Challenge Arena pairs, figures, and videos. It does not rerun Genesis or require network access.

## Watch first

[![FlightGuard one-minute tour: paired failure, recovery, harder course, and Radeon scaling](submission/flightguard-final-narrative-v6-poster.png)](submission/flightguard-final-narrative-v6.mp4)

The [one-minute judge video](submission/flightguard-final-narrative-v6.mp4) is **60.9 seconds, 1280×720, and 60 fps**. It opens with the measured Challenge Arena comparison, shows the 13-gate course, and closes with Radeon scaling and the claim boundary. The 13-gate segment is a visual-only simulation and is excluded from the 384/192 measured results.

For the shortest before/after view, open the [7-second paired Genesis replay](submission/flightguard-challenge-arena-v1.mp4): nominal PD collides at step 167 with 0/3 gates, while `robust_z` completes 3/3 gates at step 479 in the same scene.

## Capability

FlightGuard asks one practical question: **does a controller complete the same mission more reliably when vehicle and environment conditions become difficult?**

The Challenge Arena compares matched pairs. Initial state, gate geometry, mass, thrust, wind, action delay, and random streams are identical within each pair. The only intervention is:

- `kp_z`: 2.5 → 8.0
- `kd_z`: 2.0 → 3.6

| Suite | Matched pairs | Nominal PD | `robust_z` | Added successes | Nominal-only wins |
|---|---:|---:|---:|---:|---:|
| Primary adversarial | 384 | 194/384 (50.5%) | 371/384 (96.6%) | +177 (+46.1 pp) | 0 |
| Retention heldout | 192 | 121/192 (63.0%) | 192/192 (100.0%) | +71 (+37.0 pp) | 0 |

The primary result spans three preregistered seeds; their added-success counts are +57, +58, and +62. Primary failures fall from 190 to 13, a 93.16% reduction. All paired traces are finite and maximum applied-action saturation is 0.0 for both arms.

A bit-exact no-op confirms that the comparison path does not change an unchanged controller. A zero-action kill-magnitude control reaches 0/8 successes and produces 10.506417 m maximum paired-active divergence, confirming that the evaluation responds to the controller intervention.

![Challenge Arena aggregate](submission/figures/challenge-arena.svg)

## Radeon execution

Genesis runs the batched simulation through PyTorch HIP/ROCm. Every source mission and collector run reports exactly one visible `AMD Radeon Graphics`; GPU work is serialized.

A fixed one-Radeon workload measures **2,227,200 transitions**:

| Parallel environments | Mean transitions/s |
|---:|---:|
| 32 | 4,632.582556654058 |
| 128 | 18,354.411592309174 |
| 256 | 36,383.01129648785 |
| 512 | 74,246.46385791198 |

The 32→512 run reaches **16.027013647337444× intra-device speedup** with **1.0016883529585903 parallel efficiency**. Maximum observed VRAM is **962,785,280 bytes**.

## Application value

FlightGuard turns controller qualification into a reviewable pre-hardware workflow:

1. sample reproducible mass, thrust, wind, delay, and gate-course conditions;
2. run paired Genesis missions on Radeon;
3. check completion, strikes, terminal outcomes, finiteness, and action saturation;
4. compare a focused controller change across multiple seeds;
5. give reviewers the raw metrics, visual replay, and one-command smoke check.

The intended users are embodied-AI researchers and flight-control developers deciding which controller changes deserve scarce hardware-test time.

## Additional qualification evidence

The heldout three-gate suite uses seeds 303, 304, and 305:

- **384 paired course contexts** and **1,152 method episodes**;
- each registered replica completes **384/384 missions** and **1,152/1,152 gate passes**;
- zero strikes, mission failures, terminal failures, or unfinished episodes;
- all tracked mission tensors finite;
- observed mass scale 0.80046–1.19933, thrust scale 0.80609–1.19861, wind norm 0–0.59828 m/s², and action delay 0–6 steps.

The three registered replicas tie exactly, so this result supports the shared `robust_z` controller and sampled evaluator rather than a learned-method comparison.

Across 192 training-distribution collector environments, **186/192 survive**, every tracked field is finite, and maximum per-environment applied-action saturation is **0.0**.

## Full one-Radeon rerun

Full rerun entry: [`scripts/reconstruct_challenge_arena_amd.py`](scripts/reconstruct_challenge_arena_amd.py). The launcher reconstructs the submitted runner/config and supports the serial no-op, kill, three primary-seed, and three retention-seed Genesis jobs. Environment and dependency details are in [`pyproject.toml`](pyproject.toml) and the launcher help.

## Upstream contribution

[Genesis PR #3159](https://github.com/Genesis-Embodied-AI/genesis-world/pull/3159) updates the AMD Docker path from PyTorch 2.6 to AMD's PyTorch 2.8 image and adds a static regression test. It is an open software contribution and is reported separately from FlightGuard's controller-capability results.

## Key submission files

- [`docs/technical-report.md`](docs/technical-report.md): method, results, and limits
- [`submission/flightguard-final-narrative-v6.mp4`](submission/flightguard-final-narrative-v6.mp4): one-minute judge video
- [`submission/flightguard-challenge-arena-v1.mp4`](submission/flightguard-challenge-arena-v1.mp4): 7-second paired replay
- [`submission/evidence/challenge-arena/`](submission/evidence/challenge-arena/): raw pairs and aggregate metrics
- [`submission/evidence/raw-metrics/`](submission/evidence/raw-metrics/): nominal mission and collector metrics
- [`submission/evidence/radeon-formal-scaling.json`](submission/evidence/radeon-formal-scaling.json): one-Radeon scaling measurements
- [`demo/faultfork/`](demo/faultfork/): static reviewer page

## Claim boundary

FlightGuard is a simulation-only controller-qualification prototype evaluated over sampled contexts. It does not establish physical-flight safety, certification, sim-to-real transfer, a continuous flight envelope, population generalization, learned-method superiority, or SOTA superiority.
