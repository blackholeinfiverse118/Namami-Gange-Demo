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
    confidence: 90
  };
}