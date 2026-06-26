// api.ts
// Central service layer -- all backend calls go through here
// Backend: http://localhost:5000


const BASE_URL = 'http://localhost:5000';

export async function fetchResults(model: string = 'inland_port') {
  const res = await fetch(`${BASE_URL}/results?model=${model}`);
  return res.json();
}

export async function fetchSummary(model: string = 'inland_port') {
  const res = await fetch(`${BASE_URL}/summary?model=${model}`);
  return res.json();
}

export async function fetchLocationDetails(id: string, model: string) {
  const res = await fetch(`${BASE_URL}/results?location_id=${id}&model=${model}`);
  return res.json();
}

export async function fetchSignals() {
  const res = await fetch(`${BASE_URL}/marine-signals`);
  return res.json();
}

export async function fetchDigitalDepthSummary() {
  const res = await fetch(`${BASE_URL}/digital-depth?summary=true`);
  return res.json();
}

export async function fetchProposals(locationId: string) {
  const res = await fetch(`${BASE_URL}/proposal-engine?location_id=${locationId}`);
  return res.json();
}

export async function fetchInfrastructureOverlay(candidates: boolean = true) {
  const res = await fetch(`${BASE_URL}/infrastructure-overlay?candidates=${candidates}`);
  return res.json();
}


export async function runSimulation(body: any) {
  const res = await fetch(`${BASE_URL}/simulate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));

    throw new Error(errorBody.error || `Simulation request failed with status ${res.status}`);
  }
  return res.json();
}

export async function fetchDatasets(validationBreach: boolean, latencyMs: number, currentBlock: number) {
  const res = await fetch(`${BASE_URL}/datasets?validation_breach=${validationBreach}&latency_ms=${latencyMs}&current_block=${currentBlock}`);
  return res.json();
}

export function mapBackendToFrontend(result: any) {
  const levelMap: Record<string, 'HIGH' | 'MEDIUM' | 'LOW'> = {
    HIGH: 'HIGH',
    MEDIUM: 'MEDIUM',
    LOW: 'LOW',
    REJECTED: 'LOW'
  };

  return {
    id: result.location_id,
    score: Math.round(result.score),
    level: levelMap[result.level] ?? 'LOW',
    explanation: result.explanation ?? '',
    confidence: 90,
    trace: result.trace || {},
    constraints: result.constraints || {},
    scoring_model: result.scoring_model || {},
    factor_scores: result.factor_scores || {}
  };
}

export async function fetchVesselOps() {
  const res = await fetch(`${BASE_URL}/vessel-ops`);
  return res.json();
}

export async function fetchCargoOps() {
  const res = await fetch(`${BASE_URL}/cargo-ops`);
  return res.json();
}

export async function fetchVoyagePlanning(body: any = {}) {
  const res = await fetch(`${BASE_URL}/voyage-planning`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

export async function fetchRisNotices() {
  const res = await fetch(`${BASE_URL}/ris-notices`);
  return res.json();
}

export async function fetchTerminalOps() {
  const res = await fetch(`${BASE_URL}/terminal-ops`);
  return res.json();
}

export async function fetchSystemHealth() {
  const res = await fetch(`${BASE_URL}/system-health`);
  return res.json();
}

export async function fetchReplayStatus() {
  const res = await fetch(`${BASE_URL}/replay/status`);
  return res.json();
}

export async function postReplayTick() {
  const res = await fetch(`${BASE_URL}/replay/tick`, { method: 'POST' });
  return res.json();
}

export async function postReplayBreach() {
  const res = await fetch(`${BASE_URL}/replay/breach`, { method: 'POST' });
  return res.json();
}

export async function fetchReplayHistory() {
  const res = await fetch(`${BASE_URL}/replay/history`);
  return res.json();
}