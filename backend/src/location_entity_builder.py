"""
location_entity_builder.py

This file groups nearby signals into location entities.
Each entity represents a real-world location (like a city).

Then we calculate summary metrics for each location,
which will be used by scoring models.
"""

import math
from src.data_adapter import load_all_signals


# Radius (in km) to group nearby signals into one location
CLUSTER_RADIUS_KM = 75



# DISTANCE FUNCTION (HAVERSINE)

# Calculate distance between two lat/lon points
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))



# CREATE ANCHORS FROM REAL DATA

# Use urban centers (cities) as anchors
# Each city becomes one evaluation location

def _dynamic_anchors(signals):
    anchors = []

    for i, s in enumerate(
        [s for s in signals if s["signal_type"] == "urban_center"], start=1
    ):
        anchors.append((
            f"LOC{i:03d}",          # clean LOC001, LOC002... format for UI
            s["location_name"],
            s["latitude"],
            s["longitude"]
        ))

    return anchors


# BUILD SUMMARY METRICS FOR EACH LOCATION

# Combine all signals in a location into useful averages/counts
def _summarise(signals_by_type):
    s = signals_by_type

    # River data  
    river_sigs = s.get("river_station", [])
    if river_sigs:
        avg_stability = sum(r["metrics"]["flow_stability_code"] for r in river_sigs) / len(river_sigs)
        avg_nav_depth = sum(r["metrics"]["nav_depth_m"] for r in river_sigs) / len(river_sigs)
        avg_cv        = sum(r["metrics"]["flow_cv_proxy"] for r in river_sigs) / len(river_sigs)
        flood_prone   = max(r["metrics"]["flood_prone"] for r in river_sigs)
        avg_env_sens  = sum(r["metrics"]["env_sensitivity_code"] for r in river_sigs) / len(river_sigs)
    else:
        # Default values if no river data found
        avg_stability, avg_nav_depth, avg_cv = 1.0, 1.0, 99.0
        flood_prone, avg_env_sens = 1, 1.0

    # Water quality
    wq_sigs = s.get("water_quality_station", [])
    if wq_sigs:
        avg_do = sum(w["metrics"]["do_mg_l"] for w in wq_sigs) / len(wq_sigs)
        avg_bod = sum(w["metrics"]["bod_mg_l"] for w in wq_sigs) / len(wq_sigs)
        avg_wq_class = sum(w["metrics"]["pollution_class_code"] for w in wq_sigs) / len(wq_sigs)
        avg_turbidity = sum(w["metrics"]["turbidity_ntu"] for w in wq_sigs) / len(wq_sigs)
    else:
        avg_do, avg_bod, avg_wq_class, avg_turbidity = 5.0, 5.0, 2.0, 80.0

    # Terminals
    term_sigs = s.get("iwai_terminal", [])
    terminal_count = len(term_sigs)
    best_terminal_type = max((t["metrics"]["terminal_type_code"] for t in term_sigs), default=0)
    total_capacity = sum(t["metrics"]["capacity_mtpa"] for t in term_sigs) if term_sigs else 0.0
    any_rail_terminal = max((t["metrics"]["rail_connected"] for t in term_sigs), default=0)

    # Logistics
    lp_sigs = s.get("logistics_park", [])
    logistics_count = len(lp_sigs)
    best_lp_status = max((lp["metrics"]["status_code"] for lp in lp_sigs), default=0)
    total_lp_area = sum(lp["metrics"]["area_acres"] for lp in lp_sigs) if lp_sigs else 0.0
    any_water_lp = max((lp["metrics"]["water_connected"] for lp in lp_sigs), default=0)

    # Urban data
    urban_sigs = s.get("urban_center", [])
    max_city_class = max((u["metrics"]["city_class_code"] for u in urban_sigs), default=1)
    total_pop = sum(u["metrics"]["population_2023_lakhs"] for u in urban_sigs) if urban_sigs else 0.5
    has_airport = max((u["metrics"]["has_airport"] for u in urban_sigs), default=0)
    has_rail = max((u["metrics"]["has_railway_jn"] for u in urban_sigs), default=0)


     # Return final summary used by scoring models
    return {
        "flow_stability_code": round(avg_stability, 2),
        "nav_depth_m": round(avg_nav_depth, 2),
        "flow_cv_proxy": round(avg_cv, 2),
        "flood_prone": flood_prone,
        "env_sensitivity_code": round(avg_env_sens, 2),

        "avg_do_mg_l": round(avg_do, 2),
        "avg_bod_mg_l": round(avg_bod, 2),
        "avg_wq_class_code": round(avg_wq_class, 2),
        "avg_turbidity_ntu": round(avg_turbidity, 2),

        "terminal_count": terminal_count,
        "best_terminal_type": best_terminal_type,
        "total_capacity_mtpa": round(total_capacity, 2),
        "any_rail_terminal": any_rail_terminal,

        "logistics_park_count": logistics_count,
        "best_lp_status": best_lp_status,
        "total_lp_area_acres": round(total_lp_area, 2),
        "any_waterway_lp": any_water_lp,

        "max_city_class": max_city_class,
        "total_population_lakhs": round(total_pop, 2),
        "has_airport": has_airport,
        "has_rail": has_rail,

        # diagnostic: total signals collected for this location
        "total_signals": sum(len(v) for v in s.values()),
    }


# MAIN FUNCTION
def build_location_entities():
    signals = load_all_signals()

    #   Create anchors from cities
    anchors = _dynamic_anchors(signals)

    entities = []

    # For each anchor, collect nearby signals
    for eid, name, lat, lon in anchors:
        signals_by_type = {}

        for s in signals:
            d = haversine_km(lat, lon, s["latitude"], s["longitude"])
            
            # Include signals within radius
            if d <= CLUSTER_RADIUS_KM:
                signals_by_type.setdefault(s["signal_type"], []).append(s)

        # Build summary metrics for this location
        summary = _summarise(signals_by_type)

        # Create final entity
        entities.append({
            "entity_id": eid,
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "signals_by_type": signals_by_type,
            "summary_metrics": summary,
        })

    print(f"[location_entity_builder] Built {len(entities)} location entities.")
    return entities