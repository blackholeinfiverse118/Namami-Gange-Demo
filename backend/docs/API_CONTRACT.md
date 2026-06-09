# API_CONTRACT.md
## NICAI — Ganga Basin Suitability Intelligence Engine
### API Contract Document · v2.1.0

---

## Overview

This document defines the strict API contracts for all endpoints in the NICAI system. All consumers (UI, map layer, integration partners) **must** use these contracts. The backend is the source of truth — UI logic must never replicate or override scoring.

**Base URL:** `http://localhost:5000`  
**Format:** JSON only (`Content-Type: application/json`)  
**Determinism guarantee:** Same input → identical output across all runs.

---

## Standard Response Envelope

All successful responses follow this envelope:

```json
{
  "status": "success",
  "model_type": "inland_port",
  "count": 3,
  "results": [...]
}
```

All error responses:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "status": "error"
}
```

---

## Scored Result Object (Contract Type)

Every endpoint that returns scored locations returns objects conforming to this contract:

```json
{
  "location_id": "string",
  "model_type": "inland_port | seaplane | hub_spoke",
  "score": "float (0.0 – 100.0)",
  "level": "HIGH | MEDIUM | LOW | REJECTED",
  "trace": {
    "source_signals": {
      "river": ["CWC_RIV_STAB_v1", "CWC_DEPTH_v1"],
      "logistics": ["IWAI_LOG_v1", "IWAI_TERM_v1"],
      "water_quality": ["CPCB_BOD_v1", "CPCB_DO_v1"],
      "environmental": ["ENV_WETLAND_v1", "ENV_CLEAR_v1"],
      "demand": ["CENSUS_POP_v1"]
    },
    "contributing_signal_ids": ["sorted", "flat", "list"],
    "signal_to_factor_map": {
      "CWC_RIV_STAB_v1": "river_stability",
      "IWAI_LOG_v1": "logistics_access"
    }
  },
  "constraints": {
    "hard": ["wetland_zone"],
    "soft": ["logistics_absence"],
    "overridden": [],
    "is_rejected": false,
    "soft_penalty_total": 15
  },
  "scoring_model": {
    "weights": {
      "river_stability": 0.25,
      "terminal_proximity": 0.20,
      "logistics_access": 0.20,
      "water_quality": 0.20,
      "traffic_potential": 0.15
    },
    "thresholds": {
      "HIGH": 75,
      "MEDIUM": 50,
      "LOW": 0
    },
    "formula": "score = Σ(factor_score × weight) − soft_penalty"
  },
  "explanation": "Human-readable string explaining why this score/level was reached"
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `location_id` | string | Unique identifier for the location |
| `model_type` | enum | Which scoring model was applied |
| `score` | float | Final score after penalties, clamped 0–100. Always 0.0 if REJECTED. |
| `level` | enum | Suitability tier: HIGH / MEDIUM / LOW / REJECTED |
| `trace.source_signals` | object | Signal IDs grouped by data source category |
| `trace.contributing_signal_ids` | array | Flat sorted list of all signals that contributed to this score |
| `trace.signal_to_factor_map` | object | Maps each signal ID to the factor it drives |
| `constraints.hard` | array | Hard constraints that were triggered (REJECT triggers) |
| `constraints.soft` | array | Soft constraints triggered (penalty applied, no rejection) |
| `constraints.overridden` | array | Constraints bypassed in scenario mode (always flagged, never silent) |
| `constraints.is_rejected` | boolean | True if any hard constraint fired |
| `constraints.soft_penalty_total` | float | Total penalty points deducted from weighted score |
| `scoring_model.weights` | object | Weights applied per factor (must sum to 1.0) |
| `scoring_model.thresholds` | object | Score thresholds for HIGH / MEDIUM / LOW |
| `scoring_model.formula` | string | Explicit formula text — fully auditable. Always the literal string shown above. |
| `explanation` | string | Plain-language explanation of the result |

**Guarantees:**
- `trace`, `constraints`, and `scoring_model` are always present in every result — never null, never omitted
- `level` is always derived from `score` by the backend — never inferred by UI
- `constraints.overridden` is always an explicit list — scenario overrides are never silent

---

## Endpoints

---

### GET /

**Description:** API overview and available endpoints.

**Response:**
```json
{
  "system": "NICAI – Ganga Basin Suitability Intelligence Engine",
  "version": "2.1.0",
  "status": "operational",
  "endpoints": { ... },
  "models_available": ["inland_port", "seaplane", "hub_spoke"]
}
```

---

### GET /health

**Description:** System health check.

**Response:**
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

### GET /locations

**Description:** Returns all location entities currently loaded. No scoring applied.

**Response:**
```json
{
  "count": 6,
  "locations": [
    {
      "location_id": "varanasi_terminal",
      "properties": { ... }
    }
  ]
}
```

---

### GET /results

**Description:** Returns scored results for all locations.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | No | Filter by model: `inland_port`, `seaplane`, `hub_spoke`. Default: `inland_port` |
| `level` | string | No | Filter by level: `HIGH`, `MEDIUM`, `LOW`, `REJECTED` |
| `location_id` | string | No | Filter to a single location |

**Response:**
```json
{
  "model_type": "inland_port",
  "count": 6,
  "results": [
    {
      "location_id": "...",
      "model_type": "inland_port",
      "score": 72.5,
      "level": "MEDIUM",
      "trace": { ... },
      "constraints": { "hard": [], "soft": [], "overridden": [], "is_rejected": false, "soft_penalty_total": 0 },
      "scoring_model": { "weights": {...}, "thresholds": {...}, "formula": "..." },
      "explanation": "..."
    }
  ]
}
```

**Example:**
```
GET /results?model=inland_port&level=HIGH
```

---

### POST /analyze-location

**Description:** Scores a single custom location entity.

**Request Body:**
```json
{
  "entity": {
    "location_id": "my_location",
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
  },
  "model_type": "inland_port"
}
```

**Response:** Single scored result object (see Contract Type above).

**Validation errors:**
- Missing `entity` field → 400
- Invalid `model_type` → 400
- Scoring failure → 500

---

### POST /simulate

**Description:** Runs a scenario simulation and returns baseline, scenario, and delta layers.

> **Demo-locked:** Raw `base_data` injection is disabled. Attempting to pass `base_data` returns HTTP 400 with code `INJECTION_BLOCKED`. Use `scenario_id` or `dataset_id`.

**Request Body — Option A (predefined scenario):**
```json
{
  "scenario_id": "high_logistics",
  "model_type": "inland_port"
}
```

**Request Body — Option B (dataset + custom scenario):**
```json
{
  "dataset_id": "ganga_basin_reference",
  "scenario": {
    "scenario_id": "my_scenario",
    "description": "Custom policy simulation",
    "modifications": {
      "priority_weights": {
        "river_stability": 0.10,
        "terminal_proximity": 0.10,
        "logistics_access": 0.50,
        "water_quality": 0.15,
        "traffic_potential": 0.15
      },
      "constraint_overrides": ["logistics_absence"]
    }
  },
  "model_type": "inland_port"
}
```

> Custom weights must sum to exactly 1.0 — else HTTP 400 with code `INVALID_WEIGHTS`.

**Response:**
```json
{
  "status": "success",
  "model_type": "inland_port",
  "scenario_metadata": {
    "scenario_id": "high_logistics",
    "description": "...",
    "weights_changed": { ... },
    "constraints_overridden": [],
    "is_predefined": true
  },
  "baseline": [ ...scored result objects... ],
  "scenario": [ ...scored result objects... ],
  "delta": [
    {
      "location_id": "...",
      "baseline_score": 72.5,
      "baseline_level": "MEDIUM",
      "scenario_score": 81.0,
      "scenario_level": "HIGH",
      "delta": 8.5,
      "impact": "MODERATE_IMPACT",
      "level_changed": true,
      "delta_reason": "Score improved by 8.5 pts under scenario weights/overrides"
    }
  ],
  "summary": {
    "total_locations": 4,
    "high_impact_changes": 1,
    "level_changes": 1,
    "most_sensitive_location": "allahabad_confluence"
  }
}
```

**Delta impact thresholds:**

| Impact label | Condition |
|---|---|
| `HIGH_IMPACT` | \|delta\| >= 15 |
| `MODERATE_IMPACT` | \|delta\| >= 5 |
| `LOW_IMPACT` | \|delta\| < 5 |

Delta list is sorted by |delta| descending — most sensitive locations first.

**scenario_metadata fields:**

| Field | Type | Description |
|-------|------|-------------|
| `scenario_id` | string | Scenario identifier |
| `description` | string | Human-readable scenario description |
| `weights_changed` | object | Which weights were modified and to what value |
| `constraints_overridden` | array | Which constraints were bypassed (always explicit, never silent) |
| `is_predefined` | boolean | Whether this is a predefined demo scenario |

**Predefined scenario_ids:**

| scenario_id | Description |
|-------------|-------------|
| `high_logistics` | logistics_access weight boosted to 0.40, river_stability reduced to 0.15 |
| `env_priority` | water_quality weight boosted to 0.40, logistics_access reduced to 0.10 |
| `relaxed_logistics` | logistics_absence soft constraint penalty waived (flagged in output) |

**Approved dataset_ids:**
- `ganga_basin_iwai_2024`
- `ganga_basin_reference`
- `demo_baseline`

**Validation errors:**

| Code | HTTP | Trigger |
|------|------|---------|
| `INJECTION_BLOCKED` | 400 | `base_data` key present in request body |
| `UNKNOWN_SCENARIO` | 400 | `scenario_id` not in predefined list |
| `INVALID_MODEL` | 400 | `model_type` not in allowed list |
| `INVALID_WEIGHTS` | 400 | Custom weights do not sum to 1.0 |
| `UNKNOWN_DATASET` | 400 | `dataset_id` not in approved list |
| `INVALID_JSON` | 400 | Request body is not valid JSON |

---

### POST /simulate/baseline

**Description:** Baseline scoring only — no scenario modifications.

**Request Body:**
```json
{
  "model_type": "inland_port",
  "dataset_id": "ganga_basin_reference"
}
```

**Response:**
```json
{
  "status": "success",
  "model_type": "inland_port",
  "baseline": [ ...scored result objects... ],
  "count": 4
}
```

---

### POST /simulate/multi

**Description:** Runs multiple predefined scenarios and returns a comparison.

**Request Body:**
```json
{
  "scenario_ids": ["high_logistics", "env_priority", "relaxed_logistics"],
  "model_type": "inland_port"
}
```

**Response:**
```json
{
  "status": "success",
  "model_type": "inland_port",
  "baseline": [ ...scored result objects... ],
  "scenarios": [
    {
      "scenario_id": "high_logistics",
      "description": "...",
      "scenario_metadata": { ... },
      "results": [ ...scored result objects... ],
      "delta": [ ...delta entries... ],
      "summary": {
        "high_impact_changes": 1,
        "level_changes": 1,
        "most_sensitive_location": "allahabad_confluence"
      }
    }
  ],
  "scenario_count": 3
}
```

---

## GeoJSON Layer Contracts

### Baseline / Scenario Layer Properties

Every GeoJSON feature's `properties` block:

```json
{
  "location_id": "varanasi_terminal",
  "model_type": "inland_port",
  "score": 72.5,
  "level": "HIGH",
  "color": "#2ecc71",
  "delta": null,
  "reasoning": "Level: HIGH | Score: 72.5 | Key factors: river_stability, logistics_access",
  "constraints": {
    "hard": [],
    "soft": [],
    "overridden": [],
    "is_rejected": false
  },
  "scoring_model": {
    "weights": { ... },
    "formula": "score = Σ(factor_score × weight) − soft_penalty"
  },
  "trace_summary": {
    "contributing_signals": ["CWC_RIV_STAB_v1", "IWAI_LOG_v1", "..."]
  }
}
```

### Delta Layer Properties

```json
{
  "location_id": "allahabad_confluence",
  "score": 81.0,
  "level": "HIGH",
  "color": "#1abc9c",
  "delta": 8.5,
  "delta_direction": "IMPROVED",
  "impact": "MODERATE_IMPACT",
  "reasoning": "Score improved by 8.5 pts under scenario weights/overrides",
  "baseline_score": 72.5,
  "baseline_level": "MEDIUM",
  "level_changed": true,
  "constraints": {}
}
```

### Color Reference

| Value | Color | Hex |
|-------|-------|-----|
| HIGH | Green | `#2ecc71` |
| MEDIUM | Amber | `#f39c12` |
| LOW | Red | `#e74c3c` |
| REJECTED | Grey | `#7f8c8d` |
| IMPROVED (delta) | Teal | `#1abc9c` |
| DECLINED (delta) | Orange | `#e67e22` |
| UNCHANGED (delta) | Light Grey | `#95a5a6` |

---

## Constraint Reference

### Hard Constraints (always REJECT — not overridable by any scenario)

| Name | Trigger Condition |
|------|-------------------|
| `wetland_zone` | `is_wetland == True` |
| `extreme_pollution` | BOD > 8 mg/L OR DO < 4 mg/L |
| `no_env_clearance` | `env_clearance == False` |
| `insufficient_depth` | River depth < 2.0m |
| `flood_prone` | `flood_risk == True` |

### Soft Constraints (score penalty only — overridable by scenario)

| Name | Trigger Condition | Penalty |
|------|-------------------|---------|
| `logistics_absence` | Zero logistics parks within range | -15 pts |
| `low_traffic_density` | Traffic density below threshold | -10 pts |
| `poor_connectivity` | Connectivity score < 0.3 | -10 pts |
| `high_turbulence` | Turbulence index > 0.7 | -5 pts |

When a soft constraint is overridden by a scenario, it is recorded in `constraints.overridden` in the result — it is never silently bypassed.

---

## Signal Registry

| Signal ID | Source Dataset | Factor |
|-----------|---------------|--------|
| `CWC_RIV_STAB_v1` | CWC River Gauging Stations | river_stability |
| `CWC_DEPTH_v1` | CWC River Gauging Stations | river_stability |
| `CPCB_BOD_v1` | CPCB Water Quality Monitoring | water_quality |
| `CPCB_DO_v1` | CPCB Water Quality Monitoring | water_quality |
| `IWAI_LOG_v1` | IWAI Logistics Parks | logistics_access |
| `IWAI_TERM_v1` | IWAI Terminal Registry | terminal_proximity |
| `ENV_WETLAND_v1` | Environmental Sensitivity Layer | constraint_check |
| `ENV_CLEAR_v1` | Environmental Clearance Registry | constraint_check |
| `CENSUS_POP_v1` | Census Urban Centers | traffic_potential |

---

## Versioning

| Version | Changes |
|---------|---------|
| 2.1.0 | Added `is_rejected` and `soft_penalty_total` to constraints block; aligned constraint triggers and penalties to engine implementation; updated predefined scenarios to match implemented set; added error code table; clarified `--data-binary` requirement for Windows PowerShell |
| 2.0.0 | Added trace, constraints, scoring_model blocks; locked /simulate; added scenario_metadata |
| 1.0.0 | Original engine — baseline scoring + explanation |

---

## Windows PowerShell Note

When sending POST requests from Windows PowerShell, use `--data-binary @filename.json` instead of `-d @filename.json`. The `@` symbol is PowerShell's splatting operator and causes a parse error when used with `-d`. `--data-binary` bypasses this.

```powershell
Set-Content sim.json '{"scenario_id": "high_logistics", "model_type": "inland_port"}'
curl.exe -X POST http://localhost:5000/simulate -H "Content-Type: application/json" --data-binary @sim.json
```

---

*This document is the authoritative API contract for NICAI v2.1.0. Any deviation from these schemas must be versioned and documented.*