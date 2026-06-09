"""
geo_output_builder.py  (MODIFIED — GeoJSON finalization)
──────────────────────────────────────────────────────────
NICAI - Ganga Basin Intelligence Engine

Every GeoJSON feature properties block includes:
  • score
  • level
  • color
  • delta (in scenario/delta layers)
  • reasoning
  • constraints

Outputs three layers:
  1. baseline   → scored without scenario
  2. scenario   → scored with modifications
  3. delta      → difference layer for map visualization
"""

from typing import List, Dict, Any, Optional


# COLOR MAP
# ─────────────────────────────────────────────

LEVEL_COLOR_MAP = {
    "HIGH":     "#2ecc71",   # Green
    "MEDIUM":   "#f39c12",   # Amber
    "LOW":      "#e74c3c",   # Red
    "REJECTED": "#7f8c8d"    # Grey
}

DELTA_COLOR_MAP = {
    "IMPROVED":   "#1abc9c",  # Teal
    "DECLINED":   "#e67e22",  # Orange
    "UNCHANGED":  "#95a5a6"   # Light grey
}

# Approximate Ganga Basin coordinates (lon, lat) for demo locations
LOCATION_COORDS = {
    "varanasi_terminal":      [82.9739, 25.3176],
    "allahabad_confluence":   [81.8463, 25.4358],
    "patna_river_port":       [85.1376, 25.5941],
    "kanpur_industrial_zone": [80.3319, 26.4499],
    "farakka_wetland":        [87.9186, 24.8119],
    "hajipur_hub":            [85.2119, 25.6891],
    "ghazipur_terminal":      [83.5785, 25.5849],
    "sultanganj_zone":        [86.7435, 25.2457],
    "bhagalpur_port":         [86.9842, 25.2425],
    "rajmahal_site":          [87.8299, 25.0445]
}

DEFAULT_COORD = [83.0, 25.5]  # Ganga Basin centroid fallback



# FEATURE BUILDERS
# ─────────────────────────────────────────────

def _get_coords(location_id: str) -> List[float]:
    return LOCATION_COORDS.get(location_id, DEFAULT_COORD)


def _build_reasoning(result: Dict[str, Any]) -> str:
    """Extracts concise reasoning from explanation string."""
    explanation = result.get("explanation", "")
    level = result.get("level", "")
    score = result.get("score", 0)

    constraints = result.get("constraints", {})
    hard = constraints.get("hard", [])
    soft = constraints.get("soft", [])

    parts = [f"Level: {level} | Score: {score}"]

    if hard:
        parts.append(f"Hard constraints triggered: {', '.join(hard)}")
    if soft:
        parts.append(f"Soft constraints: {', '.join(soft)}")

    fm = result.get("trace", {}).get("signal_to_factor_map", {})
    if fm:
        top_factors = list(set(fm.values()))[:3]
        parts.append(f"Key factors: {', '.join(top_factors)}")

    return " | ".join(parts)


def build_baseline_feature(result: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a single GeoJSON feature for baseline layer."""
    loc_id = result["location_id"]
    level = result.get("level", "LOW")

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": _get_coords(loc_id)
        },
        "properties": {
            "location_id":   loc_id,
            "model_type":    result.get("model_type"),
            "score":         result.get("score"),
            "level":         level,
            "color":         LEVEL_COLOR_MAP.get(level, "#7f8c8d"),
            "delta":         None,
            "reasoning":     _build_reasoning(result),
            "constraints":   result.get("constraints", {}),
            "scoring_model": result.get("scoring_model", {}),
            "trace_summary": {
                "contributing_signals": result.get("trace", {}).get("contributing_signal_ids", [])
            }
        }
    }


def build_scenario_feature(result: Dict[str, Any], baseline_score: Optional[float] = None) -> Dict[str, Any]:
    """Builds a GeoJSON feature for scenario layer, includes delta if baseline provided."""
    loc_id = result["location_id"]
    level = result.get("level", "LOW")
    score = result.get("score", 0)
    delta = round(score - baseline_score, 2) if baseline_score is not None else None

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": _get_coords(loc_id)
        },
        "properties": {
            "location_id":   loc_id,
            "model_type":    result.get("model_type"),
            "score":         score,
            "level":         level,
            "color":         LEVEL_COLOR_MAP.get(level, "#7f8c8d"),
            "delta":         delta,
            "reasoning":     _build_reasoning(result),
            "constraints":   result.get("constraints", {}),
            "scoring_model": result.get("scoring_model", {}),
            "trace_summary": {
                "contributing_signals": result.get("trace", {}).get("contributing_signal_ids", [])
            }
        }
    }


def build_delta_feature(delta_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a GeoJSON feature for the delta layer (change visualization)."""
    loc_id = delta_entry["location_id"]
    delta = delta_entry.get("delta", 0)

    if delta > 1:
        direction = "IMPROVED"
    elif delta < -1:
        direction = "DECLINED"
    else:
        direction = "UNCHANGED"

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": _get_coords(loc_id)
        },
        "properties": {
            "location_id":     loc_id,
            "score":           delta_entry.get("scenario_score"),
            "level":           delta_entry.get("scenario_level"),
            "color":           DELTA_COLOR_MAP[direction],
            "delta":           delta,
            "delta_direction": direction,
            "impact":          delta_entry.get("impact"),
            "reasoning":       delta_entry.get("delta_reason", ""),
            "baseline_score":  delta_entry.get("baseline_score"),
            "baseline_level":  delta_entry.get("baseline_level"),
            "level_changed":   delta_entry.get("level_changed", False),
            "constraints":     {}   # Delta layer doesn't re-expose full constraint block
        }
    }



# LAYER BUILDERS
# ─────────────────────────────────────────────

def build_baseline_geojson(
    results: List[Dict[str, Any]],
    model_type: str
) -> Dict[str, Any]:
    """Builds complete baseline GeoJSON FeatureCollection."""
    features = [build_baseline_feature(r) for r in results]

    return {
        "type": "FeatureCollection",
        "metadata": {
            "layer_type": "baseline",
            "model_type": model_type,
            "feature_count": len(features),
            "legend": _build_legend("level")
        },
        "features": features
    }


def build_scenario_geojson(
    scenario_results: List[Dict[str, Any]],
    baseline_results: List[Dict[str, Any]],
    model_type: str,
    scenario_id: str = "scenario"
) -> Dict[str, Any]:
    """Builds scenario GeoJSON FeatureCollection."""
    baseline_map = {r["location_id"]: r["score"] for r in baseline_results}
    features = [
        build_scenario_feature(r, baseline_map.get(r["location_id"]))
        for r in scenario_results
    ]

    return {
        "type": "FeatureCollection",
        "metadata": {
            "layer_type": "scenario",
            "scenario_id": scenario_id,
            "model_type": model_type,
            "feature_count": len(features),
            "legend": _build_legend("level")
        },
        "features": features
    }


def build_delta_geojson(
    delta_entries: List[Dict[str, Any]],
    model_type: str,
    scenario_id: str = "scenario"
) -> Dict[str, Any]:
    """Builds delta GeoJSON FeatureCollection for change visualization."""
    features = [build_delta_feature(d) for d in delta_entries]

    return {
        "type": "FeatureCollection",
        "metadata": {
            "layer_type": "delta",
            "scenario_id": scenario_id,
            "model_type": model_type,
            "feature_count": len(features),
            "legend": _build_legend("delta")
        },
        "features": features
    }


def build_all_layers(
    baseline_results: List[Dict[str, Any]],
    scenario_results: List[Dict[str, Any]],
    delta_entries: List[Dict[str, Any]],
    model_type: str,
    scenario_id: str = "scenario"
) -> Dict[str, Any]:
    """Builds all three layers in one call — for UI handshake."""
    return {
        "baseline": build_baseline_geojson(baseline_results, model_type),
        "scenario": build_scenario_geojson(scenario_results, baseline_results, model_type, scenario_id),
        "delta":    build_delta_geojson(delta_entries, model_type, scenario_id)
    }



# LEGEND STRUCTURE
# ─────────────────────────────────────────────

def _build_legend(legend_type: str = "level") -> List[Dict[str, str]]:
    if legend_type == "level":
        return [
            {"label": "HIGH",     "color": LEVEL_COLOR_MAP["HIGH"],     "description": "Score ≥ threshold — suitable"},
            {"label": "MEDIUM",   "color": LEVEL_COLOR_MAP["MEDIUM"],   "description": "Score in mid-range — conditionally suitable"},
            {"label": "LOW",      "color": LEVEL_COLOR_MAP["LOW"],      "description": "Score below threshold — not recommended"},
            {"label": "REJECTED", "color": LEVEL_COLOR_MAP["REJECTED"], "description": "Hard constraint triggered — infrastructure prohibited"}
        ]
    elif legend_type == "delta":
        return [
            {"label": "IMPROVED",  "color": DELTA_COLOR_MAP["IMPROVED"],  "description": "Score increased under scenario"},
            {"label": "DECLINED",  "color": DELTA_COLOR_MAP["DECLINED"],  "description": "Score decreased under scenario"},
            {"label": "UNCHANGED", "color": DELTA_COLOR_MAP["UNCHANGED"], "description": "Score unchanged under scenario"}
        ]
    return []


def get_legend_structure() -> Dict[str, Any]:
    """Returns complete legend structure for UI handshake."""
    return {
        "level_legend": _build_legend("level"),
        "delta_legend":  _build_legend("delta"),
        "color_reference": {**LEVEL_COLOR_MAP, **DELTA_COLOR_MAP}
    }



# QUICK SELF-TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, ".")
    from scoring_engine import score_all

    entities = [
        {
            "location_id": "varanasi_terminal",
            "properties": {
                "river_stability_score": 78, "terminal_proximity_score": 85,
                "logistics_access_score": 70, "water_quality_index": 60,
                "traffic_potential_score": 75, "in_wetland": False,
                "in_flood_zone": False, "env_clearance": True, "depth_score": 65
            }
        },
        {
            "location_id": "patna_river_port",
            "properties": {
                "river_stability_score": 85, "terminal_proximity_score": 80,
                "logistics_access_score": 75, "water_quality_index": 55,
                "traffic_potential_score": 80, "in_wetland": False,
                "in_flood_zone": False, "env_clearance": True, "depth_score": 72
            }
        }
    ]

    baseline = score_all(entities, "inland_port")
    scenario = score_all(entities, "inland_port", custom_weights={
        "river_stability": 0.10, "terminal_proximity": 0.10,
        "logistics_access": 0.50, "water_quality": 0.15, "traffic_potential": 0.15
    })

    # Minimal delta
    delta = [
        {
            "location_id": e["location_id"],
            "baseline_score": b["score"], "baseline_level": b["level"],
            "scenario_score": s["score"], "scenario_level": s["level"],
            "delta": round(s["score"] - b["score"], 2),
            "impact": "MODERATE_IMPACT", "level_changed": b["level"] != s["level"],
            "delta_reason": "Test delta"
        }
        for e, b, s in zip(entities, baseline, scenario)
    ]

    layers = build_all_layers(baseline, scenario, delta, "inland_port", "high_logistics")
    print(json.dumps(layers["baseline"], indent=2))
    print("\nLegend:")
    print(json.dumps(get_legend_structure(), indent=2))
