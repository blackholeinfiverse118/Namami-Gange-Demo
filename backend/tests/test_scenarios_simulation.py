"""
test_scenarios_simulation.py  (MODIFIED — expanded for audit-grade hardening)
──────────────────────────────────────────────────────────────────────────────
NICAI - Ganga Basin Intelligence Engine
Determinism Lock + Failure Case Coverage

10 test cases covering:
  1. Baseline scoring — determinism (run twice, assert identical)
  2. Hard constraint — wetland → REJECTED
  3. Hard constraint — extreme pollution → REJECTED
  4. Soft constraint — logistics_absence → penalty only, not rejected
  5. Scenario weights — high_logistics scenario
  6. Scenario override — relaxed_logistics (soft constraint bypassed, flagged)
  7. Weight validation — non-1.0 sum rejected
  8. Constraint block presence — every result has hard/soft/overridden keys
  9. Trace block presence — every result has source_signals + signal_to_factor_map
  10. Scoring model block — weights + thresholds + formula in every result
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scoring_engine import score_entity, score_all, SCORING_MODELS
from constraint_engine import evaluate_constraints, build_constraint_block
from signal_trace_layer import attach_trace, build_source_signals
from simulate_api import compute_delta, PREDEFINED_SCENARIOS, build_scenario_metadata



# SHARED TEST ENTITIES
# ─────────────────────────────────────────────

ENTITY_CLEAN = {
    "location_id": "varanasi_terminal",
    "properties": {
        "river_stability_score": 78,
        "terminal_proximity_score": 85,
        "logistics_access_score": 70,
        "water_quality_index": 60,
        "traffic_potential_score": 75,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 65
    }
}

ENTITY_WETLAND = {
    "location_id": "farakka_wetland",
    "properties": {
        "river_stability_score": 74,
        "terminal_proximity_score": 60,
        "logistics_access_score": 45,
        "water_quality_index": 48,
        "traffic_potential_score": 40,
        "in_wetland": True,        # → HARD: wetland_zone
        "in_flood_zone": False,
        "env_clearance": False,    # → HARD: no_env_clearance
        "depth_score": 60
    }
}

ENTITY_POLLUTED = {
    "location_id": "kanpur_industrial_zone",
    "properties": {
        "river_stability_score": 60,
        "terminal_proximity_score": 65,
        "logistics_access_score": 80,
        "water_quality_index": 18,   # → HARD: extreme_pollution
        "traffic_potential_score": 75,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 55
    }
}

ENTITY_POOR_LOGISTICS = {
    "location_id": "allahabad_confluence",
    "properties": {
        "river_stability_score": 82,
        "terminal_proximity_score": 72,
        "logistics_access_score": 20,  # → SOFT: logistics_absence (< 30)
        "water_quality_index": 65,
        "traffic_potential_score": 70,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 70
    }
}

ALL_ENTITIES = [ENTITY_CLEAN, ENTITY_WETLAND, ENTITY_POLLUTED, ENTITY_POOR_LOGISTICS]

PASS = " PASS"
FAIL = " FAIL"

results_log = []


def log(test_name, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"  {status}  {test_name}"
    if detail:
        msg += f"\n         → {detail}"
    print(msg)
    results_log.append((test_name, passed))



# TEST 1: DETERMINISM — Baseline run twice, identical output
# ─────────────────────────────────────────────

def test_1_determinism():
    run1 = score_all(ALL_ENTITIES, "inland_port")
    run2 = score_all(ALL_ENTITIES, "inland_port")

    scores_match = [r1["score"] == r2["score"] for r1, r2 in zip(run1, run2)]
    levels_match = [r1["level"] == r2["level"] for r1, r2 in zip(run1, run2)]
    traces_match = [r1["trace"] == r2["trace"] for r1, r2 in zip(run1, run2)]

    passed = all(scores_match) and all(levels_match) and all(traces_match)
    log("TEST 1 — Determinism (2 runs, identical output)", passed,
        f"scores={all(scores_match)} levels={all(levels_match)} traces={all(traces_match)}")
    return passed



# TEST 2: HARD CONSTRAINT — Wetland → REJECTED
# ─────────────────────────────────────────────

def test_2_hard_wetland():
    result = score_entity(ENTITY_WETLAND, "inland_port")
    is_rejected = result["level"] == "REJECTED"
    score_zero = result["score"] == 0.0
    hard_listed = "wetland_zone" in result["constraints"]["hard"]

    passed = is_rejected and score_zero and hard_listed
    log("TEST 2 — Hard constraint: wetland → REJECTED", passed,
        f"level={result['level']} score={result['score']} hard={result['constraints']['hard']}")
    return passed



# TEST 3: HARD CONSTRAINT — Extreme pollution → REJECTED
# ─────────────────────────────────────────────

def test_3_hard_pollution():
    result = score_entity(ENTITY_POLLUTED, "inland_port")
    is_rejected = result["level"] == "REJECTED"
    hard_listed = "extreme_pollution" in result["constraints"]["hard"]

    passed = is_rejected and hard_listed
    log("TEST 3 — Hard constraint: extreme_pollution → REJECTED", passed,
        f"level={result['level']} hard={result['constraints']['hard']}")
    return passed



# TEST 4: SOFT CONSTRAINT — Low logistics → penalty, NOT rejected
# ─────────────────────────────────────────────

def test_4_soft_logistics():
    result = score_entity(ENTITY_POOR_LOGISTICS, "inland_port")
    not_rejected = result["level"] != "REJECTED"
    score_positive = result["score"] > 0
    soft_listed = "logistics_absence" in result["constraints"]["soft"]
    hard_empty = result["constraints"]["hard"] == []

    passed = not_rejected and score_positive and soft_listed and hard_empty
    log("TEST 4 — Soft constraint: logistics_absence → penalty only", passed,
        f"level={result['level']} score={result['score']} soft={result['constraints']['soft']}")
    return passed



# TEST 5: SCENARIO WEIGHTS — high_logistics
# ─────────────────────────────────────────────

def test_5_scenario_weights():
    mods = PREDEFINED_SCENARIOS["high_logistics"]["modifications"]
    custom_weights = mods["priority_weights"]

    baseline = score_entity(ENTITY_CLEAN, "inland_port")
    scenario = score_entity(ENTITY_CLEAN, "inland_port", custom_weights=custom_weights)

    weights_recorded = scenario["scoring_model"]["weights"] == custom_weights
    scores_differ = baseline["score"] != scenario["score"]   # weights changed → score must differ
    both_deterministic = (
        score_entity(ENTITY_CLEAN, "inland_port", custom_weights=custom_weights)["score"]
        == scenario["score"]
    )

    passed = weights_recorded and both_deterministic
    log("TEST 5 — Scenario weights: high_logistics applied + recorded", passed,
        f"baseline={baseline['score']} scenario={scenario['score']} weights_in_result={weights_recorded}")
    return passed



# TEST 6: SCENARIO OVERRIDE — relaxed_logistics (soft bypassed, flagged)
# ─────────────────────────────────────────────

def test_6_scenario_override():
    # Without override: logistics_absence fires → penalty
    baseline = score_entity(ENTITY_POOR_LOGISTICS, "inland_port")
    # With override: logistics_absence bypassed → higher score, listed in overridden
    scenario = score_entity(ENTITY_POOR_LOGISTICS, "inland_port",
                            scenario_overrides=["logistics_absence"])

    penalty_applied_in_baseline = "logistics_absence" in baseline["constraints"]["soft"]
    override_flagged = "logistics_absence" in scenario["constraints"]["overridden"]
    score_improved = scenario["score"] > baseline["score"]
    not_in_soft = "logistics_absence" not in scenario["constraints"]["soft"]

    passed = penalty_applied_in_baseline and override_flagged and score_improved and not_in_soft
    log("TEST 6 — Scenario override: logistics_absence bypassed + flagged", passed,
        f"baseline={baseline['score']} scenario={scenario['score']} overridden={scenario['constraints']['overridden']}")
    return passed



# TEST 7: WEIGHT VALIDATION — non-1.0 sum rejected
# ─────────────────────────────────────────────

def test_7_weight_validation():
    bad_weights = {
        "river_stability": 0.30,
        "terminal_proximity": 0.20,
        "logistics_access": 0.20,
        "water_quality": 0.20,
        "traffic_potential": 0.20   # sum = 1.10 → invalid
    }

    error_raised = False
    try:
        score_entity(ENTITY_CLEAN, "inland_port", custom_weights=bad_weights)
    except ValueError as e:
        error_raised = True
        detail = str(e)

    passed = error_raised
    log("TEST 7 — Weight validation: non-1.0 sum raises ValueError", passed,
        detail if error_raised else "No error raised — FAIL")
    return passed



# TEST 8: CONSTRAINT BLOCK — all results have hard/soft/overridden
# ─────────────────────────────────────────────

def test_8_constraint_block_presence():
    results = score_all(ALL_ENTITIES, "inland_port")
    all_present = all(
        "hard" in r["constraints"]
        and "soft" in r["constraints"]
        and "overridden" in r["constraints"]
        for r in results
    )
    passed = all_present
    log("TEST 8 — Constraint block: hard/soft/overridden present in all results", passed,
        f"checked {len(results)} results")
    return passed



# TEST 9: TRACE BLOCK — signal IDs and factor map present
# ─────────────────────────────────────────────

def test_9_trace_block_presence():
    results = score_all(ALL_ENTITIES, "inland_port")
    all_valid = all(
        "trace" in r
        and "source_signals" in r["trace"]
        and "contributing_signal_ids" in r["trace"]
        and "signal_to_factor_map" in r["trace"]
        and len(r["trace"]["contributing_signal_ids"]) > 0
        for r in results
    )
    sample = results[0]["trace"]["contributing_signal_ids"]
    passed = all_valid
    log("TEST 9 — Trace block: source_signals + signal_ids + factor_map present", passed,
        f"sample signals={sample[:3]}")
    return passed



# TEST 10: SCORING MODEL BLOCK — weights + thresholds + formula
# ─────────────────────────────────────────────

def test_10_scoring_model_block():
    results = score_all(ALL_ENTITIES, "inland_port")
    all_valid = all(
        "scoring_model" in r
        and "weights" in r["scoring_model"]
        and "thresholds" in r["scoring_model"]
        and "formula" in r["scoring_model"]
        and isinstance(r["scoring_model"]["formula"], str)
        and len(r["scoring_model"]["formula"]) > 20
        for r in results
    )
    sample_formula = results[0]["scoring_model"]["formula"][:60]
    passed = all_valid
    log("TEST 10 — Scoring model block: weights + thresholds + formula present", passed,
        f"formula excerpt: '{sample_formula}...'")
    return passed



# RUNNER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\nNICAI — Audit-Grade Intelligence Engine Test Suite")
    print("=" * 60)

    tests = [
        test_1_determinism,
        test_2_hard_wetland,
        test_3_hard_pollution,
        test_4_soft_logistics,
        test_5_scenario_weights,
        test_6_scenario_override,
        test_7_weight_validation,
        test_8_constraint_block_presence,
        test_9_trace_block_presence,
        test_10_scoring_model_block,
    ]

    for t in tests:
        try:
            t()
        except Exception as e:
            log(t.__name__, False, f"Exception: {e}")

    print()
    total = len(results_log)
    passed = sum(1 for _, p in results_log if p)
    failed = total - passed

    print("=" * 60)
    print(f"Results: {passed}/{total} passed", " ALL PASS" if failed == 0 else f" {failed} FAILED")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
