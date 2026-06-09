"""
test_bridge_barrage_constraints.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- Bridge and Barrage Constraint Layer

Tests:
  A. Bridge clearance assessment -- all risk levels
  B. Vessel class height profiles
  C. Barrage passage -- lock status variants
  D. Seaplane obstruction detection
  E. Corridor constraint scoring
  F. Reference data integrity
  G. Signal output validation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from barrage_bridge_layer import (
    assess_bridge_clearance,
    assess_barrage_passage,
    score_corridor_constraints,
    VESSEL_CLASS_HEIGHTS,
    VESSEL_CLASS_DRAFTS,
    GANGA_BARRAGES,
    GANGA_BRIDGES,
    BRIDGE_SAFE_CLEARANCE_M,
    BRIDGE_MARGINAL_CLEARANCE_M,
    BRIDGE_CRITICAL_CLEARANCE_M
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


# Block A -- Bridge clearance risk levels
def test_A1_safe_clearance():
    """Large clearance margin produces SAFE risk level."""
    result = assess_bridge_clearance(
        bridge_name="Test Bridge",
        air_clearance_m=20.0,
        vessel_class="Class-III",
        geo_coordinates=[82.9739, 25.3176]
    )
    passed = result["risk_level"] == "SAFE" and result["passage_safe"] is True
    log("TEST A1 -- Large clearance: risk=SAFE passage_safe=True",
        passed, f"risk={result['risk_level']} margin={result['clearance_margin_m']}")
    return passed


def test_A2_marginal_clearance():
    """Clearance margin between 5-10m produces MARGINAL risk."""
    result = assess_bridge_clearance(
        bridge_name="Test Bridge",
        air_clearance_m=12.0,
        vessel_class="Class-III",
        geo_coordinates=[82.9739, 25.3176]
    )
    # Class-III height=4.5m, margin=12.0-4.5=7.5m (MARGINAL: 5-10m)
    passed = result["risk_level"] == "MARGINAL"
    log("TEST A2 -- Clearance margin 7.5m: risk=MARGINAL",
        passed, f"risk={result['risk_level']} margin={result['clearance_margin_m']}")
    return passed


def test_A3_critical_clearance():
    """Low clearance margin produces CRITICAL risk."""
    result = assess_bridge_clearance(
        bridge_name="Malviya Bridge",
        air_clearance_m=8.5,
        vessel_class="Class-III",
        geo_coordinates=[82.9739, 25.3176]
    )
    # Class-III height=4.5m, margin=4.0m (CRITICAL: 2-5m)
    passed = result["risk_level"] == "CRITICAL" and result["passage_safe"] is False
    log("TEST A3 -- Clearance margin 4.0m: risk=CRITICAL passage_safe=False",
        passed, f"risk={result['risk_level']} margin={result['clearance_margin_m']}")
    return passed


def test_A4_blocked_clearance():
    """Vessel taller than bridge clearance: BLOCKED."""
    result = assess_bridge_clearance(
        bridge_name="Low Bridge",
        air_clearance_m=3.0,
        vessel_class="Class-V",
        geo_coordinates=[82.9739, 25.3176]
    )
    # Class-V height=8.0m, clearance=3.0m, margin=-5.0m
    passed = result["risk_level"] == "BLOCKED" and result["score"] == 0.0
    log("TEST A4 -- Vessel taller than bridge: BLOCKED score=0",
        passed, f"risk={result['risk_level']} margin={result['clearance_margin_m']}")
    return passed


def test_A5_safe_score_is_highest():
    """SAFE risk produces highest score."""
    safe = assess_bridge_clearance("B", 20.0, "Class-I", [82.9739, 25.3176])
    blocked = assess_bridge_clearance("B", 3.0, "Class-V", [82.9739, 25.3176])
    passed = safe["score"] > blocked["score"]
    log("TEST A5 -- SAFE score > BLOCKED score",
        passed, f"safe={safe['score']} blocked={blocked['score']}")
    return passed


def test_A6_proposal_not_empty():
    """Every bridge result has a non-empty proposal."""
    for vessel in ["Class-I", "Class-III", "Class-V"]:
        result = assess_bridge_clearance(
            "Test", 8.0, vessel, [82.9739, 25.3176]
        )
        if not result.get("proposal"):
            log("TEST A6 -- All bridge results have proposals", False,
                f"Empty proposal for {vessel}")
            return False
    log("TEST A6 -- All bridge results have non-empty proposals", True)
    return True


# Block B -- Vessel class profiles
def test_B1_all_vessel_classes_have_heights():
    """All vessel classes have height profiles defined."""
    classes = ["Class-I", "Class-II", "Class-III", "Class-IV",
               "Class-V", "Seaplane", "Barge", "Tug", "Ferry"]
    all_defined = all(c in VESSEL_CLASS_HEIGHTS for c in classes)
    log("TEST B1 -- All vessel classes have height profiles",
        all_defined,
        f"defined={list(VESSEL_CLASS_HEIGHTS.keys())}")
    return all_defined


def test_B2_all_vessel_classes_have_drafts():
    """All vessel classes have draft profiles defined."""
    classes = ["Class-I", "Class-II", "Class-III", "Class-IV",
               "Class-V", "Seaplane", "Barge", "Tug", "Ferry"]
    all_defined = all(c in VESSEL_CLASS_DRAFTS for c in classes)
    log("TEST B2 -- All vessel classes have draft profiles",
        all_defined)
    return all_defined


def test_B3_height_ordering():
    """Higher class vessels have greater heights."""
    h1 = VESSEL_CLASS_HEIGHTS["Class-I"]
    h3 = VESSEL_CLASS_HEIGHTS["Class-III"]
    h5 = VESSEL_CLASS_HEIGHTS["Class-V"]
    passed = h1 < h3 < h5
    log("TEST B3 -- Vessel height ordering: Class-I < Class-III < Class-V",
        passed,
        f"I={h1} III={h3} V={h5}")
    return passed


def test_B4_seaplane_low_height():
    """Seaplane has lower height than Class-III vessel."""
    passed = VESSEL_CLASS_HEIGHTS["Seaplane"] < VESSEL_CLASS_HEIGHTS["Class-III"]
    log("TEST B4 -- Seaplane height < Class-III height",
        passed,
        f"seaplane={VESSEL_CLASS_HEIGHTS['Seaplane']} "
        f"class3={VESSEL_CLASS_HEIGHTS['Class-III']}")
    return passed


# Block C -- Barrage passage
def test_C1_operational_lock_passable():
    """Operational lock with compatible dimensions: interruption=NONE."""
    result = assess_barrage_passage(
        barrage_id="farakka_barrage",
        vessel_class="Class-III",
        geo_coordinates=[87.9186, 24.8119]
    )
    passed = result["interruption_level"] == "NONE" and result["score"] > 0
    log("TEST C1 -- Farakka operational lock: interruption=NONE",
        passed,
        f"interruption={result['interruption_level']} score={result['score']}")
    return passed


def test_C2_no_lock_total_interruption():
    """Barrage with no lock: interruption=TOTAL."""
    result = assess_barrage_passage(
        barrage_id="bansagar_barrage",
        vessel_class="Class-III",
        geo_coordinates=[81.2833, 24.1833]
    )
    passed = result["interruption_level"] == "TOTAL" and result["score"] == 0.0
    log("TEST C2 -- Bansagar no lock: interruption=TOTAL score=0",
        passed,
        f"interruption={result['interruption_level']} score={result['score']}")
    return passed


def test_C3_under_repair_severe():
    """Lock under repair: interruption=SEVERE."""
    result = assess_barrage_passage(
        barrage_id="test_barrage",
        vessel_class="Class-II",
        geo_coordinates=[82.9739, 25.3176],
        lock_status="UNDER_REPAIR",
        lock_width_m=15.0,
        lock_length_m=80.0
    )
    passed = result["interruption_level"] == "SEVERE"
    log("TEST C3 -- Under repair lock: interruption=SEVERE",
        passed,
        f"interruption={result['interruption_level']}")
    return passed


def test_C4_seasonal_lock_moderate():
    """Seasonal lock: interruption=MODERATE."""
    result = assess_barrage_passage(
        barrage_id="test_barrage",
        vessel_class="Class-II",
        geo_coordinates=[82.9739, 25.3176],
        lock_status="SEASONAL",
        lock_width_m=15.0,
        lock_length_m=80.0
    )
    passed = result["interruption_level"] == "MODERATE"
    log("TEST C4 -- Seasonal lock: interruption=MODERATE",
        passed,
        f"interruption={result['interruption_level']}")
    return passed


def test_C5_decommissioned_total():
    """Decommissioned lock: interruption=TOTAL."""
    result = assess_barrage_passage(
        barrage_id="test_barrage",
        vessel_class="Class-I",
        geo_coordinates=[82.9739, 25.3176],
        lock_status="DECOMMISSIONED"
    )
    passed = result["interruption_level"] == "TOTAL" and result["score"] == 0.0
    log("TEST C5 -- Decommissioned lock: interruption=TOTAL",
        passed,
        f"interruption={result['interruption_level']}")
    return passed


def test_C6_proposal_not_empty():
    """Every barrage result has a non-empty proposal."""
    result = assess_barrage_passage(
        "farakka_barrage", "Class-III", [87.9186, 24.8119]
    )
    passed = bool(result.get("proposal"))
    log("TEST C6 -- Barrage result has non-empty proposal",
        passed,
        f"proposal={result.get('proposal','')[:60]}")
    return passed


# Block D -- Seaplane obstruction
def test_D1_seaplane_critical_risk_flagged():
    """Seaplane with critically low clearance flags seaplane_risk."""
    result = assess_bridge_clearance(
        bridge_name="Low Bridge",
        air_clearance_m=4.5,
        vessel_class="Seaplane",
        geo_coordinates=[82.9739, 25.3176]
    )
    # Seaplane height=4.0m, clearance=4.5m, margin=0.5m (CRITICAL)
    passed = result["seaplane_risk"] is True
    log("TEST D1 -- Seaplane critical clearance: seaplane_risk=True",
        passed,
        f"seaplane_risk={result['seaplane_risk']} "
        f"risk_level={result['risk_level']}")
    return passed


def test_D2_seaplane_safe_no_risk():
    """Seaplane with large clearance: seaplane_risk=False."""
    result = assess_bridge_clearance(
        bridge_name="High Bridge",
        air_clearance_m=20.0,
        vessel_class="Seaplane",
        geo_coordinates=[82.9739, 25.3176]
    )
    passed = result["seaplane_risk"] is False
    log("TEST D2 -- Seaplane safe clearance: seaplane_risk=False",
        passed,
        f"seaplane_risk={result['seaplane_risk']}")
    return passed


def test_D3_non_seaplane_no_seaplane_risk():
    """Non-seaplane vessel never flags seaplane_risk."""
    result = assess_bridge_clearance(
        bridge_name="Malviya Bridge",
        air_clearance_m=8.5,
        vessel_class="Class-III",
        geo_coordinates=[82.9739, 25.3176]
    )
    passed = result["seaplane_risk"] is False
    log("TEST D3 -- Non-seaplane vessel: seaplane_risk always False",
        passed,
        f"seaplane_risk={result['seaplane_risk']}")
    return passed


# Block E -- Corridor scoring
def test_E1_corridor_score_is_minimum_of_constraints():
    """Corridor composite score equals minimum of all constraint scores."""
    result = score_corridor_constraints(
        corridor_id="TEST_CORRIDOR",
        bridges=[
            {"bridge_name": "Bridge A", "air_clearance_m": 8.5,
             "geo_coordinates": [82.9739, 25.3176]},
        ],
        barrages=[
            {"barrage_id": "farakka_barrage",
             "geo_coordinates": [87.9186, 24.8119]}
        ],
        vessel_class="Class-III"
    )
    bridge_score = result["bridge_results"][0]["score"]
    barrage_score = result["barrage_results"][0]["score"]
    expected_min = min(bridge_score, barrage_score)
    passed = result["composite_constraint_score"] == expected_min
    log("TEST E1 -- Corridor score = minimum of bridge and barrage scores",
        passed,
        f"bridge={bridge_score} barrage={barrage_score} "
        f"composite={result['composite_constraint_score']}")
    return passed


def test_E2_corridor_with_no_constraints():
    """Corridor with no bridges or barrages: score=100."""
    result = score_corridor_constraints(
        corridor_id="EMPTY_CORRIDOR",
        bridges=[],
        barrages=[],
        vessel_class="Class-I"
    )
    passed = result["composite_constraint_score"] == 100.0
    log("TEST E2 -- Empty corridor (no constraints): score=100",
        passed,
        f"score={result['composite_constraint_score']}")
    return passed


def test_E3_blocked_corridor_not_passable():
    """Corridor with BLOCKED bridge: corridor_passable=False."""
    result = score_corridor_constraints(
        corridor_id="BLOCKED_CORRIDOR",
        bridges=[
            {"bridge_name": "Very Low Bridge", "air_clearance_m": 2.0,
             "geo_coordinates": [82.9739, 25.3176]},
        ],
        barrages=[],
        vessel_class="Class-V"
    )
    passed = result["corridor_passable"] is False
    log("TEST E3 -- BLOCKED bridge: corridor_passable=False",
        passed,
        f"passable={result['corridor_passable']} "
        f"score={result['composite_constraint_score']}")
    return passed


def test_E4_corridor_proposals_match_count():
    """Proposals list matches total bridge + barrage count."""
    result = score_corridor_constraints(
        corridor_id="TEST_CORRIDOR",
        bridges=[
            {"bridge_name": "B1", "air_clearance_m": 12.0,
             "geo_coordinates": [82.9739, 25.3176]},
            {"bridge_name": "B2", "air_clearance_m": 8.5,
             "geo_coordinates": [83.0, 25.4]}
        ],
        barrages=[
            {"barrage_id": "farakka_barrage",
             "geo_coordinates": [87.9186, 24.8119]}
        ],
        vessel_class="Class-III"
    )
    passed = len(result["proposals"]) == 3
    log("TEST E4 -- Proposals list matches bridge + barrage count",
        passed,
        f"proposals={len(result['proposals'])} expected=3")
    return passed


# Block F -- Reference data integrity
def test_F1_farakka_has_operational_lock():
    """Farakka Barrage reference data has OPERATIONAL lock."""
    passed = GANGA_BARRAGES["farakka_barrage"]["lock_status"] == "OPERATIONAL"
    log("TEST F1 -- Farakka Barrage: lock_status=OPERATIONAL",
        passed,
        f"lock_status={GANGA_BARRAGES['farakka_barrage']['lock_status']}")
    return passed


def test_F2_bansagar_has_no_lock():
    """Bansagar Barrage has no navigational lock."""
    passed = GANGA_BARRAGES["bansagar_barrage"]["lock_status"] == "NONE"
    log("TEST F2 -- Bansagar Barrage: lock_status=NONE (no lock)",
        passed)
    return passed


def test_F3_all_barrages_have_coordinates():
    """All barrage reference entries have valid coordinates."""
    all_valid = all(
        len(b["geo_coordinates"]) == 2
        for b in GANGA_BARRAGES.values()
    )
    log("TEST F3 -- All barrages have coordinate pairs",
        all_valid)
    return all_valid


def test_F4_all_bridges_have_clearance():
    """All bridge reference entries have positive air clearance."""
    all_valid = all(
        b["air_clearance_m"] > 0
        for b in GANGA_BRIDGES.values()
    )
    log("TEST F4 -- All bridges have positive air clearance",
        all_valid)
    return all_valid


# Block G -- Signal output
def test_G1_bridge_result_has_valid_signal():
    """Bridge clearance result produces valid marine schema signal."""
    result = assess_bridge_clearance(
        "Malviya Bridge", 8.5, "Class-III", [82.9739, 25.3176]
    )
    is_valid, errors = check_schema(result["signal"])
    passed = is_valid and errors == []
    log("TEST G1 -- Bridge result signal passes marine schema",
        passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_G2_barrage_result_has_valid_signal():
    """Barrage passage result produces valid marine schema signal."""
    result = assess_barrage_passage(
        "farakka_barrage", "Class-III", [87.9186, 24.8119]
    )
    is_valid, errors = check_schema(result["signal"])
    passed = is_valid and errors == []
    log("TEST G2 -- Barrage result signal passes marine schema",
        passed,
        f"is_valid={is_valid} errors={errors}")
    return passed


def test_G3_bridge_signal_type_correct():
    """Bridge signal has signal_type=bridge_clearance."""
    result = assess_bridge_clearance(
        "Test", 10.0, "Class-I", [82.9739, 25.3176]
    )
    passed = result["signal"]["signal_type"] == "bridge_clearance"
    log("TEST G3 -- Bridge signal_type=bridge_clearance",
        passed,
        f"signal_type={result['signal']['signal_type']}")
    return passed


def test_G4_barrage_signal_type_correct():
    """Barrage signal has signal_type=barrage_interruption."""
    result = assess_barrage_passage(
        "farakka_barrage", "Class-I", [87.9186, 24.8119]
    )
    passed = result["signal"]["signal_type"] == "barrage_interruption"
    log("TEST G4 -- Barrage signal_type=barrage_interruption",
        passed,
        f"signal_type={result['signal']['signal_type']}")
    return passed


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Bridge and Barrage Constraint Test Suite")
    print("=" * 60)

    tests = [
        test_A1_safe_clearance,
        test_A2_marginal_clearance,
        test_A3_critical_clearance,
        test_A4_blocked_clearance,
        test_A5_safe_score_is_highest,
        test_A6_proposal_not_empty,
        test_B1_all_vessel_classes_have_heights,
        test_B2_all_vessel_classes_have_drafts,
        test_B3_height_ordering,
        test_B4_seaplane_low_height,
        test_C1_operational_lock_passable,
        test_C2_no_lock_total_interruption,
        test_C3_under_repair_severe,
        test_C4_seasonal_lock_moderate,
        test_C5_decommissioned_total,
        test_C6_proposal_not_empty,
        test_D1_seaplane_critical_risk_flagged,
        test_D2_seaplane_safe_no_risk,
        test_D3_non_seaplane_no_seaplane_risk,
        test_E1_corridor_score_is_minimum_of_constraints,
        test_E2_corridor_with_no_constraints,
        test_E3_blocked_corridor_not_passable,
        test_E4_corridor_proposals_match_count,
        test_F1_farakka_has_operational_lock,
        test_F2_bansagar_has_no_lock,
        test_F3_all_barrages_have_coordinates,
        test_F4_all_bridges_have_clearance,
        test_G1_bridge_result_has_valid_signal,
        test_G2_barrage_result_has_valid_signal,
        test_G3_bridge_signal_type_correct,
        test_G4_barrage_signal_type_correct,
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