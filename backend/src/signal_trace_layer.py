"""
signal_trace_layer.py
─────────────────────
NICAI - Ganga Basin Intelligence Engine
Signal Trace Layer

Adds full traceability to every scored entity:
  • source_signals   → which raw signal IDs fed each factor
  • contributing_signal_ids → flat list of all signals used
  • signal_to_factor_map   → signal_id → factor_name mapping

"""

from typing import Dict, List, Any


# SIGNAL REGISTRY
# Maps raw CSV field names → canonical signal IDs → factor names
# Each signal ID encodes: source_dataset + field_name + version
# ─────────────────────────────────────────────

SIGNAL_REGISTRY: Dict[str, Dict[str, str]] = {
    # ── River / Hydrological signals ──────────────────────────────
    "river_stability_score":    {"signal_id": "CWC_RIV_STAB_v1",  "factor": "river_stability",    "source": "river"},
    "water_quality_index":      {"signal_id": "CPCB_WQI_v1",       "factor": "water_quality",      "source": "river"},
    "flow_turbulence_index":    {"signal_id": "CWC_TURB_v1",       "factor": "turbulence",         "source": "river"},
    "turbulence_index":         {"signal_id": "CWC_TURB_v1",       "factor": "turbulence",         "source": "river"},
    "depth_score":              {"signal_id": "CWC_DEPTH_v1",      "factor": "navigable_depth",    "source": "river"},
    "seasonal_flow_score":      {"signal_id": "CWC_SEAS_v1",       "factor": "seasonal_flow",      "source": "river"},

    # ── Logistics signals ─────────────────────────────────────────
    "logistics_access_score":   {"signal_id": "IWAI_LOG_v1",       "factor": "logistics_access",   "source": "logistics"},
    "terminal_proximity_score": {"signal_id": "IWAI_TERM_v1",      "factor": "terminal_proximity", "source": "logistics"},
    "traffic_potential_score":  {"signal_id": "IWAI_TRAF_v1",      "factor": "traffic_potential",  "source": "logistics"},
    "logistics_park_quality":   {"signal_id": "IWAI_PARK_v1",      "factor": "logistics_park",     "source": "logistics"},
    "connectivity_score":       {"signal_id": "IWAI_CONN_v1",      "factor": "connectivity",       "source": "logistics"},
    "terminal_density_score":   {"signal_id": "IWAI_DENS_v1",      "factor": "terminal_density",   "source": "logistics"},

    # ── Water Quality signals ─────────────────────────────────────
    "do_score":                 {"signal_id": "CPCB_DO_v1",        "factor": "dissolved_oxygen",   "source": "water_quality"},
    "bod_score":                {"signal_id": "CPCB_BOD_v1",       "factor": "biochemical_demand", "source": "water_quality"},
    "pollution_index":          {"signal_id": "CPCB_POLL_v1",      "factor": "pollution_level",    "source": "water_quality"},
    "coliform_score":           {"signal_id": "CPCB_COL_v1",       "factor": "coliform_count",     "source": "water_quality"},

    # ── Environmental / Constraint signals ───────────────────────
    "in_wetland":               {"signal_id": "ENV_WETLAND_v1",    "factor": "wetland_constraint", "source": "environmental"},
    "in_flood_zone":            {"signal_id": "ENV_FLOOD_v1",      "factor": "flood_constraint",   "source": "environmental"},
    "env_clearance":            {"signal_id": "ENV_CLEAR_v1",      "factor": "env_clearance",      "source": "environmental"},
    "critical_depth_flag":      {"signal_id": "ENV_CDEPTH_v1",     "factor": "critical_depth",     "source": "environmental"},
    "extreme_pollution_flag":   {"signal_id": "ENV_XPOLL_v1",      "factor": "extreme_pollution",  "source": "environmental"},

    # ── Urban / Demand signals ────────────────────────────────────
    "urban_proximity_score":    {"signal_id": "CENSUS_URB_v1",     "factor": "urban_proximity",    "source": "demand"},
    "urban_market_access":      {"signal_id": "CENSUS_MKTACC_v1",  "factor": "market_access",      "source": "demand"},
    "multi_node_proximity":     {"signal_id": "IWAI_NODPROX_v1",   "factor": "node_proximity",     "source": "logistics"},
}



# FACTOR → SIGNAL GROUPS (by model)
# ─────────────────────────────────────────────

MODEL_SIGNAL_GROUPS = {
    "inland_port": [
        "river_stability_score", "terminal_proximity_score",
        "logistics_access_score", "water_quality_index",
        "traffic_potential_score", "in_wetland", "in_flood_zone",
        "depth_score", "env_clearance", "pollution_index"
    ],
    "seaplane": [
        "flow_turbulence_index", "turbulence_index", "water_quality_index",
        "traffic_potential_score", "urban_proximity_score", "env_clearance",
        "in_wetland", "do_score", "bod_score"
    ],
    "hub_spoke": [
        "multi_node_proximity", "logistics_park_quality", "terminal_density_score",
        "connectivity_score", "urban_market_access", "traffic_potential_score",
        "logistics_access_score", "in_wetland", "in_flood_zone"
    ]
}


def build_source_signals(entity_properties: Dict[str, Any], model_type: str) -> Dict[str, List[str]]:
    """
    Given raw entity properties and model type, return source_signals dict:
    {
      "river": [...signal_ids],
      "logistics": [...signal_ids],
      "water_quality": [...signal_ids],
      "environmental": [...signal_ids],
      "demand": [...signal_ids]
    }
    Only includes signals that are actually present in the entity.
    """
    relevant_fields = MODEL_SIGNAL_GROUPS.get(model_type, list(SIGNAL_REGISTRY.keys()))
    grouped: Dict[str, List[str]] = {}

    for field in relevant_fields:
        if field in entity_properties and field in SIGNAL_REGISTRY:
            meta = SIGNAL_REGISTRY[field]
            source = meta["source"]
            sig_id = meta["signal_id"]
            if source not in grouped:
                grouped[source] = []
            if sig_id not in grouped[source]:
                grouped[source].append(sig_id)

    return grouped


def build_contributing_signal_ids(source_signals: Dict[str, List[str]]) -> List[str]:
    """
    Flatten source_signals into a single sorted list of unique signal IDs.
    """
    all_ids = []
    for ids in source_signals.values():
        all_ids.extend(ids)
    return sorted(set(all_ids))


def build_signal_to_factor_map(entity_properties: Dict[str, Any], model_type: str) -> Dict[str, str]:
    """
    Returns: { "signal_id": "factor_name" } for all signals present in this entity.
    """
    relevant_fields = MODEL_SIGNAL_GROUPS.get(model_type, list(SIGNAL_REGISTRY.keys()))
    mapping = {}

    for field in relevant_fields:
        if field in entity_properties and field in SIGNAL_REGISTRY:
            meta = SIGNAL_REGISTRY[field]
            mapping[meta["signal_id"]] = meta["factor"]

    return mapping


def attach_trace(result: Dict[str, Any], entity_properties: Dict[str, Any], model_type: str) -> Dict[str, Any]:
    """
    Main entry point. Attaches full trace block to a scored result dict.

    Adds:
      result["trace"] = {
        "source_signals": { "river": [...], "logistics": [...], ... },
        "contributing_signal_ids": [...],
        "signal_to_factor_map": { "signal_id": "factor_name" }
      }

    """
    source_signals = build_source_signals(entity_properties, model_type)
    contributing_ids = build_contributing_signal_ids(source_signals)
    signal_factor_map = build_signal_to_factor_map(entity_properties, model_type)

    result["trace"] = {
        "source_signals": source_signals,
        "contributing_signal_ids": contributing_ids,
        "signal_to_factor_map": signal_factor_map
    }

    return result


# QUICK SELF-TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    sample_entity = {
        "location_id": "varanasi_terminal",
        "river_stability_score": 78,
        "terminal_proximity_score": 85,
        "logistics_access_score": 70,
        "water_quality_index": 60,
        "traffic_potential_score": 75,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "pollution_index": 30
    }

    result = {"location_id": "varanasi_terminal", "score": 74.5, "level": "HIGH"}
    result = attach_trace(result, sample_entity, "inland_port")

    import json
    print(json.dumps(result, indent=2))
