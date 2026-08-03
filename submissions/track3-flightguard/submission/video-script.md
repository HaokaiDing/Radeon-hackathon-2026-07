# FlightGuard 7-second Challenge Arena Clip

**Recommended first view:** [`flightguard-challenge-arena-v1.mp4`](flightguard-challenge-arena-v1.mp4)

| Time | Screen action | Caption meaning |
|---:|---|---|
| 0–3.35 s | Same Genesis scene and paired initial state. Left: nominal PD. Right: `robust_z`. Both approach the same three gates. | One controller change only: `kp_z` 2.5→8.0 and `kd_z` 2.0→3.6. |
| 3.35–7.00 s | Freeze the left arm at its collision while the right arm continues through all three gates. | Nominal: collision, 0/3 gates, terminal step 167. `robust_z`: mission success, 3/3 gates, terminal step 479. |

The footer states the frozen paired aggregate: primary adversarial **194/384 = 50.5% → 371/384 = 96.6% (+46.1 pp), zero regressions**. The displayed raw pair is seed 144856705, pair 0, chosen deterministically after aggregation by sorting `(seed, pair_index)`. The clip is simulation-only and makes no SOTA, safety, sim-to-real, certification, or real-flight claim.

- Frames: 140
- Resolution: 1280×720
- FPS: 20
- Duration: 7.0 seconds
- Size: 2,146,360 bytes
- SHA-256: `aabdea74a53e07ba0b77b52cab68a5fd5f5ed03e68b81aa3647ef36d49dd5b65`
- Frozen summary: `evidence/challenge-arena/challenge-arena-summary.json`, SHA-256 `91b18677fa9fcb5f05acead2aa3fb4324188b44173ea85fda75c67e2dcb129ee`

---

# FlightGuard 210-second Reviewer Video Script

**Primary story:** FlightGuard is a Radeon-Native Sampled Nominal Flight Envelope Verifier for AMD Track 3.

**Permanent boundary:** simulation-only; sampled contexts; visual replay is metric-ineligible.

| Time | Screen action | English voice-over / captions |
|---:|---|---|
| 0–20 s | Title: **FlightGuard**. Subtitle: **Radeon-Native Sampled Nominal Flight Envelope Verifier**. Show Genesis quadrotor, three gates, one Radeon, and the simulation-only label. | “FlightGuard is a simulation-only Physical-AI application that asks a concrete question: can a quadrotor controller complete a three-gate mission across reproducible samples of vehicle and environment variation on one AMD Radeon?” |
| 20–35 s | Animate the workflow: deterministic contexts → Genesis + `robust_z` → one Radeon through ROCm → mission and integrity checks → frozen JSON. | “It generates deterministic mass, thrust, wind, delay, and course contexts, runs Genesis through PyTorch ROCm, checks mission completion and data integrity, and exports hash-bound evidence.” |
| 35–80 s | Play the existing fixed-seed 5001 truth-controller nominal visual. Keep `FIXED-SEED 5001 | TRUTH-CONTROLLER | NOMINAL VISUAL | SIMULATION ONLY | METRIC-INELIGIBLE` visible. | “This is the existing fixed-seed five thousand one truth-controller nominal visual. It demonstrates simulator motion only. It is not a heldout evidence context and is excluded from every reported metric. The aggregate result comes independently from six frozen raw metric files.” |
| 80–115 s | Show three seed cards and a large result matrix: 384 paired contexts, 1,152 method episodes, three rows each at 384/384, zero strikes/failures/unfinished. | “Across seeds three-oh-three, three-oh-four, and three-oh-five, FlightGuard evaluated three hundred eighty-four paired heldout course contexts. Each registered method replica completed three hundred eighty-four of three hundred eighty-four missions and one thousand one hundred fifty-two gate passes, with zero strikes, terminal failures, or unfinished episodes.” |
| 115–133 s | Show the sampled observed ranges: mass, thrust, wind norm, delay. Add `SAMPLED — NOT A CONTINUOUS GUARANTEE`. | “The observed samples span mass scale zero point eight zero zero four six to one point one nine nine three three, thrust scale zero point eight zero six zero nine to one point one nine eight six one, wind up to zero point five nine eight two eight meters per second squared, and action delay from zero to six steps.” |
| 133–150 s | Collector card: 186/192, all tracked fields finite, applied saturation max 0.0. | “The training-distribution collector retained one hundred eighty-six of one hundred ninety-two environments. Position, velocity, quaternion, angular velocity, and issued and applied actions were finite. Maximum per-environment applied-action saturation was zero.” |
| 150–180 s | Radeon scaling chart: 32, 128, 256, 512 environments. Show 4,632.58 → 74,246.46 transitions/s, 2,227,200 measured transitions, 16.027× speedup, max VRAM. | “On one Radeon, the fixed deployed simulation workload measured two million two hundred twenty-seven thousand two hundred transitions. Throughput rose from four thousand six hundred thirty-two point six at thirty-two environments to seventy-four thousand two hundred forty-six point five at five hundred twelve: sixteen point zero two seven times intra-device speedup.” |
| 180–198 s | Brief research-lineage panel: v4 FAIL, v5 award-ineligible, v6 rejected. Keep it visually secondary to the nominal verifier. | “FlightGuard also preserves failed research branches. Version four missed its gate, version five added zero capability over calibrated fallback, and version six admitted zero lanes. These results remain visible as limitations, not as the project headline.” |
| 198–210 s | End card: one command, evidence path, aggregate SHA prefix, and boundary checklist. | “The deliverable is a reproducible Radeon simulation verifier: source code, a one-command evidence check, frozen metrics, figures, and this workflow demo. It supports sampled nominal qualification in simulation. It does not claim physical flight, sim-to-real, safety, certification, dropout recovery, learned superiority, or a continuous envelope.” |

## Required on-screen numbers

- 384 paired heldout course contexts
- 1,152 method episodes
- each method replica: 384/384 mission success and 1,152 gate passes
- zero strikes, mission failures, terminal failures, and unfinished episodes
- collector: 186/192 survivors, all tracked fields finite, max per-environment applied saturation 0.0
- sampled observed ranges:
  - mass 0.80046–1.19933
  - thrust 0.80609–1.19861
  - wind norm 0–0.59828 m/s²
  - action delay 0–6 steps
- one-Radeon scaling: 2,227,200 transitions, 4,632.582556654058 → 74,246.46385791198 transitions/s, 16.027× speedup, 1.00169 parallel efficiency
- aggregate evidence SHA-256: `c7ca6e460e967c3070736d8120bd918a3c489f1e7d62a3ae933ab631af827f58`

## Required boundary captions

Keep these exact concepts visible wherever the corresponding evidence appears:

- `SIMULATION ONLY`
- `SAMPLED CONTEXTS — NOT A CONTINUOUS GUARANTEE`
- `VISUAL DEMO — METRIC-INELIGIBLE`
- `THREE METHOD REPLICAS TIE — NO LEARNED SUPERIORITY CLAIM`
- `MISSION METRICS DO NOT RECORD SATURATION`
- `NO DROPOUT-RECOVERY CLAIM`

The configured one-step dropout starts at step 999. It is more than 532 steps after each seed's reported mean terminal step, but the source lacks per-episode maximum terminal step. Do not say every episode finished before dropout.

## Recording notes

- Rendered artifact: `submission/flightguard-nominal-envelope-demo-v2.mp4`, 2,100 frames, 1280×720, 10 fps, 210.0 seconds, 17,428,715 bytes, SHA-256 `a5f13ea90ed64468299e925721607c2a2e896efc33fc99213f50cb0fa50799fd`.
- Renderer: `scripts/render_submission_video.py`, 26,993 bytes, SHA-256 `a0a17d91e15c92f8541da594c7c2ca04b97ce7c5326f61b08436798caace35cd`.
- Embedded visual: fixed-seed 5001 truth-controller nominal clip, SHA-256 `adc0ea528b611e55dca006d220c30ef935f32448f6b935b7b6c1a33cd9d9fbce`, metric-ineligible.
- Target: exactly 210 seconds at 1280×720 and 10 fps.
- Use the fixed-seed 5001 truth-controller nominal clip only as a visual illustration; all result cards must cite the six raw metric files and frozen aggregate JSON.
- Keep the first 35 seconds focused on the application, not on the failed v4/v5/v6 mechanisms.
- Keep failed-mechanism lineage to the 18-second limitations segment.
- Do not call the sampled observed ranges a certified or formal flight envelope.
- Do not state mission saturation; saturation is available only for the collector.
- Do not imply audio is already embedded unless an audio track is actually added and verified.
