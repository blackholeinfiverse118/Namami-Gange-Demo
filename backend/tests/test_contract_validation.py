"""
test_contract_validation.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 3 — Contract Validation Test Suite

Tests the output_contract.py validator against:
  A. Valid outputs — engine results must pass
  B. Missing required fields — each caught individually
  C. Invalid field values — wrong types, out-of-range, bad enums
  D. Score/level consistency — REJECTED must have score=0
  E. Batch validation — valid + invalid mixed list
  F. Real engine output — score_entity output must pass contract
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from output_contract import (
    check_output,
    validate_output,
    validate_batch,
    ContractViolationError
)
from scoring_engine import score_entity, score_all

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


# ── Base valid result (engine output format) ──────────────────
VALID_RESULT = {
    "location_id": "varanasi_terminal",
    "model_type": "inland_port",
    "score": 73.75,
    "level": "MEDIUM",
    "constraints": {"hard": [], "soft": [], "overridden": []},
    "scoring_model": {
        "weights": {
            "river_stability": 0.25,
            "terminal_proximity": 0.20,
            "logistics_access": 0.20,
            "water_quality": 0.20,
            "traffic_potential": 0.15
        },
        "thresholds": {"HIGH": 75, "MEDIUM": 50, "LOW": 0},
        "formula": "score = weighted sum of factor scores minus soft penalties"
    },
    "explanation": "Model: Inland Port | Level: MEDIUM | Score: 73.75",
    "trace": {
        "source_signals": {"river": ["CWC_RIV_STAB_v1"]},
        "contributing_signal_ids": ["CWC_RIV_STAB_v1"],
        "signal_to_factor_map": {"CWC_RIV_STAB_v1": "river_stability"}
    }
}

REJECTED_RESULT = {
    "location_id": "kanpur_industrial_zone",
    "model_type": "inland_port",
    "score": 0.0,
    "level": "REJECTED",
    "constraints": {
        "hard": ["extreme_pollution"],
        "soft": [],
        "overridden": []
    },
    "scoring_model": {
        "weights": {"river_stability": 0.25},
        "thresholds": {"HIGH": 75, "MEDIUM": 50, "LOW": 0},
        "formula": "HARD constraints → REJECT"
    },
    "explanation": "HARD CONSTRAINTS TRIGGERED → REJECTED"
}


# ══════════════════════════════════════════════════════════════
# BLOCK A — VALID OUTPUTS PASS
# ══════════════════════════════════════════════════════════════

def test_A1_valid_result_passes():
    """A well-formed engine result passes the contract."""
    is_valid, errors = check_output(VALID_RESULT)
    passed = is_valid and errors == []
    log("TEST A1 — Valid result passes contract", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_A2_rejected_result_passes():
    """A REJECTED result with score=0 and hard constraint passes."""
    is_valid, errors = check_output(REJECTED_RESULT)
    passed = is_valid and errors == []
    log("TEST A2 — REJECTED result (score=0, hard constraint) passes contract", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_A3_validate_output_returns_result():
    """validate_output returns the result unchanged if valid."""
    returned = validate_output(VALID_RESULT)
    passed = returned is VALID_RESULT
    log("TEST A3 — validate_output returns result unchanged when valid", passed,
        f"returned_same_object={passed}")
    return passed


def test_A4_high_score_result_passes():
    """A HIGH level result with score >= 75 passes."""
    high_result = {
        **VALID_RESULT,
        "location_id": "patna_river_port",
        "score": 80.0,
        "level": "HIGH"
    }
    is_valid, errors = check_output(high_result)
    passed = is_valid
    log("TEST A4 — HIGH level result (score=80) passes contract", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_A5_low_score_result_passes():
    """A LOW level result passes."""
    low_result = {
        **VALID_RESULT,
        "location_id": "low_site",
        "score": 30.0,
        "level": "LOW"
    }
    is_valid, errors = check_output(low_result)
    passed = is_valid
    log("TEST A5 — LOW level result (score=30) passes contract", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK B — MISSING REQUIRED FIELDS CAUGHT
# ══════════════════════════════════════════════════════════════

def test_B1_missing_location_id():
    """Missing location_id is caught."""
    r = {**VALID_RESULT}
    del r["location_id"]
    is_valid, errors = check_output(r)
    caught = any("location_id" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B1 — Missing location_id: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B2_missing_model_type():
    """Missing model_type is caught."""
    r = {**VALID_RESULT}
    del r["model_type"]
    is_valid, errors = check_output(r)
    caught = any("model_type" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B2 — Missing model_type: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B3_missing_score():
    """Missing score is caught."""
    r = {**VALID_RESULT}
    del r["score"]
    is_valid, errors = check_output(r)
    caught = any("score" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B3 — Missing score: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B4_missing_level():
    """Missing level/suitability_level is caught."""
    r = {k: v for k, v in VALID_RESULT.items()
         if k not in ("level", "suitability_level")}
    is_valid, errors = check_output(r)
    caught = any("level" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B4 — Missing level: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B5_missing_constraints():
    """Missing constraints block is caught."""
    r = {**VALID_RESULT}
    del r["constraints"]
    is_valid, errors = check_output(r)
    caught = any("constraints" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B5 — Missing constraints: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B6_missing_explanation():
    """Missing explanation/reasoning is caught."""
    r = {k: v for k, v in VALID_RESULT.items()
         if k not in ("explanation", "reasoning")}
    is_valid, errors = check_output(r)
    caught = any("reasoning" in e or "explanation" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B6 — Missing explanation/reasoning: caught by contract", passed,
        f"errors={errors}")
    return passed


def test_B7_missing_contributing_factors_and_scoring_model():
    """Missing both contributing_factors and scoring_model.weights is caught."""
    r = {k: v for k, v in VALID_RESULT.items()
         if k not in ("contributing_factors", "scoring_model")}
    is_valid, errors = check_output(r)
    caught = any("contributing_factors" in e for e in errors)
    passed = not is_valid and caught
    log("TEST B7 — Missing contributing_factors + scoring_model: caught", passed,
        f"errors={errors}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK C — INVALID FIELD VALUES CAUGHT
# ══════════════════════════════════════════════════════════════

def test_C1_empty_location_id():
    """Empty string location_id is rejected."""
    r = {**VALID_RESULT, "location_id": ""}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("location_id" in e for e in errors)
    log("TEST C1 — Empty location_id string: rejected", passed,
        f"errors={errors}")
    return passed


def test_C2_invalid_model_type():
    """Unknown model_type is rejected."""
    r = {**VALID_RESULT, "model_type": "unknown_model"}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("model_type" in e for e in errors)
    log("TEST C2 — Invalid model_type: rejected", passed,
        f"errors={errors}")
    return passed


def test_C3_score_above_100():
    """Score above 100 is rejected."""
    r = {**VALID_RESULT, "score": 101.0}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("score" in e for e in errors)
    log("TEST C3 — Score=101.0 (above 100): rejected", passed,
        f"errors={errors}")
    return passed


def test_C4_score_below_0():
    """Negative score is rejected."""
    r = {**VALID_RESULT, "score": -5.0}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("score" in e for e in errors)
    log("TEST C4 — Score=-5.0 (below 0): rejected", passed,
        f"errors={errors}")
    return passed


def test_C5_invalid_level():
    """Invalid level string is rejected."""
    r = {**VALID_RESULT, "level": "EXCELLENT"}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("level" in e for e in errors)
    log("TEST C5 — Invalid level='EXCELLENT': rejected", passed,
        f"errors={errors}")
    return passed


def test_C6_constraints_missing_subfields():
    """Constraints dict missing soft/overridden subfields is rejected."""
    r = {**VALID_RESULT, "constraints": {"hard": []}}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("constraints.soft" in e for e in errors)
    log("TEST C6 — Constraints missing soft+overridden: rejected", passed,
        f"errors={errors}")
    return passed


def test_C7_score_is_string():
    """Score as string is rejected."""
    r = {**VALID_RESULT, "score": "seventy-three"}
    is_valid, errors = check_output(r)
    passed = not is_valid and any("score" in e for e in errors)
    log("TEST C7 — Score as string: rejected", passed,
        f"errors={errors}")
    return passed


def test_C8_non_dict_result():
    """Passing a non-dict to check_output is rejected cleanly."""
    is_valid, errors = check_output("not a dict")
    passed = not is_valid and len(errors) > 0
    log("TEST C8 — Non-dict result: rejected cleanly", passed,
        f"errors={errors}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK D — SCORE / LEVEL CONSISTENCY
# ══════════════════════════════════════════════════════════════

def test_D1_rejected_with_nonzero_score():
    """REJECTED level with score > 0 is caught as inconsistency."""
    r = {
        **REJECTED_RESULT,
        "score": 45.0,   # REJECTED but score is not 0 — inconsistent
        "level": "REJECTED"
    }
    is_valid, errors = check_output(r)
    passed = not is_valid and any("inconsistency" in e for e in errors)
    log("TEST D1 — REJECTED + score=45.0: inconsistency caught", passed,
        f"errors={errors}")
    return passed


def test_D2_rejected_zero_score_no_hard_constraint():
    """REJECTED + score=0 but empty hard constraints — inconsistency caught."""
    r = {
        **VALID_RESULT,
        "score": 0.0,
        "level": "REJECTED",
        "constraints": {"hard": [], "soft": [], "overridden": []}
    }
    is_valid, errors = check_output(r)
    passed = not is_valid and any("inconsistency" in e for e in errors)
    log("TEST D2 — REJECTED + score=0 + no hard constraints: inconsistency caught", passed,
        f"errors={errors}")
    return passed


def test_D3_valid_rejected_with_hard_constraint():
    """REJECTED + score=0 + hard constraint listed — valid, no inconsistency."""
    is_valid, errors = check_output(REJECTED_RESULT)
    passed = is_valid and errors == []
    log("TEST D3 — REJECTED + score=0 + hard constraint listed: valid", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK E — BATCH VALIDATION
# ══════════════════════════════════════════════════════════════

def test_E1_batch_all_valid():
    """validate_batch with all valid results → all in valid list."""
    results = [VALID_RESULT, REJECTED_RESULT]
    valid, rejected = validate_batch(results)
    passed = len(valid) == 2 and len(rejected) == 0
    log("TEST E1 — Batch: 2 valid results → all in valid list", passed,
        f"valid={len(valid)} rejected={len(rejected)}")
    return passed


def test_E2_batch_mixed():
    """validate_batch with 1 valid + 1 invalid → correctly separated."""
    bad_result = {**VALID_RESULT, "score": 999.0, "model_type": "bad"}
    results = [VALID_RESULT, bad_result]
    valid, rejected = validate_batch(results)
    passed = len(valid) == 1 and len(rejected) == 1
    log("TEST E2 — Batch: 1 valid + 1 invalid → correctly separated", passed,
        f"valid={len(valid)} rejected={len(rejected)}")
    return passed


def test_E3_batch_rejected_has_error_key():
    """Rejected results in validate_batch have 'contract_errors' key."""
    bad_result = {**VALID_RESULT, "score": 999.0}
    _, rejected = validate_batch([bad_result])
    passed = len(rejected) == 1 and "contract_errors" in rejected[0]
    log("TEST E3 — Batch rejected results have contract_errors key", passed,
        f"contract_errors={rejected[0].get('contract_errors') if rejected else 'N/A'}")
    return passed


def test_E4_batch_empty_list():
    """validate_batch with empty list → ([], [])."""
    valid, rejected = validate_batch([])
    passed = valid == [] and rejected == []
    log("TEST E4 — Batch empty list: returns ([], [])", passed,
        f"valid={valid} rejected={rejected}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK F — REAL ENGINE OUTPUT PASSES CONTRACT
# ══════════════════════════════════════════════════════════════

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

ENTITY_REJECTED = {
    "location_id": "kanpur_industrial_zone",
    "properties": {
        "river_stability_score": 60,
        "terminal_proximity_score": 65,
        "logistics_access_score": 80,
        "water_quality_index": 18,
        "traffic_potential_score": 75,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 55
    }
}


def test_F1_real_engine_output_passes():
    """Real score_entity output passes the contract validator."""
    result = score_entity(ENTITY_CLEAN, "inland_port")
    is_valid, errors = check_output(result)
    passed = is_valid and errors == []
    log("TEST F1 — Real engine output (inland_port): passes contract", passed,
        f"is_valid={is_valid} score={result['score']} level={result['level']} errors={errors}")
    return passed


def test_F2_real_rejected_output_passes():
    """Real REJECTED engine output passes the contract validator."""
    result = score_entity(ENTITY_REJECTED, "inland_port")
    is_valid, errors = check_output(result)
    passed = is_valid and errors == []
    log("TEST F2 — Real REJECTED engine output: passes contract", passed,
        f"is_valid={is_valid} level={result['level']} errors={errors}")
    return passed


def test_F3_all_models_pass_contract():
    """All 3 model types produce contract-valid output."""
    entities = {
        "inland_port": ENTITY_CLEAN,
        "seaplane": {
            "location_id": "varanasi_seaplane",
            "properties": {
                "turbulence_index": 0.25,
                "water_quality_index": 70,
                "traffic_potential_score": 65,
                "urban_proximity_score": 72,
                "env_clearance": True,
                "in_wetland": False,
                "in_flood_zone": False
            }
        },
        "hub_spoke": {
            "location_id": "hajipur_hub",
            "properties": {
                "multi_node_proximity": 70,
                "logistics_park_quality": 65,
                "terminal_density_score": 60,
                "connectivity_score": 68,
                "urban_market_access": 72,
                "in_wetland": False,
                "in_flood_zone": False,
                "env_clearance": True
            }
        }
    }
    all_passed = True
    details = []
    for model, entity in entities.items():
        result = score_entity(entity, model)
        is_valid, errors = check_output(result)
        details.append(f"{model}={is_valid}")
        if not is_valid:
            all_passed = False
            details.append(f"  errors={errors}")
    passed = all_passed
    log("TEST F3 — All 3 models produce contract-valid output", passed,
        " | ".join(details))
    return passed


def test_F4_batch_real_engine_output():
    """score_all output batch-validated — all pass, none rejected."""
    entities = [ENTITY_CLEAN, ENTITY_REJECTED]
    results = score_all(entities, "inland_port")
    valid, rejected = validate_batch(results)
    passed = len(valid) == 2 and len(rejected) == 0
    log("TEST F4 — Batch real engine output: all pass contract", passed,
        f"valid={len(valid)} rejected={len(rejected)}")
    return passed


def test_F5_contract_violation_error_raised():
    """validate_output raises ContractViolationError on invalid result."""
    bad = {**VALID_RESULT, "score": 999.0, "model_type": "bad_model"}
    try:
        validate_output(bad)
        passed = False
        detail = "No error raised — FAIL"
    except ContractViolationError as e:
        passed = len(e.errors) >= 2
        detail = f"ContractViolationError with {len(e.errors)} errors "
    except Exception as e:
        passed = False
        detail = f"Wrong exception type: {type(e).__name__}"
    log("TEST F5 — validate_output raises ContractViolationError on bad result", passed, detail)
    return passed


# ── RUNNER ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNICAI — Contract Validation Test Suite")
    print("=" * 60)

    tests = [
        test_A1_valid_result_passes,
        test_A2_rejected_result_passes,
        test_A3_validate_output_returns_result,
        test_A4_high_score_result_passes,
        test_A5_low_score_result_passes,
        test_B1_missing_location_id,
        test_B2_missing_model_type,
        test_B3_missing_score,
        test_B4_missing_level,
        test_B5_missing_constraints,
        test_B6_missing_explanation,
        test_B7_missing_contributing_factors_and_scoring_model,
        test_C1_empty_location_id,
        test_C2_invalid_model_type,
        test_C3_score_above_100,
        test_C4_score_below_0,
        test_C5_invalid_level,
        test_C6_constraints_missing_subfields,
        test_C7_score_is_string,
        test_C8_non_dict_result,
        test_D1_rejected_with_nonzero_score,
        test_D2_rejected_zero_score_no_hard_constraint,
        test_D3_valid_rejected_with_hard_constraint,
        test_E1_batch_all_valid,
        test_E2_batch_mixed,
        test_E3_batch_rejected_has_error_key,
        test_E4_batch_empty_list,
        test_F1_real_engine_output_passes,
        test_F2_real_rejected_output_passes,
        test_F3_all_models_pass_contract,
        test_F4_batch_real_engine_output,
        test_F5_contract_violation_error_raised,
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