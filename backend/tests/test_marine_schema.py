"""
test_marine_schema.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- Unified Marine Schema

Tests all schema normalization, validation, and rejection rules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from marine_schema import (
    check_schema, normalize_signal, normalize_batch,
    build_signal, MarineSchemaError, VALID_SIGNAL_TYPES
)

PASS = "  PASS"
FAIL = "  FAIL"
results_log = []


def log(name, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"{status}  {name}"
    if detail:
        msg += f"\n         -> {detail}"
    print(msg)
    results_log.append((name, passed))


# Base valid signal
VALID_SIGNAL = {
    "event_id": "EVT_TEST_001",
    "timestamp": "2026-05-26T10:00:00",
    "geo_coordinates": [82.9739, 25.3176],
    "signal_type": "depth",
    "value": 3.5,
    "confidence_initial": 0.9,
    "source_id": "CWC_DEPTH_v1",
    "source_hash": "abc123",
    "extraction_hash": "def456",
    "conflict_density": 0.0
}


# Block A -- Valid signals pass
def test_A1_valid_signal_passes():
    is_valid, errors = check_schema(VALID_SIGNAL)
    passed = is_valid and errors == []
    log("TEST A1 -- Valid signal passes schema", passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_A2_build_signal_produces_valid():
    sig = build_signal(
        signal_type="discharge",
        value=1500.0,
        geo_coordinates=[85.1376, 25.5941],
        source_id="CWC_DISCH_v1",
        confidence_initial=0.85
    )
    is_valid, errors = check_schema(sig)
    passed = is_valid and errors == []
    log("TEST A2 -- build_signal produces valid schema signal", passed,
        f"is_valid={is_valid} event_id={sig.get('event_id')}")
    return passed


def test_A3_all_valid_signal_types_accepted():
    sample_types = ["depth", "discharge", "pollution", "bridge_clearance",
                    "cargo_movement", "tourism_node", "seaplane_feasibility"]
    all_passed = True
    for st in sample_types:
        sig = build_signal(
            signal_type=st,
            value=1.0,
            geo_coordinates=[82.9739, 25.3176],
            source_id="TEST_v1",
            confidence_initial=0.8
        )
        is_valid, _ = check_schema(sig)
        if not is_valid:
            all_passed = False
    log("TEST A3 -- Sample valid signal types all accepted", all_passed,
        f"tested {len(sample_types)} signal types")
    return all_passed


def test_A4_deterministic_event_id():
    sig1 = build_signal("depth", 3.5, [82.9739, 25.3176], "CWC_v1", 0.9)
    sig2 = build_signal("depth", 3.5, [82.9739, 25.3176], "CWC_v1", 0.9)
    passed = sig1["event_id"] == sig2["event_id"]
    log("TEST A4 -- Same input produces same event_id (deterministic)", passed,
        f"id1={sig1['event_id']} id2={sig2['event_id']}")
    return passed


def test_A5_hashes_deterministic():
    sig1 = build_signal("depth", 3.5, [82.9739, 25.3176], "CWC_v1", 0.9)
    sig2 = build_signal("depth", 3.5, [82.9739, 25.3176], "CWC_v1", 0.9)
    passed = (sig1["source_hash"] == sig2["source_hash"] and
              sig1["extraction_hash"] == sig2["extraction_hash"])
    log("TEST A5 -- Hashes are deterministic across runs", passed,
        f"source_hash match={sig1['source_hash']==sig2['source_hash']}")
    return passed


# Block B -- Missing required fields caught
def test_B1_missing_event_id():
    s = {**VALID_SIGNAL}
    del s["event_id"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("event_id" in e for e in errors)
    log("TEST B1 -- Missing event_id caught", passed, f"errors={errors}")
    return passed


def test_B2_missing_geo_coordinates():
    s = {**VALID_SIGNAL}
    del s["geo_coordinates"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("geo_coordinates" in e for e in errors)
    log("TEST B2 -- Missing geo_coordinates caught", passed, f"errors={errors}")
    return passed


def test_B3_missing_signal_type():
    s = {**VALID_SIGNAL}
    del s["signal_type"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("signal_type" in e for e in errors)
    log("TEST B3 -- Missing signal_type caught", passed, f"errors={errors}")
    return passed


def test_B4_missing_value():
    s = {**VALID_SIGNAL}
    del s["value"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("value" in e for e in errors)
    log("TEST B4 -- Missing value caught", passed, f"errors={errors}")
    return passed


def test_B5_missing_confidence():
    s = {**VALID_SIGNAL}
    del s["confidence_initial"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("confidence_initial" in e for e in errors)
    log("TEST B5 -- Missing confidence_initial caught", passed, f"errors={errors}")
    return passed


def test_B6_missing_source_id():
    s = {**VALID_SIGNAL}
    del s["source_id"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("source_id" in e for e in errors)
    log("TEST B6 -- Missing source_id caught", passed, f"errors={errors}")
    return passed


def test_B7_missing_conflict_density():
    s = {**VALID_SIGNAL}
    del s["conflict_density"]
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("conflict_density" in e for e in errors)
    log("TEST B7 -- Missing conflict_density caught", passed, f"errors={errors}")
    return passed


# Block C -- Invalid field values caught
def test_C1_invalid_signal_type():
    s = {**VALID_SIGNAL, "signal_type": "unknown_type"}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("signal_type" in e for e in errors)
    log("TEST C1 -- Invalid signal_type caught", passed, f"errors={errors}")
    return passed


def test_C2_coordinates_out_of_india():
    s = {**VALID_SIGNAL, "geo_coordinates": [200.0, 50.0]}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("geo_coordinates" in e for e in errors)
    log("TEST C2 -- Coordinates outside India bounds caught", passed,
        f"errors={errors}")
    return passed


def test_C3_confidence_above_1():
    s = {**VALID_SIGNAL, "confidence_initial": 1.5}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("confidence_initial" in e for e in errors)
    log("TEST C3 -- confidence_initial > 1.0 caught", passed, f"errors={errors}")
    return passed


def test_C4_confidence_below_0():
    s = {**VALID_SIGNAL, "confidence_initial": -0.1}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("confidence_initial" in e for e in errors)
    log("TEST C4 -- confidence_initial < 0.0 caught", passed, f"errors={errors}")
    return passed


def test_C5_conflict_density_above_1():
    s = {**VALID_SIGNAL, "conflict_density": 1.5}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("conflict_density" in e for e in errors)
    log("TEST C5 -- conflict_density > 1.0 caught", passed, f"errors={errors}")
    return passed


def test_C6_non_list_coordinates():
    s = {**VALID_SIGNAL, "geo_coordinates": "82.97,25.31"}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("geo_coordinates" in e for e in errors)
    log("TEST C6 -- Non-list geo_coordinates caught", passed, f"errors={errors}")
    return passed


def test_C7_single_coordinate():
    s = {**VALID_SIGNAL, "geo_coordinates": [82.9739]}
    is_valid, errors = check_schema(s)
    passed = not is_valid and any("geo_coordinates" in e for e in errors)
    log("TEST C7 -- Single-element coordinates caught", passed, f"errors={errors}")
    return passed


def test_C8_non_dict_signal():
    is_valid, errors = check_schema("not a dict")
    passed = not is_valid and len(errors) > 0
    log("TEST C8 -- Non-dict signal rejected cleanly", passed,
        f"errors={errors}")
    return passed


# Block D -- normalize_signal behavior
def test_D1_normalize_adds_event_id():
    raw = {
        "signal_type": "depth",
        "value": 3.5,
        "geo_coordinates": [82.9739, 25.3176],
        "source_id": "CWC_v1",
        "confidence_initial": 0.9,
        "conflict_density": 0.0
    }
    normalized = normalize_signal(raw)
    passed = "event_id" in normalized and normalized["event_id"].startswith("EVT_")
    log("TEST D1 -- normalize_signal auto-generates event_id", passed,
        f"event_id={normalized.get('event_id')}")
    return passed


def test_D2_normalize_adds_hashes():
    raw = {
        "signal_type": "discharge",
        "value": 1500.0,
        "geo_coordinates": [85.1376, 25.5941],
        "source_id": "CWC_v1",
        "confidence_initial": 0.85,
        "conflict_density": 0.0
    }
    normalized = normalize_signal(raw)
    passed = ("source_hash" in normalized and
              "extraction_hash" in normalized and
              len(normalized["source_hash"]) > 0)
    log("TEST D2 -- normalize_signal auto-generates hashes", passed,
        f"source_hash={normalized.get('source_hash')}")
    return passed


def test_D3_normalize_raises_on_invalid():
    bad = {"signal_type": "bad_type", "value": 1.0,
           "source_id": "X", "confidence_initial": 0.5}
    try:
        normalize_signal(bad)
        passed = False
    except MarineSchemaError as e:
        passed = len(e.errors) > 0
    log("TEST D3 -- normalize_signal raises MarineSchemaError on invalid",
        passed)
    return passed


def test_D4_normalize_defaults_conflict_density():
    raw = {
        "signal_type": "depth",
        "value": 2.0,
        "geo_coordinates": [82.9739, 25.3176],
        "source_id": "CWC_v1",
        "confidence_initial": 0.8
    }
    normalized = normalize_signal(raw)
    passed = normalized.get("conflict_density") == 0.0
    log("TEST D4 -- normalize_signal defaults conflict_density to 0.0", passed,
        f"conflict_density={normalized.get('conflict_density')}")
    return passed


# Block E -- batch normalization
def test_E1_batch_all_valid():
    raws = [
        build_signal("depth", 3.5, [82.9739, 25.3176], "CWC_v1", 0.9),
        build_signal("discharge", 1500.0, [85.1376, 25.5941], "CWC_v1", 0.85)
    ]
    valid, failed = normalize_batch(raws)
    passed = len(valid) == 2 and len(failed) == 0
    log("TEST E1 -- Batch all valid: 2 valid, 0 failed", passed,
        f"valid={len(valid)} failed={len(failed)}")
    return passed


def test_E2_batch_mixed():
    raws = [
        {"signal_type": "depth", "value": 3.5,
         "geo_coordinates": [82.9739, 25.3176],
         "source_id": "CWC_v1", "confidence_initial": 0.9},
        {"signal_type": "bad_type", "value": 1.0,
         "geo_coordinates": [82.9739, 25.3176],
         "source_id": "X", "confidence_initial": 0.5}
    ]
    valid, failed = normalize_batch(raws)
    passed = len(valid) == 1 and len(failed) == 1
    log("TEST E2 -- Batch mixed: 1 valid, 1 failed", passed,
        f"valid={len(valid)} failed={len(failed)}")
    return passed


def test_E3_batch_empty():
    valid, failed = normalize_batch([])
    passed = valid == [] and failed == []
    log("TEST E3 -- Batch empty list: returns ([], [])", passed)
    return passed


def test_E4_failed_has_schema_errors_key():
    raws = [{"signal_type": "bad_type", "value": 1.0,
             "source_id": "X", "confidence_initial": 0.5}]
    _, failed = normalize_batch(raws)
    passed = len(failed) == 1 and "schema_errors" in failed[0]
    log("TEST E4 -- Failed batch signals have schema_errors key", passed,
        f"schema_errors={failed[0].get('schema_errors') if failed else 'N/A'}")
    return passed


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Marine Schema Test Suite")
    print("=" * 60)

    tests = [
        test_A1_valid_signal_passes,
        test_A2_build_signal_produces_valid,
        test_A3_all_valid_signal_types_accepted,
        test_A4_deterministic_event_id,
        test_A5_hashes_deterministic,
        test_B1_missing_event_id,
        test_B2_missing_geo_coordinates,
        test_B3_missing_signal_type,
        test_B4_missing_value,
        test_B5_missing_confidence,
        test_B6_missing_source_id,
        test_B7_missing_conflict_density,
        test_C1_invalid_signal_type,
        test_C2_coordinates_out_of_india,
        test_C3_confidence_above_1,
        test_C4_confidence_below_0,
        test_C5_conflict_density_above_1,
        test_C6_non_list_coordinates,
        test_C7_single_coordinate,
        test_C8_non_dict_signal,
        test_D1_normalize_adds_event_id,
        test_D2_normalize_adds_hashes,
        test_D3_normalize_raises_on_invalid,
        test_D4_normalize_defaults_conflict_density,
        test_E1_batch_all_valid,
        test_E2_batch_mixed,
        test_E3_batch_empty,
        test_E4_failed_has_schema_errors_key,
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
    print(f"Results: {passed}/{total} passed",
          "ALL PASS" if failed == 0 else f"{failed} FAILED")
    print("=" * 60)
    import sys
    sys.exit(0 if failed == 0 else 1)