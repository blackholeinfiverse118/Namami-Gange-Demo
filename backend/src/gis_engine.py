"""
gis_engine.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Digital Depth / GIS Engine -- 5-Layer Structure

Layer 1 -- Physical:    depth, flow, discharge, wind/current
Layer 2 -- Ecological:  pollution, turbidity, stress
Layer 3 -- Economic:    cargo, CEZ, MMLP, tourism, logistics
Layer 4 -- Policy:      restricted zones, compliance, project areas
Layer 5 -- Infrastructure: ports, terminals, waterways, bridges, barrages

All layers output GeoJSON FeatureCollections.
All layers are proposal-only. No execution authority.
All coordinates are [longitude, latitude] WGS84.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional


# Layer identifiers
LAYER_PHYSICAL       = "physical"
LAYER_ECOLOGICAL     = "ecological"
LAYER_ECONOMIC       = "economic"
LAYER_POLICY         = "policy"
LAYER_INFRASTRUCTURE = "infrastructure"

VALID_LAYERS = {
    LAYER_PHYSICAL, LAYER_ECOLOGICAL,
    LAYER_ECONOMIC, LAYER_POLICY, LAYER_INFRASTRUCTURE
}

# Color maps per layer
PHYSICAL_COLORS = {
    "DEEP":       "#1a6eb5",
    "NAVIGABLE":  "#4a9fd4",
    "SHALLOW":    "#89c4e1",
    "CRITICAL":   "#d4e9f7",
    "FLOOD":      "#8b0000",
    "HIGH":       "#cc3300",
    "NORMAL":     "#2ecc71",
    "LOW":        "#f39c12"
}

ECOLOGICAL_COLORS = {
    "EXCELLENT":  "#27ae60",
    "GOOD":       "#2ecc71",
    "MODERATE":   "#f39c12",
    "POOR":       "#e74c3c",
    "CRITICAL":   "#7f0000",
    "LOW":        "#27ae60",
    "HIGH":       "#e74c3c"
}

ECONOMIC_COLORS = {
    "VIABLE":       "#2ecc71",
    "CONDITIONAL":  "#f39c12",
    "NOT_VIABLE":   "#e74c3c",
    "OPERATIONAL":  "#1abc9c",
    "PROPOSED":     "#95a5a6"
}

POLICY_COLORS = {
    "RESTRICTED":   "#7f0000",
    "COMPLIANCE":   "#e67e22",
    "PROJECT_AREA": "#3498db",
    "OPEN":         "#2ecc71"
}

INFRASTRUCTURE_COLORS = {
    "OPERATIONAL":        "#2ecc71",
    "UNDER_DEVELOPMENT":  "#f39c12",
    "PROPOSED":           "#95a5a6",
    "BLOCKED":            "#e74c3c"
}


def _base_feature(
    feature_id: str,
    geo_coordinates: List[float],
    layer: str,
    score: float,
    status: str,
    color: str,
    reasoning: str,
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """Builds a base GeoJSON Feature."""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": geo_coordinates
        },
        "properties": {
            "feature_id": feature_id,
            "layer": layer,
            "score": round(score, 2),
            "status": status,
            "color": color,
            "reasoning": reasoning,
            **properties
        }
    }


def build_physical_layer(
    segments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds Layer 1 -- Physical GIS layer.

    Each segment dict should have:
        segment_id, geo_coordinates, discharge_assessment,
        sediment_assessment, composite_flow_score

    Returns GeoJSON FeatureCollection.
    """
    features = []
    for seg in segments:
        discharge = seg.get("discharge_assessment", {})
        discharge_level = discharge.get("level", "NORMAL")
        color = PHYSICAL_COLORS.get(discharge_level, "#4a9fd4")
        score = seg.get("composite_flow_score", 0.0)

        feature = _base_feature(
            feature_id=seg.get("segment_id", "UNKNOWN"),
            geo_coordinates=seg.get("geo_coordinates", [83.0, 25.5]),
            layer=LAYER_PHYSICAL,
            score=score,
            status=discharge_level,
            color=color,
            reasoning=seg.get("reasoning", ""),
            properties={
                "discharge_level": discharge_level,
                "navigation_viable": seg.get("navigation_viable", False),
                "sediment_level": seg.get("sediment_assessment", {})
                                    .get("level", "UNKNOWN"),
                "seasonal_risk": seg.get("seasonal_assessment", {})
                                   .get("risk_level", "UNKNOWN"),
                "barrage_influence": seg.get("barrage_assessment", {})
                                       .get("influence_level") if seg.get(
                    "barrage_assessment") else "NONE"
            }
        )
        features.append(feature)

    return _build_collection(LAYER_PHYSICAL, features, PHYSICAL_COLORS)


def build_ecological_layer(
    locations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds Layer 2 -- Ecological GIS layer.

    Each location dict should have:
        location_id, geo_coordinates, stress_assessment,
        pollution_assessment, composite_ecological_score
    """
    features = []
    for loc in locations:
        stress = loc.get("stress_assessment", {})
        stress_level = stress.get("stress_level", "MODERATE")
        color = ECOLOGICAL_COLORS.get(stress_level, "#f39c12")
        score = loc.get("composite_ecological_score", 0.0)

        feature = _base_feature(
            feature_id=loc.get("location_id", "UNKNOWN"),
            geo_coordinates=loc.get("geo_coordinates", [83.0, 25.5]),
            layer=LAYER_ECOLOGICAL,
            score=score,
            status=stress_level,
            color=color,
            reasoning=loc.get("proposal", ""),
            properties={
                "stress_level": stress_level,
                "pollution_class": loc.get("pollution_assessment", {})
                                      .get("pollution_class", "UNKNOWN"),
                "turbidity_class": loc.get("turbidity_assessment", {})
                                      .get("turbidity_class", "UNKNOWN"),
                "ecological_viability": loc.get("ecological_viability", False),
                "nirmal_signal": loc.get("pollution_assessment", {})
                                    .get("nirmal_signal", ""),
                "aviral_signal": loc.get("pollution_assessment", {})
                                    .get("aviral_signal", "")
            }
        )
        features.append(feature)

    return _build_collection(LAYER_ECOLOGICAL, features, ECOLOGICAL_COLORS)


def build_economic_layer(
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds Layer 3 -- Economic GIS layer.
    Covers CEZ clusters, MMLP clusters, cargo nodes, tourism nodes.
    """
    features = []
    for node in nodes:
        score = node.get("composite_score", 0.0)
        viable = node.get("viable", score >= 60.0)
        status = "VIABLE" if viable else "CONDITIONAL"
        color = ECONOMIC_COLORS.get(status, "#f39c12")

        coords = node.get("geo_coordinates")
        if not coords:
            sig = node.get("signal", {})
            coords = sig.get("geo_coordinates", [83.0, 25.5])

        feature = _base_feature(
            feature_id=node.get("cluster_id") or node.get("node_id", "UNKNOWN"),
            geo_coordinates=coords,
            layer=LAYER_ECONOMIC,
            score=score,
            status=status,
            color=color,
            reasoning=node.get("proposal", ""),
            properties={
                "economic_type": node.get("node_type", "economic_node"),
                "viable": viable,
                "multimodal": node.get("multimodal", False)
            }
        )
        features.append(feature)

    return _build_collection(LAYER_ECONOMIC, features, ECONOMIC_COLORS)


def build_policy_layer(
    policy_zones: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds Layer 4 -- Policy GIS layer.
    Covers restricted zones, compliance regions, project areas.

    Each zone dict should have:
        zone_id, geo_coordinates, zone_type, description
    """
    features = []
    for zone in policy_zones:
        zone_type = zone.get("zone_type", "OPEN")
        color = POLICY_COLORS.get(zone_type, "#3498db")

        feature = _base_feature(
            feature_id=zone.get("zone_id", "UNKNOWN"),
            geo_coordinates=zone.get("geo_coordinates", [83.0, 25.5]),
            layer=LAYER_POLICY,
            score=zone.get("compliance_score", 50.0),
            status=zone_type,
            color=color,
            reasoning=zone.get("description", ""),
            properties={
                "zone_type": zone_type,
                "regulatory_body": zone.get("regulatory_body", "UNKNOWN"),
                "restriction_level": zone.get("restriction_level", "MODERATE"),
                "project_reference": zone.get("project_reference", "")
            }
        )
        features.append(feature)

    return _build_collection(LAYER_POLICY, features, POLICY_COLORS)


def build_infrastructure_layer(
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds Layer 5 -- Infrastructure GIS layer.
    Covers ports, terminals, waterways, bridges, barrages.
    """
    features = []
    for node in nodes:
        status = node.get("operational_status",
                          node.get("lock_status", "PROPOSED"))
        color = INFRASTRUCTURE_COLORS.get(status, "#95a5a6")
        score = node.get("composite_score",
                         node.get("score", 50.0))

        coords = node.get("geo_coordinates")
        if not coords:
            sig = node.get("signal", {})
            coords = sig.get("geo_coordinates", [83.0, 25.5])

        feature = _base_feature(
            feature_id=node.get("node_id") or
                       node.get("barrage_id") or
                       node.get("bridge_name", "UNKNOWN"),
            geo_coordinates=coords,
            layer=LAYER_INFRASTRUCTURE,
            score=score,
            status=status,
            color=color,
            reasoning=node.get("proposal", ""),
            properties={
                "infrastructure_type": node.get("node_type", "infrastructure"),
                "multimodal": node.get("multimodal", False),
                "road_connected": node.get("road_connected", False),
                "rail_connected": node.get("rail_connected", False),
                "water_connected": node.get("water_connected", False)
            }
        )
        features.append(feature)

    return _build_collection(LAYER_INFRASTRUCTURE, features,
                             INFRASTRUCTURE_COLORS)


def build_all_layers(
    physical_segments: List[Dict] = None,
    ecological_locations: List[Dict] = None,
    economic_nodes: List[Dict] = None,
    policy_zones: List[Dict] = None,
    infrastructure_nodes: List[Dict] = None
) -> Dict[str, Any]:
    """
    Builds all 5 GIS layers in one call.
    Returns a dict with all layers keyed by layer name.
    """
    layers = {}

    if physical_segments is not None:
        layers[LAYER_PHYSICAL] = build_physical_layer(physical_segments)
    if ecological_locations is not None:
        layers[LAYER_ECOLOGICAL] = build_ecological_layer(ecological_locations)
    if economic_nodes is not None:
        layers[LAYER_ECONOMIC] = build_economic_layer(economic_nodes)
    if policy_zones is not None:
        layers[LAYER_POLICY] = build_policy_layer(policy_zones)
    if infrastructure_nodes is not None:
        layers[LAYER_INFRASTRUCTURE] = build_infrastructure_layer(
            infrastructure_nodes)

    total_features = sum(
        len(layer.get("features", []))
        for layer in layers.values()
    )

    return {
        "spine_version": "v1",
        "layer_count": len(layers),
        "total_features": total_features,
        "layers": layers
    }


def _build_collection(
    layer: str,
    features: List[Dict],
    color_map: Dict
) -> Dict[str, Any]:
    """Builds a GeoJSON FeatureCollection for a layer."""
    return {
        "type": "FeatureCollection",
        "metadata": {
            "layer": layer,
            "feature_count": len(features),
            "color_map": color_map
        },
        "features": features
    }


def get_layer_summary(all_layers: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a summary of all layers for API response."""
    summary = {
        "spine_version": all_layers.get("spine_version", "v1"),
        "layer_count": all_layers.get("layer_count", 0),
        "total_features": all_layers.get("total_features", 0),
        "layers": {}
    }
    for layer_name, layer_data in all_layers.get("layers", {}).items():
        summary["layers"][layer_name] = {
            "feature_count": layer_data.get("metadata", {})
                                        .get("feature_count", 0),
            "type": "FeatureCollection"
        }
    return summary


# Self-test
if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, ".")

    from river_flow_layer import score_river_segment
    from ecological_layer import score_ecological_integrity
    from infrastructure_overlay import score_infrastructure_node, STATUS_OPERATIONAL

    print("gis_engine.py -- Self-Test")
    print("=" * 50)

    # Physical layer
    seg1 = score_river_segment(
        "NW1_VARANASI_001", [82.9739, 25.3176],
        8000.0, 400.0, 45000.0, 2500.0
    )
    seg2 = score_river_segment(
        "NW1_FARAKKA_001", [87.9186, 24.8119],
        3000.0, 2500.0, 60000.0, 800.0,
        barrage_upstream=True, barrage_upstream_discharge=10000.0
    )
    physical = build_physical_layer([seg1, seg2])
    print(f"Physical layer: {physical['metadata']['feature_count']} features")

    # Ecological layer
    eco1 = score_ecological_integrity(
        "patna_river_port", [85.1376, 25.5941],
        65.0, 2.5, 7.2, 35.0, 8.5
    )
    ecological = build_ecological_layer([eco1])
    print(f"Ecological layer: {ecological['metadata']['feature_count']} features")

    # Economic layer
    from infrastructure_overlay import score_cez_cluster
    cez = score_cez_cluster(
        "CEZ_BHAGALPUR", [86.9842, 25.2425],
        25.0, 3.0, 70.0, 65.0, True
    )
    economic = build_economic_layer([cez])
    print(f"Economic layer: {economic['metadata']['feature_count']} features")

    # Policy layer
    policy_zones = [
        {
            "zone_id": "WETLAND_FARAKKA",
            "geo_coordinates": [87.9186, 24.8119],
            "zone_type": "RESTRICTED",
            "description": "Protected wetland -- Ramsar site",
            "regulatory_body": "MoEFCC",
            "restriction_level": "ABSOLUTE",
            "compliance_score": 0.0
        }
    ]
    policy = build_policy_layer(policy_zones)
    print(f"Policy layer: {policy['metadata']['feature_count']} features")

    # Infrastructure layer
    infra1 = score_infrastructure_node(
        "PATNA_PORT_001", "major_port", [85.1376, 25.5941],
        STATUS_OPERATIONAL, True, True, True
    )
    infrastructure = build_infrastructure_layer([infra1])
    print(f"Infrastructure layer: "
          f"{infrastructure['metadata']['feature_count']} features")

    # All layers
    all_layers = build_all_layers(
        physical_segments=[seg1, seg2],
        ecological_locations=[eco1],
        economic_nodes=[cez],
        policy_zones=policy_zones,
        infrastructure_nodes=[infra1]
    )
    print(f"\nAll layers combined:")
    print(f"  Layer count: {all_layers['layer_count']}")
    print(f"  Total features: {all_layers['total_features']}")
    summary = get_layer_summary(all_layers)
    for layer_name, layer_info in summary["layers"].items():
        print(f"  {layer_name}: {layer_info['feature_count']} features")