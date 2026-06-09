// api.ts
// Central service layer -- all backend calls go through here
// Backend: http://localhost:5000


const BASE_URL = 'http://localhost:5000';

export async function fetchResults(model: string = 'inland_port') {
  const res = await fetch(`${BASE_URL}/results?model=${model}`);
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