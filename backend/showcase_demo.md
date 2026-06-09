# Showcase Demo -- NICAI Namami Gange Intelligence System
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Status:** RUNNABLE -- every step below executes against live code

---

## What This Demo Shows

This document is a complete, step-by-step walkthrough of the NICAI intelligence
system from raw dataset to map-ready output. Every command is real and runnable.
Every output shown was captured from actual execution.

The demo answers the core question of the Namami Gange programme:
"Which locations along the Ganga Basin are suitable for infrastructure
development, and why?"

---

## Pre-Demo Setup -- Run Once

Ensure you are in the project root directory:
```
cd C:\Ganga-Basin-Suitability-Intelligence-Final-Convergence
```

Ensure Flask is installed:
```
pip install flask
```

---

## STEP 1 -- Verify the Engine is Alive

**What this shows:** The intelligence engine is running and healthy.

**Command:**
```
cd src
python api.py
```

**Expected output:**
```
NICAI API -- Starting on http://localhost:5000
```

**In a second terminal, verify health:**
```
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "entities_loaded": 6,
  "models_available": ["inland_port", "seaplane", "hub_spoke"],
  "determinism": "guaranteed",
  "ml_used": false
}
```

**What this proves:**
- System is live
- 6 Ganga Basin locations are loaded
- 3 scoring models are available
- No machine learning -- pure deterministic logic
- Determinism is guaranteed

---

## STEP 2 -- Score All Locations (Baseline Run)

**What this shows:** All 6 Ganga Basin locations scored for Inland Port
suitability in a single API call.

**Command:**
```
curl http://localhost:5000/results?model=inland_port
```

**Expected response (abbreviated):**
```json
{
  "model_type": "inland_port",
  "count": 6,
  "results": [
    {
      "location_id": "varanasi_terminal",
      "score": 73.75,
      "level": "MEDIUM",
      "constraints": { "hard": [], "soft": [], "overridden": [] }
    },
    {
      "location_id": "patna_river_port",
      "score": 75.25,
      "level": "HIGH",
      "constraints": { "hard": [], "soft": [], "overridden": [] }
    },
    {
      "location_id": "kanpur_industrial_zone",
      "score": 0.0,
      "level": "REJECTED",
      "constraints": { "hard": ["extreme_pollution"], "soft": [], "overridden": [] }
    },
    {
      "location_id": "farakka_wetland",
      "score": 0.0,
      "level": "REJECTED",
      "constraints": { "hard": ["wetland_zone", "no_env_clearance"], "soft": [], "overridden": [] }
    }
  ]
}
```

**What this shows:**
- Patna is the highest scoring location (75.25 -- HIGH)
- Kanpur is permanently REJECTED due to extreme water pollution (WQI=18, threshold < 20)
- Farakka is permanently REJECTED -- protected wetland + no environmental clearance
- Every result includes the exact reason for its score

---

## STEP 3 -- Deep Dive into a Single Location

**What this shows:** Full explainability for one location -- every factor,
every signal, every constraint, the formula used.

**Command:**
```
curl -X POST http://localhost:5000/analyze-location ^
  -H "Content-Type: application/json" ^
  -d "{\"entity\": {\"location_id\": \"patna_river_port\", \"properties\": {\"river_stability_score\": 85, \"terminal_proximity_score\": 80, \"logistics_access_score\": 75, \"water_quality_index\": 55, \"traffic_potential_score\": 80, \"in_wetland\": false, \"in_flood_zone\": false, \"env_clearance\": true, \"depth_score\": 72}}, \"model_type\": \"inland_port\"}"
```

**Expected response:**
```json
{
  "location_id": "patna_river_port",
  "model_type": "inland_port",
  "score": 75.25,
  "level": "HIGH",
  "factor_scores": {
    "river_stability": 85.0,
    "terminal_proximity": 80.0,
    "logistics_access": 75.0,
    "water_quality": 55.0,
    "traffic_potential": 80.0
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
    "formula": "score = (river_stability_score x 0.25) + (terminal_proximity_score x 0.20) + (logistics_access_score x 0.20) + (water_quality_index x 0.20) + (traffic_potential_score x 0.15)"
  },
  "explanation": "Model: Inland Port | Level: HIGH | Score: 75.25 | river_stability: 85.0 x 0.25 = 21.25 | terminal_proximity: 80.0 x 0.20 = 16.0 | logistics_access: 75.0 x 0.20 = 15.0 | water_quality: 55.0 x 0.20 = 11.0 | traffic_potential: 80.0 x 0.15 = 12.0",
  "trace": {
    "source_signals": {
      "river": ["CWC_RIV_STAB_v1", "CPCB_WQI_v1"],
      "logistics": ["IWAI_TERM_v1", "IWAI_LOG_v1", "IWAI_TRAF_v1"],
      "environmental": ["ENV_WETLAND_v1", "ENV_FLOOD_v1", "ENV_CLEAR_v1"]
    },
    "contributing_signal_ids": [
      "CPCB_WQI_v1", "CWC_RIV_STAB_v1", "ENV_CLEAR_v1",
      "ENV_FLOOD_v1", "ENV_WETLAND_v1", "IWAI_LOG_v1",
      "IWAI_TERM_v1", "IWAI_TRAF_v1"
    ]
  }
}
```

**What this shows:**
- Full factor-by-factor breakdown: which factor contributed how many points
- Scoring formula exposed -- anyone can verify the math manually
- Every signal traced back to its source dataset (CWC, CPCB, IWAI)
- No black box -- complete audit trail from raw data to final score

**Manual verification:**
```
85.0 x 0.25 = 21.25   (river_stability)
80.0 x 0.20 = 16.00   (terminal_proximity)
75.0 x 0.20 = 15.00   (logistics_access)
55.0 x 0.20 = 11.00   (water_quality)
80.0 x 0.15 = 12.00   (traffic_potential)
                ------
Total         = 75.25  HIGH
```

---

## STEP 4 -- Show Hard Constraint in Action

**What this shows:** A location with extreme pollution is permanently
rejected -- no score, no override possible in strict mode.

**Command:**
```
curl -X POST http://localhost:5000/analyze-location ^
  -H "Content-Type: application/json" ^
  -d "{\"entity\": {\"location_id\": \"kanpur_industrial_zone\", \"properties\": {\"river_stability_score\": 60, \"terminal_proximity_score\": 65, \"logistics_access_score\": 80, \"water_quality_index\": 18, \"traffic_potential_score\": 75, \"in_wetland\": false, \"in_flood_zone\": false, \"env_clearance\": true, \"depth_score\": 55}}, \"model_type\": \"inland_port\"}"
```

**Expected response:**
```json
{
  "location_id": "kanpur_industrial_zone",
  "score": 0.0,
  "level": "REJECTED",
  "constraints": {
    "hard": ["extreme_pollution"],
    "soft": [],
    "overridden": []
  },
  "explanation": "HARD CONSTRAINTS TRIGGERED -> REJECTED | extreme_pollution: HARD REJECT: Extreme water pollution -- unusable for port/seaplane"
}
```

**What this shows:**
- Water quality index of 18 is below the threshold of 20
- Hard constraint fires -- score is forced to 0.0 regardless of other factors
- Even though logistics_access=80 is excellent, the location is still REJECTED
- This is non-negotiable in strict mode -- it cannot be overridden
- Kanpur's industrial pollution makes it unsuitable for any port infrastructure

---

## STEP 5 -- Show Soft Constraint and Penalty

**What this shows:** A location with poor logistics gets a score penalty
but is NOT rejected -- it can still be developed with investment.

**Command:**
```
curl -X POST http://localhost:5000/analyze-location ^
  -H "Content-Type: application/json" ^
  -d "{\"entity\": {\"location_id\": \"allahabad_confluence\", \"properties\": {\"river_stability_score\": 82, \"terminal_proximity_score\": 72, \"logistics_access_score\": 20, \"water_quality_index\": 65, \"traffic_potential_score\": 70, \"in_wetland\": false, \"in_flood_zone\": false, \"env_clearance\": true, \"depth_score\": 70}}, \"model_type\": \"inland_port\"}"
```

**Expected response:**
```json
{
  "location_id": "allahabad_confluence",
  "score": 47.4,
  "level": "LOW",
  "constraints": {
    "hard": [],
    "soft": ["logistics_absence"],
    "overridden": []
  },
  "explanation": "Model: Inland Port | Level: LOW | Score: 47.4 | Soft constraint penalties: -15 pts | logistics_absence"
}
```

**What this shows:**
- Logistics access score of 20 is below the threshold of 30
- Soft constraint fires: 15-point penalty applied
- Score drops from 62.4 (without penalty) to 47.4 (with penalty)
- Location is LOW, not REJECTED -- it can be developed if logistics are improved
- Clear policy signal: invest in logistics infrastructure to unlock this location

---

## STEP 6 -- GeoJSON Output (Map-Ready Payload)

**What this shows:** The engine produces GeoJSON that Nikhil can load
directly into any map renderer.

**Command (from src/):**
```
python geo_output_builder.py
```

**Output structure:**
```json
{
  "type": "FeatureCollection",
  "metadata": {
    "layer_type": "baseline",
    "model_type": "inland_port",
    "feature_count": 2
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [82.9739, 25.3176]
      },
      "properties": {
        "location_id": "varanasi_terminal",
        "score": 73.75,
        "level": "MEDIUM",
        "color": "#f39c12",
        "reasoning": "Level: MEDIUM | Score: 73.75"
      }
    }
  ]
}
```

**What this shows:**
- Real coordinates: [82.9739, 25.3176] is Varanasi on the Ganga
- Color #f39c12 (amber) assigned for MEDIUM level -- ready for map marker
- reasoning field populates the map tooltip directly
- Nikhil loads this JSON and renders the map -- no additional processing needed
- Full sample output is in sample_outputs/baseline_inland_port.geojson

---

## STEP 7 -- Determinism Proof (Run Live)

**What this shows:** The exact same request produces the exact same result
every single time -- no randomness, no ML variance.

**Command:**
```
python tests/test_determinism.py
```

**Expected output (key lines):**
```
  PASS  TEST 1 -- Single entity score: 10 runs identical
         -> all scores = 75.25 | unique values = {75.25}
  PASS  TEST 6 -- Batch score_all: 10 runs, all 3 entities identical
         -> unique batch outputs = 1

Results: 10/10 passed  ALL PASS
```

**What this shows:**
- The engine was run 10 times on identical input
- Every single run produced score=75.25 -- zero variance
- This is the foundation of government-grade trust in the system

---

## STEP 8 -- Contract Validation (Live)

**What this shows:** Every output is validated against a strict schema
before it can be used. Invalid outputs are rejected automatically.

**Command:**
```
python tests/test_contract_validation.py
```

**Expected output (key lines):**
```
  PASS  TEST F1 -- Real engine output (inland_port): passes contract
         -> is_valid=True score=73.75 level=MEDIUM errors=[]
  PASS  TEST F2 -- Real REJECTED engine output: passes contract
         -> is_valid=True level=REJECTED errors=[]

Results: 32/32 passed  ALL PASS
```

**What this shows:**
- Real engine output passes the contract validator
- The validator catches bad outputs before they reach the map
- 32 contract rules enforced on every result

---

## STEP 9 -- Full Test Suite (All 120 Tests)

**What this shows:** The complete engineering verification of the system.

**Commands (run from project root):**
```
python tests/test_scenarios_simulation.py
python tests/test_determinism.py
python tests/test_boundaries.py
python tests/test_failures.py
python tests/test_contract_validation.py
```

**Expected results:**
```
Results: 10/10 passed  ALL PASS
Results: 10/10 passed  ALL PASS
Results: 22/22 passed  ALL PASS
Results: 20/20 passed  ALL PASS
Results: 32/32 passed  ALL PASS
```

**For API tests (requires server running in Terminal 1):**
```
python tests/test_api.py
```
```
Results: 26/26 passed  ALL PASS
```

**Total: 120 tests, all pass.**

---

## Complete Demo Flow Summary

```
STEP 1   Start API server           -> Engine is live, 6 locations loaded
STEP 2   GET /results               -> All 6 locations scored instantly
STEP 3   POST /analyze-location     -> Patna = HIGH (75.25), full explanation
STEP 4   POST with Kanpur           -> REJECTED (extreme_pollution hard constraint)
STEP 5   POST with Allahabad        -> LOW (logistics_absence soft constraint, -15 pts)
STEP 6   python geo_output_builder  -> GeoJSON with real coordinates + colors
STEP 7   python test_determinism    -> 10 identical runs, zero variance
STEP 8   python test_contract       -> 32/32 contract rules enforced
STEP 9   All 120 tests              -> Full engineering verification
```

---

## Key Messages for Reviewers

1. This is not a mock -- every command runs against real Python code and
   real Ganga Basin datasets (IWAI, CPCB, CWC, Census)

2. The system is deterministic -- same input always produces same output.
   No ML, no randomness. Suitable for government audit.

3. Every score is explainable -- the formula, weights, and contributing
   signals are exposed in every API response.

4. Hard constraints are non-negotiable -- Kanpur's extreme pollution
   results in REJECT regardless of any other factor.

5. The output contract enforces data quality -- invalid outputs are
   caught and rejected before they reach the visualization layer.

6. The system is showcase-ready -- API live, tests passing, GeoJSON
   output ready for map rendering.
