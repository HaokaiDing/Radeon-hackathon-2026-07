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

# FlightGuard 210-second Challenge Arena Workflow Video

**Primary reviewer artifact:** [`flightguard-challenge-arena-workflow-demo-v3.mp4`](flightguard-challenge-arena-workflow-demo-v3.mp4)

**Product story:** FlightGuard turns a visible Genesis mission failure into a matched, reproducible controller-qualification result on one AMD Radeon.

**Permanent boundary:** simulation-only; sampled contexts; comparison against the project's nominal PD controller; no SOTA, safety, sim-to-real, certification, or real-flight claim.

| Time | Screen action | Burned English caption |
|---:|---|---|
| 0–7 s | Play the complete submitted Challenge Arena clip. The same Genesis scene shows nominal PD colliding while `robust_z` clears all three gates. | “Same scene and random stream: nominal collides; `robust_z` clears all three gates.” |
| 7–20 s | Title/product card: **FlightGuard** and **Challenge Arena controller qualification**. | “FlightGuard turns a visible Genesis failure into a reproducible controller decision on one AMD Radeon.” |
| 20–38 s | Workflow: freeze → pair → Genesis/ROCm → gates → frozen evidence. | “Freeze one hypothesis, pair every context, simulate on ROCm, enforce gates, and export frozen evidence.” |
| 38–58 s | Terminal-style card with the frozen no-op command and submitted PASS output: Genesis 1.2.3, PyTorch ROCm, `cuda:0`, one visible AMD Radeon. | “This submitted no-op run reports Genesis 1.2.3, PyTorch ROCm, one visible AMD Radeon, and bit-exact PASS.” |
| 58–88 s | Primary adversarial bars and cards: 194/384 → 371/384, +177, +46.1 pp, 93.16% failure reduction. | “On 384 primary adversarial pairs, mission success rises from 194 to 371 with zero nominal-only wins.” |
| 88–108 s | Retention cards: 121/192 → 192/192, zero nominal-only wins; seed deltas +23, +26, +22. | “On 192 separate heldout pairs, `robust_z` retains every nominal success and reaches 192 of 192.” |
| 108–128 s | Diagnostic cards: no-op bit-exact; zero action 0/8 success, 0 gates, 10.506417 m divergence. | “The no-op is bit-exact, while zero action yields zero successes and a 10.506417 meter divergence.” |
| 128–150 s | Isolated intervention: `kp_z` 2.5→8.0 and `kd_z` 2.0→3.6. Mark all paired context variables unchanged. | “Only `kp_z` and `kd_z` change; initial state, gates, domain parameters, and random streams stay paired.” |
| 150–175 s | One-Radeon scaling chart: 32, 128, 256, 512 environments and 2,227,200 measured transitions. | “A fixed one-Radeon workload scales from 32 to 512 environments over 2,227,200 measured transitions.” |
| 175–193 s | Show `python3 scripts/judge_smoke.py` and its frozen PASS headlines. | “A CPU-only judge command checks raw metrics, diagnostics, aggregates, media, and claim boundaries.” |
| 193–205 s | Application cards: find failure, qualify change, review evidence. | “The result is a controller-qualification workflow for embodied-AI researchers and flight-control developers.” |
| 205–210 s | Final claim-boundary card. | “The claim is simulation-only and sampled: no SOTA, safety, sim-to-real, or real-flight conclusion.” |

## Required on-screen numbers

- primary adversarial: 384 pairs, 194/384 → 371/384, +177, +46.1 pp, 93.16% failure reduction, zero nominal-only wins
- retention heldout: 192 pairs, 121/192 → 192/192, +71, zero nominal-only wins
- diagnostics: no-op bit-exact; zero action 0/8 mission success, 0 gates, 10.506417 m maximum paired-active position divergence
- isolated controller change: `kp_z` 2.5→8.0; `kd_z` 2.0→3.6
- one-Radeon scaling: 2,227,200 transitions; 32→512 environments; 16.027× intra-device speedup
- frozen Challenge Arena summary SHA-256: `91b18677fa9fcb5f05acead2aa3fb4324188b44173ea85fda75c67e2dcb129ee`

## Required boundary captions

- `SIMULATION ONLY`
- `SAMPLED CONTEXTS ONLY`
- `PROJECT NOMINAL PD BASELINE`
- `NO SOTA / SAFETY / SIM-TO-REAL / REAL-FLIGHT CLAIM`

## Recording notes

- Rendered artifact: `submission/flightguard-challenge-arena-workflow-demo-v3.mp4`
- Frames: 2,100
- Resolution: 1280×720
- FPS: 10
- Duration: 210.0 seconds
- Codec requested/reported: `mp4v` / `FMP4`
- Audio: none
- Size: 17,874,513 bytes
- SHA-256: `d72057ff2a1bdf1796240a857f6451f545c070204ec6dcbe551f2dd039e00670`
- Renderer: `scripts/render_challenge_arena_workflow_video_v3.py`, 32,850 bytes, SHA-256 `ed138fc753771172b8922ce83b6ebf52a1e2010247aadf87fa1e0cfb9883fe84`
- The first 70 output frames consume all 140 frames of the 20 fps Challenge Arena clip by exact 2:1 downsampling.
- All narration is burned English text; the MP4 has no audio track.
- V2 remains a historical reviewer artifact and is still validated by `judge_smoke.py`.
