"""
test_proposal_engine.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- Proposal Engine

Tests:
  A. build_proposal -- core structure and required fields
  B. propose_navigability -- all viable/non-viable cases
  C. propose_bridge_clearance -- all risk levels
  D. propose_ecological_status -- all stress levels
  E. propose_infrastructure_readiness -- all score ranges
  F. propose_seaplane_feasibility -- all combinations
  G. generate_location_proposals -- multi-layer output
  H. Provenance and determinism
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from proposal_engine import (
    build_proposal, propose_navigability, propose_bridge_clearance,
    propose_ecological_status, propose_infrastructure_readiness,
    propose_seaplane_feasibility, generate_location_proposals,
    PROPOSAL_TYPE_NAVIGABILITY, PROPOSAL_TYPE_CONSTRAINT,
    PROPOSAL_TYPE_ECOLOGICAL, PROPOSAL_TYPE_INFRASTRUCTURE,
    PROPOSAL_TYPE_CONNECTIVITY,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW,
    PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW
)

PASS = "  PASS"
FAIL = "  FAIL"
results_log = []
COORDS = [85.1376, 25.5941]


def log(name, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"{status}  {name}"
    if detail:
        msg += f"\n         -> {detail}"
    print(msg)
    results_log.append((name, passed))


# Block A -- build_proposal core structure
def test_A1_required_fields_present():
    """build_proposal produces all required fields."""
    p = build_proposal(
        proposal_type=PROPOSAL_TYPE_NAVIGABILITY,
        subject="TEST",
        proposal_text="Test proposal",
        confidence=0.9,
        score=80.0,
        source_ids=["SRC_v1"],
        contributing_signals=["depth"],
        reasoning="Test reasoning",
        geo_coordinates=COORDS
    )
    required = [
        "proposal_type", "subject", "proposal_text", "confidence",
        "confidence_label", "score", "priority", "source_ids",
        "contributing_signals", "reasoning", "geo_coordinates",
        "conditions", "provenance", "metadata"
    ]
    missing = [f for f in required if f not in p]
    passed = len(missing) == 0
    log("TEST A1 -- build_proposal: all required fields present",
        passed, f"missing={missing}")
    return passed


def test_A2_provenance_deterministic_true():
    """All proposals have deterministic=True and ml_used=False."""
    p = build_proposal(
        PROPOSAL_TYPE_NAVIGABILITY, "T", "T", 0.9, 80.0,
        ["S"], ["d"], "R", COORDS
    )
    passed = (p["provenance"]["deterministic"] is True and
              p["provenance"]["ml_used"] is False)
    log("TEST A2 -- Provenance: deterministic=True ml_used=False",
        passed,
        f"deterministic={p['provenance']['deterministic']} "
        f"ml_used={p['provenance']['ml_used']}")
    return passed


def test_A3_confidence_label_high():
    """Confidence >= 0.80 gets label HIGH."""
    p = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                       0.85, 80.0, ["S"], ["d"], "R", COORDS)
    passed = p["confidence_label"] == CONFIDENCE_HIGH
    log("TEST A3 -- Confidence 0.85: label=HIGH",
        passed, f"label={p['confidence_label']}")
    return passed


def test_A4_confidence_label_medium():
    """Confidence 0.55-0.79 gets label MEDIUM."""
    p = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                       0.65, 80.0, ["S"], ["d"], "R", COORDS)
    passed = p["confidence_label"] == CONFIDENCE_MEDIUM
    log("TEST A4 -- Confidence 0.65: label=MEDIUM",
        passed, f"label={p['confidence_label']}")
    return passed


def test_A5_confidence_clamped():
    """Confidence is clamped to [0.0, 1.0]."""
    p = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                       1.5, 80.0, ["S"], ["d"], "R", COORDS)
    passed = p["confidence"] == 1.0
    log("TEST A5 -- Confidence clamped to 1.0 when > 1.0",
        passed, f"confidence={p['confidence']}")
    return passed


def test_A6_score_clamped():
    """Score is clamped to [0.0, 100.0]."""
    p = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                       0.9, 150.0, ["S"], ["d"], "R", COORDS)
    passed = p["score"] == 100.0
    log("TEST A6 -- Score clamped to 100.0 when > 100",
        passed, f"score={p['score']}")
    return passed


def test_A7_priority_from_score():
    """Priority is derived from score when not explicitly set."""
    p_high = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                            0.9, 80.0, ["S"], ["d"], "R", COORDS)
    p_crit = build_proposal(PROPOSAL_TYPE_NAVIGABILITY, "T", "T",
                            0.9, 10.0, ["S"], ["d"], "R", COORDS)
    passed = (p_high["priority"] == PRIORITY_HIGH and
              p_crit["priority"] == PRIORITY_CRITICAL)
    log("TEST A7 -- Priority derived from score correctly",
        passed,
        f"score=80->priority={p_high['priority']} "
        f"score=10->priority={p_crit['priority']}")
    return passed


# Block B -- propose_navigability
def test_B1_viable_proposal_contains_suitable():
    """Viable navigability proposal contains 'suitable'."""
    p = propose_navigability(
        "SEG_001", "NW1", "Class-III", "November",
        80.5, 4.2, 0.85, COORDS, "LOW"
    )
    passed = "suitable" in p["proposal_text"].lower()
    log("TEST B1 -- Viable navigability: proposal contains 'suitable'",
        passed)
    return passed


def test_B2_non_viable_proposal_contains_not_suitable():
    """Non-viable navigability proposal contains 'NOT suitable'."""
    p = propose_navigability(
        "SEG_001", "NW1", "Class-III", "July",
        15.0, 0.5, 0.3, COORDS, "HIGH"
    )
    passed = "NOT suitable" in p["proposal_text"]
    log("TEST B2 -- Non-viable navigability: proposal contains 'NOT suitable'",
        passed)
    return passed


def test_B3_navigability_type_correct():
    """Navigability proposal has correct type."""
    p = propose_navigability(
        "SEG_001", "NW1", "Class-III", "November",
        80.5, 4.2, 0.85, COORDS, "LOW"
    )
    passed = p["proposal_type"] == PROPOSAL_TYPE_NAVIGABILITY
    log("TEST B3 -- Navigability proposal type correct",
        passed, f"type={p['proposal_type']}")
    return passed


def test_B4_non_viable_has_conditions():
    """Non-viable navigability proposal has conditions listed."""
    p = propose_navigability(
        "SEG_001", "NW1", "Class-V", "July",
        10.0, 0.3, 0.3, COORDS, "HIGH"
    )
    passed = len(p["conditions"]) > 0
    log("TEST B4 -- Non-viable navigability has conditions",
        passed, f"conditions={p['conditions']}")
    return passed


# Block C -- propose_bridge_clearance
def test_C1_safe_bridge_no_conditions():
    """SAFE bridge clearance has no conditions."""
    p = propose_bridge_clearance(
        "High Bridge", "Class-III", 15.5, "SAFE", 95.0, COORDS
    )
    passed = len(p["conditions"]) == 0
    log("TEST C1 -- SAFE bridge: no conditions",
        passed)
    return passed


def test_C2_blocked_bridge_has_conditions():
    """BLOCKED bridge has conditions listed."""
    p = propose_bridge_clearance(
        "Low Bridge", "Class-V", -5.0, "BLOCKED", 0.0, COORDS
    )
    passed = len(p["conditions"]) > 0
    log("TEST C2 -- BLOCKED bridge: conditions listed",
        passed, f"conditions={p['conditions']}")
    return passed


def test_C3_critical_bridge_proposal_mentions_risk():
    """CRITICAL bridge proposal mentions risk."""
    p = propose_bridge_clearance(
        "Malviya Bridge", "Class-III", 4.0, "CRITICAL", 20.0, COORDS
    )
    passed = ("CRITICAL" in p["proposal_text"] or
              "risk" in p["proposal_text"].lower())
    log("TEST C3 -- CRITICAL bridge: proposal mentions risk",
        passed)
    return passed


def test_C4_bridge_type_is_constraint():
    """Bridge clearance proposal has CONSTRAINT type."""
    p = propose_bridge_clearance(
        "Test", "Class-I", 10.0, "SAFE", 95.0, COORDS
    )
    passed = p["proposal_type"] == PROPOSAL_TYPE_CONSTRAINT
    log("TEST C4 -- Bridge proposal type=CONSTRAINT",
        passed, f"type={p['proposal_type']}")
    return passed


# Block D -- propose_ecological_status
def test_D1_critical_stress_priority_critical():
    """CRITICAL ecological stress gets CRITICAL priority."""
    p = propose_ecological_status(
        "kanpur", "CRITICAL", "CRITICAL", 0.93,
        "CRITICAL signal", "flow signal", 0.8, COORDS
    )
    passed = p["priority"] == PRIORITY_CRITICAL
    log("TEST D1 -- CRITICAL stress: priority=CRITICAL",
        passed, f"priority={p['priority']}")
    return passed


def test_D2_critical_has_intervention_condition():
    """CRITICAL ecological proposal mentions Namami Gange."""
    p = propose_ecological_status(
        "kanpur", "CRITICAL", "CRITICAL", 0.93,
        "CRITICAL signal", "flow signal", 0.8, COORDS
    )
    passed = any("Namami Gange" in c for c in p["conditions"])
    log("TEST D2 -- CRITICAL ecological: Namami Gange in conditions",
        passed, f"conditions={p['conditions']}")
    return passed


def test_D3_low_stress_no_conditions():
    """LOW ecological stress has no conditions."""
    p = propose_ecological_status(
        "patna", "LOW", "GOOD", 75.0,
        "Nirmal ok", "Aviral ok", 0.9, COORDS
    )
    passed = len(p["conditions"]) == 0
    log("TEST D3 -- LOW stress: no conditions",
        passed)
    return passed


def test_D4_ecological_type_correct():
    """Ecological proposal has ECOLOGICAL type."""
    p = propose_ecological_status(
        "test", "LOW", "GOOD", 75.0, "N", "A", 0.9, COORDS
    )
    passed = p["proposal_type"] == PROPOSAL_TYPE_ECOLOGICAL
    log("TEST D4 -- Ecological proposal type=ECOLOGICAL",
        passed)
    return passed


# Block E -- propose_infrastructure_readiness
def test_E1_multimodal_high_score_priority():
    """Multimodal + high score gets HIGH priority."""
    p = propose_infrastructure_readiness(
        "PATNA_PORT", "major_port", 100.0, True, "OPERATIONAL", COORDS
    )
    passed = p["priority"] in (PRIORITY_HIGH, "HIGH")
    log("TEST E1 -- Multimodal + score=100: HIGH priority",
        passed, f"priority={p['priority']}")
    return passed


def test_E2_low_score_not_viable_text():
    """Low score produces NOT VIABLE text."""
    p = propose_infrastructure_readiness(
        "TEST_NODE", "candidate_location_108", 15.0,
        False, "CANDIDATE", COORDS
    )
    passed = "NOT VIABLE" in p["proposal_text"]
    log("TEST E2 -- Score=15: proposal contains NOT VIABLE",
        passed)
    return passed


def test_E3_infrastructure_type_correct():
    """Infrastructure proposal has INFRASTRUCTURE type."""
    p = propose_infrastructure_readiness(
        "TEST", "major_port", 80.0, True, "OPERATIONAL", COORDS
    )
    passed = p["proposal_type"] == PROPOSAL_TYPE_INFRASTRUCTURE
    log("TEST E3 -- Infrastructure proposal type correct",
        passed)
    return passed


# Block F -- propose_seaplane_feasibility
def test_F1_all_clear_full_feasibility():
    """All conditions met: full feasibility."""
    p = propose_seaplane_feasibility(
        "varanasi", 3.5, "MODERATE", False, True, True, COORDS
    )
    passed = "FEASIBLE" in p["proposal_text"] and len(p["conditions"]) == 0
    log("TEST F1 -- All clear: seaplane FEASIBLE no conditions",
        passed, f"text excerpt={p['proposal_text'][:50]}")
    return passed


def test_F2_no_last_mile_conditional():
    """No last-mile: conditional feasibility."""
    p = propose_seaplane_feasibility(
        "varanasi", 3.5, "MODERATE", False, True, False, COORDS
    )
    passed = ("conditional" in p["proposal_text"].lower() and
              len(p["conditions"]) > 0)
    log("TEST F2 -- No last-mile: conditional feasibility",
        passed)
    return passed


def test_F3_bridge_obstruction_blocks():
    """Bridge obstruction makes seaplane not feasible."""
    p = propose_seaplane_feasibility(
        "varanasi", 3.5, "MODERATE", True, True, True, COORDS
    )
    passed = "NOT feasible" in p["proposal_text"]
    log("TEST F3 -- Bridge obstruction: NOT feasible",
        passed)
    return passed


def test_F4_low_depth_blocks():
    """Insufficient depth blocks seaplane."""
    p = propose_seaplane_feasibility(
        "site", 0.3, "CLEAR", False, True, True, COORDS
    )
    passed = "NOT feasible" in p["proposal_text"]
    log("TEST F4 -- Low depth: seaplane NOT feasible",
        passed)
    return passed


def test_F5_seaplane_type_connectivity():
    """Seaplane proposal has CONNECTIVITY type."""
    p = propose_seaplane_feasibility(
        "test", 3.5, "MODERATE", False, True, True, COORDS
    )
    passed = p["proposal_type"] == PROPOSAL_TYPE_CONNECTIVITY
    log("TEST F5 -- Seaplane proposal type=CONNECTIVITY",
        passed)
    return passed


# Block G -- generate_location_proposals
def test_G1_returns_list():
    """generate_location_proposals returns a list."""
    proposals = generate_location_proposals(
        "patna_river_port", COORDS
    )
    passed = isinstance(proposals, list)
    log("TEST G1 -- generate_location_proposals returns list",
        passed)
    return passed


def test_G2_with_navigability_result():
    """Navigability result generates navigability proposal."""
    nav_result = {
        "waterway_id": "NW1",
        "vessel_class": "Class-III",
        "month_name": "November",
        "composite_navigability_score": 80.5,
        "depth_assessment": {"depth_m": 4.2},
        "navigability_confidence": 0.85,
        "seasonal_assessment": {"risk_level": "LOW"}
    }
    proposals = generate_location_proposals(
        "patna", COORDS, navigability_result=nav_result
    )
    types = [p["proposal_type"] for p in proposals]
    passed = PROPOSAL_TYPE_NAVIGABILITY in types
    log("TEST G2 -- Navigability result: NAVIGABILITY proposal generated",
        passed, f"types={types}")
    return passed


def test_G3_critical_sorted_first():
    """CRITICAL priority proposals sorted first."""
    nav_result = {
        "waterway_id": "NW1",
        "vessel_class": "Class-III",
        "month_name": "November",
        "composite_navigability_score": 80.5,
        "depth_assessment": {"depth_m": 4.2},
        "navigability_confidence": 0.85,
        "seasonal_assessment": {"risk_level": "LOW"}
    }
    eco_result = {
        "stress_assessment": {"stress_level": "CRITICAL"},
        "pollution_assessment": {
            "pollution_class": "CRITICAL",
            "nirmal_signal": "CRITICAL signal",
            "aviral_signal": "flow signal"
        },
        "composite_ecological_score": 0.93,
        "confidence": 0.8
    }
    proposals = generate_location_proposals(
        "kanpur", COORDS,
        navigability_result=nav_result,
        ecological_result=eco_result
    )
    if not proposals:
        log("TEST G3 -- CRITICAL sorted first", False, "No proposals")
        return False
    passed = proposals[0]["priority"] == PRIORITY_CRITICAL
    log("TEST G3 -- CRITICAL priority proposal sorted first",
        passed,
        f"first_priority={proposals[0]['priority']}")
    return passed


def test_G4_empty_input_returns_empty():
    """No results provided: returns empty list."""
    proposals = generate_location_proposals("test", COORDS)
    passed = proposals == []
    log("TEST G4 -- No results provided: empty list returned",
        passed)
    return passed


# Block H -- Provenance and determinism
def test_H1_same_input_same_proposal():
    """Same input produces identical proposal text (determinism)."""
    kwargs = dict(
        segment_id="SEG_001", waterway_id="NW1",
        vessel_class="Class-III", month_name="November",
        composite_score=80.5, depth_m=4.2,
        confidence=0.85, geo_coordinates=COORDS, seasonal_risk="LOW"
    )
    p1 = propose_navigability(**kwargs)
    p2 = propose_navigability(**kwargs)
    passed = p1["proposal_text"] == p2["proposal_text"]
    log("TEST H1 -- Determinism: same input same proposal text",
        passed)
    return passed


def test_H2_all_proposals_have_source_ids():
    """All proposal types have non-empty source_ids."""
    proposals = [
        propose_navigability("S", "NW1", "Class-III", "Nov",
                             80.0, 4.0, 0.85, COORDS, "LOW"),
        propose_bridge_clearance("B", "Class-III", 5.0, "SAFE", 95.0, COORDS),
        propose_ecological_status("L", "LOW", "GOOD", 75.0, "N", "A", 0.9, COORDS),
        propose_infrastructure_readiness("N", "major_port", 80.0, True, "OPERATIONAL", COORDS),
        propose_seaplane_feasibility("S", 3.5, "MODERATE", False, True, True, COORDS)
    ]
    all_have = all(len(p["source_ids"]) > 0 for p in proposals)
    log("TEST H2 -- All proposal types have source_ids",
        all_have)
    return all_have


def test_H3_all_proposals_have_contributing_signals():
    """All proposal types have contributing_signals listed."""
    proposals = [
        propose_navigability("S", "NW1", "Class-III", "Nov",
                             80.0, 4.0, 0.85, COORDS, "LOW"),
        propose_bridge_clearance("B", "Class-III", 5.0, "SAFE", 95.0, COORDS),
        propose_ecological_status("L", "LOW", "GOOD", 75.0, "N", "A", 0.9, COORDS),
    ]
    all_have = all(len(p["contributing_signals"]) > 0 for p in proposals)
    log("TEST H3 -- All proposals have contributing_signals",
        all_have)
    return all_have


def test_H4_signal_count_in_provenance():
    """Provenance signal_count matches contributing_signals length."""
    p = propose_navigability(
        "S", "NW1", "Class-III", "Nov", 80.0, 4.0, 0.85, COORDS, "LOW"
    )
    passed = (p["provenance"]["signal_count"] ==
              len(p["contributing_signals"]))
    log("TEST H4 -- Provenance signal_count matches contributing_signals",
        passed,
        f"provenance={p['provenance']['signal_count']} "
        f"list={len(p['contributing_signals'])}")
    return passed


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Proposal Engine Test Suite")
    print("=" * 60)

    tests = [
        test_A1_required_fields_present,
        test_A2_provenance_deterministic_true,
        test_A3_confidence_label_high,
        test_A4_confidence_label_medium,
        test_A5_confidence_clamped,
        test_A6_score_clamped,
        test_A7_priority_from_score,
        test_B1_viable_proposal_contains_suitable,
        test_B2_non_viable_proposal_contains_not_suitable,
        test_B3_navigability_type_correct,
        test_B4_non_viable_has_conditions,
        test_C1_safe_bridge_no_conditions,
        test_C2_blocked_bridge_has_conditions,
        test_C3_critical_bridge_proposal_mentions_risk,
        test_C4_bridge_type_is_constraint,
        test_D1_critical_stress_priority_critical,
        test_D2_critical_has_intervention_condition,
        test_D3_low_stress_no_conditions,
        test_D4_ecological_type_correct,
        test_E1_multimodal_high_score_priority,
        test_E2_low_score_not_viable_text,
        test_E3_infrastructure_type_correct,
        test_F1_all_clear_full_feasibility,
        test_F2_no_last_mile_conditional,
        test_F3_bridge_obstruction_blocks,
        test_F4_low_depth_blocks,
        test_F5_seaplane_type_connectivity,
        test_G1_returns_list,
        test_G2_with_navigability_result,
        test_G3_critical_sorted_first,
        test_G4_empty_input_returns_empty,
        test_H1_same_input_same_proposal,
        test_H2_all_proposals_have_source_ids,
        test_H3_all_proposals_have_contributing_signals,
        test_H4_signal_count_in_provenance,
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