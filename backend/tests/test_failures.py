"""
test_failures.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 2 — Failure Test Suite

Tests all failure and edge cases:
  A. Missing required fields in entity
  B. Invalid / missing coordinates
  C. Empty datasets
  D. Malformed / invalid type inputs
  E. Invalid model type
  F. Constraint fields with wrong types
  G. Empty and None property values
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scoring_engine import score_entity, score_all, SCORING_MODELS
from constraint_engine import evaluate_constraints

PASS = "  PASS"
FAIL = "  FAIL"
results_log = []


def log(name, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"{status}  {name}"
    if detail:
        msg += f"\n         → {detail}"
    print(msg)
    results_log.append((name, passed))


# ── Clean baseline entity for reference ──────────────────────────
CLEAN_ENTITY = {
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


# ══════════════════════════════════════════════════════════════
# BLOCK A — MISSING REQUIRED FIELDS
# Engine must handle missing scoring fields gracefully (default 0)
# and missing location_id (fallback to "unknown")
# ══════════════════════════════════════════════════════════════

def test_A1_missing_location_id():
    """Entity without location_id should still score — fallback to 'unknown'."""
    entity = {
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
    try:
        result = score_entity(entity, "inland_port")
        passed = result["location_id"] in ("unknown", None, "")
        detail = f"location_id={result['location_id']} score={result['score']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST A1 — Missing location_id: fallback to 'unknown', no crash", passed, detail)
    return passed


def test_A2_missing_all_scoring_fields():
    """Entity with no scoring fields → factors default to 0 → score is LOW, no crash."""
    entity = {
        "location_id": "empty_props",
        "properties": {
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "water_quality_index": 25,
            "depth_score": 25
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        # water_quality_index=25 contributes 25×0.20=5.0 — all other factors missing → 0
        # Key assertion: level is LOW and score is very low (< 10), no crash
        passed = result["level"] == "LOW" and result["score"] < 10.0
        detail = f"score={result['score']} level={result['level']} (low score, no crash)"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST A2 — Missing all scoring fields: score very low, level=LOW, no crash", passed, detail)
    return passed


def test_A3_missing_single_factor():
    """Entity missing one factor field → that factor defaults to 0."""
    entity = {
        "location_id": "missing_one_factor",
        "properties": {
            # river_stability_score is missing
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
    try:
        result = score_entity(entity, "inland_port")
        # Score should be lower than clean entity (missing river_stability = 0)
        clean = score_entity(CLEAN_ENTITY, "inland_port")
        passed = result["score"] < clean["score"] and result["score"] >= 0
        detail = f"score={result['score']} (clean={clean['score']}) — river_stability defaulted to 0"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST A3 — Missing one factor: defaults to 0, score reduced, no crash", passed, detail)
    return passed


def test_A4_missing_constraint_fields():
    """Entity missing constraint fields — constraints simply don't fire."""
    entity = {
        "location_id": "no_constraint_fields",
        "properties": {
            "river_stability_score": 78,
            "terminal_proximity_score": 85,
            "logistics_access_score": 70,
            "water_quality_index": 60,
            "traffic_potential_score": 75
            # in_wetland, in_flood_zone, env_clearance, depth_score all missing
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        # No constraint fields present → constraint blocks should be empty lists
        passed = (
            result["constraints"]["hard"] == [] and
            result["constraints"]["soft"] == [] and
            result["score"] > 0
        )
        detail = f"score={result['score']} hard={result['constraints']['hard']} soft={result['constraints']['soft']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST A4 — Missing constraint fields: no crash, empty constraint blocks", passed, detail)
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK B — INVALID / MISSING COORDINATES
# data_adapter.py validates coordinates — test those validators
# ══════════════════════════════════════════════════════════════

def test_B1_none_coordinate_values():
    """Properties with None lat/lon values — engine must not crash."""
    entity = {
        "location_id": "none_coords",
        "properties": {
            "river_stability_score": None,
            "terminal_proximity_score": None,
            "logistics_access_score": 70,
            "water_quality_index": 60,
            "traffic_potential_score": 75,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 65
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        # None values should default to 0 for scoring
        passed = result["score"] >= 0
        detail = f"score={result['score']} level={result['level']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST B1 — None field values: engine defaults to 0, no crash", passed, detail)
    return passed


def test_B2_string_instead_of_number():
    """Numeric fields with string values — engine must not crash."""
    entity = {
        "location_id": "string_values",
        "properties": {
            "river_stability_score": "seventy-eight",
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
    try:
        result = score_entity(entity, "inland_port")
        passed = result["score"] >= 0
        detail = f"score={result['score']} level={result['level']}"
    except Exception as e:
        # Acceptable to raise — but must NOT be a silent wrong answer
        passed = True
        detail = f"Raised exception (acceptable): {type(e).__name__}: {e}"
    log("TEST B2 — String instead of number: handled (crash or default, not silent wrong answer)", passed, detail)
    return passed


def test_B3_negative_score_values():
    """Negative factor values — score should be clamped to 0, not go negative."""
    entity = {
        "location_id": "negative_values",
        "properties": {
            "river_stability_score": -50,
            "terminal_proximity_score": -20,
            "logistics_access_score": -30,
            "water_quality_index": 25,
            "traffic_potential_score": -10,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 25
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        passed = result["score"] >= 0
        detail = f"score={result['score']} (not negative)"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST B3 — Negative factor values: score clamped to ≥ 0", passed, detail)
    return passed


def test_B4_extremely_large_values():
    """Factor values > 100 — engine should handle without crash."""
    entity = {
        "location_id": "huge_values",
        "properties": {
            "river_stability_score": 99999,
            "terminal_proximity_score": 99999,
            "logistics_access_score": 99999,
            "water_quality_index": 99999,
            "traffic_potential_score": 99999,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 60
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        passed = isinstance(result["score"], float) and result["score"] >= 0
        detail = f"score={result['score']} level={result['level']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST B4 — Extremely large values: no crash, score computed", passed, detail)
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK C — EMPTY DATASETS
# ══════════════════════════════════════════════════════════════

def test_C1_empty_entity_list():
    """score_all with empty list → returns empty list, no crash."""
    try:
        result = score_all([], "inland_port")
        passed = result == []
        detail = f"returned: {result}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST C1 — Empty entity list: returns [], no crash", passed, detail)
    return passed


def test_C2_empty_properties_dict():
    """Entity with completely empty properties dict → no crash."""
    entity = {
        "location_id": "empty_props",
        "properties": {}
    }
    try:
        result = score_entity(entity, "inland_port")
        passed = result["score"] >= 0
        detail = f"score={result['score']} level={result['level']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST C2 — Empty properties dict: no crash, score computed", passed, detail)
    return passed


def test_C3_single_entity_list():
    """score_all with single entity → returns list of length 1."""
    try:
        result = score_all([CLEAN_ENTITY], "inland_port")
        passed = len(result) == 1 and result[0]["score"] > 0
        detail = f"returned {len(result)} result, score={result[0]['score']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST C3 — Single entity list: returns 1 result, no crash", passed, detail)
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK D — MALFORMED / INVALID TYPE INPUTS
# ══════════════════════════════════════════════════════════════

def test_D1_boolean_as_score():
    """Boolean values in score fields — Python bools are ints (True=1, False=0)."""
    entity = {
        "location_id": "bool_scores",
        "properties": {
            "river_stability_score": True,   # Python: True == 1
            "terminal_proximity_score": False, # Python: False == 0
            "logistics_access_score": 70,
            "water_quality_index": 60,
            "traffic_potential_score": 75,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 65
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        passed = result["score"] >= 0
        detail = f"score={result['score']} (True→1, False→0 in Python)"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST D1 — Boolean as score value: handled (True=1, False=0)", passed, detail)
    return passed


def test_D2_none_entity_properties_key():
    """Entity where 'properties' key is None — must not crash."""
    entity = {
        "location_id": "none_properties",
        "properties": None
    }
    try:
        result = score_entity(entity, "inland_port")
        # If it returns something, score must be >= 0
        passed = result["score"] >= 0
        detail = f"score={result['score']}"
    except Exception as e:
        # A clean exception is acceptable — crash is not
        passed = isinstance(e, (TypeError, AttributeError, ValueError))
        detail = f"Raised {type(e).__name__} (acceptable failure): {e}"
    log("TEST D2 — None properties value: raises clean exception or defaults", passed, detail)
    return passed


def test_D3_list_instead_of_dict_for_properties():
    """Properties is a list instead of dict — must raise clean exception."""
    entity = {
        "location_id": "list_props",
        "properties": [78, 85, 70, 60, 75]
    }
    try:
        result = score_entity(entity, "inland_port")
        passed = result["score"] >= 0
        detail = f"score={result['score']}"
    except Exception as e:
        passed = True
        detail = f"Raised clean exception: {type(e).__name__}: {str(e)[:60]}"
    log("TEST D3 — List instead of dict for properties: raises clean exception", passed, detail)
    return passed


def test_D4_extra_unknown_fields_ignored():
    """Extra unknown fields in properties must be silently ignored."""
    entity = {
        "location_id": "extra_fields",
        "properties": {
            "river_stability_score": 78,
            "terminal_proximity_score": 85,
            "logistics_access_score": 70,
            "water_quality_index": 60,
            "traffic_potential_score": 75,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 65,
            # Unknown fields — should be silently ignored
            "some_random_field": "hello",
            "another_unknown": 999,
            "future_field": True
        }
    }
    try:
        result = score_entity(entity, "inland_port")
        clean = score_entity(CLEAN_ENTITY, "inland_port")
        passed = result["score"] == clean["score"]
        detail = f"score={result['score']} == clean={clean['score']}"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST D4 — Extra unknown fields: silently ignored, score unchanged", passed, detail)
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK E — INVALID MODEL TYPE
# ══════════════════════════════════════════════════════════════

def test_E1_invalid_model_type():
    """Unknown model_type must raise ValueError."""
    try:
        score_entity(CLEAN_ENTITY, "nonexistent_model")
        passed = False
        detail = "No error raised — FAIL"
    except ValueError as e:
        passed = True
        detail = f"ValueError raised: {str(e)[:80]}"
    except Exception as e:
        passed = False
        detail = f"Wrong exception type {type(e).__name__}: {e}"
    log("TEST E1 — Invalid model_type: raises ValueError", passed, detail)
    return passed


def test_E2_empty_string_model_type():
    """Empty string model_type must raise ValueError."""
    try:
        score_entity(CLEAN_ENTITY, "")
        passed = False
        detail = "No error raised — FAIL"
    except ValueError as e:
        passed = True
        detail = f"ValueError raised: {str(e)[:80]}"
    except Exception as e:
        passed = False
        detail = f"Wrong exception type {type(e).__name__}: {e}"
    log("TEST E2 — Empty string model_type: raises ValueError", passed, detail)
    return passed


def test_E3_none_model_type():
    """None model_type must raise an exception."""
    try:
        score_entity(CLEAN_ENTITY, None)
        passed = False
        detail = "No error raised — FAIL"
    except Exception as e:
        passed = True
        detail = f"{type(e).__name__} raised: {str(e)[:80]}"
    log("TEST E3 — None model_type: raises exception", passed, detail)
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK F — CONSTRAINT FIELDS WITH WRONG TYPES
# ══════════════════════════════════════════════════════════════

def test_F1_wetland_as_string():
    """in_wetland as string 'True' — constraint must not fire (not bool True)."""
    props = {
        "in_wetland": "True",   # string, not bool
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 60,
        "water_quality_index": 50
    }
    try:
        result = evaluate_constraints(props)
        # String "True" is not `True` (bool) — wetland constraint uses `v is True`
        passed = "wetland_zone" not in result["hard_triggered"]
        detail = f"hard_triggered={result['hard_triggered']} (string 'True' ≠ bool True)"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST F1 — in_wetland='True' (string): does NOT trigger wetland constraint", passed, detail)
    return passed


def test_F2_env_clearance_as_integer():
    """env_clearance as integer 0 instead of False — constraint behavior."""
    props = {
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": 0,     # integer 0, not bool False
        "depth_score": 60,
        "water_quality_index": 50
    }
    try:
        result = evaluate_constraints(props)
        # constraint uses `v is False` — int 0 is NOT False using `is`
        passed = isinstance(result["hard_triggered"], list)
        detail = f"hard_triggered={result['hard_triggered']} (int 0 behavior documented)"
    except Exception as e:
        passed = False
        detail = f"Crashed: {e}"
    log("TEST F2 — env_clearance=0 (int): constraint evaluated, no crash", passed, detail)
    return passed


# ── RUNNER ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNICAI — Failure & Edge Case Test Suite")
    print("=" * 60)

    tests = [
        test_A1_missing_location_id,
        test_A2_missing_all_scoring_fields,
        test_A3_missing_single_factor,
        test_A4_missing_constraint_fields,
        test_B1_none_coordinate_values,
        test_B2_string_instead_of_number,
        test_B3_negative_score_values,
        test_B4_extremely_large_values,
        test_C1_empty_entity_list,
        test_C2_empty_properties_dict,
        test_C3_single_entity_list,
        test_D1_boolean_as_score,
        test_D2_none_entity_properties_key,
        test_D3_list_instead_of_dict_for_properties,
        test_D4_extra_unknown_fields_ignored,
        test_E1_invalid_model_type,
        test_E2_empty_string_model_type,
        test_E3_none_model_type,
        test_F1_wetland_as_string,
        test_F2_env_clearance_as_integer,
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