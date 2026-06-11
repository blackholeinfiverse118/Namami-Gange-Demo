# Namami Gange Demo

Integrated demonstration repository for the Namami Gange Intelligence Platform.

This repository combines the Suitability Intelligence Backend, the Next.js Frontend Dashboard, and a complete intelligence documentation package covering Namami Gange, NICAI, and SVACS systems.

---

## Repository Structure

```text
Namami-Gange-Demo/
├── backend/                          Suitability Intelligence Engine (Flask/Python)
│   ├── src/                          Core intelligence modules
│   ├── data_raw/                     Raw CSV datasets (CPCB, CWC, IWAI, logistics)
│   ├── outputs/                      Generated suitability results (JSON)
│   ├── tests/                        Test suite
│   └── proofs/                       Execution and validation proofs
├── docs/
│   ├── evidence/                     Supporting evidence from NG, NICAI, SVACS
│   ├── integration/                  System integration flow documentation
│   ├── payloads/                     Intelligence payload outputs (JSON)
│   ├── reports/                      Analysis and review reports
│   └── review_packets/               Master review packet
├── frontend/                         Next.js / TypeScript dashboard
│   └── src/
│       ├── components/               UI components (map, signals, panels)
│       ├── services/                 API service layer
│       └── app/                      Next.js app directory
├── .gitignore
├── DEPLOYMENT_GUIDE.md
├── README.md
└── REVIEW_PACKET.md
```

---

## Prerequisites

### Backend

- Python 3.10+
- pip

### Frontend

- Node.js 18+
- npm

---

## Backend Setup

```bash
cd backend/src
pip install -r requirements.txt
python api.py
```

Backend starts on:
http://localhost:5000

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend starts on:
http://localhost:3000

---

## API Endpoints

GET /results?model=inland_port
GET /results?model=hub_spoke
GET /results?model=seaplane
GET /simulate
GET /health

---

## Documentation Package

| Folder | Contents |
| --- | --- |
| docs/payloads | LOCATION_INTELLIGENCE.json, DEMO_INTELLIGENCE_PAYLOAD.json, OPPORTUNITY_INTELLIGENCE.json, CONSTRAINT_INTELLIGENCE.json |
| docs/reports | NICAI_SVACS_REPORT.md, DATASET_INVENTORY.md, LOCATION_EXPLANATIONS.md, COMMODORE_QA.md, SHOWCASE_GAP_REPORT.md, DEMO_READINESS_REPORT.md |
| docs/review_packets | MASTER_REVIEW_PACKET.md |
| docs/integration | SYSTEM_INTEGRATION_FLOW.md |
| docs/evidence | Backend outputs, NICAI artifacts, SVACS artifacts, Namami Gange audit documents |

---

## Validation Checklist

- Backend starts successfully
- Frontend starts successfully
- CORS enabled
- API requests return HTTP 200
- Dashboard loads and renders backend data
- Intelligence payloads present and schema-valid
- Documentation package complete

---

## Known Limitations

Some dashboard views (Collaboration, Governance, Infrastructure Network, Realtime Signals) continue to use static demonstration content and are not yet fully API-driven. These do not affect core intelligence pipeline validation.

---

## Systems Covered

This repository integrates intelligence artifacts from:

- Namami Gange Suitability Intelligence Engine
- NICAI Intelligence Engine
- SVACS Operational Intelligence Components

---

## Demo Readiness

READY FOR WEDNESDAY DEMONSTRATION

No integration blockers identified. Intelligence pipeline traceable from dataset to dashboard payload.