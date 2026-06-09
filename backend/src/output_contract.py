"""
output_contract.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 3 — Strict Output Contract Layer

Validates every scored result against the mandatory output schema:
{
    location_id        → str, non-empty
    latitude           → float, valid India range OR None (API mode)
    longitude          → float, valid India range OR None (API mode)
    model_type         → str, one of 3 valid models
    score              → float, 0.0-100.0
    suitability_level  → str, HIGH/MEDIUM/LOW/REJECTED  (also accepts "level" key)
    contributing_factors → dict OR present in scoring_model
    constraints        → dict with hard/soft/overridden keys
    reasoning          → str, non-empty  (also accepts "explanation" key)
}

Usage:
    from output_contract import validate_output, ContractViolationError
    validate_output(result)          # raises ContractViolationError if invalid
    is_valid, errors = check_output(result)  # returns (bool, list of error strings)
"""

from typing import Any, Dict, List, Tuple

# ── Valid values ──────────────────────────────────────────────
VALID_MODEL_TYPES = {"inland_port", "seaplane", "hub_spoke"}
VALID_LEVELS = {"HIGH", "MEDIUM", "LOW", "REJECTED"}

# India bounding box (loose — covers all of Ganga Basin)
LAT_MIN, LAT_MAX = 6.0, 37.0
LON_MIN, LON_MAX = 68.0, 97.5


class ContractViolationError(Exception):
    """Raised when a scored result fails contract validation."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(
            f"Output contract violation — {len(errors)} error(s):\n" +
            "\n".join(f"  [{i+1}] {e}" for i, e in enumerate(errors))
        )


# ── Individual field validators ───────────────────────────────

def _check_location_id(result: Dict, errors: List[str]):
    val = result.get("location_id")
    if val is None:
        errors.append("location_id: missing (required)")
    elif not isinstance(val, str):
        errors.append(f"location_id: must be str, got {type(val).__name__}")
    elif val.strip() == "":
        errors.append("location_id: must not be empty string")


def _check_coordinates(result: Dict, errors: List[str]):
    """
    Coordinates are required for GeoJSON output.
    In API mode (POST /analyze-location), lat/lon may be None — this is allowed.
    They are validated only when present.
    """
    lat = result.get("latitude")
    lon = result.get("longitude")

    if lat is not None:
        if not isinstance(lat, (int, float)):
            errors.append(f"latitude: must be numeric, got {type(lat).__name__}")
        elif not (LAT_MIN <= float(lat) <= LAT_MAX):
            errors.append(
                f"latitude: {lat} out of India bounds [{LAT_MIN}, {LAT_MAX}]"
            )

    if lon is not None:
        if not isinstance(lon, (int, float)):
            errors.append(f"longitude: must be numeric, got {type(lon).__name__}")
        elif not (LON_MIN <= float(lon) <= LON_MAX):
            errors.append(
                f"longitude: {lon} out of India bounds [{LON_MIN}, {LON_MAX}]"
            )


def _check_model_type(result: Dict, errors: List[str]):
    val = result.get("model_type")
    if val is None:
        errors.append("model_type: missing (required)")
    elif val not in VALID_MODEL_TYPES:
        errors.append(
            f"model_type: '{val}' invalid. Must be one of {sorted(VALID_MODEL_TYPES)}"
        )


def _check_score(result: Dict, errors: List[str]):
    val = result.get("score")
    if val is None:
        errors.append("score: missing (required)")
    elif isinstance(val, bool) or not isinstance(val, (int, float)):
        errors.append(f"score: must be numeric, got {type(val).__name__} (value={val!r})")
    elif not (0.0 <= val <= 100.0):
        errors.append(f"score: {val} out of valid range [0.0, 100.0]")


def _check_level(result: Dict, errors: List[str]) -> str:
    """
    Accepts either 'suitability_level' (task spec) or 'level' (engine output).
    Returns the key that was found, or None.
    """
    val = result.get("suitability_level") or result.get("level")
    key = "suitability_level" if "suitability_level" in result else "level"

    if val is None:
        errors.append("suitability_level / level: missing (required)")
        return None
    elif val not in VALID_LEVELS:
        errors.append(
            f"{key}: '{val}' invalid. Must be one of {sorted(VALID_LEVELS)}"
        )
    return key


def _check_score_level_consistency(result: Dict, errors: List[str]):
    score = result.get("score")
    level = result.get("suitability_level") or result.get("level")

    if score is None or level is None:
        return
    # Only run consistency check if score is actually numeric
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return

    if level == "REJECTED" and float(score) != 0.0:
        errors.append(
            f"score/level inconsistency: level=REJECTED but score={score} (must be 0.0)"
        )

    constraints = result.get("constraints", {})
    hard = constraints.get("hard", [])
    if float(score) == 0.0 and level == "REJECTED" and len(hard) == 0:
        errors.append(
            "score/level inconsistency: REJECTED with score=0.0 but no hard constraints listed"
        )


def _check_contributing_factors(result: Dict, errors: List[str]):
    """
    Accepts either:
    - 'contributing_factors' key (task spec)
    - 'scoring_model.weights' (engine output — equivalent information)
    """
    cf = result.get("contributing_factors")
    sm = result.get("scoring_model", {})

    if cf is not None:
        if not isinstance(cf, dict):
            errors.append(
                f"contributing_factors: must be dict, got {type(cf).__name__}"
            )
    elif sm and isinstance(sm.get("weights"), dict) and len(sm["weights"]) > 0:
        pass  # scoring_model.weights serves as contributing_factors — accepted
    else:
        errors.append(
            "contributing_factors: missing. Must provide either "
            "'contributing_factors' dict or 'scoring_model.weights' dict"
        )


def _check_constraints(result: Dict, errors: List[str]):
    val = result.get("constraints")
    if val is None:
        errors.append("constraints: missing (required)")
        return
    if not isinstance(val, dict):
        errors.append(f"constraints: must be dict, got {type(val).__name__}")
        return
    for key in ("hard", "soft", "overridden"):
        if key not in val:
            errors.append(f"constraints.{key}: missing (required sub-field)")
        elif not isinstance(val[key], list):
            errors.append(
                f"constraints.{key}: must be list, got {type(val[key]).__name__}"
            )


def _check_reasoning(result: Dict, errors: List[str]):
    """
    Accepts either 'reasoning' (task spec) or 'explanation' (engine output).
    """
    val = result.get("reasoning") or result.get("explanation")
    if val is None:
        errors.append("reasoning / explanation: missing (required)")
    elif not isinstance(val, str):
        errors.append(
            f"reasoning / explanation: must be str, got {type(val).__name__}"
        )
    elif val.strip() == "":
        errors.append("reasoning / explanation: must not be empty string")


# ── Main validators ───────────────────────────────────────────

def check_output(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a scored result against the output contract.

    Returns:
        (is_valid: bool, errors: List[str])

    Does NOT raise — use validate_output() if you want exceptions.
    """
    if not isinstance(result, dict):
        return False, [f"Result must be a dict, got {type(result).__name__}"]

    errors: List[str] = []

    _check_location_id(result, errors)
    _check_coordinates(result, errors)
    _check_model_type(result, errors)
    _check_score(result, errors)
    _check_level(result, errors)
    _check_score_level_consistency(result, errors)
    _check_contributing_factors(result, errors)
    _check_constraints(result, errors)
    _check_reasoning(result, errors)

    return len(errors) == 0, errors


def validate_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a scored result. Raises ContractViolationError if invalid.
    Returns the result unchanged if valid (for chaining).

    Usage:
        result = validate_output(score_entity(entity, "inland_port"))
    """
    is_valid, errors = check_output(result)
    if not is_valid:
        raise ContractViolationError(errors)
    return result


def validate_batch(results: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    """
    Validates a list of results.

    Returns:
        (valid_results, rejected_results)
        rejected_results each have an added 'contract_errors' key.
    """
    valid = []
    rejected = []
    for r in results:
        is_valid, errors = check_output(r)
        if is_valid:
            valid.append(r)
        else:
            rejected.append({**r, "contract_errors": errors})
    return valid, rejected


# ── QUICK SELF-TEST ───────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("output_contract.py — Self-Test")
    print("=" * 50)

    # Valid result (engine output format)
    valid_result = {
        "location_id": "varanasi_terminal",
        "model_type": "inland_port",
        "score": 73.75,
        "level": "MEDIUM",
        "constraints": {"hard": [], "soft": [], "overridden": []},
        "scoring_model": {
            "weights": {"river_stability": 0.25, "terminal_proximity": 0.20},
            "thresholds": {"HIGH": 75, "MEDIUM": 50},
            "formula": "score = weighted sum"
        },
        "explanation": "Model: Inland Port | Level: MEDIUM | Score: 73.75",
        "trace": {"source_signals": {}, "contributing_signal_ids": []}
    }

    is_valid, errors = check_output(valid_result)
    print(f"Valid result: is_valid={is_valid} errors={errors}")

    # Invalid result — missing fields
    invalid_result = {
        "location_id": "",           # empty string — invalid
        "model_type": "bad_model",   # unknown model
        "score": 150.0,              # out of range
        "level": "SUPER_HIGH",       # invalid level
        "constraints": {"hard": []}  # missing soft + overridden
    }

    is_valid2, errors2 = check_output(invalid_result)
    print(f"\nInvalid result: is_valid={is_valid2}")
    print("Errors:")
    for e in errors2:
        print(f"  - {e}")

    # ContractViolationError test
    print("\nTesting ContractViolationError raise:")
    try:
        validate_output(invalid_result)
    except ContractViolationError as e:
        print(f"  Caught: {type(e).__name__} with {len(e.errors)} errors ")