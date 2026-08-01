"use strict";

const EVIDENCE = Object.freeze({
  campaigns: Object.freeze({
    v4: Object.freeze({
      status: "SCIENTIFIC_FAIL",
      faultSuccess: Object.freeze({ patch: 11, actionOnly: 0, raw: 33, cal: 32 }),
      episodes: 36,
      failureReduction: 11 / 36,
      awardEvidenceEligible: false,
    }),
    v5: Object.freeze({
      status: "DEVELOPMENT_PASS_AWARD_INELIGIBLE",
      faultSuccess: Object.freeze({ patch: 10, actionOnly: 0, cal: 10 }),
      faultEpisodes: 12,
      nominalSuccess: Object.freeze({ patch: 12, cal: 12 }),
      nominalEpisodes: 12,
      postOnsetRawBitExactFieldCount: 19,
      incrementalCapability: 0,
      awardEvidenceEligible: false,
    }),
    v6Checkpoint30: Object.freeze({
      status: "SCIENTIFIC_FAIL",
      lanes: 12,
      admittedLanes: 0,
      exactCalFallbackLanes: 12,
      rank8Lanes: 12,
      sigmaPassLanes: 12,
      sigmaRange: Object.freeze([0.019169591096042157, 0.0321526465925691]),
      splitHalfPassLanes: 0,
      deltaVRmsePassLanes: 0,
      rotationRmsePassLanes: 0,
      deltaVQ95PassLanes: 3,
      rotationQ95PassLanes: 3,
      recurrencePass: true,
      disabledNoOpPass: true,
      enabledKillPass: true,
      checkpoints31And32Audited: false,
      awardEvidenceEligible: false,
    }),
  }),
  scaling: Object.freeze({
    status: "PASS",
    fixedPipeline: "r5 nominal deployed simulation pipeline",
    oneRadeonGpu: true,
    totalMeasuredTransitions: 2227200,
    environments: Object.freeze([32, 128, 256, 512]),
    meanTransitionsPerSecond: Object.freeze([
      4632.582556654058,
      18354.411592309174,
      36383.01129648785,
      74246.46385791198,
    ]),
    speedup512Vs32: 16.027013647337444,
    parallelEfficiency512Vs32: 1.0016883529585903,
    maximumCoefficientOfVariation: 0.0033317633931520337,
    gpuUsePercentMean: Object.freeze([77.3544, 76.2593, 77.0864, 78.4684]),
    maximumGpuUsePercent: 86,
    maximumVramUsedBytes: 962785280,
    performanceAcceptanceAchieved: true,
    scientificSuperiorityClaimed: false,
  }),
  benchmark: Object.freeze({
    seed: 5101,
    activeEpisodes: 96,
    episodesPerStratum: 16,
    learnedTerminalFailures: 53,
    learnedFailureRate: 53 / 96,
    allLearnedTensorsFinite: true,
    gateVerdict: "ARCHIVED_EXPLORATION_ONLY",
    passingStrata: 3,
    requiredPassingStrata: 4,
    acceptedFailureRange: Object.freeze([2, 12]),
  }),
  structuralSmoke: Object.freeze({
    seed: 5001,
    pairs: 24,
    steps: 400,
    activationStep: 300,
    responseSteps: 100,
    maximumPreOnsetPairDifference: 0,
    trackedPairingFields: Object.freeze([
      "position",
      "velocity",
      "quaternion",
      "angular_velocity",
      "issued_action",
      "applied_action",
    ]),
    medianDivergenceM: 0.1562103629,
    passingStrata: 6,
    totalStrata: 6,
    visibleGpuCount: 1,
    allTrackedTensorsFinite: true,
    verdict: "ARCHIVED_EXPLORATION_ONLY",
  }),
  sourceHashes: Object.freeze({
    v4Summary: "4ebab98a9b9c3b134548ef646c30aaafbd7d6ddeaa8a0485b667ee8054f80f8b",
    v5Summary: "d546a620931fc3afb2c074d749e1fe017ba6c4dcdf2d05b570855a913e83b034",
    v6Checkpoint30: "905925dedc62a41a8b4c35ace8b1c5a1bd1d97c9cb4d43a5f513f3827cf0a678",
    v6AuditReceipt: "521738135a3dcc28dc42ecd8b4f01fe5abe925b8353a45577d0b8b5de9e3e8c1",
    captureTerminal: "923c24124f9af6d53d82a80c9efd72d8e5ada962a4ceb30adf48e232c2c341be",
    radeonScaling: "98d9b331907f9968ae65054c6f9d840dc0440eb9209c14e955dc628df736f072",
  }),
});

const STRATA = Object.freeze({
  12: Object.freeze({
    name: "Thrust × horizontal wind",
    description: "Thrust scale 0.94–0.98 with horizontal wind 0.3–0.6 m/s².",
    failures: 13,
    direction: Object.freeze([1, -0.7]),
  }),
  13: Object.freeze({
    name: "Thrust × signed vertical wind",
    description: "Thrust scale 0.94–0.98 with absolute vertical wind 0.1–0.2 m/s².",
    failures: 11,
    direction: Object.freeze([-0.5, -1]),
  }),
  14: Object.freeze({
    name: "Horizontal wind × action delay",
    description: "Horizontal wind 0.3–0.6 m/s² with an action delay of 4–6 steps.",
    failures: 2,
    direction: Object.freeze([1, 0.5]),
  }),
  15: Object.freeze({
    name: "Signed vertical wind × action delay",
    description: "Absolute vertical wind 0.1–0.2 m/s² with an action delay of 4–6 steps.",
    failures: 0,
    direction: Object.freeze([-0.65, 0.8]),
  }),
  16: Object.freeze({
    name: "Thrust × horizontal wind × delay",
    description:
      "Thrust scale 0.94–0.98, horizontal wind 0.3–0.6 m/s², and 4–6 delay steps.",
    failures: 15,
    direction: Object.freeze([1.2, 0.15]),
  }),
  17: Object.freeze({
    name: "Joint adversarial composition",
    description:
      "Thrust, horizontal and signed vertical wind, plus 3–5 action-delay steps.",
    failures: 12,
    direction: Object.freeze([-1, -0.25]),
  }),
});

const state = {
  mode: "evidence",
  step: EVIDENCE.structuralSmoke.activationStep,
  onset: EVIDENCE.structuralSmoke.activationStep,
  severity: 1,
  selectedStratum: 12,
  playing: false,
  animationTimer: null,
};

const elements = {
  modeButtons: [...document.querySelectorAll("[data-mode-button]")],
  stepSlider: document.querySelector("#step-slider"),
  onsetSlider: document.querySelector("#onset-slider"),
  severitySlider: document.querySelector("#severity-slider"),
  stepReadout: document.querySelector("#step-readout"),
  phaseReadout: document.querySelector("#phase-readout"),
  onsetLabel: document.querySelector("#onset-label"),
  timelineOnset: document.querySelector("#timeline-onset"),
  timelineTrack: document.querySelector(".timeline-track"),
  exploreControls: document.querySelector("#explore-controls"),
  exploreOnsetValue: document.querySelector("#explore-onset-value"),
  severityValue: document.querySelector("#severity-value"),
  modeNotice: document.querySelector("#mode-notice"),
  playButton: document.querySelector("#play-button"),
  nominalDrone: document.querySelector("#nominal-drone"),
  faultDrone: document.querySelector("#fault-drone"),
  faultWave: document.querySelector("#fault-wave"),
  faultStatus: document.querySelector("#fault-status"),
  faultCaption: document.querySelector("#fault-caption"),
  nominalCanvas: document.querySelector("#nominal-canvas"),
  faultCanvas: document.querySelector("#fault-canvas"),
  heatCells: [...document.querySelectorAll(".heat-cell")],
  detailId: document.querySelector("#detail-id"),
  detailName: document.querySelector("#detail-name"),
  detailDescription: document.querySelector("#detail-description"),
  detailCount: document.querySelector("#detail-count"),
  detailGate: document.querySelector("#detail-gate"),
  exportButton: document.querySelector("#export-button"),
  downloadStatus: document.querySelector("#download-status"),
};

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function getPhase() {
  if (state.step < state.onset) {
    return "MATCHED HISTORY";
  }
  if (state.step === state.onset) {
    return "INTERVENTION ONSET";
  }
  return "POST-ONSET RESPONSE";
}

function getGateLabel(failures) {
  const [minimum, maximum] = EVIDENCE.benchmark.acceptedFailureRange;
  if (failures < minimum) {
    return "BELOW PREREGISTERED RANGE";
  }
  if (failures > maximum) {
    return "ABOVE PREREGISTERED RANGE";
  }
  return "WITHIN PREREGISTERED RANGE";
}

function getFlightPoint(step, faulted) {
  const routeProgress = step / EVIDENCE.structuralSmoke.steps;
  const base = {
    x: 17 + routeProgress * 68,
    y: 59 - Math.sin(routeProgress * Math.PI) * 11,
  };

  if (!faulted || step <= state.onset) {
    return base;
  }

  const responseProgress = clamp(
    (step - state.onset) / Math.max(1, EVIDENCE.structuralSmoke.steps - state.onset),
    0,
    1,
  );
  const [directionX, directionY] = STRATA[state.selectedStratum].direction;
  const bend = responseProgress * responseProgress * state.severity;

  return {
    x: clamp(base.x + directionX * 17 * bend, 8, 92),
    y: clamp(base.y + directionY * 22 * bend, 10, 88),
  };
}

function sizeCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.max(1, Math.round(rect.width * pixelRatio));
  const height = Math.max(1, Math.round(rect.height * pixelRatio));

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  const context = canvas.getContext("2d");
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  return { context, width: rect.width, height: rect.height };
}

function drawFlightPath(canvas, faulted) {
  const { context, width, height } = sizeCanvas(canvas);
  context.clearRect(0, 0, width, height);

  const samples = 60;
  const currentSample = Math.floor((state.step / EVIDENCE.structuralSmoke.steps) * samples);
  context.lineCap = "round";
  context.lineJoin = "round";

  context.beginPath();
  for (let index = 0; index <= currentSample; index += 1) {
    const point = getFlightPoint(
      (index / samples) * EVIDENCE.structuralSmoke.steps,
      faulted,
    );
    const x = (point.x / 100) * width;
    const y = (point.y / 100) * height;
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  }
  context.strokeStyle = faulted ? "#f45d48" : "#1f5eff";
  context.globalAlpha = 0.64;
  context.lineWidth = 3;
  context.stroke();

  context.globalAlpha = 1;
  context.setLineDash([5, 8]);
  context.beginPath();
  for (let index = 0; index <= samples; index += 1) {
    const point = getFlightPoint(
      (index / samples) * EVIDENCE.structuralSmoke.steps,
      faulted,
    );
    const x = (point.x / 100) * width;
    const y = (point.y / 100) * height;
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  }
  context.strokeStyle = faulted ? "rgba(244, 93, 72, 0.22)" : "rgba(31, 94, 255, 0.2)";
  context.lineWidth = 1.5;
  context.stroke();
  context.setLineDash([]);
}

function positionDrone(drone, point, faulted) {
  drone.style.left = `${point.x}%`;
  drone.style.top = `${point.y}%`;
  const responseProgress =
    state.step > state.onset
      ? (state.step - state.onset) /
        Math.max(1, EVIDENCE.structuralSmoke.steps - state.onset)
      : 0;
  const tilt = faulted
    ? 45 + STRATA[state.selectedStratum].direction[0] * responseProgress * 17
    : 45;
  drone.style.transform = `translate(-50%, -50%) rotate(${tilt}deg)`;
}

function renderReplay() {
  const onsetPercent = (state.onset / EVIDENCE.structuralSmoke.steps) * 100;
  const stepPercent = (state.step / EVIDENCE.structuralSmoke.steps) * 100;
  const faultActive = state.step >= state.onset;

  elements.stepReadout.textContent = String(state.step);
  elements.phaseReadout.textContent = getPhase();
  elements.onsetLabel.textContent =
    state.mode === "evidence" ? "fault @ 300" : `illustrative @ ${state.onset}`;
  elements.timelineOnset.style.left = `${onsetPercent}%`;
  elements.timelineTrack.style.setProperty("--step-progress", `${stepPercent}%`);

  const nominalPoint = getFlightPoint(state.step, false);
  const faultPoint = getFlightPoint(state.step, true);
  positionDrone(elements.nominalDrone, nominalPoint, false);
  positionDrone(elements.faultDrone, faultPoint, true);

  elements.faultWave.style.left = `${faultPoint.x}%`;
  elements.faultWave.style.top = `${faultPoint.y}%`;
  elements.faultWave.classList.toggle("is-active", faultActive);
  elements.faultStatus.textContent = faultActive ? "ACTIVE" : "ARMED";
  elements.faultCaption.textContent =
    state.mode === "evidence"
      ? "Coincident perception blackout and scheduled fault activate once at step 300."
      : `Illustrative-only onset at step ${state.onset}; severity ${state.severity.toFixed(1)}×.`;

  drawFlightPath(elements.nominalCanvas, false);
  drawFlightPath(elements.faultCanvas, true);
}

function setStep(nextStep) {
  state.step = clamp(
    Number(nextStep),
    0,
    EVIDENCE.structuralSmoke.steps,
  );
  elements.stepSlider.value = String(state.step);
  renderReplay();
}

function stopPlayback() {
  if (state.animationTimer !== null) {
    window.clearInterval(state.animationTimer);
  }
  state.animationTimer = null;
  state.playing = false;
  elements.playButton.innerHTML = '<span aria-hidden="true">▶</span><span>Play</span>';
  elements.playButton.setAttribute("aria-label", "Play replay");
}

function togglePlayback() {
  if (state.playing) {
    stopPlayback();
    return;
  }

  if (state.step >= EVIDENCE.structuralSmoke.steps) {
    setStep(0);
  }
  state.playing = true;
  elements.playButton.innerHTML = '<span aria-hidden="true">Ⅱ</span><span>Pause</span>';
  elements.playButton.setAttribute("aria-label", "Pause replay");
  state.animationTimer = window.setInterval(() => {
    if (state.step >= EVIDENCE.structuralSmoke.steps) {
      stopPlayback();
      return;
    }
    setStep(state.step + 2);
  }, 34);
}

function setMode(mode) {
  if (mode !== "evidence" && mode !== "explore") {
    return;
  }
  state.mode = mode;
  document.body.dataset.mode = mode;
  elements.modeButtons.forEach((button) => {
    const active = button.dataset.modeButton === mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  const exploring = mode === "explore";
  elements.onsetSlider.disabled = !exploring;
  elements.severitySlider.disabled = !exploring;
  elements.exploreControls.setAttribute("aria-hidden", String(!exploring));

  if (!exploring) {
    state.onset = EVIDENCE.structuralSmoke.activationStep;
    state.severity = 1;
    elements.onsetSlider.value = String(state.onset);
    elements.severitySlider.value = "100";
  }

  elements.exploreOnsetValue.textContent = String(state.onset);
  elements.severityValue.textContent = `${state.severity.toFixed(1)}×`;
  elements.modeNotice.innerHTML = exploring
    ? '<span class="status-dot" aria-hidden="true"></span><strong>Explore mode</strong><span>Illustrative controls are isolated from frozen evidence and export.</span>'
    : '<span class="status-dot" aria-hidden="true"></span><strong>Evidence mode</strong><span>Frozen onset at step 300. Motion is a schematic, not a raw trajectory.</span>';
  renderReplay();
}

function selectStratum(stratumId) {
  const stratum = STRATA[stratumId];
  if (!stratum) {
    return;
  }

  state.selectedStratum = Number(stratumId);
  elements.heatCells.forEach((cell) => {
    const selected = Number(cell.dataset.stratum) === state.selectedStratum;
    cell.classList.toggle("is-selected", selected);
    cell.setAttribute("aria-pressed", String(selected));
  });

  elements.detailId.textContent = `S${state.selectedStratum}`;
  elements.detailName.textContent = stratum.name;
  elements.detailDescription.textContent = stratum.description;
  elements.detailCount.textContent = `${stratum.failures} / ${EVIDENCE.benchmark.episodesPerStratum}`;
  elements.detailGate.textContent = getGateLabel(stratum.failures);
  renderReplay();
}

function buildCertificate() {
  const archivedFailuresByStratum = {};
  Object.entries(STRATA).forEach(([identifier, stratum]) => {
    archivedFailuresByStratum[identifier] = {
      terminal_failures: stratum.failures,
      episodes: EVIDENCE.benchmark.episodesPerStratum,
      archived_exploration_gate: getGateLabel(stratum.failures),
    };
  });

  return {
    schema: "faultfork.evidence-certificate.v2",
    generated_at: new Date().toISOString(),
    project: "FlightGuard / FaultFork",
    product: "Radeon-native fail-closed embodied-flight claim auditor",
    scope: {
      domain: "Genesis simulation",
      compute: "single AMD Radeon GPU, serial execution",
      evidence_class: "frozen_development_claim_audit",
      single_t265_development_event: true,
      causal_only_relative_to: "ROS bag record-time availability proxy",
      scaling_workload: "fixed r5 nominal deployed simulation pipeline on one Radeon",
      claims_excluded: [
        "safety improvement",
        "sim-to-real transfer",
        "hardware-in-the-loop validation",
        "real-flight repair",
        "formal superiority",
        "upstream contribution",
      ],
    },
    frozen_evidence: {
      v4: EVIDENCE.campaigns.v4,
      v5: EVIDENCE.campaigns.v5,
      v6_checkpoint_30: EVIDENCE.campaigns.v6Checkpoint30,
      decision: "NO_CANDIDATE_MECHANISM_CLAIM_ESTABLISHED",
    },
    throughput_evidence: EVIDENCE.scaling,
    archived_exploration_non_claim: {
      benchmark_seed: EVIDENCE.benchmark.seed,
      active_episodes: EVIDENCE.benchmark.activeEpisodes,
      terminal_failures: EVIDENCE.benchmark.learnedTerminalFailures,
      terminal_failures_by_stratum: archivedFailuresByStratum,
      note: "This retained explorer is not v4/v5/v6 claim evidence.",
    },
    provenance: {
      sha256: EVIDENCE.sourceHashes,
      prohibited_fields_accessed: [],
    },
    interface_state: {
      mode_at_export: state.mode,
      selected_archived_stratum: state.selectedStratum,
      note:
        "Explore parameters and schematic motion are intentionally excluded from frozen_evidence.",
    },
  };
}

function downloadCertificate() {
  const certificate = buildCertificate();
  const serialized = `${JSON.stringify(certificate, null, 2)}\n`;
  const blob = new Blob([serialized], { type: "application/json" });
  const downloadUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = downloadUrl;
  anchor.download = "faultfork-evidence-certificate.json";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(downloadUrl);
  elements.downloadStatus.textContent =
    "Certificate generated from the frozen evidence manifest.";
}

elements.modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.modeButton));
});
elements.stepSlider.addEventListener("input", (event) => {
  stopPlayback();
  setStep(event.target.value);
});
elements.onsetSlider.addEventListener("input", (event) => {
  state.onset = Number(event.target.value);
  elements.exploreOnsetValue.textContent = String(state.onset);
  renderReplay();
});
elements.severitySlider.addEventListener("input", (event) => {
  state.severity = Number(event.target.value) / 100;
  elements.severityValue.textContent = `${state.severity.toFixed(1)}×`;
  renderReplay();
});
elements.playButton.addEventListener("click", togglePlayback);
elements.heatCells.forEach((cell) => {
  cell.addEventListener("click", () => selectStratum(cell.dataset.stratum));
});
elements.exportButton.addEventListener("click", downloadCertificate);
window.addEventListener("resize", renderReplay);

setMode("evidence");
selectStratum(12);
