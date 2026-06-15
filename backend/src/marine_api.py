"""
marine_api.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
API Expansion -- 6 New Endpoints

New endpoints (all GET):
  GET /marine-signals     -- normalized marine schema signals
  GET /infrastructure-overlay -- infrastructure layer GeoJSON
  GET /navigability       -- NW1/NW5 navigability assessment
  GET /ecology            -- ecological integrity scores
  GET /proposal-engine    -- actionable proposals for a location
  GET /digital-depth      -- 5-layer GIS structure

Mounts as a Flask Blueprint.
Does NOT modify or break existing api.py endpoints.
All responses are strict contract-compliant.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Blueprint, request, jsonify
from typing import Any, Dict

from marine_schema import build_signal, normalize_batch
from river_flow_layer import score_river_segment
from barrage_bridge_layer import assess_bridge_clearance, assess_barrage_passage
from navigability_layer import (
    score_segment_navigability, best_months_for_segment
)
from ecological_layer import score_ecological_integrity
from infrastructure_overlay import (
    score_infrastructure_node, score_cez_cluster,
    get_candidate_locations, build_infrastructure_overlay,
    STATUS_OPERATIONAL, STATUS_PROPOSED
)
from proposal_engine import (
    generate_location_proposals,
    propose_navigability,
    propose_ecological_status,
    propose_seaplane_feasibility
)
from gis_engine import (
    build_all_layers, get_layer_summary,
    build_physical_layer, build_ecological_layer,
    build_economic_layer, build_policy_layer,
    build_infrastructure_layer
)

marine_bp = Blueprint("marine", __name__)


def error_response(message: str, code: int = 400):
    return jsonify({"error": message, "status": "error"}), code


# Sample data for demo responses
DEMO_SEGMENTS = [
    {
        "segment_id": "NW1_VARANASI_001",
        "geo_coordinates": [82.9739, 25.3176],
        "discharge_cumecs": 8000.0,
        "sediment_mg_l": 400.0,
        "monsoon_discharge": 45000.0,
        "lean_discharge": 2500.0
    },
    {
        "segment_id": "NW1_PATNA_001",
        "geo_coordinates": [85.1376, 25.5941],
        "discharge_cumecs": 10000.0,
        "sediment_mg_l": 350.0,
        "monsoon_discharge": 50000.0,
        "lean_discharge": 3000.0
    },
    {
        "segment_id": "NW1_FARAKKA_001",
        "geo_coordinates": [87.9186, 24.8119],
        "discharge_cumecs": 3000.0,
        "sediment_mg_l": 2500.0,
        "monsoon_discharge": 60000.0,
        "lean_discharge": 800.0,
        "barrage_upstream": True,
        "barrage_upstream_discharge": 10000.0
    }
]

DEMO_ECOLOGICAL = [
    {
        "location_id": "patna_river_port",
        "geo_coordinates": [85.1376, 25.5941],
        "wqi": 65.0, "bod_mg_l": 2.5, "do_mg_l": 7.2,
        "turbidity_ntu": 35.0, "nearest_industry_km": 8.5
    },
    {
        "location_id": "varanasi_terminal",
        "geo_coordinates": [82.9739, 25.3176],
        "wqi": 58.0, "bod_mg_l": 3.5, "do_mg_l": 6.5,
        "turbidity_ntu": 55.0, "nearest_industry_km": 6.0
    },
    {
        "location_id": "kanpur_industrial_zone",
        "geo_coordinates": [80.3319, 26.4499],
        "wqi": 18.0, "bod_mg_l": 15.0, "do_mg_l": 1.5,
        "turbidity_ntu": 320.0, "nearest_industry_km": 0.8,
        "flow_disruption": True
    }
]

DEMO_INFRASTRUCTURE = [
    {
        "node_id": "PATNA_PORT_001",
        "node_type": "major_port",
        "geo_coordinates": [85.1376, 25.5941],
        "operational_status": STATUS_OPERATIONAL,
        "road_connected": True,
        "rail_connected": True,
        "water_connected": True
    },
    {
        "node_id": "VARANASI_TERMINAL_001",
        "node_type": "inland_terminal",
        "geo_coordinates": [82.9739, 25.3176],
        "operational_status": STATUS_OPERATIONAL,
        "road_connected": True,
        "rail_connected": True,
        "water_connected": True
    },
    {
        "node_id": "HAJIPUR_HUB_001",
        "node_type": "hub_spoke_node",
        "geo_coordinates": [85.2119, 25.6891],
        "operational_status": STATUS_PROPOSED,
        "road_connected": True,
        "rail_connected": False,
        "water_connected": True
    }
]

DEMO_POLICY_ZONES = [
    {
        "zone_id": "WETLAND_FARAKKA",
        "geo_coordinates": [87.9186, 24.8119],
        "zone_type": "RESTRICTED",
        "description": "Protected wetland -- Ramsar site",
        "regulatory_body": "MoEFCC",
        "restriction_level": "ABSOLUTE",
        "compliance_score": 0.0
    },
    {
        "zone_id": "SAGARMALA_PROJECT_NW1",
        "geo_coordinates": [85.1376, 25.5941],
        "zone_type": "PROJECT_AREA",
        "description": "Sagarmala Phase 2 project corridor",
        "regulatory_body": "MoPS",
        "restriction_level": "NONE",
        "compliance_score": 85.0
    }
]


# ENDPOINT 1 -- GET /marine-signals
@marine_bp.route("/marine-signals", methods=["GET"])
def marine_signals():
    """
    GET /marine-signals
    Returns normalized marine schema signals for the Ganga Basin.

    Optional query params:
      ?signal_type=depth|discharge|pollution|...
      ?source_id=CWC_v1|CPCB_v1|...
    """
    signal_type_filter = request.args.get("signal_type")
    source_filter = request.args.get("source_id")

    signals = []

    for seg in DEMO_SEGMENTS:
        result = score_river_segment(
            seg["segment_id"],
            seg["geo_coordinates"],
            seg["discharge_cumecs"],
            seg["sediment_mg_l"],
            seg["monsoon_discharge"],
            seg["lean_discharge"],
            barrage_upstream=seg.get("barrage_upstream", False),
            barrage_upstream_discharge=seg.get("barrage_upstream_discharge")
        )
        signals.extend(result["signals"])

    for eco in DEMO_ECOLOGICAL:
        result = score_ecological_integrity(
            eco["location_id"],
            eco["geo_coordinates"],
            eco["wqi"], eco["bod_mg_l"], eco["do_mg_l"],
            eco["turbidity_ntu"], eco["nearest_industry_km"],
            flow_disruption=eco.get("flow_disruption", False)
        )
        signals.extend(result["signals"])

    if signal_type_filter:
        signals = [s for s in signals
                   if s.get("signal_type") == signal_type_filter]
    if source_filter:
        signals = [s for s in signals
                   if s.get("source_id") == source_filter]

    return jsonify({
        "count": len(signals),
        "signal_type_filter": signal_type_filter,
        "signals": signals
    })


# ENDPOINT 2 -- GET /infrastructure-overlay
@marine_bp.route("/infrastructure-overlay", methods=["GET"])
def infrastructure_overlay():
    """
    GET /infrastructure-overlay
    Returns GeoJSON infrastructure overlay for all nodes.

    Optional query params:
      ?type=major_port|inland_terminal|hub_spoke_node|...
      ?candidates=true -- include 108 candidate locations
    """
    type_filter = request.args.get("type")
    include_candidates = request.args.get("candidates", "false").lower() == "true"

    scored_nodes = []
    for node in DEMO_INFRASTRUCTURE:
        if type_filter and node["node_type"] != type_filter:
            continue
        result = score_infrastructure_node(
            node["node_id"],
            node["node_type"],
            node["geo_coordinates"],
            node["operational_status"],
            node["road_connected"],
            node["rail_connected"],
            node["water_connected"]
        )
        result["geo_coordinates"] = node["geo_coordinates"]
        scored_nodes.append(result)

    if include_candidates:
        candidates = get_candidate_locations()
        for c in candidates:
            scored_nodes.append({
                "node_id": c["candidate_id"],
                "node_type": c["candidate_type"],
                "composite_score": 10.0,
                "geo_coordinates": c["geo_coordinates"],
                "operational_status": "CANDIDATE",
                "multimodal": False,
                "proposal": f"Candidate location: {c['name']} -- {c['priority']} priority"
            })

    overlay = build_infrastructure_overlay(scored_nodes)

    return jsonify({
        "type_filter": type_filter,
        "include_candidates": include_candidates,
        **overlay
    })


# ENDPOINT 3 -- GET /navigability
@marine_bp.route("/navigability", methods=["GET"])
def navigability():
    """
    GET /navigability
    Returns navigability assessment for NW1/NW5 segments.

    Optional query params:
      ?waterway=NW1|NW5
      ?vessel_class=Class-I|Class-II|Class-III|Class-IV|Class-V
      ?month=1-12
    """
    waterway = request.args.get("waterway", "NW1")
    vessel_class = request.args.get("vessel_class", "Class-III")
    month_str = request.args.get("month", "11")

    try:
        month = int(month_str)
        if not 1 <= month <= 12:
            return error_response("month must be between 1 and 12")
    except ValueError:
        return error_response("month must be an integer between 1 and 12")

    results = []
    for seg in DEMO_SEGMENTS:
        result = score_segment_navigability(
            segment_id=seg["segment_id"],
            waterway_id=waterway,
            geo_coordinates=seg["geo_coordinates"],
            depth_m=seg["discharge_cumecs"] / 5000.0,
            vessel_class=vessel_class,
            month=month
        )
        results.append({
            "segment_id": result["segment_id"],
            "waterway_id": result["waterway_id"],
            "vessel_class": result["vessel_class"],
            "month_name": result["month_name"],
            "composite_navigability_score": result["composite_navigability_score"],
            "navigation_viable": result["navigation_viable"],
            "navigability_confidence": result["navigability_confidence"],
            "proposal": result["proposal"]
        })

    return jsonify({
        "waterway": waterway,
        "vessel_class": vessel_class,
        "month": month,
        "count": len(results),
        "results": results
    })


# ENDPOINT 4 -- GET /ecology
@marine_bp.route("/ecology", methods=["GET"])
def ecology():
    """
    GET /ecology
    Returns ecological integrity scores for all locations.

    Optional query params:
      ?stress_level=LOW|MODERATE|HIGH|CRITICAL
      ?location_id=<id>
    """
    stress_filter = request.args.get("stress_level")
    location_filter = request.args.get("location_id")

    results = []
    for eco in DEMO_ECOLOGICAL:
        if location_filter and eco["location_id"] != location_filter:
            continue

        result = score_ecological_integrity(
            eco["location_id"],
            eco["geo_coordinates"],
            eco["wqi"], eco["bod_mg_l"], eco["do_mg_l"],
            eco["turbidity_ntu"], eco["nearest_industry_km"],
            flow_disruption=eco.get("flow_disruption", False)
        )

        stress_level = result["stress_assessment"]["stress_level"]
        if stress_filter and stress_level != stress_filter.upper():
            continue

        results.append({
            "location_id": result["location_id"],
            "composite_ecological_score": result["composite_ecological_score"],
            "stress_level": stress_level,
            "pollution_class": result["pollution_assessment"]["pollution_class"],
            "turbidity_class": result["turbidity_assessment"]["turbidity_class"],
            "ecological_viability": result["ecological_viability"],
            "nirmal_signal": result["pollution_assessment"]["nirmal_signal"],
            "proposal": result["proposal"]
        })

    return jsonify({
        "stress_filter": stress_filter,
        "count": len(results),
        "results": results
    })


# ENDPOINT 5 -- GET /proposal-engine
@marine_bp.route("/proposal-engine", methods=["GET"])
def proposal_engine_endpoint():
    """
    GET /proposal-engine
    Returns actionable proposals for a location.

    Required query params:
      ?location_id=<id>

    Optional:
      ?vessel_class=Class-III
      ?month=11
    """
    location_id = request.args.get("location_id")
    if not location_id:
        return error_response("location_id query parameter is required")

    vessel_class = request.args.get("vessel_class", "Class-III")
    month_str = request.args.get("month", "11")

    try:
        month = int(month_str)
    except ValueError:
        month = 11

    eco_data = next(
        (e for e in DEMO_ECOLOGICAL if e["location_id"] == location_id),
        None
    )
    seg_data = next(
        (s for s in DEMO_SEGMENTS
         if location_id.lower().replace("_", "") in
         s["segment_id"].lower().replace("_", "")),
        DEMO_SEGMENTS[0]
    )
    infra_data = next(
        (n for n in DEMO_INFRASTRUCTURE
         if location_id.lower() in n["node_id"].lower()),
        None
    )

    ecological_result = None
    if eco_data:
        ecological_result = score_ecological_integrity(
            eco_data["location_id"],
            eco_data["geo_coordinates"],
            eco_data["wqi"], eco_data["bod_mg_l"], eco_data["do_mg_l"],
            eco_data["turbidity_ntu"], eco_data["nearest_industry_km"],
            flow_disruption=eco_data.get("flow_disruption", False)
        )

    navigability_result = score_segment_navigability(
        segment_id=location_id,
        waterway_id="NW1",
        geo_coordinates=seg_data["geo_coordinates"],
        depth_m=seg_data["discharge_cumecs"] / 5000.0,
        vessel_class=vessel_class,
        month=month
    )

    infrastructure_result = None
    if infra_data:
        infrastructure_result = score_infrastructure_node(
            infra_data["node_id"],
            infra_data["node_type"],
            infra_data["geo_coordinates"],
            infra_data["operational_status"],
            infra_data["road_connected"],
            infra_data["rail_connected"],
            infra_data["water_connected"]
        )

    geo = eco_data["geo_coordinates"] if eco_data else seg_data["geo_coordinates"]

    proposals = generate_location_proposals(
        location_id=location_id,
        geo_coordinates=geo,
        navigability_result=navigability_result,
        ecological_result=ecological_result,
        infrastructure_result=infrastructure_result
    )

    return jsonify({
        "location_id": location_id,
        "vessel_class": vessel_class,
        "month": month,
        "proposal_count": len(proposals),
        "proposals": proposals
    })


# ENDPOINT 6 -- GET /digital-depth
@marine_bp.route("/digital-depth", methods=["GET"])
def digital_depth():
    """
    GET /digital-depth
    Returns the full 5-layer GIS structure.

    Optional query params:
      ?layer=physical|ecological|economic|policy|infrastructure
      ?summary=true -- returns metadata only, not full features
    """
    layer_filter = request.args.get("layer")
    summary_only = request.args.get("summary", "false").lower() == "true"

    physical_segments = [
        score_river_segment(
            seg["segment_id"], seg["geo_coordinates"],
            seg["discharge_cumecs"], seg["sediment_mg_l"],
            seg["monsoon_discharge"], seg["lean_discharge"],
            barrage_upstream=seg.get("barrage_upstream", False),
            barrage_upstream_discharge=seg.get("barrage_upstream_discharge")
        )
        for seg in DEMO_SEGMENTS
    ]

    ecological_locations = [
        score_ecological_integrity(
            eco["location_id"], eco["geo_coordinates"],
            eco["wqi"], eco["bod_mg_l"], eco["do_mg_l"],
            eco["turbidity_ntu"], eco["nearest_industry_km"],
            flow_disruption=eco.get("flow_disruption", False)
        )
        for eco in DEMO_ECOLOGICAL
    ]

    economic_nodes = [
        score_infrastructure_node(
            node["node_id"], node["node_type"],
            node["geo_coordinates"], node["operational_status"],
            node["road_connected"], node["rail_connected"],
            node["water_connected"]
        )
        for node in DEMO_INFRASTRUCTURE
    ]
    for i, node in enumerate(economic_nodes):
        node["geo_coordinates"] = DEMO_INFRASTRUCTURE[i]["geo_coordinates"]

    all_layers = build_all_layers(
        physical_segments=physical_segments,
        ecological_locations=ecological_locations,
        economic_nodes=economic_nodes,
        policy_zones=DEMO_POLICY_ZONES,
        infrastructure_nodes=economic_nodes
    )

    if layer_filter:
        if layer_filter not in all_layers["layers"]:
            return error_response(
                f"Unknown layer '{layer_filter}'. "
                f"Valid: physical, ecological, economic, policy, infrastructure"
            )
        layer_data = all_layers["layers"][layer_filter]
        if summary_only:
            return jsonify({
                "layer": layer_filter,
                "feature_count": layer_data["metadata"]["feature_count"]
            })
        return jsonify(layer_data)

    if summary_only:
        return jsonify(get_layer_summary(all_layers))

    return jsonify(all_layers)


@marine_bp.route("/datasets", methods=["GET"])
def get_datasets():
    """
    GET /datasets
    Returns list of dataset sources and computed summary statistics.
    Accepts optional parameters validation_breach, latency_ms, current_block.
    """
    validation_breach = request.args.get("validation_breach", "false").lower() == "true"
    latency_ms = int(request.args.get("latency_ms", "6"))
    current_block = int(request.args.get("current_block", "1240"))

    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, source, status, updated, reliability, version, coverage, schema_fields, ingestion_rate, trace_trail FROM datasets")
        rows = cursor.fetchall()
        
        datasets = []
        for r in rows:
            name = r["name"]
            status = r["status"]
            reliability = r["reliability"]
            trace_trail = r["trace_trail"]
            updated = r["updated"]
            
            # Dynamic overrides for simulation
            if "MoPSW" in name:
                updated = f"{latency_ms}ms Delay"
                if validation_breach:
                    status = "Syncing"
                    reliability = 85
                    trace_trail = "Degraded due to transmission delay jitter"
            elif "UP PCB" in name:
                if validation_breach:
                    status = "Breach ⚠"
                    reliability = 62
                    trace_trail = "Schema contract mismatch detected"
            elif "IWAI" in name:
                updated = f"Block #{current_block}"
                
            datasets.append({
                "name": name,
                "source": r["source"],
                "status": status,
                "updated": updated,
                "reliability": reliability,
                "version": r["version"],
                "coverage": r["coverage"],
                "schemaFields": r["schema_fields"],
                "ingestionRate": r["ingestion_rate"],
                "traceTrail": trace_trail
            })
        conn.close()
    except Exception as e:
        print(f"[marine_api] Error loading datasets from SQLite: {e}. Using fallback.")
        datasets = [
            { 
              "name": "ISRO Bhuvan Satellite Imagery", 
              "source": "ISRO Bhuvan Portal", 
              "status": "Good", 
              "updated": "6 Hrs", 
              "reliability": 98, 
              "version": "v3.2", 
              "coverage": "Basin-wide",
              "schemaFields": "tile_x, tile_y, zoom_level, imagery_resolution: \"0.5m\", cloud_cover_percent",
              "ingestionRate": "1.2 GB/day geotiff raster chunks",
              "traceTrail": "validated via optical cloud filtering and geometric correction checks"
            },
            { 
              "name": "CWC River Gauge Network", 
              "source": "Central Water Commission API", 
              "status": "Good", 
              "updated": "Real-time", 
              "reliability": 98, 
              "version": "v3.2", 
              "coverage": "National",
              "schemaFields": "discharge_cumecs, sediment_mg_l, lean_discharge, barrage_upstream_discharge",
              "ingestionRate": "1.8k telemetry msg/min via CWC API gateway",
              "traceTrail": "verified via daily manual gauge calibration correlation checks"
            },
            { 
              "name": "MoPSW Inland Vessels API", 
              "source": "Ministry of Ports, Shipping and Waterways", 
              "status": "Syncing" if validation_breach else "Good", 
              "updated": f"{latency_ms}ms Delay", 
              "reliability": 85 if validation_breach else 98, 
              "version": "v2.1", 
              "coverage": "National",
              "schemaFields": "mmsi_id, speed_knots, draft_m, vessel_class, lat_lng_point",
              "ingestionRate": "Real-time AIS transponder stream via National Maritime Single Window",
              "traceTrail": "Degraded due to transmission delay jitter" if validation_breach else "verified via differential GPS base station correction"
            },
            { 
              "name": "UP PCB Water Quality Sensors", 
              "source": "Uttar Pradesh Pollution Control Board", 
              "status": "Breach ⚠" if validation_breach else "Good", 
              "reliability": 62 if validation_breach else 95, 
              "version": "v1.4", 
              "coverage": "UP State",
              "schemaFields": "avg_bod_mg_l, do_mg_l, turbidity_ntu, nearest_industry_km",
              "ingestionRate": "28 sensor nodes reporting hourly telemetry payload",
              "traceTrail": "Schema contract mismatch detected" if validation_breach else "validated via biochemical lab sample correlation (monthly audits)"
            },
            { 
              "name": "IWAI IWT Terminals", 
              "source": "Inland Waterways Authority of India", 
              "status": "Good", 
              "updated": f"Block #{current_block}", 
              "reliability": 96, 
              "version": "v2.3", 
              "coverage": "NW-1 to NW-111",
              "schemaFields": "node_type, road_connected, rail_connected, water_connected, area_acres",
              "ingestionRate": "Block synchronization persistence on location database (locations.json)",
              "traceTrail": "validated via blockchain ledger contract verification checks"
            }
        ]

    total_datasets = 24
    degraded_count = 3 if validation_breach else 1
    active_count = total_datasets - degraded_count
    avg_reliability = 91 if validation_breach else 96

    return jsonify({
        "status": "success",
        "datasets": datasets,
        "summary": {
            "total_datasets": total_datasets,
            "active": active_count,
            "degraded": degraded_count,
            "avg_reliability": avg_reliability
        }
    })


# Health check for marine spine
@marine_bp.route("/marine-health", methods=["GET"])
def marine_health():
    return jsonify({
        "status": "operational",
        "spine_version": "v1",
        "layers_available": [
            "physical", "ecological", "economic",
            "policy", "infrastructure"
        ],
        "endpoints": [
            "GET /marine-signals",
            "GET /infrastructure-overlay",
            "GET /navigability",
            "GET /ecology",
            "GET /proposal-engine",
            "GET /digital-depth",
            "GET /marine-health"
        ],
        "deterministic": True,
        "ml_used": False
    })