# API Execution Proof
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the Flask API is live, contract-compliant, and handles
all valid and invalid requests correctly. Every output below was captured
from a running API server (localhost:5000) during live test execution.

---

## Server Startup

**Command run:**
```
cd src
python api.py
```

**Terminal output:**
```
NICAI API -- Starting on http://localhost:5000
```

Server confirmed running on http://localhost:5000 before tests were executed.

---

## API Test Suite: 26/26 Pass

**Command run:**
```
python tests/test_api.py
```

**Terminal output:**
```
NICAI -- API Test Suite
============================================================
Target: http://localhost:5000
  Server is running. Starting tests...

  PASS  TEST A1 -- GET /health: returns 200
         -> status=200
  PASS  TEST A2 -- GET /health: all required fields present
         -> missing=[] | status=healthy | ml_used=False
  PASS  TEST A3 -- GET /health: ml_used=False confirmed
         -> ml_used=False
  PASS  TEST A4 -- GET /health: determinism='guaranteed'
         -> determinism=guaranteed
  PASS  TEST B1 -- GET /locations: returns 200
         -> status=200
  PASS  TEST B2 -- GET /locations: has count + locations list
         -> count=6 locations_type=list
  PASS  TEST B3 -- GET /locations: count matches list length
         -> count=6 list_len=6
  PASS  TEST C1 -- GET /results: returns 200
         -> status=200
  PASS  TEST C2 -- GET /results: all contract fields present in every result
         -> checked 6 results | missing=[]
  PASS  TEST C3 -- GET /results: all scores are numeric
         -> non-numeric scores at: []
  PASS  TEST C4 -- GET /results: all levels are valid (HIGH/MEDIUM/LOW/REJECTED)
         -> invalid levels at: []
  PASS  TEST D1 -- POST /analyze-location: valid request -> 200
         -> status=200
  PASS  TEST D2 -- POST /analyze-location: all contract fields present
         -> missing=[] | score=73.75 level=MEDIUM
  PASS  TEST D3 -- POST /analyze-location: deterministic (2 identical requests)
         -> run1=73.75 run2=73.75
  PASS  TEST D4 -- POST /analyze-location: wetland entity -> REJECTED score=0
         -> level=REJECTED score=0.0
  PASS  TEST D5 -- POST /analyze-location: all 3 models work
         -> inland_port=200 | seaplane=200 | hub_spoke=200
  PASS  TEST E1 -- POST /analyze-location: missing 'entity' -> 400
         -> status=400 body='entity' field is required
  PASS  TEST E2 -- POST /analyze-location: unknown model_type -> 400
         -> status=400 error=Invalid model_type. Must be one of: ['inland_port', 'seaplane', 'hub_spoke']
  PASS  TEST E3 -- POST /analyze-location: empty JSON body -> 400
         -> status=400
  PASS  TEST E4 -- POST /analyze-location: non-JSON body -> 400
         -> status=400
  PASS  TEST E5 -- POST /analyze-location: missing model_type -> defaults to inland_port
         -> status=200 model_type=inland_port
  PASS  TEST F1 -- GET /results?model=seaplane: all results are seaplane
         -> count=6 all_seaplane=True
  PASS  TEST F2 -- GET /results?level=REJECTED: all results are REJECTED
         -> count=2 all_rejected=True
  PASS  TEST F3 -- GET /results?location_id=varanasi_terminal: filtered correctly
         -> count=1 all_match=True
  PASS  TEST G1 -- GET /nonexistent: returns 404
         -> status=404
  PASS  TEST G2 -- POST /health: returns 405 Method Not Allowed
         -> status=405
============================================================
Results: 26/26 passed  ALL PASS
============================================================
```

---

## What Each Block Proves

**Block A -- GET /health (4 tests)**
- API responds with HTTP 200
- All required fields present: status, entities_loaded, models_available, determinism, ml_used
- ml_used confirmed False -- no machine learning in the system
- determinism field confirmed "guaranteed"

**Block B -- GET /locations (3 tests)**
- Location list endpoint returns HTTP 200
- Response contains count and locations list
- count field exactly matches actual list length (6 locations)

**Block C -- GET /results (4 tests)**
- Results endpoint returns HTTP 200
- All 6 results contain every contract-required field
- All scores are numeric (no string or null values)
- All levels are valid values: HIGH, MEDIUM, LOW, or REJECTED

**Block D -- POST /analyze-location valid requests (5 tests)**
- Valid entity scores correctly, returns HTTP 200
- Response contains all contract fields: location_id, model_type, score, level,
  trace, constraints, explanation, scoring_model
- Two identical POST requests produce identical scores (run1=73.75, run2=73.75)
- Wetland entity correctly returns REJECTED with score=0.0
- All 3 model types (inland_port, seaplane, hub_spoke) return HTTP 200

**Block E -- POST /analyze-location bad requests (5 tests)**
- Missing entity field returns HTTP 400 with descriptive error message
- Unknown model_type returns HTTP 400
- Empty JSON body returns HTTP 400
- Non-JSON body returns HTTP 400
- Missing model_type defaults to inland_port without error

**Block F -- Query parameter filtering (3 tests)**
- ?model=seaplane returns only seaplane results (6/6 correct)
- ?level=REJECTED returns only REJECTED results (2/2 correct)
- ?location_id=varanasi_terminal returns only that location (1 result, exact match)

**Block G -- Error handlers (2 tests)**
- Unknown endpoint returns HTTP 404
- Wrong HTTP method returns HTTP 405

---

## Sample API Response

POST /analyze-location with varanasi_terminal entity:

```json
{
  "location_id": "varanasi_terminal",
  "model_type": "inland_port",
  "score": 73.75,
  "level": "MEDIUM",
  "constraints": {
    "hard": [],
    "soft": [],
    "overridden": []
  },
  "scoring_model": {
    "weights": {
      "river_stability": 0.25,
      "terminal_proximity": 0.2,
      "logistics_access": 0.2,
      "water_quality": 0.2,
      "traffic_potential": 0.15
    },
    "thresholds": { "HIGH": 75, "MEDIUM": 50, "LOW": 0 },
    "formula": "score = weighted sum of factor scores minus soft penalties"
  },
  "explanation": "Model: Inland Port | Level: MEDIUM | Score: 73.75"
}
```

---

## Summary

| Endpoint block | Tests | Result |
|---|---|---|
| GET /health | 4/4 | ALL PASS |
| GET /locations | 3/3 | ALL PASS |
| GET /results | 4/4 | ALL PASS |
| POST /analyze-location (valid) | 5/5 | ALL PASS |
| POST /analyze-location (bad requests) | 5/5 | ALL PASS |
| GET /results (query filters) | 3/3 | ALL PASS |
| Error handlers (404, 405) | 2/2 | ALL PASS |
| **Total** | **26/26** | **ALL PASS** |

**Conclusion:** The Flask API is live, deterministic, contract-compliant,
and handles all valid requests, bad requests, and error conditions correctly.
