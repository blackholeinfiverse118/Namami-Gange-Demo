"""
data_adapter.py

This file loads all raw CSV data and converts it into a common format
so that all other modules can use it easily.

Each row is converted into a "signal" dictionary:
{
    signal_id,
    source_dataset,
    location_name,
    latitude,
    longitude,
    signal_type,
    metrics: {...},
    tags: [...]
}
"""

import csv
import os
import math


# Convert text into a standard format (lowercase, no symbols)
def _normalize_text(val):
    if not val:
        return ""
    return str(val).lower().replace("-", " ").replace(".", " ").strip()

# Define paths to data folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW  = os.path.join(BASE_DIR, "data_raw")

# Read CSV file and return list of rows
def _csv(filename):
    path = os.path.join(DATA_RAW, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Validate required fields and convert lat/lon to float
def _validate(row, required_fields, source):
    """Returns (lat, lon) as floats or raises ValueError."""
    for field in required_fields:
        if not row.get(field, "").strip():
            raise ValueError(f"[{source}] Missing field '{field}' in row: {row}")
    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
    except ValueError:
        raise ValueError(f"[{source}] Non-numeric lat/lon in row: {row}")
    if not (6.0 <= lat <= 37.0) or not (68.0 <= lon <= 97.5):
        raise ValueError(f"[{source}] Coordinates out of India bounds: lat={lat}, lon={lon}")
    return lat, lon

# Convert value to float safely (avoid crashes)
def _safe_float(val, default=None):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# 1. IWAI Terminals ────────────────────────────────────────────────────────
def load_iwai_terminals():
    """
    Produces signal_type = 'iwai_terminal'
    Key metrics: capacity_mtpa, connectivity_road (bool), connectivity_rail (bool),
                 terminal_type_code
    """
    rows = _csv("iwai_terminals_nw1.csv")
    signals = []
    for row in rows:
        lat, lon = _validate(row, ["terminal_id","terminal_name","latitude","longitude"], "IWAI")
        # Encode terminal type to numeric code for scoring
        ttype = row.get("terminal_type", "").lower()
        if "multimodal" in ttype:
            type_code = 3   # highest capability
        elif "intermodal" in ttype:
            type_code = 2
        elif "fixed" in ttype:
            type_code = 2
        else:
            type_code = 1   # floating terminal

        road = _normalize_text(row.get("connectivity_road", ""))
        rail = _normalize_text(row.get("connectivity_rail", ""))

        road_ok = 1 if any(k in road for k in ["nh", "highway", "expressway", "road"]) else 0
        rail_ok = 1 if any(k in rail for k in ["yes", "junction", "jn", "rail", "dfc"]) else 0

        signals.append({
            "signal_id":      row["terminal_id"],
            "source_dataset": "iwai_terminals_nw1",
            "location_name":  row["terminal_name"],
            "latitude":       lat,
            "longitude":      lon,
            "signal_type":    "iwai_terminal",
            "metrics": {
                "capacity_mtpa":    _safe_float(row.get("capacity_mtpa"), 0.10),
                "terminal_type_code": type_code,
                "road_connected":   road_ok,
                "rail_connected":   rail_ok,
                "operational":      1 if row.get("operational_status","").lower() == "operational" else 0,
            },
            "tags": [row.get("state",""), row.get("terminal_type",""), "nw1"],
        })
    print(f"  [data_adapter] IWAI terminals loaded: {len(signals)}")
    return signals


# 2. Water Quality Stations ────────────────────────────────────────────────
def load_water_quality():
    """
    Produces signal_type = 'water_quality_station'
    Key metrics: do_mg_l, bod_mg_l, ph, turbidity_ntu, pollution_class_code
    pollution_class_code: A=5 (best), B=4, C=3, D=2, E=1 (worst)
    """
    CLASS_MAP = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
    rows = _csv("cpcb_water_quality_ganga.csv")
    signals = []
    for row in rows:
        lat, lon = _validate(row, ["station_id","station_name","latitude","longitude"], "CPCB")
        pc = row.get("pollution_class","B").strip().upper()
        signals.append({
            "signal_id":      row["station_id"],
            "source_dataset": "cpcb_water_quality_ganga",
            "location_name":  row["station_name"],
            "latitude":       lat,
            "longitude":      lon,
            "signal_type":    "water_quality_station",
            "metrics": {
                "do_mg_l":           _safe_float(row.get("do_mg_l"), 6.0),
                "bod_mg_l":          _safe_float(row.get("bod_mg_l"), 3.0),
                "ph":                _safe_float(row.get("ph"), 7.5),
                "turbidity_ntu":     _safe_float(row.get("turbidity_ntu"), 50.0),
                "conductivity":      _safe_float(row.get("conductivity_us_cm"), 300.0),
                "ammonia_mg_l":      _safe_float(row.get("ammonia_mg_l"), 0.3),
                "pollution_class_code": CLASS_MAP.get(pc, 3),
            },
            "tags": [row.get("state",""), row.get("river",""), "cpcb_rtwqm"],
        })
    print(f"  [data_adapter] Water quality stations loaded: {len(signals)}")
    return signals


# 3. Logistics Parks ───────────────────────────────────────────────────────
def load_logistics_parks():
    """
    Produces signal_type = 'logistics_park'
    Key metrics: area_acres, road_ok, rail_ok, waterway_ok, status_code
    status_code: Operational=3, Under Development=2, Proposed/DPR Stage=1
    """
    STATUS_MAP = {"operational": 3, "under development": 2, "under construction": 2,
                  "dpr stage": 1, "proposed": 1}
    rows = _csv("logistics_parks_ganga_belt.csv")
    signals = []
    for row in rows:
        lat, lon = _validate(row, ["park_id","park_name","latitude","longitude"], "Logistics")
        status_raw = row.get("status","").strip().lower()
        status_code = STATUS_MAP.get(status_raw, 1)

        road = _normalize_text(row.get("road_connectivity", ""))
        rail = _normalize_text(row.get("rail_connectivity", ""))
        water = _normalize_text(row.get("waterway_connectivity", ""))
        road_ok  = 1 if any(k in road for k in ["nh", "highway", "expressway", "road"]) else 0
        rail_ok  = 1 if any(k in rail for k in ["yes", "junction", "jn", "rail", "dfc"]) else 0
        water_ok = 1 if any(k in water for k in ["nw", "river", "waterway", "ganga", "hooghly"]) else 0

        signals.append({
            "signal_id":      row["park_id"],
            "source_dataset": "logistics_parks_ganga_belt",
            "location_name":  row["park_name"],
            "latitude":       lat,
            "longitude":      lon,
            "signal_type":    "logistics_park",
            "metrics": {
                "area_acres":      _safe_float(row.get("area_acres"), 100.0),
                "status_code":     status_code,
                "road_connected":  road_ok,
                "rail_connected":  rail_ok,
                "water_connected": water_ok,
            },
            "tags": [row.get("state",""), row.get("park_type",""), "logistics"],
        })
    print(f"  [data_adapter] Logistics parks loaded: {len(signals)}")
    return signals


# 4. River / CWC Stations ──────────────────────────────────────────────────
def load_river_stations():
    """
    Produces signal_type = 'river_station'
    Key metrics: avg_discharge_cumec, flow_stability_code, nav_depth_m,
                 flood_prone_flag, env_sensitivity_code
    """
    STABILITY_MAP  = {"low": 1, "medium": 2, "medium-high": 3, "high": 4}
    ENV_MAP        = {"low": 3, "medium": 2, "high": 1}  # high sensitivity = lower score
    rows = _csv("cwc_river_stations_ganga.csv")
    signals = []
    for row in rows:
        lat, lon = _validate(row, ["station_id","station_name","latitude","longitude"], "CWC")
        stability_raw = row.get("flow_stability_index","medium").strip().lower()
        env_raw       = row.get("environmental_sensitivity","medium").strip().lower()
        # strip trailing note like " - dolphin habitat"
        stability_key = stability_raw.split(" - ")[0].strip()
        env_key       = env_raw.split(" - ")[0].strip()

        # Compute coefficient of variation proxy: monsoon / lean ratio
        q_m = _safe_float(row.get("monsoon_discharge_cumec"), 10000.0)
        q_l = _safe_float(row.get("lean_discharge_cumec"), 200.0)
        cv_proxy = q_m / max(q_l, 1.0)   # lower = more stable

        signals.append({
            "signal_id":      row["station_id"],
            "source_dataset": "cwc_river_stations_ganga",
            "location_name":  row["station_name"],
            "latitude":       lat,
            "longitude":      lon,
            "signal_type":    "river_station",
            "metrics": {
                "avg_discharge_cumec":  _safe_float(row.get("avg_discharge_cumec"), 1000.0),
                "monsoon_discharge":    q_m,
                "lean_discharge":       q_l,
                "flow_cv_proxy":        round(cv_proxy, 2),
                "nav_depth_m":          _safe_float(row.get("navigability_depth_m"), 2.0),
                "water_level_var_m":    _safe_float(row.get("water_level_variation_m"), 15.0),
                "flow_stability_code":  STABILITY_MAP.get(stability_key, 2),
                "flood_prone":          1 if row.get("flood_prone","").strip().lower() == "yes" else 0,
                "env_sensitivity_code": ENV_MAP.get(env_key, 2),
            },
            "tags": [row.get("state",""), row.get("river",""), "cwc", "hydrology"],
        })
    print(f"  [data_adapter] River stations loaded: {len(signals)}")
    return signals


# 5. Urban Centers ─────────────────────────────────────────────────────────
def load_urban_centers():
    """
    Produces signal_type = 'urban_center'
    Key metrics: population_lakhs, has_airport, has_railway_jn, city_class_code
    """
    CLASS_MAP = {"mega city": 5, "metro": 4, "tier-1 city": 3,
                 "tier-2 city": 2, "class-i city": 2,
                 "industrial town": 2, "class-ii city": 1,
                 "class-iii city": 1, "small town": 1}
    rows = _csv("urban_centers_ganga_basin.csv")
    signals = []
    for row in rows:
        lat, lon = _validate(row, ["city_id","city_name","latitude","longitude"], "Urban")
        cc = row.get("city_class","Class-I City").strip().lower()
        signals.append({
            "signal_id":      row["city_id"],
            "source_dataset": "urban_centers_ganga_basin",
            "location_name":  row["city_name"],
            "latitude":       lat,
            "longitude":      lon,
            "signal_type":    "urban_center",
            "metrics": {
                "population_2023_lakhs": _safe_float(row.get("population_est_2023_lakhs"), 1.0),
                "has_airport":           1 if row.get("has_airport","").strip().lower() == "yes" else 0,
                "has_railway_jn":        1 if row.get("has_railway_jn","").strip().lower() == "yes" else 0,
                "has_highway":           1 if row.get("has_highway_access","").strip().lower() == "yes" else 0,
                "city_class_code":       CLASS_MAP.get(cc, 2),
            },
            "tags": [row.get("state",""), cc, "urban"],
        })
    print(f"  [data_adapter] Urban centers loaded: {len(signals)}")
    return signals


# Master loader ────────────────────────────────────────────────────────────
def load_all_signals():
    """
    Loads all 5 datasets, returns a single flat list of signals.
    Any row that fails validation is skipped with a warning (not a crash).
    """
    print("[data_adapter] Loading all raw datasets...")
    all_signals = []
    loaders = [
        load_iwai_terminals,
        load_water_quality,
        load_logistics_parks,
        load_river_stations,
        load_urban_centers,
    ]
    for loader in loaders:
        try:
            signals = loader()
            all_signals.extend(signals)
        except Exception as e:
            print(f"  [WARNING] Loader {loader.__name__} failed: {e}")
    print(f"[data_adapter] Total signals loaded: {len(all_signals)}\n")
    return all_signals


if __name__ == "__main__":
    signals = load_all_signals()
    # Print a sample from each type
    seen = set()
    for s in signals:
        t = s["signal_type"]
        if t not in seen:
            print(f"\n--- Sample [{t}] ---")
            print(f"  id:       {s['signal_id']}")
            print(f"  name:     {s['location_name']}")
            print(f"  lat/lon:  {s['latitude']}, {s['longitude']}")
            print(f"  metrics:  {s['metrics']}")
            seen.add(t)
