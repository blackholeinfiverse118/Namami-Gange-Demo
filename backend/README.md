# Ganga Basin Suitability Intelligence Engine
## + Scenario Simulation & Sensitivity Intelligence Layer

---

## Overview

This project implements a **deterministic, audit-grade intelligence system** to evaluate locations across the Ganga Basin for infrastructure suitability, with a full **Scenario Simulation + Sensitivity Analysis Layer** for what-if policy exploration.

It assesses three major use cases:

- Inland Port Development
- Seaplane Landing Zones
- Hub-Spoke Logistics Networks

The system uses **real-world datasets** and **rule-based scoring logic** to generate interpretable, fully traceable results — and allows planners to simulate how results change under modified constraints or priorities.

Every output is traceable to its source dataset. Every score is explainable by its formula. Every constraint is enforced without exception.

---

## Key Features

- Fully deterministic (no ML / no randomness)
- Uses real datasets (IWAI, CPCB, CWC, logistics parks, urban centers)
- Multi-factor scoring system (0–100)
- **Signal trace layer** — every score traceable to source dataset signals (CWC, CPCB, IWAI, Census)
- **Hard vs soft constraint engine** — HARD constraints always reject, SOFT constraints apply score penalty only
- **Scoring model exposure** — weights, thresholds, and formula included in every result
- GeoJSON output for map visualization (baseline, scenario, and delta layers)
- Detailed explanation layer (why HIGH / MEDIUM / LOW / REJECTED)
- REST API using Flask — strict contract-compliant responses
- **Scenario simulation engine** — what-if analysis without breaking core logic
- **Sensitivity analysis** — per-location delta between baseline and scenario
- **Multi-scenario comparison** — best/worst/most sensitive across scenarios
- **3-layer geo output** — baseline, scenario, and delta layers for map rendering

---

## Project Structure

```
data_raw/                          → Raw datasets (CSV)
src/
  models/                          → 3 scoring models (inland_port, seaplane, hub_spoke)
  data_adapter.py                  → Loads and normalises raw CSV data
  location_entity_builder.py       → Groups signals into location profiles
  scoring_engine.py                → Main deterministic scoring engine (MODIFIED)
  explanation_layer.py             → Human-readable explanation generator
  api.py                           → Flask API — contract-standardized endpoints (MODIFIED)

  # ── Audit-Grade Layer (sprint additions) ──
  signal_trace_layer.py            → Signal registry + trace block builder (NEW)
  constraint_engine.py             → Hard vs soft constraint engine (MODIFIED)
  geo_output_builder.py            → 3-layer GeoJSON output builder (MODIFIED)
  simulate_api.py                  → POST /simulate endpoints — locked contract (MODIFIED)

  # ── Simulation Layer ──
  scenario_model.py                → Scenario input schema + validation
  weight_engine.py                 → Weight adjustment (sum-to-1 enforced)
  sensitivity_engine.py            → Delta computation + impact classification
  scenario_runner.py               → Simulation orchestrator

tests/
  test_scenarios.py                → Original engine tests
  test_scenarios_simulation.py     → Audit-grade test suite (10 cases, all pass)

demo_cases/
  demo_case_1.json                 → Demo: Inland Port Identification
  demo_case_2.json                 → Demo: Hub-Spoke Optimization
  demo_case_3.json                 → Demo: Scenario Comparison

docs/
  API_CONTRACT.md                  → Full API contract — schemas, field definitions, constraint reference

outputs/                           → Generated results (JSON / GeoJSON)
REVIEW_PACKET.md                   → Full technical review documentation
```

---

## How to Run

### 0. Install dependency

```bash
pip install flask
```

### 1. Test each module individually (run from inside `src/`)

```bash
cd src/

python signal_trace_layer.py     # Test trace block generation
python constraint_engine.py      # Test hard/soft constraint enforcement
python scoring_engine.py         # Test full scoring pipeline
python geo_output_builder.py     # Test GeoJSON layer output
```

Each file prints its own self-test output so you can verify it's working before starting the API.

### 2. Run the full test suite (run from root)

```bash
cd ..
python tests/test_scenarios_simulation.py
```

Expected: `Results: 10/10 passed ✓ ALL PASS`

Covers: determinism, hard constraints, soft constraints, scenario weights, override flagging, weight validation, and presence of all contract blocks (trace, constraints, scoring_model).

### 3. Start the API server

Make sure these two lines are present near the bottom of `src/api.py`, just above `app.run(...)`:

```python
from simulate_api import simulate_bp
app.register_blueprint(simulate_bp)
```

Then start the server:

```bash
cd src/
python api.py
```

Server runs at: `http://localhost:5000`

### 4. Verify the API is live

```bash
curl.exe http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "entities_loaded": 6,
  "models_available": ["inland_port", "seaplane", "hub_spoke"],
  "determinism": "guaranteed",
  "ml_used": false
}
```

---

## API Endpoints

### Core Engine

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API overview and available endpoints |
| `/health` | GET | System status |
| `/locations` | GET | All location entities |
| `/results` | GET | All suitability results (filterable) |
| `/results?model=inland_port` | GET | Filter by model type |
| `/results?level=HIGH` | GET | Filter by suitability level |
| `/results?location_id=varanasi_terminal` | GET | Filter by location |
| `/analyze-location` | POST | Score a custom location entity |

### Simulation Layer

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulate` | POST | Run single scenario + delta analysis |
| `/simulate/multi` | POST | Run multiple scenarios + comparison |
| `/simulate/baseline` | POST | Baseline run only (no modifications) |

> **Note:** `/simulate` does **not** accept raw `base_data` injection. Use `scenario_id` for predefined scenarios or `dataset_id` for approved datasets. See `docs/API_CONTRACT.md` for full details.

---

## Scored Result — Output Contract

Every endpoint that returns scored locations produces objects in this exact shape:

```json
{
  "location_id": "varanasi_terminal",
  "model_type": "inland_port",
  "score": 73.75,
  "level": "MEDIUM",
  "trace": {
    "source_signals": {
      "river": ["CWC_RIV_STAB_v1", "CPCB_WQI_v1"],
      "logistics": ["IWAI_LOG_v1", "IWAI_TERM_v1", "IWAI_TRAF_v1"],
      "environmental": ["ENV_WETLAND_v1", "ENV_FLOOD_v1", "ENV_CLEAR_v1"]
    },
    "contributing_signal_ids": ["CPCB_WQI_v1", "CWC_RIV_STAB_v1", "..."],
    "signal_to_factor_map": {
      "CWC_RIV_STAB_v1": "river_stability",
      "IWAI_LOG_v1": "logistics_access"
    }
  },
  "constraints": {
    "hard": [],
    "soft": [],
    "overridden": []
  },
  "scoring_model": {
    "weights": {
      "river_stability": 0.25,
      "terminal_proximity": 0.20,
      "logistics_access": 0.20,
      "water_quality": 0.20,
      "traffic_potential": 0.15
    },
    "thresholds": { "HIGH": 75, "MEDIUM": 50, "LOW": 0 },
    "formula": "score = Σ(factor_score × weight) − soft_penalties; HARD → REJECT"
  },
  "explanation": "Model: Inland Port | Level: MEDIUM | Score: 73.75 | Factor contributions: ..."
}
```

---

## POST /simulate — Quick Example

```bash
curl.exe -X POST http://localhost:5000/simulate \
  -H "Content-Type: application/json" \
  -d "{\"scenario_id\": \"high_logistics\", \"model_type\": \"inland_port\"}"
```

Or with a custom scenario:

```json
POST http://localhost:5000/simulate
Content-Type: application/json

{
  "scenario": {
    "scenario_id": "my_scenario",
    "description": "Boost logistics weight to 0.50",
    "modifications": {
      "priority_weights": {
        "river_stability": 0.10,
        "terminal_proximity": 0.10,
        "logistics_access": 0.50,
        "water_quality": 0.15,
        "traffic_potential": 0.15
      }
    }
  },
  "model_type": "inland_port"
}
```

### Predefined Scenario IDs

| scenario_id | Description |
|-------------|-------------|
| `high_logistics` | Logistics weight boosted to 0.50 |
| `env_priority` | Water quality weight boosted to 0.40 |
| `connectivity_focus` | Terminal proximity and logistics weight elevated |
| `relaxed_logistics` | Soft logistics constraint bypassed (flagged in output) |

---

## Constraint System

### Hard Constraints — always REJECT (score = 0, level = REJECTED)

| Constraint | Trigger |
|------------|---------|
| `wetland_zone` | Location is within a protected wetland |
| `extreme_pollution` | Water quality index < 20 |
| `flood_zone` | Location within active flood zone |
| `critical_depth` | Depth score < 20 |
| `no_env_clearance` | Environmental clearance not obtained |

### Soft Constraints — score penalty only, location not rejected

| Constraint | Trigger | Penalty |
|------------|---------|---------|
| `logistics_absence` | Logistics access score < 30 | −15 pts |
| `low_traffic` | Traffic potential score < 25 | −10 pts |
| `poor_connectivity` | Connectivity score < 25 | −10 pts |
| `high_turbulence` | Turbulence index > 0.7 | −12 pts |

Scenario overrides are always recorded in `constraints.overridden` — never silent.

---

## Models Implemented

### 1. Inland Port Model
River stability · Terminal proximity · Logistics access · Water quality · Traffic potential

### 2. Seaplane Model
Flow turbulence · Water surface quality · Traffic density · Urban proximity · Environmental clearance

### 3. Hub-Spoke Model
Multi-node proximity · Logistics park quality · Terminal density · Connectivity · Urban market access

---

## GeoJSON Layers

`geo_output_builder.py` produces three layers for map rendering:

| Layer | Color basis | Use |
|-------|-------------|-----|
| `baseline` | Level (HIGH=green, MEDIUM=amber, LOW=red, REJECTED=grey) | Initial map render |
| `scenario` | Level under scenario weights | Comparison view |
| `delta` | Direction (IMPROVED=teal, DECLINED=orange, UNCHANGED=grey) | Change visualization |

Every GeoJSON feature's `properties` block includes: `score`, `level`, `color`, `delta`, `reasoning`, `constraints`.

---

## Demo Cases

Three pre-built demo scenarios are in `demo_cases/`:

| File | Use Case | Key Insight |
|------|----------|-------------|
| `demo_case_1.json` | Inland Port Identification | Kanpur always rejected (extreme pollution), Patna highest scorer |
| `demo_case_2.json` | Hub-Spoke Optimization | Patna as primary hub, Sultanganj soft-constrained but developable |
| `demo_case_3.json` | Scenario Comparison | Allahabad most sensitive location across all 3 policy scenarios |

---

## Key Design Principles

- No ML, no randomness — rule-based arithmetic only
- Fully explainable scoring — formula exposed in every result
- Real-world constraints enforced — HARD REJECT is non-negotiable
- Scenario mode always flagged — overrides recorded, never silent
- Weights must sum to 1.0 — invalid inputs rejected before engine runs
- All simulation outputs include WHY the score changed, not just the delta value
- Backend is source of truth — UI reads from API, never replicates logic

---

## Integration

| Team | Consumes |
|------|----------|
| Nikhil (UI / Map Layer) | GeoJSON layers from `geo_output_builder.py` — color, level, delta, reasoning |
| Ankita Prajapati (Validation) | Approved dataset registry in `simulate_api.py` + signal registry in `signal_trace_layer.py` |
| Vinayak Tiwari (Testing) | `tests/test_scenarios_simulation.py` — 10 cases, determinism + contract validation |

Full API schemas, field definitions, and constraint reference: see `docs/API_CONTRACT.md`.

---

## Author

Nupur Gavane
