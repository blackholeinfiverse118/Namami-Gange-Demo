# Runtime Execution Proof
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the intelligence engine executes end-to-end in a real
runtime environment -- not a mock, not a simulation, not documentation only.
Every output below was produced by running actual Python files against real
logic and captured directly from the terminal.

---

## PROOF 1 -- Scoring Engine Self-Test

**Command run:**
```
cd src
python scoring_engine.py
```

**Output -- Location 1: Varanasi Terminal (MEDIUM)**
```json
{
  "location_id": "varanasi_terminal",
  "model_type": "inland_port",
  "score": 73.75,
  "level": "MEDIUM",
  "factor_scores": {
    "river_stability": 78.0,
    "terminal_proximity": 85.0,
    "logistics_access": 70.0,
    "water_quality": 60.0,
    "traffic_potential": 75.0
  },
  "constraints": { "hard": [], "soft": [], "overridden": [] },
  "scoring_model": {
    "weights": {
      "river_stability": 0.25,
      "terminal_proximity": 0.2,
      "logistics_access": 0.2,
      "water_quality": 0.2,
      "traffic_potential": 0.15
    },
    "thresholds": { "HIGH": 75, "MEDIUM": 50, "LOW": 0 },
    "formula": "score = (river_stability_score x 0.25) + (terminal_proximity_score x 0.20) + (logistics_access_score x 0.20) + (water_quality_index x 0.20) + (traffic_potential_score x 0.15); then subtract soft constraint penalties; clamped to [0, 100]; HARD constraints -> REJECT (score = 0, level = REJECTED)"
  },
  "explanation": "Model: Inland Port | Level: MEDIUM | Score: 73.75 | Factor contributions: | river_stability: 78.0 x 0.25 = 19.5 | terminal_proximity: 85.0 x 0.2 = 17.0 | logistics_access: 70.0 x 0.2 = 14.0 | water_quality: 60.0 x 0.2 = 12.0 | traffic_potential: 75.0 x 0.15 = 11.25",
  "trace": {
    "source_signals": {
      "river": ["CWC_RIV_STAB_v1", "CPCB_WQI_v1"],
      "logistics": ["IWAI_TERM_v1", "IWAI_LOG_v1", "IWAI_TRAF_v1"],
      "environmental": ["ENV_WETLAND_v1", "ENV_FLOOD_v1", "ENV_CLEAR_v1"],
      "water_quality": ["CPCB_POLL_v1"]
    },
    "contributing_signal_ids": [
      "CPCB_POLL_v1", "CPCB_WQI_v1", "CWC_RIV_STAB_v1",
      "ENV_CLEAR_v1", "ENV_FLOOD_v1", "ENV_WETLAND_v1",
      "IWAI_LOG_v1", "IWAI_TERM_v1", "IWAI_TRAF_v1"
    ],
    "signal_to_factor_map": {
      "CWC_RIV_STAB_v1": "river_stability",
      "IWAI_TERM_v1": "terminal_proximity",
      "IWAI_LOG_v1": "logistics_access",
      "CPCB_WQI_v1": "water_quality",
      "IWAI_TRAF_v1": "traffic_potential",
      "ENV_WETLAND_v1": "wetland_constraint",
      "ENV_FLOOD_v1": "flood_constraint",
      "ENV_CLEAR_v1": "env_clearance",
      "CPCB_POLL_v1": "pollution_level"
    }
  }
}
```

**Output -- Location 2: Patna Wetland Site (REJECTED)**
```json
{
  "location_id": "patna_wetland_site",
  "model_type": "inland_port",
  "score": 0.0,
  "level": "REJECTED",
  "constraints": {
    "hard": ["wetland_zone"],
    "soft": [],
    "overridden": []
  },
  "explanation": "HARD CONSTRAINTS TRIGGERED -> REJECTED | wetland_zone: HARD REJECT: Protected wetland -- infrastructure prohibited"
}
```

**What this proves:**
- Engine runs from command line with zero errors
- Deterministic score computed: 73.75 for Varanasi Terminal
- Hard constraint correctly triggered: wetland_zone -> REJECTED, score forced to 0.0
- Full trace block attached: 9 contributing signal IDs, all traceable to source datasets
- Formula exposed in every result -- fully auditable

---

## PROOF 2 -- Full Test Suite: 10/10 Pass

**Command run:**
```
python tests/test_scenarios_simulation.py
```

**Terminal output:**
```
NICAI -- Audit-Grade Intelligence Engine Test Suite
============================================================
   PASS  TEST 1 -- Determinism (2 runs, identical output)
         -> scores=True levels=True traces=True
   PASS  TEST 2 -- Hard constraint: wetland -> REJECTED
         -> level=REJECTED score=0.0 hard=['wetland_zone', 'no_env_clearance']
   PASS  TEST 3 -- Hard constraint: extreme_pollution -> REJECTED
         -> level=REJECTED hard=['extreme_pollution']
   PASS  TEST 4 -- Soft constraint: logistics_absence -> penalty only
         -> level=LOW score=47.4 soft=['logistics_absence']
   PASS  TEST 5 -- Scenario weights: high_logistics applied + recorded
         -> baseline=73.75 scenario=71.55 weights_in_result=True
   PASS  TEST 6 -- Scenario override: logistics_absence bypassed + flagged
         -> baseline=47.4 scenario=62.4 overridden=['logistics_absence']
   PASS  TEST 7 -- Weight validation: non-1.0 sum raises ValueError
         -> Weights must sum to 1.0. Got: 1.1
   PASS  TEST 8 -- Constraint block: hard/soft/overridden present in all results
         -> checked 4 results
   PASS  TEST 9 -- Trace block: source_signals + signal_ids + factor_map present
         -> sample signals=['CPCB_WQI_v1', 'CWC_DEPTH_v1', 'CWC_RIV_STAB_v1']
   PASS  TEST 10 -- Scoring model block: weights + thresholds + formula present
         -> formula excerpt: 'score = (river_stability_score x 0.25) + (terminal_proximity...'
============================================================
Results: 10/10 passed  ALL PASS
============================================================
```

---

## PROOF 3 -- Determinism: 10-Run Identical Output

**Command run:**
```
python tests/test_determinism.py
```

**Terminal output:**
```
NICAI -- Determinism Test Suite (10-Run Proof)
============================================================
Each test runs the engine 10 times on identical input.
All 10 outputs must be identical to pass.

  PASS  TEST 1 -- Single entity score: 10 runs identical
         -> all scores = 75.25 | unique values = {75.25}
  PASS  TEST 2 -- Single entity level: 10 runs identical
         -> all levels = HIGH | unique values = {'HIGH'}
  PASS  TEST 3 -- Single entity explanation: 10 runs identical
         -> unique explanation count = 1
  PASS  TEST 4 -- Single entity trace: 10 runs identical
         -> unique trace count = 1
  PASS  TEST 5 -- REJECTED entity: 10 runs always score=0.0 level=REJECTED
         -> scores unique={0.0} levels unique={'REJECTED'}
  PASS  TEST 6 -- Batch score_all: 10 runs, all 3 entities identical
         -> unique batch outputs = 1
  PASS  TEST 7 -- Seaplane model: 10 runs identical
         -> score = 74.15 | unique = {74.15}
  PASS  TEST 8 -- Hub-Spoke model: 10 runs identical
         -> score = 66.65 | unique = {66.65}
  PASS  TEST 9 -- Custom weights scenario: 10 runs identical
         -> score = 63.45 | unique = {63.45}
  PASS  TEST 10 -- Constraint override scenario: 10 runs identical
         -> score = 65.35 | unique = {65.35}
============================================================
Results: 10/10 passed  ALL PASS
============================================================
```

**What this proves:**
- Same input produces identical score across 10 independent runs: no randomness
- All 3 models (inland_port, seaplane, hub_spoke) are deterministic
- Custom weight scenarios are deterministic
- Constraint override scenarios are deterministic
- REJECTED entities always produce score=0.0

---

## Summary

| Proof | Command | Result |
|---|---|---|
| Engine self-test | python src/scoring_engine.py | 2 locations scored, 1 REJECTED |
| Full test suite | python tests/test_scenarios_simulation.py | 10/10 ALL PASS |
| Determinism proof | python tests/test_determinism.py | 10/10 ALL PASS, 10 runs each |

**Conclusion:** The engine is operational, deterministic, and runtime-verified.
No mocks. No stubs. Real execution on real logic.
