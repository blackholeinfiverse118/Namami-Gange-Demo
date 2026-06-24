"""
api.py  (MODIFIED — API contract standardization)
───────────────────────────────────────────────────
NICAI - Ganga Basin Intelligence Engine

All endpoints return strict contract-compliant responses.
GET /results → { location_id, model_type, score, level, trace, constraints, explanation }
GET /health   → system status
GET /locations → location entities
POST /analyze-location → single entity scoring
"""

import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))

from scoring_engine import score_entity, score_all, SCORING_MODELS
from signal_trace_layer import attach_trace
from constraint_engine import evaluate_constraints, build_constraint_block

app = Flask(__name__)
CORS(app)

# DATA LOADING HELPERS
# ─────────────────────────────────────────────

def load_sample_entities() -> List[Dict[str, Any]]:
    """
    Loads location entities from the SQLite database.
    """
    try:
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT location_id, name, latitude, longitude, summary_metrics FROM locations")
        rows = cursor.fetchall()
        
        entities = []
        for r in rows:
            entities.append({
                "location_id": r["location_id"],
                "name": r["name"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "summary_metrics": json.loads(r["summary_metrics"])
            })
        conn.close()
        return entities
    except Exception as e:
        print(f"[api] Error loading entities from SQLite: {e}. Falling back to mock data.")
        # Fallback reference locations
        return [
            {
                "location_id": "varanasi_terminal",
                "properties": {
                    "river_stability_score": 78, "terminal_proximity_score": 85,
                    "logistics_access_score": 70, "water_quality_index": 60,
                    "traffic_potential_score": 75, "in_wetland": False,
                    "in_flood_zone": False, "env_clearance": True,
                    "pollution_index": 45, "depth_score": 65
                }
            },
            {
                "location_id": "allahabad_confluence",
                "properties": {
                    "river_stability_score": 82, "terminal_proximity_score": 72,
                    "logistics_access_score": 68, "water_quality_index": 52,
                    "traffic_potential_score": 70, "in_wetland": False,
                    "in_flood_zone": False, "env_clearance": True,
                    "pollution_index": 50, "depth_score": 70
                }
            },
            {
                "location_id": "patna_river_port",
                "properties": {
                    "river_stability_score": 85, "terminal_proximity_score": 80,
                    "logistics_access_score": 75, "water_quality_index": 55,
                    "traffic_potential_score": 80, "in_wetland": False,
                    "in_flood_zone": False, "env_clearance": True,
                    "pollution_index": 40, "depth_score": 72
                }
            },
            {
                "location_id": "kanpur_industrial_zone",
                "properties": {
                    "river_stability_score": 60, "terminal_proximity_score": 65,
                    "logistics_access_score": 80, "water_quality_index": 18,
                    "traffic_potential_score": 75, "in_wetland": False,
                    "in_flood_zone": False, "env_clearance": True,
                    "pollution_index": 85, "depth_score": 55
                }
            },
            {
                "location_id": "farakka_wetland",
                "properties": {
                    "river_stability_score": 74, "terminal_proximity_score": 60,
                    "logistics_access_score": 45, "water_quality_index": 48,
                    "traffic_potential_score": 40, "in_wetland": True,
                    "in_flood_zone": False, "env_clearance": False,
                    "pollution_index": 35, "depth_score": 60
                }
            },
            {
                "location_id": "hajipur_hub",
                "properties": {
                    "river_stability_score": 72, "terminal_proximity_score": 68,
                    "logistics_access_score": 62, "water_quality_index": 58,
                    "traffic_potential_score": 65, "in_wetland": False,
                    "in_flood_zone": False, "env_clearance": True,
                    "pollution_index": 42, "depth_score": 62,
                    "multi_node_proximity": 70, "logistics_park_quality": 65,
                    "terminal_density_score": 60, "connectivity_score": 68,
                    "urban_market_access": 72
                }
            }
        ]



# CONTRACT RESPONSE BUILDER
# ─────────────────────────────────────────────

def build_contract_response(scored: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforces the GET /results contract shape.
    Returns ONLY the contract-defined fields.
    """
    return {
        "location_id":  scored.get("location_id"),
        "model_type":   scored.get("model_type"),
        "score":        scored.get("score"),
        "level":        scored.get("level"),
        "trace":        scored.get("trace"),
        "constraints":  scored.get("constraints"),
        "explanation":  scored.get("explanation"),
        "scoring_model": scored.get("scoring_model")
    }


def error_response(message: str, code: int = 400) -> tuple:
    return jsonify({"error": message, "status": "error"}), code



# ENDPOINTS
# ─────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "system": "NICAI – Ganga Basin Suitability Intelligence Engine",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "GET /health":             "System health check",
            "GET /locations":          "All location entities",
            "GET /results":            "All suitability results (filterable)",
            "POST /analyze-location":  "Score a custom location entity"
        },
        "models_available": list(SCORING_MODELS.keys())
    })


@app.route("/health", methods=["GET"])
def health():
    entities = load_sample_entities()
    return jsonify({
        "status": "healthy",
        "entities_loaded": len(entities),
        "models_available": list(SCORING_MODELS.keys()),
        "determinism": "guaranteed",
        "ml_used": False
    })


@app.route("/locations", methods=["GET"])
def locations():
    entities = load_sample_entities()
    return jsonify({
        "count": len(entities),
        "locations": entities
    })


@app.route("/results", methods=["GET"])
def results():
    """
    GET /results
    Optional query params:
      ?model=inland_port|seaplane|hub_spoke
      ?level=HIGH|MEDIUM|LOW|REJECTED
      ?location_id=<id>

    Returns contract-compliant result objects.
    """
    model_filter   = request.args.get("model")
    level_filter   = request.args.get("level")
    location_filter = request.args.get("location_id")

    model_type = model_filter if model_filter in SCORING_MODELS else "inland_port"
    entities = load_sample_entities()

    if location_filter:
        entities = [e for e in entities if e.get("location_id") == location_filter]

    try:
        scored_list = score_all(entities, model_type)
    except Exception as e:
        return error_response(str(e), 500)

    results_out = [build_contract_response(s) for s in scored_list]

    if level_filter:
        results_out = [r for r in results_out if r["level"] == level_filter.upper()]

    return jsonify({
        "model_type": model_type,
        "count": len(results_out),
        "results": results_out
    })


@app.route("/analyze-location", methods=["POST"])
def analyze_location():
    """
    POST /analyze-location
    Body: { "entity": {...}, "model_type": "inland_port" }
    Scores a single custom entity and returns contract-compliant result.
    """
    body = request.get_json(silent=True)
    if not body:
        return error_response("Request body must be valid JSON")

    entity = body.get("entity")
    model_type = body.get("model_type", "inland_port")

    if not entity:
        return error_response("'entity' field is required")

    if model_type not in SCORING_MODELS:
        return error_response(f"Invalid model_type. Must be one of: {list(SCORING_MODELS.keys())}")

    try:
        scored = score_entity(entity, model_type)
        return jsonify(build_contract_response(scored))
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"Scoring error: {str(e)}", 500)


@app.route("/dataset-health", methods=["GET"])
def dataset_health():

    from source_health_service import SourceHealthService

    service = SourceHealthService()

    return jsonify({
        "status": "success",
        "datasets": service.get_dataset_health()
    })


@app.route("/dataset-freshness", methods=["GET"])
def dataset_freshness():

    from source_health_service import SourceHealthService

    service = SourceHealthService()

    data = service.get_dataset_health()

    return jsonify({
        "status": "success",
        "freshness_report": data
    })


@app.route("/source-status", methods=["GET"])
def source_status():

    from source_health_service import SourceHealthService

    service = SourceHealthService()

    data = service.get_dataset_health()

    healthy = len(
        [d for d in data if d["health_status"] == "HEALTHY"]
    )

    warning = len(
        [d for d in data if d["health_status"] == "WARNING"]
    )

    stale = len(
        [d for d in data if d["health_status"] == "STALE"]
    )

    return jsonify({
    "status": "success",
    "healthy_sources": healthy,
    "warning_sources": warning,
    "stale_sources": stale,
    "total_sources": len(data),
    "sources": data
})


@app.route("/intelligence-health", methods=["GET"])
def intelligence_health():

    from source_health_service import SourceHealthService

    service = SourceHealthService()

    data = service.get_dataset_health()

    healthy = len(
        [d for d in data if d["health_status"] == "HEALTHY"]
    )

    score = round(
        (healthy / len(data)) * 100,
        2
    ) if data else 0

    return jsonify({
        "status": "healthy",
        "intelligence_health_score": score,
        "datasets_monitored": len(data),
        "healthy_sources": healthy
    })



# ERROR HANDLERS
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "status": 405}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500


@app.route("/summary", methods=["GET"])
def summary():
    """
    GET /summary
    Optional query param: ?model=inland_port|seaplane|hub_spoke
    Returns composite metrics: avg_suitability, basin_alerts, total_locations, level_counts
    """
    model_filter = request.args.get("model")
    model_type = model_filter if model_filter in SCORING_MODELS else "inland_port"
    entities = load_sample_entities()
    
    try:
        scored_list = score_all(entities, model_type)
    except Exception as e:
        return error_response(str(e), 500)
        
    scores = [s["score"] for s in scored_list if s["level"] != "REJECTED"]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    
    levels = [s["level"] for s in scored_list]
    alerts_count = levels.count("REJECTED") + levels.count("LOW")
    
    return jsonify({
        "status": "success",
        "model_type": model_type,
        "avg_suitability": avg_score,
        "basin_alerts": alerts_count,
        "total_locations": len(entities),
        "level_counts": {
            "HIGH": levels.count("HIGH"),
            "MEDIUM": levels.count("MEDIUM"),
            "LOW": levels.count("LOW"),
            "REJECTED": levels.count("REJECTED")
        }
    })


if __name__ == "__main__":
    print("NICAI API -- Starting on http://localhost:5000")
    from db import init_db
    init_db()
    from simulate_api import simulate_bp
    from marine_api import marine_bp
    app.register_blueprint(simulate_bp)
    app.register_blueprint(marine_bp)
    app.run(debug=False, host="0.0.0.0", port=5000)