# REVIEW_PACKET.md
## NICAI — Ganga Basin Suitability Intelligence Engine
### Final Convergence Review Packet · v2.0.0

**Author:** Nupur Gavane
**Sprint:** Audit-Grade Intelligence + API Contracts + Demo Surface
**Status:** Final — All tests passing, API live and verified

---

## 1. ENTRY POINT

**Start here to run the system:**

```bash
# Install dependency
pip install flask

# Start the full API server
cd src/
python api.py
```

Server starts at: `http://localhost:5000`

**Verify the system is live:**
```
GET http://localhost:5000/health
```

Expected response (verified in execution):
```json
{
  "determinism": "guaranteed",
  "entities_loaded": 6,
  "ml_used": false,
  "models_available": ["inland_port", "seaplane", "hub_spoke"],
  "status": "healthy"
}
```

---

## 2. CORE FLOW (3 Files)

### File 1: `src/signal_trace_layer.py`
**Role:** Makes every output traceable to its source dataset.

Builds three trace sub-blocks on every scored result:
- `source_signals` — signal IDs grouped by dataset category (river/CWC, logistics/IWAI, water_quality/CPCB, environmental, demand/Census)
- `contributing_signal_ids` — flat sorted list of all signals that fed this score
- `signal_to_factor_map` — maps each signal ID to the factor it drives

Key function: `attach_trace(result, entity_properties, model_type)` — attaches trace block without modifying score.

### File 2: `src/constraint_engine.py`
**Role:** Enforces hard vs soft constraints deterministically.

- **HARD constraints** (wetland, extreme pollution, flood zone, critical depth, no env clearance) → always REJECT, score = 0, level = REJECTED
- **SOFT constraints** (logistics absence, low traffic, poor connectivity, high turbulence) → score penalty only, location not rejected
- Scenario overrides always logged in `constraints.overridden` — never silent

Key function: `evaluate_constraints(entity_properties, scenario_overrides)` → returns full constraint result including penalty amount and rejection reason.

### File 3: `src/scoring_engine.py`
**Role:** Single source of truth for all scoring. Deterministic, no ML.

Supports two input schemas:
- API input (`entity["properties"]`) — pre-normalised scoring fields
- Internal input (`entity["summary_metrics"]`) — raw dataset fields from `location_entity_builder.py`, translated via documented normalisation rules

Steps per entity:
1. Resolve input schema
2. Evaluate constraints
3. Compute per-factor scores
4. Apply weighted sum
5. Apply soft penalties
6. Apply hard reject if triggered
7. Build explanation
8. Attach trace block

Key functions: `score_entity(entity, model_type)`, `score_all(entities, model_type)`

---

## 3. LIVE FLOW

```
HTTP Request
    ↓
api.py / simulate_api.py
    ↓
score_entity() [scoring_engine.py]
    ├── evaluate_constraints()    [constraint_engine.py]
    │     ├── HARD → REJECT
    │     └── SOFT → penalty
    ├── compute_factor_scores()
    ├── compute_weighted_score()
    ├── apply_soft_penalty()
    ├── assign_level()
    ├── build_explanation()
    └── attach_trace()            [signal_trace_layer.py]
    ↓
Contract response: { location_id, model_type, score, level,
                     trace, constraints, scoring_model, explanation }
    ↓
geo_output_builder.py (for map layer)
    ↓
GeoJSON: { baseline, scenario, delta } layers
    ↓
UI / Map (Nikhil's layer)
```

---

## 4. WHAT WAS BUILT (This Sprint)

### New Files
| File | Purpose |
|------|---------|
| `src/signal_trace_layer.py` | Signal registry + trace block builder |
| `docs/API_CONTRACT.md` | Full API contract — schemas, field definitions, constraint reference |
| `demo_cases/demo_case_1.json` | Demo: Inland Port Identification |
| `demo_cases/demo_case_2.json` | Demo: Hub-Spoke Optimization |
| `demo_cases/demo_case_3.json` | Demo: Scenario Comparison |

### Modified Files
| File | Changes |
|------|---------|
| `src/scoring_engine.py` | Added `scoring_model` block; integrated trace + constraint blocks; dual input schema support (properties + summary_metrics) |
| `src/constraint_engine.py` | HARD vs SOFT separation; `constraint_detail` per trigger; `overridden` block always explicit |
| `src/simulate_api.py` | Raw `base_data` injection blocked; `scenario_metadata` added; approved dataset + predefined scenario validation |
| `src/geo_output_builder.py` | All 6 required GeoJSON properties (score, level, color, delta, reasoning, constraints); 3-layer output |
| `src/api.py` | Contract-enforced response shape via `build_contract_response()` |
| `tests/test_scenarios.py` | Rewritten to use unified scoring engine; dual sys.path fix; `adapt_entity()` bridge |
| `tests/test_scenarios_simulation.py` | Expanded to 10 audit-grade test cases |

---

## 5. FAILURE CASES

### Case 1: Hard Constraint — Wetland
**Input:** `in_wetland: true`
**Output:** `score=0.0, level=REJECTED, constraints.hard=["wetland_zone"]`
**Verified:** Farakka wetland → REJECTED in live API

### Case 2: Hard Constraint — Extreme Pollution
**Input:** `water_quality_index: 18` (below threshold of 20)
**Output:** `score=0.0, level=REJECTED, constraints.hard=["extreme_pollution"]`
**Verified:** Kanpur industrial zone → REJECTED across all 3 models

### Case 3: Multiple Hard Constraints
**Input:** `in_wetland: true` AND `env_clearance: false`
**Output:** Both listed in `constraints.hard`, score=0
**Verified:** Farakka wetland → `hard: ["wetland_zone", "no_env_clearance"]`

### Case 4: Soft Constraint — Logistics Absence
**Input:** `logistics_access_score: 20` (below 30 threshold)
**Output:** `constraints.soft=["logistics_absence"]`, score reduced by 15pts, NOT rejected
**Verified:** Allahabad confluence → score=44.8, level=LOW (soft penalty applied)

### Case 5: Raw base_data Injection Blocked
**Input:** POST /simulate with `"base_data": []`
**Output:** 400 error — `"Direct base_data injection is disabled in demo mode"`

### Case 6: Unknown scenario_id
**Input:** `"scenario_id": "fake_scenario"`
**Output:** 400 error listing available predefined scenarios

### Case 7: Invalid model_type
**Input:** `"model_type": "submarine_port"`
**Output:** 400 error listing valid model types

### Case 8: Missing Entity Fields
**Input:** Entity missing optional fields
**Output:** Engine skips missing signals gracefully, scores on available fields. No crash.

### Case 9: Weights Not Summing to 1.0
**Input:** Weights summing to 1.10
**Output:** `ValueError: Weights must sum to 1.0. Got: 1.1`
**Verified:** test_scenarios_simulation.py TEST 7

### Case 10: Schema Mismatch (summary_metrics input)
**Input:** Entity from `location_entity_builder` using `summary_metrics` keys
**Output:** Engine translates via documented normalisation rules, produces real scores
**Verified:** test_scenarios.py — all 9/9 passing with real dataset entities

---

## 6. PROOF

### Test Results (Executed and Verified)

```
test_scenarios_simulation.py:
  ✓ PASS  TEST 1  — Determinism (2 runs, identical output)
  ✓ PASS  TEST 2  — Hard constraint: wetland → REJECTED
  ✓ PASS  TEST 3  — Hard constraint: extreme_pollution → REJECTED
  ✓ PASS  TEST 4  — Soft constraint: logistics_absence → penalty only
  ✓ PASS  TEST 5  — Scenario weights: high_logistics applied + recorded
  ✓ PASS  TEST 6  — Scenario override: logistics_absence bypassed + flagged
  ✓ PASS  TEST 7  — Weight validation: non-1.0 sum raises ValueError
  ✓ PASS  TEST 8  — Constraint block: hard/soft/overridden present in all results
  ✓ PASS  TEST 9  — Trace block: source_signals + signal_ids + factor_map present
  ✓ PASS  TEST 10 — Scoring model block: weights + thresholds + formula present
  Results: 10/10 passed ✓ ALL PASS

test_scenarios.py:
  [PASS] SCENARIO 1 — High Connectivity (LOC014): hard constraint valid
  [PASS] SCENARIO 2 — Env Restricted (LOC011): REJECTED
  [PASS] SCENARIO 3 — Isolated Region (LOC001): REJECTED
  [PASS] SCENARIO 4 — Mixed Signals (LOC004): LOW (score=45.1)
  Results: 9/9 passed ✓ ALL PASS
```

### Live API Outputs (Verified)

**GET /health:**
```json
{"status":"healthy","determinism":"guaranteed","ml_used":false,
 "entities_loaded":6,"models_available":["inland_port","seaplane","hub_spoke"]}
```

**GET /results?level=HIGH — only Patna qualifies:**
```json
{"count":1,"model_type":"inland_port",
 "results":[{"location_id":"patna_river_port","score":75.25,"level":"HIGH"}]}
```

**GET /results?level=REJECTED — Kanpur (extreme pollution) + Farakka (wetland):**
```json
{"count":2,"results":[
  {"location_id":"kanpur_industrial_zone","level":"REJECTED",
   "constraints":{"hard":["extreme_pollution"]}},
  {"location_id":"farakka_wetland","level":"REJECTED",
   "constraints":{"hard":["wetland_zone","no_env_clearance"]}}
]}
```

**Scoring formula verified (Patna, inland_port):**
```
river_stability:    85.0 × 0.25 = 21.25
terminal_proximity: 80.0 × 0.20 = 16.00
logistics_access:   75.0 × 0.20 = 15.00
water_quality:      55.0 × 0.20 = 11.00
traffic_potential:  80.0 × 0.15 = 12.00
                              TOTAL = 75.25 → HIGH ✓
```

**Soft constraint verified (Allahabad, logistics_access=20):**
```
Raw score:    59.8
Soft penalty: -15 (logistics_absence)
Final score:  44.8 → LOW
```

**Signal trace verified (varanasi_terminal):**
```json
{
  "source_signals": {
    "river":        ["CWC_RIV_STAB_v1", "CPCB_WQI_v1", "CWC_DEPTH_v1"],
    "logistics":    ["IWAI_TERM_v1", "IWAI_LOG_v1", "IWAI_TRAF_v1"],
    "environmental":["ENV_WETLAND_v1", "ENV_FLOOD_v1", "ENV_CLEAR_v1"],
    "water_quality":["CPCB_POLL_v1"]
  },
  "contributing_signal_ids": [
    "CPCB_POLL_v1","CPCB_WQI_v1","CWC_DEPTH_v1","CWC_RIV_STAB_v1",
    "ENV_CLEAR_v1","ENV_FLOOD_v1","ENV_WETLAND_v1",
    "IWAI_LOG_v1","IWAI_TERM_v1","IWAI_TRAF_v1"
  ]
}
```

### Determinism Proof
Same entity run 50 times → identical score every run (61.6).
Same entity run through test suite twice → identical trace, level, constraints.
No random, no time-based, no ML — pure arithmetic on input values.

---

## Integration Checklist

| Team | Consumes | Status |
|------|----------|--------|
| Nikhil (UI/Map) | GeoJSON layers — color, level, delta, reasoning |  Ready — `geo_output_builder.py` |
| Ankita (Validation) | Approved dataset registry in `simulate_api.py` |  Ready — `APPROVED_DATASETS` dict |
| Vinayak (Testing) | `tests/test_scenarios_simulation.py` — 10 cases |  10/10 passing |

Full API schemas and field definitions: `docs/API_CONTRACT.md`

---

*This system is ready for demonstration to decision-makers.
Every output is traceable. Every score is explainable.
Every constraint is enforced. Every API response is contract-compliant.*