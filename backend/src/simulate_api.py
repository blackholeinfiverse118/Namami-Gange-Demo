"""
simulate_api.py  (MODIFIED — contract lock + demo hardening)
──────────────────────────────────────────────────────────────
NICAI - Ganga Basin Intelligence Engine

  1. Raw base_data injection REMOVED for demo
  2. Only dataset-driven inputs OR predefined scenarios accepted
  3. scenario_metadata block added to all responses
  4. All overrides flagged — never silent
"""

import json
import os
import sys
from flask import Blueprint, request, jsonify
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(__file__))

from scoring_engine import score_entity, score_all, SCORING_MODELS
from constraint_engine import HARD_CONSTRAINTS, SOFT_CONSTRAINTS

simulate_bp = Blueprint("simulate", __name__)


# PREDEFINED SCENARIOS (demo-safe inputs)
# ─────────────────────────────────────────────

PREDEFINED_SCENARIOS = {
    "high_logistics": {
        "scenario_id": "high_logistics",
        "description": "Boost logistics weight — policy push for supply-chain infrastructure",
        "modifications": {
            "priority_weights": {
                "river_stability": 0.10,
                "terminal_proximity": 0.10,
                "logistics_access": 0.50,
                "water_quality": 0.15,
                "traffic_potential": 0.15
            }
        }
    },
    "env_priority": {
        "scenario_id": "env_priority",
        "description": "Environmental quality elevated — green corridor policy",
        "modifications": {
            "priority_weights": {
                "river_stability": 0.20,
                "terminal_proximity": 0.10,
                "logistics_access": 0.15,
                "water_quality": 0.40,
                "traffic_potential": 0.15
            }
        }
    },
    "connectivity_focus": {
        "scenario_id": "connectivity_focus",
        "description": "Hub-spoke connectivity prioritized for last-mile optimization",
        "modifications": {
            "priority_weights": {
                "river_stability": 0.15,
                "terminal_proximity": 0.25,
                "logistics_access": 0.30,
                "water_quality": 0.15,
                "traffic_potential": 0.15
            }
        }
    },
    "relaxed_logistics": {
        "scenario_id": "relaxed_logistics",
        "description": "Soft logistics constraint bypassed — planned future infrastructure",
        "modifications": {
            "exclude_zones": ["logistics_absence"]
        }
    }
}


# DATASET REGISTRY (approved input sources)
# ─────────────────────────────────────────────

APPROVED_DATASETS = {
    "ganga_basin_iwai_2024": "data_raw/ganga_basin_locations.csv",
    "ganga_basin_reference": "data_raw/locations.json",
    "demo_baseline": "demo_cases/demo_case_1.json"
}


def load_from_dataset(dataset_id: str) -> Optional[List[Dict[str, Any]]]:
    """Loads entities from an approved dataset by ID."""
    if dataset_id not in APPROVED_DATASETS:
        return None
    path = os.path.join(os.path.dirname(__file__), "..", APPROVED_DATASETS[dataset_id])
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("entities", [])


def load_demo_entities() -> List[Dict[str, Any]]:
    """Fallback demo entities for simulation."""
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
                "logistics_access_score": 20,   # → soft constraint: logistics_absence
                "water_quality_index": 52,
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
                "logistics_access_score": 80, "water_quality_index": 18,   # → HARD: extreme_pollution
                "traffic_potential_score": 75, "in_wetland": False,
                "in_flood_zone": False, "env_clearance": True,
                "pollution_index": 85, "depth_score": 55
            }
        }
    ]



# SCENARIO METADATA BUILDER
# ─────────────────────────────────────────────

def build_scenario_metadata(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds the scenario_metadata block for response.
    Always explicit — never silent about what changed.
    """
    mods = scenario.get("modifications", {})
    weights_changed = mods.get("priority_weights", {})
    constraints_overridden = mods.get("exclude_zones", [])

    return {
        "scenario_id":            scenario.get("scenario_id", "custom"),
        "description":            scenario.get("description", ""),
        "weights_changed":        weights_changed,
        "constraints_overridden": constraints_overridden,
        "is_predefined":          scenario.get("scenario_id") in PREDEFINED_SCENARIOS
    }



# DELTA COMPUTATION
# ─────────────────────────────────────────────

def compute_delta(baseline_results: List[Dict], scenario_results: List[Dict]) -> List[Dict]:
    """
    Computes delta between baseline and scenario for each location.
    Returns sensitivity analysis per location.
    """
    baseline_map = {r["location_id"]: r for r in baseline_results}
    delta_list = []

    for s_result in scenario_results:
        loc_id = s_result["location_id"]
        b_result = baseline_map.get(loc_id)

        if not b_result:
            continue

        b_score = b_result["score"]
        s_score = s_result["score"]
        delta = round(s_score - b_score, 2)

        if abs(delta) >= 15:
            impact = "HIGH_IMPACT"
        elif abs(delta) >= 5:
            impact = "MODERATE_IMPACT"
        else:
            impact = "LOW_IMPACT"

        delta_list.append({
            "location_id":     loc_id,
            "baseline_score":  b_score,
            "baseline_level":  b_result["level"],
            "scenario_score":  s_score,
            "scenario_level":  s_result["level"],
            "delta":           delta,
            "impact":          impact,
            "level_changed":   b_result["level"] != s_result["level"],
            "delta_reason":    _explain_delta(b_result, s_result, delta)
        })

    return sorted(delta_list, key=lambda x: abs(x["delta"]), reverse=True)


def _explain_delta(baseline: Dict, scenario: Dict, delta: float) -> str:
    if delta > 0:
        return f"Score improved by {abs(delta)} pts under scenario weights/overrides"
    elif delta < 0:
        return f"Score decreased by {abs(delta)} pts under scenario weights/overrides"
    else:
        return "Score unchanged — scenario modifications did not affect this location"



# ENDPOINTS
# ─────────────────────────────────────────────

@simulate_bp.route("/simulate", methods=["POST"])
def simulate():
    """
    POST /simulate — LOCKED CONTRACT

    Accepted body formats:
    1. Predefined scenario by ID:
       { "scenario_id": "high_logistics", "model_type": "inland_port" }

    2. Dataset-driven with custom scenario:
       { "dataset_id": "ganga_basin_reference", "scenario": {...}, "model_type": "inland_port" }

    RAW base_data injection is NOT accepted in demo mode.

    Returns: baseline, scenario, delta, scenario_metadata
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    model_type = body.get("model_type", "inland_port")
    if model_type not in SCORING_MODELS:
        return jsonify({"error": f"Invalid model_type. Must be one of: {list(SCORING_MODELS.keys())}"}), 400

    # ── Reject raw base_data injection ────────────────────────────
    if "base_data" in body:
        return jsonify({
            "error": "Direct base_data injection is disabled in demo mode.",
            "hint": "Use 'dataset_id' with an approved dataset, or 'scenario_id' for a predefined scenario.",
            "approved_datasets": list(APPROVED_DATASETS.keys()),
            "predefined_scenarios": list(PREDEFINED_SCENARIOS.keys())
        }), 400

    # ── Resolve scenario ──────────────────────────────────────────
    scenario_id = body.get("scenario_id")
    if scenario_id:
        if scenario_id not in PREDEFINED_SCENARIOS:
            return jsonify({
                "error": f"Unknown scenario_id: '{scenario_id}'",
                "available": list(PREDEFINED_SCENARIOS.keys())
            }), 400
        scenario = PREDEFINED_SCENARIOS[scenario_id]
    else:
        scenario = body.get("scenario")
        if not scenario:
            return jsonify({"error": "Provide either 'scenario_id' or 'scenario' object"}), 400

    # ── Resolve entities ──────────────────────────────────────────
    dataset_id = body.get("dataset_id")
    if dataset_id:
        entities = load_from_dataset(dataset_id)
        if entities is None:
            return jsonify({
                "error": f"Dataset '{dataset_id}' not found or not approved.",
                "approved_datasets": list(APPROVED_DATASETS.keys())
            }), 400
    else:
        entities = load_demo_entities()

    # ── Extract modifications ─────────────────────────────────────
    mods = scenario.get("modifications", {})
    custom_weights = mods.get("priority_weights")
    overrides = mods.get("exclude_zones", [])

    # ── Validate custom weights ───────────────────────────────────
    if custom_weights:
        weight_sum = round(sum(custom_weights.values()), 4)
        if abs(weight_sum - 1.0) > 0.01:
            return jsonify({
                "error": f"Weights must sum to 1.0. Got: {weight_sum}",
                "weights_provided": custom_weights
            }), 400

    # ── Run baseline ──────────────────────────────────────────────
    try:
        baseline_results = score_all(entities, model_type)
        scenario_results = score_all(entities, model_type, custom_weights, overrides)
    except Exception as e:
        return jsonify({"error": f"Scoring failed: {str(e)}"}), 500

    delta_results = compute_delta(baseline_results, scenario_results)
    scenario_metadata = build_scenario_metadata(scenario)

    return jsonify({
        "status": "success",
        "model_type": model_type,
        "scenario_metadata": scenario_metadata,
        "baseline": baseline_results,
        "scenario": scenario_results,
        "delta": delta_results,
        "summary": {
            "total_locations": len(entities),
            "high_impact_changes": sum(1 for d in delta_results if d["impact"] == "HIGH_IMPACT"),
            "level_changes": sum(1 for d in delta_results if d["level_changed"]),
            "most_sensitive_location": delta_results[0]["location_id"] if delta_results else None
        }
    })


@simulate_bp.route("/simulate/baseline", methods=["POST"])
def simulate_baseline():
    """
    POST /simulate/baseline
    Runs baseline scoring only — no scenario modifications.
    Body: { "model_type": "inland_port", "dataset_id": "..." (optional) }
    """
    body = request.get_json(silent=True) or {}
    model_type = body.get("model_type", "inland_port")

    if model_type not in SCORING_MODELS:
        return jsonify({"error": f"Invalid model_type"}), 400

    dataset_id = body.get("dataset_id")
    if dataset_id:
        entities = load_from_dataset(dataset_id)
        if entities is None:
            return jsonify({"error": f"Dataset '{dataset_id}' not found"}), 400
    else:
        entities = load_demo_entities()

    try:
        results = score_all(entities, model_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "status": "success",
        "model_type": model_type,
        "baseline": results,
        "count": len(results)
    })


@simulate_bp.route("/simulate/multi", methods=["POST"])
def simulate_multi():
    """
    POST /simulate/multi
    Runs multiple predefined scenarios and returns comparison.
    Body: {
      "scenario_ids": ["high_logistics", "env_priority"],
      "model_type": "inland_port"
    }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    model_type = body.get("model_type", "inland_port")
    scenario_ids = body.get("scenario_ids", [])

    if not scenario_ids:
        return jsonify({"error": "'scenario_ids' list is required"}), 400

    invalid = [s for s in scenario_ids if s not in PREDEFINED_SCENARIOS]
    if invalid:
        return jsonify({
            "error": f"Unknown scenario_ids: {invalid}",
            "available": list(PREDEFINED_SCENARIOS.keys())
        }), 400

    entities = load_demo_entities()

    try:
        baseline_results = score_all(entities, model_type)
    except Exception as e:
        return jsonify({"error": f"Baseline scoring failed: {str(e)}"}), 500

    scenario_comparisons = []
    for sid in scenario_ids:
        scenario = PREDEFINED_SCENARIOS[sid]
        mods = scenario.get("modifications", {})
        custom_weights = mods.get("priority_weights")
        overrides = mods.get("exclude_zones", [])

        try:
            s_results = score_all(entities, model_type, custom_weights, overrides)
            delta = compute_delta(baseline_results, s_results)
            scenario_comparisons.append({
                "scenario_id": sid,
                "description": scenario["description"],
                "scenario_metadata": build_scenario_metadata(scenario),
                "results": s_results,
                "delta": delta,
                "summary": {
                    "high_impact_changes": sum(1 for d in delta if d["impact"] == "HIGH_IMPACT"),
                    "level_changes": sum(1 for d in delta if d["level_changed"]),
                    "most_sensitive_location": delta[0]["location_id"] if delta else None
                }
            })
        except Exception as e:
            scenario_comparisons.append({
                "scenario_id": sid,
                "error": str(e)
            })

    return jsonify({
        "status": "success",
        "model_type": model_type,
        "baseline": baseline_results,
        "scenarios": scenario_comparisons,
        "scenario_count": len(scenario_comparisons)
    })
