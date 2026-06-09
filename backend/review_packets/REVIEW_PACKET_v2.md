# REVIEW PACKET v2
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Version:** 2.0 (Sprint 4 -- Convergence)
**Status:** SHOWCASE READY

---

## IMPORTANT NOTE TO REVIEWER

This is not a design document. This is a proof document.
Every claim in this packet is backed by runnable code, terminal output,
or a passing test. Nothing here is aspirational or theoretical.

If you want to verify any claim, the commands to do so are included inline.

---

## SECTION 1 -- ENTRY POINT

### How to Start the System in 3 Commands

**Terminal 1 -- Start the API:**
```
cd C:\Ganga-Basin-Suitability-Intelligence-Final-Convergence\src
python api.py
```

Expected output:
```
NICAI API -- Starting on http://localhost:5000
```

**Terminal 2 -- Verify it is alive:**
```
curl http://localhost:5000/health
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

**Terminal 2 -- Score all locations:**
```
curl http://localhost:5000/results?model=inland_port
```

The system is now running. All 6 Ganga Basin locations are scored and
available via the API. No further setup required.

---

## SECTION 2 -- CORE FLOW (3 Files)

The entire intelligence pipeline runs through these 3 files in order:

### File 1: src/data_adapter.py
**What it does:** Loads all 5 real datasets from data_raw/ and converts
every row into a structured signal dictionary.

Datasets loaded:
- iwai_terminals_nw1.csv -- IWAI terminal infrastructure
- cpcb_water_quality_ganga.csv -- CPCB water quality monitoring
- cwc_river_stations_ganga.csv -- CWC river hydrology
- logistics_parks_ganga_belt.csv -- Logistics park infrastructure
- urban_centers_ganga_basin.csv -- Urban demand centers

Output: flat list of signal dicts, each with signal_id, source_dataset,
latitude, longitude, signal_type, metrics, tags.

**To run:**
```
cd src
python data_adapter.py
```

### File 2: src/scoring_engine.py
**What it does:** Takes a location entity with properties and produces
a fully scored, traced, explained result.

Steps executed internally:
1. Resolve input format (API input or internal entity)
2. Evaluate hard and soft constraints
3. Compute per-factor scores
4. Apply weights to compute raw score
5. Apply soft constraint penalties
6. Apply hard constraint rejection if triggered
7. Build explanation string
8. Attach signal trace

Output: scored result dict with score, level, constraints, scoring_model,
explanation, trace, factor_scores.

**To run:**
```
cd src
python scoring_engine.py
```

### File 3: src/api.py
**What it does:** Flask API that exposes the engine over HTTP.
All endpoints return strict contract-compliant responses.

Endpoints:
- GET /health
- GET /locations
- GET /results (filterable by model, level, location_id)
- POST /analyze-location
- POST /simulate
- POST /simulate/multi
- POST /simulate/baseline

**To run:**
```
cd src
python api.py
```

---

## SECTION 3 -- LIVE FLOW

End-to-end data flow from raw CSV to map-ready output:

```
data_raw/*.csv (5 real datasets)
        |
        | data_adapter.py -- loads, validates, normalizes
        v
signals list (IWAI + CPCB + CWC + Logistics + Urban signals)
        |
        | location_entity_builder.py -- clusters signals within 75 km radius
        v
location entities (6 Ganga Basin locations with summary_metrics)
        |
        | scoring_engine.py -- deterministic rule-based scoring
        v
scored results (score, level, factor_scores, constraints, trace, explanation)
        |
        | output_contract.py -- validates every result against strict schema
        v
contract-valid results
        |
        | api.py -- exposes via Flask HTTP endpoints
        v
JSON API responses
        |
        | geo_output_builder.py -- converts to GeoJSON FeatureCollection
        v
GeoJSON layers (baseline, scenario, delta) with coordinates + colors
        |
        | Nikhil (Visualization Layer)
        v
Map rendered with scored locations
```

**Live verification command:**
```
curl http://localhost:5000/results?model=inland_port
```

This single command triggers the entire flow above and returns
contract-valid, map-ready scored results.

---

## SECTION 4 -- WHAT WAS BUILT

### Sprint 4 Additions (this sprint)

All files below were created in this sprint. Nothing from Sprint 3 was
modified.

**New test files:**

| File | Tests | Coverage |
|---|---|---|
| tests/test_determinism.py | 10 | 10-run identical output proof, all 3 models |
| tests/test_boundaries.py | 22 | 74.9/75.1 km boundary, score thresholds, constraint triggers |
| tests/test_failures.py | 20 | Missing fields, invalid types, empty datasets, malformed records |
| tests/test_api.py | 26 | All API endpoints, valid/bad requests, error handlers |
| tests/test_contract_validation.py | 32 | Output contract: all fields, types, consistency rules |

**New source file:**

| File | Purpose |
|---|---|
| src/output_contract.py | Strict schema validator -- rejects invalid outputs |

**New proof files:**

| File | What it proves |
|---|---|
| proofs/runtime_execution_proof.md | Engine runs end-to-end, real terminal output |
| proofs/determinism_proof.md | Boundary tests 22/22, failure tests 20/20 |
| proofs/api_execution_proof.md | API 26/26 pass, all endpoints verified live |
| proofs/geo_output_proof.md | GeoJSON produced with real coordinates and colors |

**New documentation files:**

| File | Purpose |
|---|---|
| integration_surface.md | Contracts for Shravani, Ankita, Nikhil, Tester |
| showcase_demo.md | 9-step runnable demo walkthrough |
| sample_api_requests.json | 19 ready-to-use API requests with expected outputs |
| sample_outputs/baseline_inland_port.geojson | Real GeoJSON with 6 locations |
| review_packets/REVIEW_PACKET_v2.md | This document |

### Sprint 3 Foundations (carried forward, not modified)

| File | What it provides |
|---|---|
| src/scoring_engine.py | Deterministic scoring, 3 models, weight exposure |
| src/api.py | Flask API, all endpoints, contract responses |
| src/constraint_engine.py | Hard/soft constraints, penalties, override flagging |
| src/signal_trace_layer.py | Signal registry, trace block builder |
| src/geo_output_builder.py | 3-layer GeoJSON output |
| src/data_adapter.py | 5 real dataset loaders with validation |
| src/location_entity_builder.py | 75 km radius clustering, haversine distance |
| src/explanation_layer.py | Human-readable scoring explanations |
| tests/test_scenarios_simulation.py | Original 10-test audit suite |

---

## SECTION 5 -- FAILURE CASES

### Hard Constraint Failures (REJECT -- non-negotiable)

| Location | Constraint | Trigger | Score | Level |
|---|---|---|---|---|
| Kanpur Industrial Zone | extreme_pollution | WQI=18 (threshold < 20) | 0.0 | REJECTED |
| Farakka Wetland | wetland_zone | in_wetland=true | 0.0 | REJECTED |
| Farakka Wetland | no_env_clearance | env_clearance=false | 0.0 | REJECTED |

Hard constraints cannot be overridden in strict mode. They represent
absolute disqualifiers: protected wetlands, extreme pollution, flood zones,
insufficient depth, missing environmental clearance.

**Verified by:** tests/test_scenarios_simulation.py Tests 2 and 3

### Soft Constraint Failures (penalty -- developable with investment)

| Location | Constraint | Trigger | Penalty | Score Impact |
|---|---|---|---|---|
| Allahabad Confluence | logistics_absence | logistics_access_score=20 (threshold < 30) | -15 pts | 62.4 -> 47.4 |

Soft constraints apply a score penalty but do not reject the location.
They represent gaps that can be resolved through targeted infrastructure
investment.

**Verified by:** tests/test_scenarios_simulation.py Test 4

### Input Failure Handling

| Failure Mode | Engine Response | Test |
|---|---|---|
| Missing location_id | Fallback to "unknown", continues scoring | test_failures.py A1 |
| Missing scoring fields | Defaults to 0, low score, no crash | test_failures.py A2 |
| None field values | Defaults to 0, no crash | test_failures.py B1 |
| String instead of number | Raises clean ValueError | test_failures.py B2 |
| Negative values | Score clamped to 0 | test_failures.py B3 |
| Empty entity list | Returns empty list | test_failures.py C1 |
| Invalid model type | Raises ValueError with valid options listed | test_failures.py E1 |

### API Failure Handling

| Request | API Response | Test |
|---|---|---|
| Missing entity field | HTTP 400 with descriptive error | test_api.py E1 |
| Unknown model_type | HTTP 400 with valid options listed | test_api.py E2 |
| Empty JSON body | HTTP 400 | test_api.py E3 |
| Non-JSON body | HTTP 400 | test_api.py E4 |
| Unknown endpoint | HTTP 404 | test_api.py G1 |
| Wrong HTTP method | HTTP 405 | test_api.py G2 |

---

## SECTION 6 -- PROOF

### Test Suite Results (all captured from live terminal execution)

```
python tests/test_scenarios_simulation.py
Results: 10/10 passed  ALL PASS

python tests/test_determinism.py
Results: 10/10 passed  ALL PASS

python tests/test_boundaries.py
Results: 22/22 passed  ALL PASS

python tests/test_failures.py
Results: 20/20 passed  ALL PASS

python tests/test_contract_validation.py
Results: 32/32 passed  ALL PASS

python tests/test_api.py
Results: 26/26 passed  ALL PASS
```

Total: 120 tests, 0 failures.

### Determinism Proof (key output)

The engine was run 10 times on identical input. Every run produced
identical output:

```
TEST 1 -- Single entity score: 10 runs identical
         -> all scores = 75.25 | unique values = {75.25}
TEST 6 -- Batch score_all: 10 runs, all 3 entities identical
         -> unique batch outputs = 1
```

Full proof: proofs/determinism_proof.md

### Boundary Proof (key output)

```
TEST A1 -- 74.9 km signal: inside cluster radius (<= 75 km)   PASS
TEST A2 -- 75.1 km signal: outside cluster radius (> 75 km)   PASS
TEST B1 -- Score 75.0 -> HIGH                                  PASS
TEST B2 -- Score 74.9 -> MEDIUM (just below HIGH threshold)    PASS
TEST D1 -- WQI=19 triggers extreme_pollution (< 20)            PASS
TEST D2 -- WQI=20 does NOT trigger extreme_pollution           PASS
```

Full proof: proofs/determinism_proof.md

### API Proof (key output)

```
TEST D3 -- POST /analyze-location: deterministic (2 identical requests)
         -> run1=73.75 run2=73.75                              PASS
TEST D4 -- POST /analyze-location: wetland entity -> REJECTED
         -> level=REJECTED score=0.0                           PASS
TEST G1 -- GET /nonexistent: returns 404                       PASS
TEST G2 -- POST /health: returns 405 Method Not Allowed        PASS
```

Full proof: proofs/api_execution_proof.md

### GeoJSON Proof

Real coordinates produced for Ganga Basin locations:
- varanasi_terminal: [82.9739, 25.3176] -- Varanasi, UP
- patna_river_port: [85.1376, 25.5941] -- Patna, Bihar

Colors correctly assigned:
- MEDIUM -> #f39c12 (amber)
- HIGH -> #2ecc71 (green)
- REJECTED -> #7f8c8d (grey)

Full proof: proofs/geo_output_proof.md
Sample output: sample_outputs/baseline_inland_port.geojson

### Contract Validation Proof

Real engine output validated against strict schema:

```
TEST F1 -- Real engine output (inland_port): passes contract
         -> is_valid=True score=73.75 level=MEDIUM errors=[]   PASS
TEST F2 -- Real REJECTED engine output: passes contract
         -> is_valid=True level=REJECTED errors=[]             PASS
TEST F3 -- All 3 models produce contract-valid output
         -> inland_port=True | seaplane=True | hub_spoke=True  PASS
```

---

## SECTION 7 -- INTEGRATION SURFACES

Full contracts defined in integration_surface.md. Summary:

### Shravani -> Nupur (Data Contract)
- Delivers: 5 CSV datasets in specified column format
- Nupur ingests via: src/data_adapter.py
- Validation: lat/lon bounds checked, required fields checked, bad rows skipped
- Failure handling: bad rows skipped with WARNING, processing continues

### Ankita -> Nupur (Validation Contract)
- Validates: every scored result against output_contract.py schema
- Tool: python tests/test_contract_validation.py (32 rules)
- Escalation: any contract violation reported to Nupur before showcase

### Nupur -> Nikhil (Visualization Contract)
- Delivers: GeoJSON FeatureCollection with score, level, color, delta, reasoning
- Endpoint: GET /results?model=inland_port or POST /simulate
- Color map: HIGH=#2ecc71, MEDIUM=#f39c12, LOW=#e74c3c, REJECTED=#7f8c8d
- Nikhil must NOT replicate scoring logic in the frontend

### Nupur -> Tester (Test Contract)
- Delivers: 6 test suites, 120 tests total
- All suites must pass before showcase
- API tests require server running on localhost:5000
- Any failure escalated to Nupur immediately

---

## SECTION 8 -- DETERMINISM VERIFICATION

### What Determinism Means in This System

Determinism means: given the same input, the engine always produces the
exact same output. No randomness. No ML variance. No time-dependent values.

This is a deliberate design choice for government-grade trust. A reviewer
must be able to re-run the engine on the same data one week later and get
the exact same scores.

### How Determinism is Achieved

- All scoring is arithmetic: weighted sum of numeric factor scores
- Weights are fixed constants defined in SCORING_MODELS
- Constraint thresholds are fixed constants
- No random number generators are used anywhere
- No ML models or probabilistic logic anywhere in the codebase
- No external API calls or time-based values in scoring

### Determinism Test Results

10 independent runs on 3 different entity types:

| Entity | Model | Runs | Unique Scores | Result |
|---|---|---|---|---|
| patna_river_port | inland_port | 10 | 1 (75.25) | PASS |
| hajipur_hub | inland_port | 10 | 1 | PASS |
| kanpur_industrial_zone | inland_port | 10 | 1 (0.0 REJECTED) | PASS |
| varanasi_terminal | seaplane | 10 | 1 (74.15) | PASS |
| hajipur_hub | hub_spoke | 10 | 1 (66.65) | PASS |
| patna_river_port | custom weights | 10 | 1 (63.45) | PASS |
| hajipur_hub | override scenario | 10 | 1 (65.35) | PASS |

**To verify yourself:**
```
python tests/test_determinism.py
```

Expected: Results: 10/10 passed  ALL PASS

---

## SECTION 9 -- SHOWCASE FLOW

The complete showcase can be delivered in under 10 minutes using the
9-step flow in showcase_demo.md. Summary:

### Step 1 -- Start (30 seconds)
```
cd src && python api.py
curl http://localhost:5000/health
```
Shows: system is live, ml_used=false, determinism=guaranteed

### Step 2 -- Score All Locations (1 minute)
```
curl http://localhost:5000/results?model=inland_port
```
Shows: Patna=HIGH, Kanpur=REJECTED, Farakka=REJECTED, others scored

### Step 3 -- Explainability Deep Dive (2 minutes)
POST /analyze-location with Patna entity.
Shows: score=75.25, full factor breakdown, formula exposed, signal trace

### Step 4 -- Hard Constraint in Action (1 minute)
POST /analyze-location with Kanpur entity (WQI=18).
Shows: REJECTED, score=0.0, extreme_pollution constraint, cannot be overridden

### Step 5 -- Soft Constraint and Policy Signal (1 minute)
POST /analyze-location with Allahabad entity (logistics=20).
Shows: LOW (not REJECTED), -15 pt penalty, location developable with investment

### Step 6 -- GeoJSON Map Output (1 minute)
```
python geo_output_builder.py
```
Shows: FeatureCollection with real coordinates, color-coded by suitability

### Step 7 -- Determinism Proof (1 minute)
```
python tests/test_determinism.py
```
Shows: 10/10 pass, same score 10 times, zero variance

### Step 8 -- Contract Validation (1 minute)
```
python tests/test_contract_validation.py
```
Shows: 32/32 pass, every output schema rule enforced

### Step 9 -- Full Test Suite (1 minute)
Run all 5 test suites.
Shows: 120 tests, all pass

### Total Showcase Time: Under 10 minutes
### Everything runs live. Nothing is pre-recorded or mocked.

---

## FINAL SUMMARY

| Requirement from Sprint Brief | Status |
|---|---|
| Real datasets used | DONE -- 5 real CSVs (IWAI, CPCB, CWC, Logistics, Urban) |
| Deterministic intelligence | DONE -- rule-based arithmetic, no ML, 10-run proof |
| Validated contracts | DONE -- output_contract.py, 32 contract rules |
| API outputs | DONE -- Flask API, 6 endpoints, contract-compliant |
| Map consumption (GeoJSON) | DONE -- 3-layer GeoJSON with colors and coordinates |
| Runtime proof | DONE -- 4 proof files with real terminal output |
| No mock-only demos | DONE -- every step in showcase_demo.md is runnable |
| Architecture proven | DONE -- 120 tests passing, live API verified |
| Integration surfaces defined | DONE -- integration_surface.md, all 4 team contracts |
| Showcase preparation | DONE -- showcase_demo.md, sample_api_requests.json |
| Review packet proof-heavy | DONE -- this document, all claims backed by test output |

**Distance from prototype to real product: materially reduced.**
**The system is deterministic, contract-validated, API-live, and showcase-ready.**
