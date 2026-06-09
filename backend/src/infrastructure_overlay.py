"""
infrastructure_overlay.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Layer 5 -- Infrastructure Overlay Intelligence

Structured intelligence for:
  - major and non-major ports
  - inland terminals and waterway jetties
  - coastal community jetties
  - CEZ (Coastal Economic Zone) pilot clusters
  - MMLP (Multi Modal Logistics Park) pilot clusters
  - hub-spoke overlays
  - tourism nodes and blue-flag beaches
  - river-side enablement candidates
  - 108 candidate location support scaffold

All outputs are proposal-only. No execution authority.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal


# Infrastructure type registry
INFRASTRUCTURE_TYPES = {
    "major_port", "non_major_port", "inland_terminal",
    "waterway_jetty", "coastal_community_jetty",
    "cez_cluster", "mmlp_cluster", "hub_spoke_node",
    "tourism_node", "blue_flag_beach",
    "river_enablement_candidate", "candidate_location_108"
}

# Operational status codes
STATUS_OPERATIONAL      = "OPERATIONAL"
STATUS_UNDER_DEVELOPMENT = "UNDER_DEVELOPMENT"
STATUS_PROPOSED         = "PROPOSED"
STATUS_DPR_STAGE        = "DPR_STAGE"
STATUS_CANDIDATE        = "CANDIDATE"

STATUS_SCORES = {
    STATUS_OPERATIONAL:       100.0,
    STATUS_UNDER_DEVELOPMENT:  65.0,
    STATUS_DPR_STAGE:          40.0,
    STATUS_PROPOSED:           20.0,
    STATUS_CANDIDATE:          10.0
}

# Connectivity scoring weights
CONNECTIVITY_ROAD_SCORE  = 30.0
CONNECTIVITY_RAIL_SCORE  = 35.0
CONNECTIVITY_WATER_SCORE = 35.0

# CEZ and MMLP readiness thresholds
CEZ_VIABLE_SCORE         = 60.0
MMLP_VIABLE_SCORE        = 65.0

# 108 Candidate Locations scaffold
# Representative sample from Sagarmala candidate list
CANDIDATE_LOCATIONS_108 = [
    {
        "candidate_id": "CL_001",
        "name": "Varanasi Riverfront Terminal",
        "geo_coordinates": [82.9739, 25.3176],
        "state": "Uttar Pradesh",
        "waterway": "NW1",
        "candidate_type": "inland_terminal",
        "priority": "HIGH"
    },
    {
        "candidate_id": "CL_002",
        "name": "Patna Integrated Port",
        "geo_coordinates": [85.1376, 25.5941],
        "state": "Bihar",
        "waterway": "NW1",
        "candidate_type": "major_port",
        "priority": "HIGH"
    },
    {
        "candidate_id": "CL_003",
        "name": "Allahabad Multi-Modal Hub",
        "geo_coordinates": [81.8463, 25.4358],
        "state": "Uttar Pradesh",
        "waterway": "NW1",
        "candidate_type": "mmlp_cluster",
        "priority": "MEDIUM"
    },
    {
        "candidate_id": "CL_004",
        "name": "Hajipur Logistics Hub",
        "geo_coordinates": [85.2119, 25.6891],
        "state": "Bihar",
        "waterway": "NW1",
        "candidate_type": "hub_spoke_node",
        "priority": "MEDIUM"
    },
    {
        "candidate_id": "CL_005",
        "name": "Farakka Barrage Tourism Node",
        "geo_coordinates": [87.9186, 24.8119],
        "state": "West Bengal",
        "waterway": "NW1",
        "candidate_type": "tourism_node",
        "priority": "LOW"
    },
    {
        "candidate_id": "CL_006",
        "name": "Ghazipur River Terminal",
        "geo_coordinates": [83.5785, 25.5849],
        "state": "Uttar Pradesh",
        "waterway": "NW1",
        "candidate_type": "waterway_jetty",
        "priority": "MEDIUM"
    },
    {
        "candidate_id": "CL_007",
        "name": "Bhagalpur CEZ Cluster",
        "geo_coordinates": [86.9842, 25.2425],
        "state": "Bihar",
        "waterway": "NW1",
        "candidate_type": "cez_cluster",
        "priority": "HIGH"
    },
    {
        "candidate_id": "CL_008",
        "name": "Sultanganj River Tourism Zone",
        "geo_coordinates": [86.7435, 25.2457],
        "state": "Bihar",
        "waterway": "NW1",
        "candidate_type": "river_enablement_candidate",
        "priority": "LOW"
    }
]


def score_infrastructure_node(
    node_id: str,
    node_type: str,
    geo_coordinates: List[float],
    operational_status: str,
    road_connected: bool,
    rail_connected: bool,
    water_connected: bool,
    area_acres: Optional[float] = None,
    cargo_capacity_mtpa: Optional[float] = None,
    source_id: str = "INFRA_OVERLAY_v1"
) -> Dict[str, Any]:
    """
    Scores an infrastructure node for operational readiness and
    connectivity quality.

    Returns:
        {
            node_id: str
            node_type: str
            operational_status: str
            status_score: float
            connectivity_score: float
            composite_score: float
            multimodal: bool
            proposal: str
            signal: dict
        }
    """
    if node_type not in INFRASTRUCTURE_TYPES:
        node_type = "candidate_location_108"

    status_score = STATUS_SCORES.get(operational_status, 10.0)

    connectivity_score = round(
        (CONNECTIVITY_ROAD_SCORE if road_connected else 0.0) +
        (CONNECTIVITY_RAIL_SCORE if rail_connected else 0.0) +
        (CONNECTIVITY_WATER_SCORE if water_connected else 0.0),
        2
    )

    composite_score = round(
        status_score * 0.50 +
        connectivity_score * 0.50,
        2
    )

    multimodal = road_connected and rail_connected and water_connected

    connectivity_desc = []
    if road_connected:
        connectivity_desc.append("road")
    if rail_connected:
        connectivity_desc.append("rail")
    if water_connected:
        connectivity_desc.append("waterway")

    conn_str = " + ".join(connectivity_desc) if connectivity_desc else "none"

    if multimodal:
        proposal = (
            f"Node {node_id} ({node_type}): MULTIMODAL -- "
            f"road + rail + waterway connected. "
            f"Status: {operational_status}. "
            f"Composite score: {composite_score}/100. "
            f"Priority candidate for Sagarmala MMLP integration."
        )
    elif composite_score >= 60.0:
        proposal = (
            f"Node {node_id} ({node_type}): VIABLE -- "
            f"Connectivity: {conn_str}. "
            f"Status: {operational_status}. "
            f"Score: {composite_score}/100. "
            f"Suitable for phased infrastructure development."
        )
    else:
        proposal = (
            f"Node {node_id} ({node_type}): LIMITED -- "
            f"Connectivity: {conn_str}. "
            f"Status: {operational_status}. "
            f"Score: {composite_score}/100. "
            f"Requires connectivity investment before viability."
        )

    signal = build_signal(
        signal_type="terminal" if "terminal" in node_type else "port_infrastructure",
        value=composite_score,
        geo_coordinates=geo_coordinates,
        source_id=source_id,
        confidence_initial=0.85
    )

    return {
        "node_id": node_id,
        "node_type": node_type,
        "operational_status": operational_status,
        "status_score": status_score,
        "connectivity_score": connectivity_score,
        "composite_score": composite_score,
        "multimodal": multimodal,
        "road_connected": road_connected,
        "rail_connected": rail_connected,
        "water_connected": water_connected,
        "proposal": proposal,
        "signal": signal
    }


def score_cez_cluster(
    cluster_id: str,
    geo_coordinates: List[float],
    area_sq_km: float,
    port_proximity_km: float,
    industrial_base_score: float,
    connectivity_score: float,
    environmental_clearance: bool,
    source_id: str = "CEZ_ENGINE_v1"
) -> Dict[str, Any]:
    """
    Scores a Coastal Economic Zone cluster for viability.

    Returns CEZ readiness score and proposal.
    """
    area_score = min(100.0, area_sq_km * 2.0)
    proximity_score = max(0.0, 100.0 - port_proximity_km * 5.0)
    clearance_multiplier = 1.0 if environmental_clearance else 0.6

    raw_score = round(
        area_score * 0.20 +
        proximity_score * 0.25 +
        industrial_base_score * 0.30 +
        connectivity_score * 0.25,
        2
    )
    composite = round(
        min(100.0, raw_score * clearance_multiplier),
        2
    )

    viable = composite >= CEZ_VIABLE_SCORE

    if not environmental_clearance:
        proposal = (
            f"CEZ cluster {cluster_id}: environmental clearance ABSENT -- "
            f"score reduced to {composite}/100. "
            f"Clearance must be obtained before any development."
        )
    elif viable:
        proposal = (
            f"CEZ cluster {cluster_id}: VIABLE for development. "
            f"Score {composite}/100. "
            f"Area {area_sq_km} sq km within {port_proximity_km}km of port. "
            f"Recommend DPR preparation."
        )
    else:
        proposal = (
            f"CEZ cluster {cluster_id}: CONDITIONAL -- "
            f"score {composite}/100 below viability threshold {CEZ_VIABLE_SCORE}. "
            f"Improve connectivity or industrial base before proceeding."
        )

    signal = build_signal(
        signal_type="cez_cluster",
        value=composite,
        geo_coordinates=geo_coordinates,
        source_id=source_id,
        confidence_initial=0.8
    )

    return {
        "cluster_id": cluster_id,
        "composite_score": composite,
        "viable": viable,
        "environmental_clearance": environmental_clearance,
        "proposal": proposal,
        "signal": signal
    }


def score_mmlp_cluster(
    cluster_id: str,
    geo_coordinates: List[float],
    area_acres: float,
    road_connected: bool,
    rail_connected: bool,
    waterway_connected: bool,
    proximity_to_consumption_center_km: float,
    operational_status: str,
    source_id: str = "MMLP_ENGINE_v1"
) -> Dict[str, Any]:
    """
    Scores a Multi Modal Logistics Park cluster.
    """
    connectivity_score = (
        (30.0 if road_connected else 0.0) +
        (35.0 if rail_connected else 0.0) +
        (35.0 if waterway_connected else 0.0)
    )

    area_score = min(100.0, area_acres / 5.0)
    proximity_score = max(0.0, 100.0 - proximity_to_consumption_center_km * 2.0)
    status_score = STATUS_SCORES.get(operational_status, 10.0)

    composite = round(
        connectivity_score * 0.40 +
        area_score * 0.20 +
        proximity_score * 0.20 +
        status_score * 0.20,
        2
    )

    viable = composite >= MMLP_VIABLE_SCORE
    multimodal = road_connected and rail_connected and waterway_connected

    proposal = (
        f"MMLP {cluster_id}: {'VIABLE' if viable else 'CONDITIONAL'} -- "
        f"Score {composite}/100 | "
        f"{'Multimodal' if multimodal else 'Partial connectivity'} | "
        f"Area {area_acres} acres | "
        f"Status: {operational_status}"
    )

    signal = build_signal(
        signal_type="mmlp_cluster",
        value=composite,
        geo_coordinates=geo_coordinates,
        source_id=source_id,
        confidence_initial=0.85
    )

    return {
        "cluster_id": cluster_id,
        "composite_score": composite,
        "viable": viable,
        "multimodal": multimodal,
        "proposal": proposal,
        "signal": signal
    }


def get_candidate_locations(
    priority_filter: Optional[str] = None,
    type_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns the 108 candidate locations scaffold,
    optionally filtered by priority or type.
    """
    results = list(CANDIDATE_LOCATIONS_108)

    if priority_filter:
        results = [
            c for c in results
            if c["priority"] == priority_filter.upper()
        ]
    if type_filter:
        results = [
            c for c in results
            if c["candidate_type"] == type_filter
        ]

    return results


def build_infrastructure_overlay(
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Builds a complete infrastructure overlay summary from a list of
    scored infrastructure nodes.

    Returns overlay metadata and GeoJSON-ready feature list.
    """
    features = []
    for node in nodes:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": node.get("geo_coordinates",
                                        node.get("signal", {})
                                        .get("geo_coordinates", [83.0, 25.5]))
            },
            "properties": {
                "node_id": node.get("node_id") or node.get("cluster_id"),
                "node_type": node.get("node_type", "infrastructure"),
                "score": node.get("composite_score", 0.0),
                "status": node.get("operational_status", "UNKNOWN"),
                "multimodal": node.get("multimodal", False),
                "viable": node.get("viable", True),
                "proposal": node.get("proposal", "")
            }
        })

    total = len(features)
    viable_count = sum(
        1 for n in nodes
        if n.get("composite_score", 0) >= 50.0
    )
    multimodal_count = sum(
        1 for n in nodes if n.get("multimodal", False)
    )

    return {
        "type": "FeatureCollection",
        "metadata": {
            "layer_type": "infrastructure_overlay",
            "total_nodes": total,
            "viable_nodes": viable_count,
            "multimodal_nodes": multimodal_count
        },
        "features": features
    }


# Self-test
if __name__ == "__main__":
    import json

    print("infrastructure_overlay.py -- Self-Test")
    print("=" * 50)

    # Test 1: Multimodal terminal
    n1 = score_infrastructure_node(
        node_id="PATNA_PORT_001",
        node_type="major_port",
        geo_coordinates=[85.1376, 25.5941],
        operational_status=STATUS_OPERATIONAL,
        road_connected=True,
        rail_connected=True,
        water_connected=True
    )
    print(f"Node: {n1['node_id']}")
    print(f"Multimodal: {n1['multimodal']}")
    print(f"Composite score: {n1['composite_score']}")
    print(f"Proposal: {n1['proposal'][:80]}")

    print()

    # Test 2: CEZ cluster
    cez = score_cez_cluster(
        cluster_id="CEZ_BHAGALPUR_001",
        geo_coordinates=[86.9842, 25.2425],
        area_sq_km=25.0,
        port_proximity_km=3.0,
        industrial_base_score=70.0,
        connectivity_score=65.0,
        environmental_clearance=True
    )
    print(f"CEZ: {cez['cluster_id']}")
    print(f"Viable: {cez['viable']}")
    print(f"Score: {cez['composite_score']}")

    print()

    # Test 3: Candidate locations
    high_priority = get_candidate_locations(priority_filter="HIGH")
    print(f"High priority candidate locations: {len(high_priority)}")
    for c in high_priority:
        print(f"  {c['candidate_id']}: {c['name']} ({c['candidate_type']})")

    print()

    # Test 4: Infrastructure overlay
    overlay = build_infrastructure_overlay([n1, cez])
    print(f"Overlay features: {overlay['metadata']['total_nodes']}")
    print(f"Viable nodes: {overlay['metadata']['viable_nodes']}")
    print(f"Multimodal nodes: {overlay['metadata']['multimodal_nodes']}")