"""
test_contradictions.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- Contradiction Engine and Append-Only Truth

Tests:
  A. Contradiction detection between conflicting sources
  B. Append-only semantics -- no deletion, no modification
  C. Conflict density increments correctly
  D. Non-contradicting signals pass through cleanly
  E. TruthStore filtering and summary
  F. detect_and_record batch function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from marine_schema import build_signal
from contradiction_engine import (
    TruthStore, ContradictionRecord,
    detect_and_record, _coords_match, _values_contradict
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


def _make_signal(signal_type, value, source_id, coords=None):
    return build_signal(
        signal_type=signal_type,
        value=value,
        geo_coordinates=coords or [82.9739, 25.3176],
        source_id=source_id,
        confidence_initial=0.9
    )


# Block A -- Contradiction detection
def test_A1_contradiction_detected_different_sources():
    """Two sources report different depth values at same location."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s1)
    store.append(s2)
    passed = store.contradiction_count == 1
    log("TEST A1 -- Contradiction detected: different sources, different values",
        passed, f"contradictions={store.contradiction_count}")
    return passed


def test_A2_no_contradiction_same_source():
    """Same source reporting twice -- no contradiction."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "CWC_v1")
    store.append(s1)
    store.append(s2)
    passed = store.contradiction_count == 0
    log("TEST A2 -- No contradiction: same source, different values",
        passed, f"contradictions={store.contradiction_count}")
    return passed


def test_A3_no_contradiction_different_type():
    """Different signal types at same location -- no contradiction."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("discharge", 1500.0, "IWAI_v1")
    store.append(s1)
    store.append(s2)
    passed = store.contradiction_count == 0
    log("TEST A3 -- No contradiction: different signal types",
        passed, f"contradictions={store.contradiction_count}")
    return passed


def test_A4_no_contradiction_different_location():
    """Same type, same source group, but different locations -- no contradiction."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1", [82.9739, 25.3176])
    s2 = _make_signal("depth", 2.1, "IWAI_v1", [85.1376, 25.5941])
    store.append(s1)
    store.append(s2)
    passed = store.contradiction_count == 0
    log("TEST A4 -- No contradiction: different locations",
        passed, f"contradictions={store.contradiction_count}")
    return passed


def test_A5_contradiction_record_preserves_both_values():
    """ContradictionRecord must preserve both values."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s1)
    store.append(s2)
    records = store.get_contradictions()
    passed = (
        len(records) == 1 and
        records[0]["value_a"] == 3.5 and
        records[0]["value_b"] == 2.1
    )
    log("TEST A5 -- Contradiction record preserves both values",
        passed, f"value_a={records[0].get('value_a')} value_b={records[0].get('value_b')}")
    return passed


def test_A6_contradiction_resolution_ambiguous():
    """Contradiction resolution must be AMBIGUOUS."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s1)
    store.append(s2)
    records = store.get_contradictions()
    passed = records[0]["resolution"] == "AMBIGUOUS"
    log("TEST A6 -- Contradiction resolution is AMBIGUOUS (not resolved)",
        passed, f"resolution={records[0].get('resolution')}")
    return passed


# Block B -- Append-only semantics
def test_B1_both_signals_preserved_after_contradiction():
    """Both contradicting signals remain in the store."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s1)
    store.append(s2)
    passed = store.signal_count == 2
    log("TEST B1 -- Both signals preserved after contradiction (append-only)",
        passed, f"signal_count={store.signal_count}")
    return passed


def test_B2_store_grows_monotonically():
    """Signal count only ever increases."""
    store = TruthStore()
    counts = []
    for i in range(5):
        s = _make_signal("discharge", float(i * 100), f"SRC_{i}")
        store.append(s)
        counts.append(store.signal_count)
    passed = counts == [1, 2, 3, 4, 5]
    log("TEST B2 -- Store grows monotonically (no deletion)",
        passed, f"counts={counts}")
    return passed


def test_B3_original_signal_not_modified():
    """Original signal dict is not modified when contradiction occurs."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    original_density = s1["conflict_density"]
    store.append(s1)
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s2)
    # s1 in the store should still have its original conflict_density
    stored_s1 = store.get_signals(signal_type="depth", source_id="CWC_v1")[0]
    passed = stored_s1["conflict_density"] == original_density
    log("TEST B3 -- Original signal not modified after contradiction",
        passed,
        f"original_density={original_density} stored_density={stored_s1['conflict_density']}")
    return passed


# Block C -- Conflict density
def test_C1_conflict_density_increases_on_contradiction():
    """Incoming signal gets increased conflict_density after contradiction."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    store.append(s1)
    result = store.append(s2)
    passed = result["conflict_density"] > 0.0
    log("TEST C1 -- Conflict density increases on contradiction",
        passed, f"conflict_density={result['conflict_density']}")
    return passed


def test_C2_conflict_density_capped_at_1():
    """Conflict density never exceeds 1.0."""
    store = TruthStore()
    # Create many contradictions for same location
    s1 = _make_signal("depth", 3.5, "SRC_A")
    store.append(s1)
    result = None
    for i in range(10):
        s = _make_signal("depth", float(i + 1), f"SRC_{i}")
        result = store.append(s)
    passed = result["conflict_density"] <= 1.0
    log("TEST C2 -- Conflict density capped at 1.0",
        passed, f"final_density={result['conflict_density'] if result else 'N/A'}")
    return passed


def test_C3_no_conflict_density_increase_without_contradiction():
    """Clean signal keeps conflict_density=0.0."""
    store = TruthStore()
    s = _make_signal("discharge", 1500.0, "CWC_v1",
                     coords=[85.1376, 25.5941])
    result = store.append(s)
    passed = result["conflict_density"] == 0.0
    log("TEST C3 -- Clean signal: conflict_density stays 0.0",
        passed, f"conflict_density={result['conflict_density']}")
    return passed


# Block D -- Helper functions
def test_D1_coords_match_within_tolerance():
    """Coordinates within 0.01 degree tolerance match."""
    passed = _coords_match([82.9739, 25.3176], [82.9740, 25.3177])
    log("TEST D1 -- Coordinates within tolerance: match=True",
        passed)
    return passed


def test_D2_coords_no_match_outside_tolerance():
    """Coordinates outside tolerance do not match."""
    passed = not _coords_match([82.9739, 25.3176], [85.1376, 25.5941])
    log("TEST D2 -- Coordinates outside tolerance: match=False",
        passed)
    return passed


def test_D3_values_contradict_large_difference():
    """Values differing by more than 5% contradict."""
    passed = _values_contradict(3.5, 2.1)
    log("TEST D3 -- Large numeric difference: values contradict",
        passed)
    return passed


def test_D4_values_no_contradict_small_difference():
    """Values differing by less than 5% do not contradict."""
    passed = not _values_contradict(3.5, 3.52)
    log("TEST D4 -- Small numeric difference: values do not contradict",
        passed)
    return passed


def test_D5_string_values_contradict():
    """Different string values always contradict."""
    passed = _values_contradict("OPEN", "CLOSED")
    log("TEST D5 -- Different string values: contradict",
        passed)
    return passed


def test_D6_same_string_no_contradict():
    """Same string values do not contradict."""
    passed = not _values_contradict("OPEN", "OPEN")
    log("TEST D6 -- Same string values: no contradiction",
        passed)
    return passed


# Block E -- TruthStore filtering and summary
def test_E1_filter_by_signal_type():
    """get_signals filters by signal_type correctly."""
    store = TruthStore()
    store.append(_make_signal("depth", 3.5, "CWC_v1"))
    store.append(_make_signal("discharge", 1500.0, "CWC_v1",
                              coords=[85.1376, 25.5941]))
    depth_signals = store.get_signals(signal_type="depth")
    passed = len(depth_signals) == 1 and depth_signals[0]["signal_type"] == "depth"
    log("TEST E1 -- get_signals filters by signal_type",
        passed, f"depth_count={len(depth_signals)}")
    return passed


def test_E2_conflict_summary_correct():
    """get_conflict_summary returns correct totals."""
    store = TruthStore()
    s1 = _make_signal("depth", 3.5, "CWC_v1")
    s2 = _make_signal("depth", 2.1, "IWAI_v1")
    s3 = _make_signal("discharge", 1500.0, "CWC_v1",
                      coords=[85.1376, 25.5941])
    store.append(s1)
    store.append(s2)
    store.append(s3)
    summary = store.get_conflict_summary()
    passed = (
        summary["total_signals"] == 3 and
        summary["total_contradictions"] == 1
    )
    log("TEST E2 -- conflict_summary: total_signals=3 total_contradictions=1",
        passed, f"summary={summary}")
    return passed


def test_E3_empty_store_summary():
    """Empty store returns zero counts."""
    store = TruthStore()
    summary = store.get_conflict_summary()
    passed = (
        summary["total_signals"] == 0 and
        summary["total_contradictions"] == 0
    )
    log("TEST E3 -- Empty store: all counts zero",
        passed, f"summary={summary}")
    return passed


# Block F -- detect_and_record
def test_F1_detect_and_record_all_valid():
    """detect_and_record appends all valid signals."""
    store = TruthStore()
    signals = [
        _make_signal("depth", 3.5, "CWC_v1"),
        _make_signal("discharge", 1500.0, "CWC_v1",
                     coords=[85.1376, 25.5941])
    ]
    result = detect_and_record(store, signals)
    passed = result["appended"] == 2 and result["failed"] == 0
    log("TEST F1 -- detect_and_record: 2 valid signals appended",
        passed, f"appended={result['appended']} failed={result['failed']}")
    return passed


def test_F2_detect_and_record_finds_contradiction():
    """detect_and_record reports contradiction count."""
    store = TruthStore()
    signals = [
        _make_signal("depth", 3.5, "CWC_v1"),
        _make_signal("depth", 2.1, "IWAI_v1")
    ]
    result = detect_and_record(store, signals)
    passed = result["contradictions_found"] == 1
    log("TEST F2 -- detect_and_record: contradiction found and reported",
        passed, f"contradictions_found={result['contradictions_found']}")
    return passed


def test_F3_detect_and_record_empty():
    """detect_and_record with empty list returns zeros."""
    store = TruthStore()
    result = detect_and_record(store, [])
    passed = result["appended"] == 0 and result["failed"] == 0
    log("TEST F3 -- detect_and_record: empty list returns zeros",
        passed)
    return passed


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Contradiction Engine Test Suite")
    print("=" * 60)

    tests = [
        test_A1_contradiction_detected_different_sources,
        test_A2_no_contradiction_same_source,
        test_A3_no_contradiction_different_type,
        test_A4_no_contradiction_different_location,
        test_A5_contradiction_record_preserves_both_values,
        test_A6_contradiction_resolution_ambiguous,
        test_B1_both_signals_preserved_after_contradiction,
        test_B2_store_grows_monotonically,
        test_B3_original_signal_not_modified,
        test_C1_conflict_density_increases_on_contradiction,
        test_C2_conflict_density_capped_at_1,
        test_C3_no_conflict_density_increase_without_contradiction,
        test_D1_coords_match_within_tolerance,
        test_D2_coords_no_match_outside_tolerance,
        test_D3_values_contradict_large_difference,
        test_D4_values_no_contradict_small_difference,
        test_D5_string_values_contradict,
        test_D6_same_string_no_contradict,
        test_E1_filter_by_signal_type,
        test_E2_conflict_summary_correct,
        test_E3_empty_store_summary,
        test_F1_detect_and_record_all_valid,
        test_F2_detect_and_record_finds_contradiction,
        test_F3_detect_and_record_empty,
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