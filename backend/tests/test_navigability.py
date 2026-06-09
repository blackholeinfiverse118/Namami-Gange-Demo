"""
test_navigability.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- NW5 + Navigability Layer

Tests:
  A. Depth compatibility -- all categories and vessel classes
  B. Seasonal closure probability -- NW1 and NW5
  C. Segment navigability scoring
  D. Best months finder
  E. Proposal output validation
  F. Signal output validation
  G. Boundary and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from navigability_layer import (
    assess_depth_compatibility,
    get_seasonal_closure_probability,
    score_segment_navigability,
    best_months_for_segment,
    VESSEL_DRAFT_CLEARANCE,
    NW1_SEASONAL_INDEX,
    NW5_SEASONAL_INDEX,
    NATIONAL_WATERWAYS,
    DEPTH_DEEP_WATER,
    DEPTH_NAVIGABLE,
    DEPTH_SHALLOW,
    DEPTH_CRITICAL
)
from marine_schema import check_schema

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


# Block A -- Depth compatibility
def test_A1_deep_water_compatible():
    """Depth >= 5.0m is DEEP category."""
    result = assess_depth_compatibility(5.0, "Class-III")
    passed = result["depth_category"] == "DEEP" and result["score"] == 100.0
    log("TEST A1 -- Depth 5.0m: category=DEEP score=100",
        passed,
        f"category={result['depth_category']} score={result['score']}")
    return passed


def test_A2_navigable_depth():
    """Depth 3.0-5.0m is NAVIGABLE category."""
    result = assess_depth_compatibility(3.5, "Class-III")
    passed = result["depth_category"] == "NAVIGABLE" and result["score"] == 80.0
    log("TEST A2 -- Depth 3.5m: category=NAVIGABLE score=80",
        passed,
        f"category={result['depth_category']} score={result['score']}")
    return passed


def test_A3_shallow_depth():
    """Depth 1.5-3.0m is SHALLOW category."""
    result = assess_depth_compatibility(2.0, "Class-I")
    passed = result["depth_category"] == "SHALLOW"
    log("TEST A3 -- Depth 2.0m: category=SHALLOW",
        passed,
        f"category={result['depth_category']}")
    return passed


def test_A4_critical_depth():
    """Depth below 1.5m is CRITICAL category."""
    result = assess_depth_compatibility(1.0, "Class-I")
    passed = result["depth_category"] == "CRITICAL"
    log("TEST A4 -- Depth 1.0m: category=CRITICAL",
        passed,
        f"category={result['depth_category']}")
    return passed


def test_A5_incompatible_depth_score_zero():
    """Depth insufficient for vessel class: score=0, compatible=False."""
    result = assess_depth_compatibility(1.2, "Class-IV")
    passed = result["compatible"] is False and result["score"] == 0.0
    log("TEST A5 -- Depth 1.2m for Class-IV: compatible=False score=0",
        passed,
        f"compatible={result['compatible']} required={result['required_depth_m']}")
    return passed


def test_A6_compatible_depth_score_positive():
    """Sufficient depth: compatible=True, score > 0."""
    result = assess_depth_compatibility(4.0, "Class-III")
    passed = result["compatible"] is True and result["score"] > 0
    log("TEST A6 -- Depth 4.0m for Class-III: compatible=True score>0",
        passed,
        f"compatible={result['compatible']} score={result['score']}")
    return passed


def test_A7_all_vessel_classes_have_requirements():
    """All vessel classes have draft clearance requirements defined."""
    classes = ["Class-I", "Class-II", "Class-III", "Class-IV",
               "Class-V", "Seaplane", "Barge", "Tug", "Ferry"]
    all_defined = all(c in VESSEL_DRAFT_CLEARANCE for c in classes)
    log("TEST A7 -- All vessel classes have depth requirements",
        all_defined)
    return all_defined


def test_A8_depth_requirement_ordering():
    """Higher class vessels need more depth."""
    d1 = VESSEL_DRAFT_CLEARANCE["Class-I"]
    d3 = VESSEL_DRAFT_CLEARANCE["Class-III"]
    d5 = VESSEL_DRAFT_CLEARANCE["Class-V"]
    passed = d1 < d3 < d5
    log("TEST A8 -- Depth requirement: Class-I < Class-III < Class-V",
        passed,
        f"I={d1} III={d3} V={d5}")
    return passed


# Block B -- Seasonal closure
def test_B1_nw1_monsoon_high_risk():
    """NW1 in July (peak monsoon): HIGH closure risk."""
    result = get_seasonal_closure_probability("NW1", 7)
    passed = result["risk_level"] == "HIGH" and result["operational"] is False
    log("TEST B1 -- NW1 July: HIGH risk operational=False",
        passed,
        f"risk={result['risk_level']} "
        f"closure_prob={result['closure_probability']}")
    return passed


def test_B2_nw1_winter_low_risk():
    """NW1 in November: LOW closure risk."""
    result = get_seasonal_closure_probability("NW1", 11)
    passed = result["risk_level"] == "LOW" and result["operational"] is True
    log("TEST B2 -- NW1 November: LOW risk operational=True",
        passed,
        f"risk={result['risk_level']} index={result['navigability_index']}")
    return passed


def test_B3_nw5_seasonal_data_present():
    """NW5 has seasonal data for all 12 months."""
    passed = len(NW5_SEASONAL_INDEX) == 12
    log("TEST B3 -- NW5 has 12-month seasonal data",
        passed,
        f"months={len(NW5_SEASONAL_INDEX)}")
    return passed


def test_B4_nw1_seasonal_data_present():
    """NW1 has seasonal data for all 12 months."""
    passed = len(NW1_SEASONAL_INDEX) == 12
    log("TEST B4 -- NW1 has 12-month seasonal data",
        passed,
        f"months={len(NW1_SEASONAL_INDEX)}")
    return passed


def test_B5_navigability_index_range():
    """All navigability indices are between 0.0 and 1.0."""
    all_valid = all(
        0.0 <= v <= 1.0
        for v in list(NW1_SEASONAL_INDEX.values()) +
                 list(NW5_SEASONAL_INDEX.values())
    )
    log("TEST B5 -- All navigability indices in range [0.0, 1.0]",
        all_valid)
    return all_valid


def test_B6_closure_prob_is_complement():
    """Closure probability = 1.0 - navigability_index."""
    result = get_seasonal_closure_probability("NW1", 3)
    expected = round(1.0 - NW1_SEASONAL_INDEX[3], 2)
    passed = result["closure_probability"] == expected
    log("TEST B6 -- Closure probability = 1.0 - navigability_index",
        passed,
        f"closure={result['closure_probability']} expected={expected}")
    return passed


def test_B7_month_name_correct():
    """Month name returned correctly."""
    result = get_seasonal_closure_probability("NW1", 1)
    passed = result["month_name"] == "January"
    log("TEST B7 -- Month 1 name is January",
        passed,
        f"month_name={result['month_name']}")
    return passed


# Block C -- Segment navigability scoring
def test_C1_viable_segment_scores_positive():
    """Viable segment produces positive composite score."""
    result = score_segment_navigability(
        segment_id="TEST_SEG_001",
        waterway_id="NW1",
        geo_coordinates=[85.1376, 25.5941],
        depth_m=4.2,
        vessel_class="Class-III",
        month=11
    )
    passed = result["composite_navigability_score"] > 0 and result["navigation_viable"] is True
    log("TEST C1 -- Viable segment: score>0 viable=True",
        passed,
        f"score={result['composite_navigability_score']} "
        f"viable={result['navigation_viable']}")
    return passed


def test_C2_insufficient_depth_not_viable():
    """Segment with insufficient depth: navigation_viable=False."""
    result = score_segment_navigability(
        segment_id="SHALLOW_SEG",
        waterway_id="NW1",
        geo_coordinates=[82.9739, 25.3176],
        depth_m=0.5,
        vessel_class="Class-IV",
        month=11
    )
    passed = result["navigation_viable"] is False
    log("TEST C2 -- Insufficient depth: navigation_viable=False",
        passed,
        f"depth=0.5m viable={result['navigation_viable']}")
    return passed


def test_C3_monsoon_month_not_viable():
    """Segment in peak monsoon month: navigation_viable=False."""
    result = score_segment_navigability(
        segment_id="MONSOON_SEG",
        waterway_id="NW1",
        geo_coordinates=[82.9739, 25.3176],
        depth_m=4.0,
        vessel_class="Class-III",
        month=7
    )
    passed = result["navigation_viable"] is False
    log("TEST C3 -- Peak monsoon (July): navigation_viable=False",
        passed,
        f"month=July viable={result['navigation_viable']}")
    return passed


def test_C4_score_range_valid():
    """Composite score is always in range 0-100."""
    test_cases = [
        (0.5, "Class-V", 7),
        (4.0, "Class-III", 11),
        (10.0, "Class-I", 1)
    ]
    all_valid = True
    for depth, vessel, month in test_cases:
        result = score_segment_navigability(
            "TEST", "NW1", [82.9739, 25.3176],
            depth, vessel, month
        )
        if not (0.0 <= result["composite_navigability_score"] <= 100.0):
            all_valid = False
    log("TEST C4 -- All composite scores in range [0.0, 100.0]",
        all_valid)
    return all_valid


def test_C5_confidence_range_valid():
    """Navigability confidence is always in range 0-1."""
    result = score_segment_navigability(
        "TEST", "NW1", [82.9739, 25.3176], 4.0, "Class-III", 11
    )
    passed = 0.0 <= result["navigability_confidence"] <= 1.0
    log("TEST C5 -- Navigability confidence in range [0.0, 1.0]",
        passed,
        f"confidence={result['navigability_confidence']}")
    return passed


def test_C6_produces_3_signals():
    """score_segment_navigability produces exactly 3 signals."""
    result = score_segment_navigability(
        "TEST", "NW1", [82.9739, 25.3176], 4.0, "Class-III", 11
    )
    passed = len(result["signals"]) == 3
    log("TEST C6 -- score_segment_navigability produces 3 signals",
        passed,
        f"signals={len(result['signals'])}")
    return passed


def test_C7_deterministic_same_input():
    """Same input produces identical score (determinism check)."""
    kwargs = dict(
        segment_id="DET_SEG",
        waterway_id="NW1",
        geo_coordinates=[85.1376, 25.5941],
        depth_m=3.8,
        vessel_class="Class-III",
        month=11
    )
    r1 = score_segment_navigability(**kwargs)
    r2 = score_segment_navigability(**kwargs)
    passed = r1["composite_navigability_score"] == r2["composite_navigability_score"]
    log("TEST C7 -- Determinism: same input produces same score",
        passed,
        f"run1={r1['composite_navigability_score']} "
        f"run2={r2['composite_navigability_score']}")
    return passed


# Block D -- Best months
def test_D1_best_months_returns_sorted():
    """best_months_for_segment returns months sorted by score descending."""
    result = best_months_for_segment(
        "TEST_SEG", "NW1", [82.9739, 25.3176], 3.5, "Class-III"
    )
    scores = [m["score"] for m in result["best_months"]]
    passed = scores == sorted(scores, reverse=True)
    log("TEST D1 -- Best months sorted by score descending",
        passed,
        f"top3_scores={scores[:3]}")
    return passed


def test_D2_best_months_all_viable():
    """All months in best_months list are viable."""
    result = best_months_for_segment(
        "TEST_SEG", "NW1", [82.9739, 25.3176], 3.5, "Class-III"
    )
    all_viable = all(m["viable"] for m in result["best_months"])
    log("TEST D2 -- All best_months entries are viable",
        all_viable,
        f"viable_count={result['viable_month_count']}")
    return all_viable


def test_D3_all_months_ranked_has_12():
    """all_months_ranked always contains all 12 months."""
    result = best_months_for_segment(
        "TEST_SEG", "NW1", [82.9739, 25.3176], 3.5, "Class-III"
    )
    passed = len(result["all_months_ranked"]) == 12
    log("TEST D3 -- all_months_ranked contains all 12 months",
        passed,
        f"count={len(result['all_months_ranked'])}")
    return passed


def test_D4_monsoon_months_not_in_best():
    """Peak monsoon months (June-August) not in top best months."""
    result = best_months_for_segment(
        "TEST_SEG", "NW1", [82.9739, 25.3176], 3.5, "Class-III"
    )
    top_month_names = {m["month_name"] for m in result["best_months"][:6]}
    monsoon_in_top = bool(
        top_month_names & {"June", "July", "August"}
    )
    passed = not monsoon_in_top
    log("TEST D4 -- Peak monsoon months not in top best months",
        passed,
        f"top_months={top_month_names}")
    return passed


# Block E -- Proposal validation
def test_E1_viable_proposal_says_feasible():
    """Viable segment proposal contains FEASIBLE."""
    result = score_segment_navigability(
        "PATNA_001", "NW1", [85.1376, 25.5941],
        4.2, "Class-III", 11
    )
    passed = "FEASIBLE" in result["proposal"]
    log("TEST E1 -- Viable segment proposal contains FEASIBLE",
        passed,
        f"proposal excerpt: {result['proposal'][:60]}")
    return passed


def test_E2_non_viable_proposal_says_not_feasible():
    """Non-viable segment proposal contains NOT FEASIBLE."""
    result = score_segment_navigability(
        "SHALLOW_001", "NW1", [82.9739, 25.3176],
        0.5, "Class-IV", 7
    )
    passed = "NOT FEASIBLE" in result["proposal"]
    log("TEST E2 -- Non-viable proposal contains NOT FEASIBLE",
        passed,
        f"proposal excerpt: {result['proposal'][:60]}")
    return passed


def test_E3_proposal_contains_vessel_class():
    """Proposal mentions the vessel class."""
    result = score_segment_navigability(
        "TEST", "NW1", [85.1376, 25.5941],
        4.0, "Class-III", 11
    )
    passed = "Class-III" in result["proposal"]
    log("TEST E3 -- Proposal mentions vessel class",
        passed)
    return passed


def test_E4_proposal_contains_month():
    """Proposal mentions the month name."""
    result = score_segment_navigability(
        "TEST", "NW1", [85.1376, 25.5941],
        4.0, "Class-III", 11
    )
    passed = "November" in result["proposal"]
    log("TEST E4 -- Proposal mentions month name",
        passed)
    return passed


# Block F -- Signal validation
def test_F1_all_signals_pass_schema():
    """All 3 signals from score_segment_navigability pass marine schema."""
    result = score_segment_navigability(
        "TEST", "NW1", [85.1376, 25.5941],
        4.0, "Class-III", 11
    )
    all_valid = True
    for sig in result["signals"]:
        is_valid, errors = check_schema(sig)
        if not is_valid:
            all_valid = False
    log("TEST F1 -- All 3 signals pass marine schema",
        all_valid)
    return all_valid


def test_F2_signal_types_correct():
    """Signals have correct signal types: depth, navigability_confidence, segment_score."""
    result = score_segment_navigability(
        "TEST", "NW1", [85.1376, 25.5941],
        4.0, "Class-III", 11
    )
    signal_types = {s["signal_type"] for s in result["signals"]}
    expected = {"depth", "navigability_confidence", "segment_score"}
    passed = signal_types == expected
    log("TEST F2 -- Signal types: depth, navigability_confidence, segment_score",
        passed,
        f"types={signal_types}")
    return passed


# Block G -- Boundary and edge cases
def test_G1_national_waterways_defined():
    """NW1 and NW5 are defined in NATIONAL_WATERWAYS."""
    passed = "NW1" in NATIONAL_WATERWAYS and "NW5" in NATIONAL_WATERWAYS
    log("TEST G1 -- NW1 and NW5 defined in NATIONAL_WATERWAYS",
        passed)
    return passed


def test_G2_depth_thresholds_ordered():
    """Depth thresholds are in correct ascending order."""
    passed = (
        DEPTH_CRITICAL < DEPTH_SHALLOW < DEPTH_NAVIGABLE < DEPTH_DEEP_WATER
    )
    log("TEST G2 -- Depth thresholds in correct order",
        passed,
        f"CRITICAL={DEPTH_CRITICAL} SHALLOW={DEPTH_SHALLOW} "
        f"NAVIGABLE={DEPTH_NAVIGABLE} DEEP={DEPTH_DEEP_WATER}")
    return passed


def test_G3_zero_depth_not_viable():
    """Zero depth: not compatible with any vessel."""
    result = assess_depth_compatibility(0.0, "Seaplane")
    passed = result["compatible"] is False and result["score"] == 0.0
    log("TEST G3 -- Zero depth: compatible=False score=0",
        passed,
        f"compatible={result['compatible']}")
    return passed


def test_G4_unknown_waterway_defaults():
    """Unknown waterway ID returns default values without crash."""
    try:
        result = get_seasonal_closure_probability("NW99", 6)
        passed = isinstance(result["navigability_index"], float)
    except Exception as e:
        passed = False
    log("TEST G4 -- Unknown waterway: returns default, no crash",
        passed)
    return passed


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Navigability Layer Test Suite")
    print("=" * 60)

    tests = [
        test_A1_deep_water_compatible,
        test_A2_navigable_depth,
        test_A3_shallow_depth,
        test_A4_critical_depth,
        test_A5_incompatible_depth_score_zero,
        test_A6_compatible_depth_score_positive,
        test_A7_all_vessel_classes_have_requirements,
        test_A8_depth_requirement_ordering,
        test_B1_nw1_monsoon_high_risk,
        test_B2_nw1_winter_low_risk,
        test_B3_nw5_seasonal_data_present,
        test_B4_nw1_seasonal_data_present,
        test_B5_navigability_index_range,
        test_B6_closure_prob_is_complement,
        test_B7_month_name_correct,
        test_C1_viable_segment_scores_positive,
        test_C2_insufficient_depth_not_viable,
        test_C3_monsoon_month_not_viable,
        test_C4_score_range_valid,
        test_C5_confidence_range_valid,
        test_C6_produces_3_signals,
        test_C7_deterministic_same_input,
        test_D1_best_months_returns_sorted,
        test_D2_best_months_all_viable,
        test_D3_all_months_ranked_has_12,
        test_D4_monsoon_months_not_in_best,
        test_E1_viable_proposal_says_feasible,
        test_E2_non_viable_proposal_says_not_feasible,
        test_E3_proposal_contains_vessel_class,
        test_E4_proposal_contains_month,
        test_F1_all_signals_pass_schema,
        test_F2_signal_types_correct,
        test_G1_national_waterways_defined,
        test_G2_depth_thresholds_ordered,
        test_G3_zero_depth_not_viable,
        test_G4_unknown_waterway_defaults,
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