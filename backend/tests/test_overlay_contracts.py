"""
test_overlay_contracts.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Test Suite -- Infrastructure Overlay and GIS Layer Contracts

Tests:
  A. Infrastructure node scoring -- all status types
  B. CEZ cluster scoring
  C. MMLP cluster scoring
  D. Candidate locations scaffold
  E. Infrastructure overlay GeoJSON output
  F. GIS engine -- all 5 layers
  G. GIS layer contract validation
  H. Ecological layer scoring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure_overlay import (
    score_infrastructure_node, score_cez_cluster,
    score_mmlp_cluster, get_candidate_locations,
    build_infrastructure_overlay,
    STATUS_OPERATIONAL, STATUS_UNDER_DEVELOPMENT,
    STATUS_PROPOSED, STATUS_DPR_STAGE, STATUS_CANDIDATE,
    CANDIDATE_LOCATIONS_108, CEZ_VIABLE_SCORE, MMLP_VIABLE_SCORE
)
from gis_engine import (
    build_physical_layer, build_ecological_layer,
    build_economic_layer, build_policy_layer,
    build_infrastructure_layer, build_all_layers,
    get_layer_summary, VALID_LAYERS,
    LAYER_PHYSICAL, LAYER_ECOLOGICAL, LAYER_ECONOMIC,
    LAYER_POLICY, LAYER_INFRASTRUCTURE
)
from ecological_layer import score_ecological_integrity
from river_flow_layer import score_river_segment
from marine_schema import check_schema

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


# Block A -- Infrastructure node scoring
def test_A1_operational_multimodal_score_100():
    """Operational + all 3 connectivity: score=100."""
    result = score_infrastructure_node(
        "TEST_001", "major_port", COORDS,
        STATUS_OPERATIONAL, True, True, True
    )
    passed = result["composite_score"] == 100.0 and result["multimodal"] is True
    log("TEST A1 -- Operational + multimodal: score=100 multimodal=True",
        passed,
        f"score={result['composite_score']} multimodal={result['multimodal']}")
    return passed


def test_A2_candidate_no_connectivity_low_score():
    """Candidate status + no connectivity: low score."""
    result = score_infrastructure_node(
        "TEST_002", "candidate_location_108", COORDS,
        STATUS_CANDIDATE, False, False, False
    )
    passed = result["composite_score"] < 20.0
    log("TEST A2 -- Candidate + no connectivity: score < 20",
        passed, f"score={result['composite_score']}")
    return passed


def test_A3_all_status_types_produce_scores():
    """All status types produce valid scores."""
    statuses = [STATUS_OPERATIONAL, STATUS_UNDER_DEVELOPMENT,
                STATUS_PROPOSED, STATUS_DPR_STAGE, STATUS_CANDIDATE]
    all_valid = True
    for s in statuses:
        result = score_infrastructure_node(
            "T", "major_port", COORDS, s, True, False, True
        )
        if not (0.0 <= result["composite_score"] <= 100.0):
            all_valid = False
    log("TEST A3 -- All status types produce valid scores",
        all_valid,
        f"statuses tested={len(statuses)}")
    return all_valid


def test_A4_multimodal_requires_all_three():
    """Multimodal=True only when all 3 connectivity types present."""
    full = score_infrastructure_node(
        "T", "major_port", COORDS, STATUS_OPERATIONAL,
        True, True, True
    )
    partial = score_infrastructure_node(
        "T", "major_port", COORDS, STATUS_OPERATIONAL,
        True, True, False
    )
    passed = full["multimodal"] is True and partial["multimodal"] is False
    log("TEST A4 -- Multimodal requires all 3 connectivity types",
        passed,
        f"full_multimodal={full['multimodal']} "
        f"partial_multimodal={partial['multimodal']}")
    return passed


def test_A5_node_has_valid_signal():
    """Infrastructure node produces valid marine schema signal."""
    result = score_infrastructure_node(
        "PATNA_001", "major_port", COORDS,
        STATUS_OPERATIONAL, True, True, True
    )
    is_valid, errors = check_schema(result["signal"])
    passed = is_valid and errors == []
    log("TEST A5 -- Infrastructure node signal passes marine schema",
        passed, f"is_valid={is_valid} errors={errors}")
    return passed


def test_A6_proposal_not_empty():
    """All infrastructure nodes have non-empty proposals."""
    for status in [STATUS_OPERATIONAL, STATUS_PROPOSED, STATUS_CANDIDATE]:
        result = score_infrastructure_node(
            "T", "major_port", COORDS, status, True, False, True
        )
        if not result.get("proposal"):
            log("TEST A6 -- All nodes have proposals", False,
                f"Empty proposal for {status}")
            return False
    log("TEST A6 -- All infrastructure nodes have non-empty proposals", True)
    return True


# Block B -- CEZ cluster scoring
def test_B1_cez_viable_above_threshold():
    """CEZ with good scores is viable."""
    result = score_cez_cluster(
        "CEZ_001", COORDS, 25.0, 3.0, 70.0, 65.0, True
    )
    passed = result["viable"] is True and result["composite_score"] >= CEZ_VIABLE_SCORE
    log("TEST B1 -- CEZ viable: score >= threshold",
        passed,
        f"score={result['composite_score']} threshold={CEZ_VIABLE_SCORE}")
    return passed


def test_B2_cez_no_clearance_score_reduced():
    """CEZ without environmental clearance has reduced score."""
    with_clear = score_cez_cluster(
        "CEZ_002", COORDS, 25.0, 3.0, 70.0, 65.0, True
    )
    without_clear = score_cez_cluster(
        "CEZ_003", COORDS, 25.0, 3.0, 70.0, 65.0, False
    )
    passed = without_clear["composite_score"] < with_clear["composite_score"]
    log("TEST B2 -- CEZ no clearance: score reduced",
        passed,
        f"with={with_clear['composite_score']} "
        f"without={without_clear['composite_score']}")
    return passed


def test_B3_cez_no_clearance_proposal_mentions_clearance():
    """CEZ without clearance mentions clearance in proposal."""
    result = score_cez_cluster(
        "CEZ_004", COORDS, 25.0, 3.0, 70.0, 65.0, False
    )
    passed = "clearance" in result["proposal"].lower()
    log("TEST B3 -- CEZ no clearance: proposal mentions clearance",
        passed)
    return passed


def test_B4_cez_signal_valid():
    """CEZ cluster produces valid marine schema signal."""
    result = score_cez_cluster(
        "CEZ_005", COORDS, 25.0, 3.0, 70.0, 65.0, True
    )
    is_valid, errors = check_schema(result["signal"])
    passed = is_valid
    log("TEST B4 -- CEZ signal passes marine schema",
        passed, f"is_valid={is_valid}")
    return passed


# Block C -- MMLP cluster scoring
def test_C1_mmlp_multimodal_viable():
    """MMLP with full connectivity and large area is viable."""
    result = score_mmlp_cluster(
        "MMLP_001", COORDS, 500.0, True, True, True, 5.0,
        STATUS_OPERATIONAL
    )
    passed = result["viable"] is True and result["multimodal"] is True
    log("TEST C1 -- MMLP multimodal operational: viable=True",
        passed,
        f"viable={result['viable']} score={result['composite_score']}")
    return passed


def test_C2_mmlp_no_connectivity_not_viable():
    """MMLP with no connectivity: not viable."""
    result = score_mmlp_cluster(
        "MMLP_002", COORDS, 100.0, False, False, False, 50.0,
        STATUS_PROPOSED
    )
    passed = result["viable"] is False
    log("TEST C2 -- MMLP no connectivity proposed: not viable",
        passed, f"viable={result['viable']} score={result['composite_score']}")
    return passed


def test_C3_mmlp_signal_valid():
    """MMLP cluster produces valid marine schema signal."""
    result = score_mmlp_cluster(
        "MMLP_003", COORDS, 300.0, True, True, False, 10.0,
        STATUS_OPERATIONAL
    )
    is_valid, errors = check_schema(result["signal"])
    passed = is_valid
    log("TEST C3 -- MMLP signal passes marine schema",
        passed, f"is_valid={is_valid}")
    return passed


# Block D -- Candidate locations scaffold
def test_D1_scaffold_has_entries():
    """108 candidate locations scaffold has entries."""
    passed = len(CANDIDATE_LOCATIONS_108) > 0
    log("TEST D1 -- Candidate locations scaffold has entries",
        passed, f"count={len(CANDIDATE_LOCATIONS_108)}")
    return passed


def test_D2_all_candidates_have_required_fields():
    """All candidate locations have required fields."""
    required = ["candidate_id", "name", "geo_coordinates",
                "state", "waterway", "candidate_type", "priority"]
    all_valid = all(
        all(f in c for f in required)
        for c in CANDIDATE_LOCATIONS_108
    )
    log("TEST D2 -- All candidates have required fields",
        all_valid)
    return all_valid


def test_D3_filter_by_priority_high():
    """Filter by HIGH priority returns only HIGH entries."""
    results = get_candidate_locations(priority_filter="HIGH")
    passed = all(c["priority"] == "HIGH" for c in results)
    log("TEST D3 -- Priority filter HIGH: all returned are HIGH",
        passed,
        f"count={len(results)}")
    return passed


def test_D4_filter_by_type():
    """Filter by type returns only matching entries."""
    results = get_candidate_locations(type_filter="tourism_node")
    passed = all(c["candidate_type"] == "tourism_node" for c in results)
    log("TEST D4 -- Type filter tourism_node: all returned match",
        passed, f"count={len(results)}")
    return passed


def test_D5_no_filter_returns_all():
    """No filter returns all candidate locations."""
    all_results = get_candidate_locations()
    passed = len(all_results) == len(CANDIDATE_LOCATIONS_108)
    log("TEST D5 -- No filter: returns all candidate locations",
        passed,
        f"returned={len(all_results)} total={len(CANDIDATE_LOCATIONS_108)}")
    return passed


# Block E -- Infrastructure overlay GeoJSON
def test_E1_overlay_is_feature_collection():
    """build_infrastructure_overlay returns FeatureCollection."""
    node = score_infrastructure_node(
        "TEST", "major_port", COORDS, STATUS_OPERATIONAL,
        True, True, True
    )
    node["geo_coordinates"] = COORDS
    overlay = build_infrastructure_overlay([node])
    passed = overlay["type"] == "FeatureCollection"
    log("TEST E1 -- Infrastructure overlay is FeatureCollection",
        passed, f"type={overlay['type']}")
    return passed


def test_E2_overlay_feature_count_matches():
    """Overlay feature count matches input node count."""
    nodes = []
    for i in range(3):
        n = score_infrastructure_node(
            f"TEST_{i}", "major_port", COORDS,
            STATUS_OPERATIONAL, True, False, True
        )
        n["geo_coordinates"] = COORDS
        nodes.append(n)
    overlay = build_infrastructure_overlay(nodes)
    passed = len(overlay["features"]) == 3
    log("TEST E2 -- Overlay feature count matches input",
        passed, f"features={len(overlay['features'])}")
    return passed


def test_E3_overlay_metadata_present():
    """Overlay has metadata with required keys."""
    node = score_infrastructure_node(
        "TEST", "major_port", COORDS, STATUS_OPERATIONAL,
        True, True, True
    )
    node["geo_coordinates"] = COORDS
    overlay = build_infrastructure_overlay([node])
    required_meta = ["layer_type", "total_nodes",
                     "viable_nodes", "multimodal_nodes"]
    passed = all(k in overlay["metadata"] for k in required_meta)
    log("TEST E3 -- Overlay metadata has required keys",
        passed, f"metadata keys={list(overlay['metadata'].keys())}")
    return passed


# Block F -- GIS engine all 5 layers
def test_F1_all_5_layers_built():
    """build_all_layers produces all 5 layers."""
    seg = score_river_segment(
        "SEG_001", COORDS, 8000.0, 400.0, 45000.0, 2500.0
    )
    eco = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    node = score_infrastructure_node(
        "N1", "major_port", COORDS, STATUS_OPERATIONAL,
        True, True, True
    )
    node["geo_coordinates"] = COORDS
    policy = [{"zone_id": "Z1", "geo_coordinates": COORDS,
               "zone_type": "PROJECT_AREA",
               "description": "Test", "regulatory_body": "MoPS",
               "restriction_level": "NONE", "compliance_score": 80.0}]

    all_layers = build_all_layers(
        physical_segments=[seg],
        ecological_locations=[eco],
        economic_nodes=[node],
        policy_zones=policy,
        infrastructure_nodes=[node]
    )
    passed = all_layers["layer_count"] == 5
    log("TEST F1 -- build_all_layers: 5 layers built",
        passed, f"layer_count={all_layers['layer_count']}")
    return passed


def test_F2_valid_layer_names():
    """All 5 layer identifiers are in VALID_LAYERS."""
    passed = all(layer in VALID_LAYERS for layer in [
        LAYER_PHYSICAL, LAYER_ECOLOGICAL, LAYER_ECONOMIC,
        LAYER_POLICY, LAYER_INFRASTRUCTURE
    ])
    log("TEST F2 -- All layer names are in VALID_LAYERS",
        passed)
    return passed


def test_F3_physical_layer_has_features():
    """Physical layer built from river segments has features."""
    seg = score_river_segment(
        "SEG_001", COORDS, 8000.0, 400.0, 45000.0, 2500.0
    )
    layer = build_physical_layer([seg])
    passed = (layer["type"] == "FeatureCollection" and
              layer["metadata"]["feature_count"] == 1)
    log("TEST F3 -- Physical layer: FeatureCollection with 1 feature",
        passed,
        f"feature_count={layer['metadata']['feature_count']}")
    return passed


def test_F4_ecological_layer_has_features():
    """Ecological layer built from ecological results has features."""
    eco = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    layer = build_ecological_layer([eco])
    passed = layer["metadata"]["feature_count"] == 1
    log("TEST F4 -- Ecological layer: 1 feature built",
        passed,
        f"feature_count={layer['metadata']['feature_count']}")
    return passed


def test_F5_empty_layer_inputs_safe():
    """Empty inputs to all layers: no crash, 0 features."""
    layers = build_all_layers(
        physical_segments=[],
        ecological_locations=[],
        economic_nodes=[],
        policy_zones=[],
        infrastructure_nodes=[]
    )
    total = layers["total_features"]
    passed = total == 0
    log("TEST F5 -- Empty layer inputs: 0 features, no crash",
        passed, f"total_features={total}")
    return passed


# Block G -- GIS layer contract validation
def test_G1_physical_feature_has_required_properties():
    """Physical layer features have required properties."""
    seg = score_river_segment(
        "SEG_001", COORDS, 8000.0, 400.0, 45000.0, 2500.0
    )
    layer = build_physical_layer([seg])
    feature = layer["features"][0]
    required_props = ["feature_id", "layer", "score",
                      "status", "color", "reasoning"]
    props = feature["properties"]
    missing = [p for p in required_props if p not in props]
    passed = len(missing) == 0
    log("TEST G1 -- Physical feature has required properties",
        passed, f"missing={missing}")
    return passed


def test_G2_ecological_feature_has_nirmal_signal():
    """Ecological features include Nirmal Ganga signal."""
    eco = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    layer = build_ecological_layer([eco])
    feature = layer["features"][0]
    passed = "nirmal_signal" in feature["properties"]
    log("TEST G2 -- Ecological feature has nirmal_signal property",
        passed)
    return passed


def test_G3_all_features_have_coordinates():
    """All features in all layers have valid coordinates."""
    seg = score_river_segment(
        "SEG_001", COORDS, 8000.0, 400.0, 45000.0, 2500.0
    )
    layer = build_physical_layer([seg])
    all_valid = all(
        len(f["geometry"]["coordinates"]) == 2
        for f in layer["features"]
    )
    log("TEST G3 -- All physical features have valid coordinates",
        all_valid)
    return all_valid


def test_G4_layer_summary_correct():
    """get_layer_summary returns correct metadata."""
    seg = score_river_segment(
        "SEG_001", COORDS, 8000.0, 400.0, 45000.0, 2500.0
    )
    all_layers = build_all_layers(physical_segments=[seg])
    summary = get_layer_summary(all_layers)
    passed = (
        "layer_count" in summary and
        "total_features" in summary and
        "layers" in summary
    )
    log("TEST G4 -- get_layer_summary has required keys",
        passed,
        f"keys={list(summary.keys())}")
    return passed


def test_G5_policy_feature_has_zone_type():
    """Policy features include zone_type property."""
    policy = [{"zone_id": "Z1", "geo_coordinates": COORDS,
               "zone_type": "RESTRICTED",
               "description": "Test zone", "regulatory_body": "MoEFCC",
               "restriction_level": "ABSOLUTE", "compliance_score": 0.0}]
    layer = build_policy_layer(policy)
    feature = layer["features"][0]
    passed = "zone_type" in feature["properties"]
    log("TEST G5 -- Policy feature has zone_type property",
        passed,
        f"zone_type={feature['properties'].get('zone_type')}")
    return passed


# Block H -- Ecological layer scoring
def test_H1_kanpur_critical_stress():
    """Kanpur with known bad values: CRITICAL stress."""
    result = score_ecological_integrity(
        "kanpur", [80.3319, 26.4499],
        18.0, 15.0, 1.5, 320.0, 0.8,
        flow_disruption=True
    )
    passed = result["stress_assessment"]["stress_level"] == "CRITICAL"
    log("TEST H1 -- Kanpur: CRITICAL ecological stress",
        passed,
        f"stress={result['stress_assessment']['stress_level']}")
    return passed


def test_H2_patna_viable_ecology():
    """Patna with good values: ecological_viability=True."""
    result = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    passed = result["ecological_viability"] is True
    log("TEST H2 -- Patna: ecological_viability=True",
        passed)
    return passed


def test_H3_produces_4_signals():
    """score_ecological_integrity produces exactly 4 signals."""
    result = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    passed = len(result["signals"]) == 4
    log("TEST H3 -- Ecological integrity produces 4 signals",
        passed, f"signals={len(result['signals'])}")
    return passed


def test_H4_all_ecological_signals_valid():
    """All 4 ecological signals pass marine schema."""
    result = score_ecological_integrity(
        "patna", COORDS, 65.0, 2.5, 7.2, 35.0, 8.5
    )
    all_valid = all(check_schema(s)[0] for s in result["signals"])
    log("TEST H4 -- All ecological signals pass marine schema",
        all_valid)
    return all_valid


# Runner
if __name__ == "__main__":
    print("\nNICAI -- Infrastructure Overlay and GIS Layer Test Suite")
    print("=" * 60)

    tests = [
        test_A1_operational_multimodal_score_100,
        test_A2_candidate_no_connectivity_low_score,
        test_A3_all_status_types_produce_scores,
        test_A4_multimodal_requires_all_three,
        test_A5_node_has_valid_signal,
        test_A6_proposal_not_empty,
        test_B1_cez_viable_above_threshold,
        test_B2_cez_no_clearance_score_reduced,
        test_B3_cez_no_clearance_proposal_mentions_clearance,
        test_B4_cez_signal_valid,
        test_C1_mmlp_multimodal_viable,
        test_C2_mmlp_no_connectivity_not_viable,
        test_C3_mmlp_signal_valid,
        test_D1_scaffold_has_entries,
        test_D2_all_candidates_have_required_fields,
        test_D3_filter_by_priority_high,
        test_D4_filter_by_type,
        test_D5_no_filter_returns_all,
        test_E1_overlay_is_feature_collection,
        test_E2_overlay_feature_count_matches,
        test_E3_overlay_metadata_present,
        test_F1_all_5_layers_built,
        test_F2_valid_layer_names,
        test_F3_physical_layer_has_features,
        test_F4_ecological_layer_has_features,
        test_F5_empty_layer_inputs_safe,
        test_G1_physical_feature_has_required_properties,
        test_G2_ecological_feature_has_nirmal_signal,
        test_G3_all_features_have_coordinates,
        test_G4_layer_summary_correct,
        test_G5_policy_feature_has_zone_type,
        test_H1_kanpur_critical_stress,
        test_H2_patna_viable_ecology,
        test_H3_produces_4_signals,
        test_H4_all_ecological_signals_valid,
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