# Integration Surface Definitions
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Version:** 1.0
**Status:** ACTIVE -- all team members must conform to these contracts

---

## Purpose

This document defines the exact integration boundaries between all members
of the NICAI ecosystem. Every input schema, output schema, ownership boundary,
runtime behavior, and failure handling rule is specified here.

No ambiguity is permitted. If something is not specified here, escalate
to the Build Lead before proceeding.

---

## Team Map

| Member | Role | Direction |
|---|---|---|
| Shravani Harde | Data Layer | Sends data TO Nupur (input) |
| Ankita Prajapati | Validation Layer | Validates contracts FROM Nupur (audit) |
| Nikhil | Visualization Layer | Consumes GeoJSON FROM Nupur (output) |
| Tester | Functional Validation | Runs tests AGAINST Nupur's API (verification) |
| Nupur Gavane | Build Lead | Owns intelligence engine, all contracts originate here |

---

## CONTRACT 1 -- DATA CONTRACT
### Shravani Harde (Data Layer) -> Nupur Gavane (Intelligence Engine)

### Ownership
- Shravani owns: raw CSV datasets, dataset versioning, data quality
- Nupur owns: ingestion logic (data_adapter.py), normalization, signal production

### Input Schema -- Raw CSV Datasets

Shravani must deliver datasets in the following format.
Any deviation must be communicated to Nupur before delivery.

**Dataset 1: IWAI Terminals (iwai_terminals_nw1.csv)**

Required columns:
```
terminal_id         -- string, unique identifier, non-empty
terminal_name       -- string, human-readable name
latitude            -- float, India bounds: 6.0 to 37.0
longitude           -- float, India bounds: 68.0 to 97.5
capacity_mtpa       -- float, metric tonnes per annum
terminal_type       -- string: "Multimodal", "Intermodal", "Fixed", "Floating"
connectivity_road   -- string: contains "NH", "highway", "expressway" if connected
connectivity_rail   -- string: contains "yes", "junction", "rail", "DFC" if connected
operational_status  -- string: "Operational" or other
state               -- string, state name
```

**Dataset 2: Water Quality (cpcb_water_quality_ganga.csv)**

Required columns:
```
station_id          -- string, unique identifier
station_name        -- string
latitude            -- float, India bounds
longitude           -- float, India bounds
do_mg_l             -- float, dissolved oxygen in mg/L
bod_mg_l            -- float, biochemical oxygen demand in mg/L
ph                  -- float, pH value
turbidity_ntu       -- float, turbidity in NTU
conductivity_us_cm  -- float, conductivity in uS/cm
ammonia_mg_l        -- float, ammonia in mg/L
pollution_class     -- string: "A", "B", "C", "D", or "E"
state               -- string
river               -- string
```

**Dataset 3: CWC River Stations (cwc_river_stations_ganga.csv)**

Required columns:
```
station_id              -- string, unique identifier
station_name            -- string
latitude                -- float, India bounds
longitude               -- float, India bounds
avg_discharge_cumec     -- float, average discharge in cumecs
monsoon_discharge_cumec -- float
lean_discharge_cumec    -- float
navigability_depth_m    -- float, depth in metres
water_level_variation_m -- float
flow_stability_index    -- string: "low", "medium", "medium-high", "high"
flood_prone             -- string: "yes" or "no"
environmental_sensitivity -- string: "low", "medium", "high"
state                   -- string
river                   -- string
```

**Dataset 4: Logistics Parks (logistics_parks_ganga_belt.csv)**

Required columns:
```
park_id             -- string, unique identifier
park_name           -- string
latitude            -- float, India bounds
longitude           -- float, India bounds
area_acres          -- float
status              -- string: "Operational", "Under Development", "DPR Stage", "Proposed"
road_connectivity   -- string
rail_connectivity   -- string
waterway_connectivity -- string
state               -- string
park_type           -- string
```

**Dataset 5: Urban Centers (urban_centers_ganga_basin.csv)**

Required columns:
```
city_id             -- string, unique identifier
city_name           -- string
latitude            -- float, India bounds
longitude           -- float, India bounds
population_est_2023_lakhs -- float
has_airport         -- string: "yes" or "no"
has_railway_jn      -- string: "yes" or "no"
has_highway_access  -- string: "yes" or "no"
city_class          -- string: "Mega City", "Metro", "Tier-1 City", "Tier-2 City", etc.
state               -- string
```

### Validation Rules Nupur Enforces on Ingestion

- latitude must be between 6.0 and 37.0 (India bounds)
- longitude must be between 68.0 and 97.5 (India bounds)
- All required fields must be non-empty
- Non-numeric lat/lon raises ValueError and skips the row (no crash)
- Out-of-bounds coordinates raise ValueError and skip the row

### Failure Handling

| Failure | Behaviour |
|---|---|
| Missing required field | Row skipped with WARNING log, processing continues |
| Non-numeric lat/lon | Row skipped with WARNING log |
| Out-of-bounds coordinates | Row skipped with WARNING log |
| Entire dataset missing | Loader logs WARNING, returns empty list, engine continues with remaining datasets |
| Empty CSV file | Returns empty list, no crash |

### Expected Runtime Behavior

- data_adapter.py loads all 5 datasets on engine startup
- Total signals loaded printed to console: "[data_adapter] Total signals loaded: N"
- Each dataset loader prints its own count
- Signals are passed to location_entity_builder.py for clustering

### Dataset Versioning

- Shravani must notify Nupur of any schema changes before delivery
- Column renames require data_adapter.py update
- New columns are ignored unless Nupur updates the adapter
- Current dataset versions are the files in data_raw/

---

## CONTRACT 2 -- VALIDATION CONTRACT
### Ankita Prajapati (Validation Layer) -> Nupur Gavane (Intelligence Engine)

### Ownership
- Ankita owns: schema validation, contract compliance checking, audit sign-off
- Nupur owns: output schema definition, contract specification

### What Ankita Validates

Ankita validates that every scored result produced by the engine conforms to
the output contract defined in src/output_contract.py.

### Output Schema Ankita Validates Against

Every scored result must contain these fields:

```
location_id         -- string, non-empty
model_type          -- string: one of "inland_port", "seaplane", "hub_spoke"
score               -- float, range 0.0 to 100.0 inclusive
level               -- string: one of "HIGH", "MEDIUM", "LOW", "REJECTED"
constraints         -- dict with exactly these sub-fields:
                         hard: list of strings
                         soft: list of strings
                         overridden: list of strings
scoring_model       -- dict with:
                         weights: dict of factor -> float
                         thresholds: dict with HIGH, MEDIUM, LOW keys
                         formula: non-empty string
explanation         -- string, non-empty
trace               -- dict with:
                         source_signals: dict
                         contributing_signal_ids: list of strings
                         signal_to_factor_map: dict
```

### Consistency Rules Ankita Checks

- If level is REJECTED, score must be 0.0
- If score is 0.0 and level is REJECTED, at least one hard constraint must be listed
- score must be numeric (not string, not boolean, not null)
- All constraint sub-fields (hard, soft, overridden) must be lists

### How to Run Validation

```
python tests/test_contract_validation.py
```

Expected result: 32/32 passed ALL PASS

Ankita can also validate a single result programmatically:

```python
from src.output_contract import check_output, validate_output
is_valid, errors = check_output(result)
```

### Signal Registry Reference

Ankita validates signal IDs against the registry in src/signal_trace_layer.py.
Valid signal ID prefixes: CWC_, CPCB_, IWAI_, ENV_, CENSUS_
Valid signal ID suffix: _v1 (current version)

### Failure Handling

| Failure | Behaviour |
|---|---|
| Missing required field | check_output returns is_valid=False with specific error message |
| Invalid field value | check_output returns is_valid=False with specific error message |
| Score out of range | Caught and reported: "score: N out of valid range [0.0, 100.0]" |
| Invalid model_type | Caught and reported with list of valid options |
| REJECTED with nonzero score | Caught and reported as "score/level inconsistency" |
| Non-dict result | Caught and reported: "Result must be a dict, got TYPE" |

### Escalation

If Ankita finds contract violations in engine output, escalate to Nupur
with the full errors list from check_output before any showcase run.

---

## CONTRACT 3 -- VISUALIZATION CONTRACT
### Nupur Gavane (Intelligence Engine) -> Nikhil (Visualization Layer)

### Ownership
- Nupur owns: GeoJSON production, color mapping, legend structure
- Nikhil owns: map rendering, UI display, layer switching

### What Nupur Delivers to Nikhil

Three GeoJSON FeatureCollection layers, each as a separate JSON payload:

**Layer 1: baseline**
- Scored locations without any scenario modifications
- Color based on suitability level

**Layer 2: scenario**
- Scored locations under modified weights or constraints
- Color based on suitability level under scenario
- delta field shows score difference from baseline

**Layer 3: delta**
- Change visualization between baseline and scenario
- Color based on direction: IMPROVED, DECLINED, UNCHANGED

### GeoJSON Feature Schema -- What Nikhil Receives

Every feature in every layer has this properties structure:

```json
{
  "location_id":   "string -- unique location identifier",
  "model_type":    "string -- inland_port | seaplane | hub_spoke",
  "score":         "float -- 0.0 to 100.0",
  "level":         "string -- HIGH | MEDIUM | LOW | REJECTED",
  "color":         "string -- hex color code for map marker",
  "delta":         "float or null -- score difference from baseline (null in baseline layer)",
  "reasoning":     "string -- human-readable explanation for tooltip",
  "constraints":   {
    "hard":        "list -- hard constraints that fired",
    "soft":        "list -- soft constraints that fired",
    "overridden":  "list -- constraints bypassed in scenario mode"
  },
  "scoring_model": {
    "weights":     "dict -- factor weights used",
    "thresholds":  "dict -- HIGH/MEDIUM/LOW thresholds",
    "formula":     "string -- scoring formula"
  },
  "trace_summary": {
    "contributing_signals": "list -- signal IDs that fed this score"
  }
}
```

### Color Reference -- What Nikhil Uses for Map Markers

Level colors (baseline and scenario layers):
```
HIGH      #2ecc71   green
MEDIUM    #f39c12   amber
LOW       #e74c3c   red
REJECTED  #7f8c8d   grey
```

Delta colors (delta layer only):
```
IMPROVED  #1abc9c   teal
DECLINED  #e67e22   orange
UNCHANGED #95a5a6   light grey
```

### API Endpoints Nikhil Calls

```
GET  /results?model=inland_port          -- baseline results for a model
GET  /results?level=HIGH                 -- filter by level
GET  /results?location_id=varanasi_terminal  -- single location
POST /analyze-location                   -- score a custom location
POST /simulate                           -- run scenario, returns all 3 layers
POST /simulate/multi                     -- run multiple scenarios
```

### Sample API Call for Map Load

```
GET http://localhost:5000/results?model=inland_port
```

Returns all 6 locations scored, ready for map rendering.

### Coordinate System

All coordinates are [longitude, latitude] in GeoJSON standard (not lat/lon).
Example: Varanasi = [82.9739, 25.3176]
Coordinate reference system: WGS84 (EPSG:4326)

### Failure Handling

| Failure | What Nikhil Should Do |
|---|---|
| API returns 500 | Show error state on map, do not crash UI |
| location_id not in LOCATION_COORDS | Feature uses default centroid [83.0, 25.5] |
| score is null | Do not render marker, log warning |
| API unreachable | Show "Engine offline" message |

### What Nikhil Must NOT Do

- Do not replicate scoring logic in the frontend
- Do not hardcode scores or levels
- Do not modify GeoJSON before rendering
- The backend is the single source of truth for all scores

---

## CONTRACT 4 -- TEST CONTRACT
### Nupur Gavane (Intelligence Engine) -> Tester (Functional Validation)

### Ownership
- Nupur owns: test entity definitions, expected outputs, engine behavior
- Tester owns: test execution, runtime verification, result documentation

### Test Suites Available

| File | Tests | What It Covers |
|---|---|---|
| tests/test_scenarios_simulation.py | 10 | Core engine: determinism, hard/soft constraints, scenario weights, trace blocks |
| tests/test_determinism.py | 10 | 10-run identical output proof for all models |
| tests/test_boundaries.py | 22 | Threshold boundaries, coordinate edge cases, weight validation |
| tests/test_failures.py | 20 | Missing fields, invalid types, empty datasets, malformed records |
| tests/test_api.py | 26 | All API endpoints: health, locations, results, analyze-location |
| tests/test_contract_validation.py | 32 | Output contract validator: all fields, types, consistency rules |

**Total: 120 tests**

### How to Run All Tests

Run from project root:

```
python tests/test_scenarios_simulation.py
python tests/test_determinism.py
python tests/test_boundaries.py
python tests/test_failures.py
python tests/test_contract_validation.py
```

For API tests, start the server first:
```
cd src
python api.py
```
Then in a second terminal:
```
python tests/test_api.py
```

### Expected Results

All suites must show ALL PASS. Any failure must be escalated to Nupur
immediately before showcase.

```
Results: 10/10 passed  ALL PASS
Results: 10/10 passed  ALL PASS
Results: 22/22 passed  ALL PASS
Results: 20/20 passed  ALL PASS
Results: 26/26 passed  ALL PASS
Results: 32/32 passed  ALL PASS
```

### Test Entity Reference

These entities are used across test suites and represent known expected outcomes:

**ENTITY_CLEAN (varanasi_terminal)**
```json
{
  "location_id": "varanasi_terminal",
  "properties": {
    "river_stability_score": 78,
    "terminal_proximity_score": 85,
    "logistics_access_score": 70,
    "water_quality_index": 60,
    "traffic_potential_score": 75,
    "in_wetland": false,
    "in_flood_zone": false,
    "env_clearance": true,
    "depth_score": 65
  }
}
```
Expected: score=73.75, level=MEDIUM, no constraints triggered

**ENTITY_WETLAND (farakka_wetland)**
- in_wetland=true, env_clearance=false
- Expected: level=REJECTED, score=0.0, hard=["wetland_zone", "no_env_clearance"]

**ENTITY_POLLUTED (kanpur_industrial_zone)**
- water_quality_index=18 (below 20 threshold)
- Expected: level=REJECTED, score=0.0, hard=["extreme_pollution"]

**ENTITY_POOR_LOGISTICS (allahabad_confluence)**
- logistics_access_score=20 (below 30 threshold)
- Expected: level=LOW, score=47.4, soft=["logistics_absence"]

### Failure Handling During Testing

| Failure | Action |
|---|---|
| Any test FAIL | Stop, document the failure, escalate to Nupur immediately |
| API connection refused | Confirm server is running: cd src && python api.py |
| Import error | Confirm you are running from project root, not from src/ |
| ModuleNotFoundError | Check sys.path -- tests add src/ automatically |

### What Tester Must NOT Do

- Do not modify test files without Nupur's approval
- Do not mark a FAIL as acceptable without escalation
- Do not run tests from inside the src/ directory (run from project root)
- Do not skip test suites before showcase

---

## Summary -- Integration Boundaries

```
Shravani (CSV datasets)
        |
        | data_raw/*.csv
        v
Nupur (data_adapter.py -> location_entity_builder.py -> scoring_engine.py)
        |
        | scored results (JSON)
        |-----> Ankita (output_contract.py validation)
        |
        | GeoJSON layers
        |-----> Nikhil (map rendering)
        |
        | Flask API (localhost:5000)
        |-----> Tester (test suites)
```

All contracts are enforced by code, not by trust.
- Data contract: data_adapter.py validates on ingestion
- Output contract: output_contract.py validates every result
- API contract: api.py enforces request/response schemas
- Test contract: 120 tests verify all behaviors

**Any integration question not answered here must be escalated to Nupur
before the showcase.**
