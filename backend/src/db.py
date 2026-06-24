import sqlite3
import json
import os
import sys

# Ensure backend/src is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "master_db.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print(f"[db] Initializing database at {DB_FILE}...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        source TEXT,
        status TEXT,
        updated TEXT,
        reliability INTEGER,
        version TEXT,
        coverage TEXT,
        schema_fields TEXT,
        ingestion_rate TEXT,
        trace_trail TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        signal_id TEXT PRIMARY KEY,
        source_dataset TEXT,
        location_name TEXT,
        latitude REAL,
        longitude REAL,
        signal_type TEXT,
        metrics TEXT,
        tags TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        location_id TEXT PRIMARY KEY,
        name TEXT,
        latitude REAL,
        longitude REAL,
        signals_by_type TEXT,
        summary_metrics TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_refresh_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT,
    refresh_time TEXT,
    refresh_status TEXT,
    refresh_duration_ms INTEGER,
    version TEXT,
    notes TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset_health (
    dataset_name TEXT PRIMARY KEY,
    last_refresh TEXT,
    freshness_score REAL,
    health_status TEXT,
    confidence_impact REAL,
    source_reachable INTEGER,
    refresh_latency_ms INTEGER
    )
    """)

    conn.commit()

    # Check if we need to seed
    cursor.execute("SELECT COUNT(*) FROM datasets")
    if cursor.fetchone()[0] == 0:
        seed_db(conn)
    else:
        print("[db] Database already seeded.")
    
    conn.close()

def seed_db(conn):
    print("[db] Seeding database with baseline data...")
    cursor = conn.cursor()

    # Seed baseline datasets
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
          "status": "Good", 
          "updated": "6ms Delay", 
          "reliability": 98, 
          "version": "v2.1", 
          "coverage": "National",
          "schemaFields": "mmsi_id, speed_knots, draft_m, vessel_class, lat_lng_point",
          "ingestionRate": "Real-time AIS transponder stream via National Maritime Single Window",
          "traceTrail": "verified via differential GPS base station correction"
        },
        { 
          "name": "UP PCB Water Quality Sensors", 
          "source": "Uttar Pradesh Pollution Control Board", 
          "status": "Good", 
          "updated": "Real-time", 
          "reliability": 95, 
          "version": "v1.4", 
          "coverage": "UP State",
          "schemaFields": "avg_bod_mg_l, do_mg_l, turbidity_ntu, nearest_industry_km",
          "ingestionRate": "28 sensor nodes reporting hourly telemetry payload",
          "traceTrail": "validated via biochemical lab sample correlation (monthly audits)"
        },
        { 
          "name": "IWAI IWT Terminals", 
          "source": "Inland Waterways Authority of India", 
          "status": "Good", 
          "updated": "Block #1240", 
          "reliability": 96, 
          "version": "v2.3", 
          "coverage": "NW-1 to NW-111",
          "schemaFields": "node_type, road_connected, rail_connected, water_connected, area_acres",
          "ingestionRate": "Block synchronization persistence on location database (locations.json)",
          "traceTrail": "validated via blockchain ledger contract verification checks"
        }
    ]

    for d in datasets:
        cursor.execute("""
        INSERT INTO datasets (name, source, status, updated, reliability, version, coverage, schema_fields, ingestion_rate, trace_trail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["name"], d["source"], d["status"], d["updated"], d["reliability"],
            d["version"], d["coverage"], d["schemaFields"], d["ingestionRate"], d["traceTrail"]
        ))

    # Seed raw signals
    try:
        from data_adapter import load_all_signals
        signals = load_all_signals()
        for s in signals:
            cursor.execute("""
            INSERT OR REPLACE INTO signals (signal_id, source_dataset, location_name, latitude, longitude, signal_type, metrics, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["signal_id"], s["source_dataset"], s["location_name"],
                s["latitude"], s["longitude"], s["signal_type"],
                json.dumps(s["metrics"]), json.dumps(s["tags"])
            ))
    except Exception as e:
        print(f"[db] Warning: Failed to seed raw signals: {e}")

    # Seed built location entities
    try:
        from location_entity_builder import build_location_entities
        entities = build_location_entities()
        for e in entities:
            name_lower = e["name"].lower()
            if "varanasi" in name_lower:
                loc_id = "varanasi_terminal"
            elif "allahabad" in name_lower or "prayagraj" in name_lower:
                loc_id = "allahabad_confluence"
            elif "patna" in name_lower:
                loc_id = "patna_river_port"
            elif "kanpur" in name_lower:
                loc_id = "kanpur_industrial_zone"
            elif "farakka" in name_lower:
                loc_id = "farakka_wetland"
            elif "hajipur" in name_lower:
                loc_id = "hajipur_hub"
            else:
                loc_id = e["entity_id"]

            cursor.execute("""
            INSERT OR REPLACE INTO locations (location_id, name, latitude, longitude, signals_by_type, summary_metrics)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                loc_id, e["name"], e["latitude"], e["longitude"],
                json.dumps(e["signals_by_type"]), json.dumps(e["summary_metrics"])
            ))
    except Exception as e:
        print(f"[db] Warning: Failed to seed location entities: {e}")

    # Explicitly seed Kolkata and the other primary UI locations to guarantee direct data access
    print("[db] Seeding primary UI demo locations explicitly...")
    ui_locations = [
        {
            "location_id": "varanasi_terminal",
            "name": "Varanasi Corridor NW-1",
            "latitude": 25.3176,
            "longitude": 82.9739,
            "summary_metrics": {
                "flow_stability_code": 4.0, "nav_depth_m": 3.2, "flow_cv_proxy": 12.0, "flood_prone": 0, "env_sensitivity_code": 2.0,
                "avg_do_mg_l": 7.5, "avg_bod_mg_l": 2.1, "avg_wq_class_code": 4.0, "avg_turbidity_ntu": 32.0,
                "terminal_count": 2, "best_terminal_type": 3, "total_capacity_mtpa": 8.0, "any_rail_terminal": 1,
                "logistics_park_count": 2, "best_lp_status": 3, "total_lp_area_acres": 120.0, "any_waterway_lp": 1,
                "max_city_class": 3, "total_population_lakhs": 25.0, "has_airport": 1, "has_rail": 1, "total_signals": 15
            }
        },
        {
            "location_id": "allahabad_confluence",
            "name": "Prayagraj Sangam Confluence",
            "latitude": 25.4358,
            "longitude": 81.8463,
            "summary_metrics": {
                "flow_stability_code": 2.0, "nav_depth_m": 2.1, "flow_cv_proxy": 25.0, "flood_prone": 1, "env_sensitivity_code": 3.0,
                "avg_do_mg_l": 6.8, "avg_bod_mg_l": 2.8, "avg_wq_class_code": 3.0, "avg_turbidity_ntu": 48.0,
                "terminal_count": 1, "best_terminal_type": 2, "total_capacity_mtpa": 2.5, "any_rail_terminal": 0,
                "logistics_park_count": 0, "best_lp_status": 0, "total_lp_area_acres": 0.0, "any_waterway_lp": 0,
                "max_city_class": 2, "total_population_lakhs": 15.0, "has_airport": 1, "has_rail": 1, "total_signals": 8
            }
        },
        {
            "location_id": "patna_river_port",
            "name": "Patna Terminal NW-1",
            "latitude": 25.6112,
            "longitude": 85.1444,
            "summary_metrics": {
                "flow_stability_code": 3.0, "nav_depth_m": 2.6, "flow_cv_proxy": 18.0, "flood_prone": 1, "env_sensitivity_code": 2.0,
                "avg_do_mg_l": 7.0, "avg_bod_mg_l": 3.4, "avg_wq_class_code": 3.0, "avg_turbidity_ntu": 52.0,
                "terminal_count": 1, "best_terminal_type": 2, "total_capacity_mtpa": 4.0, "any_rail_terminal": 1,
                "logistics_park_count": 1, "best_lp_status": 2, "total_lp_area_acres": 80.0, "any_waterway_lp": 1,
                "max_city_class": 3, "total_population_lakhs": 30.0, "has_airport": 1, "has_rail": 1, "total_signals": 12
            }
        },
        {
            "location_id": "kanpur_industrial_zone",
            "name": "Kanpur Industrial Reach",
            "latitude": 26.4499,
            "longitude": 80.3319,
            "summary_metrics": {
                "flow_stability_code": 1.0, "nav_depth_m": 1.4, "flow_cv_proxy": 40.0, "flood_prone": 1, "env_sensitivity_code": 3.0,
                "avg_do_mg_l": 1.5, "avg_bod_mg_l": 8.4, "avg_wq_class_code": 1.0, "avg_turbidity_ntu": 180.0,
                "terminal_count": 0, "best_terminal_type": 0, "total_capacity_mtpa": 0.0, "any_rail_terminal": 0,
                "logistics_park_count": 1, "best_lp_status": 3, "total_lp_area_acres": 150.0, "any_waterway_lp": 0,
                "max_city_class": 3, "total_population_lakhs": 35.0, "has_airport": 0, "has_rail": 1, "total_signals": 20
            }
        },
        {
            "location_id": "farakka_wetland",
            "name": "Farakka Ecological Reach",
            "latitude": 24.8119,
            "longitude": 87.9186,
            "summary_metrics": {
                "flow_stability_code": 2.0, "nav_depth_m": 2.0, "flow_cv_proxy": 35.0, "flood_prone": 1, "env_sensitivity_code": 3.0,
                "avg_do_mg_l": 5.5, "avg_bod_mg_l": 4.8, "avg_wq_class_code": 2.0, "avg_turbidity_ntu": 95.0,
                "terminal_count": 1, "best_terminal_type": 1, "total_capacity_mtpa": 1.5, "any_rail_terminal": 0,
                "logistics_park_count": 0, "best_lp_status": 0, "total_lp_area_acres": 0.0, "any_waterway_lp": 0,
                "max_city_class": 1, "total_population_lakhs": 2.0, "has_airport": 0, "has_rail": 0, "total_signals": 6
            }
        },
        {
            "location_id": "kolkata",
            "name": "Haldia-Kolkata Port Grid",
            "latitude": 22.5726,
            "longitude": 88.3639,
            "summary_metrics": {
                "flow_stability_code": 3.0, "nav_depth_m": 4.8, "flow_cv_proxy": 15.0, "flood_prone": 0, "env_sensitivity_code": 1.0,
                "avg_do_mg_l": 7.0, "avg_bod_mg_l": 2.5, "avg_wq_class_code": 4.0, "avg_turbidity_ntu": 40.0,
                "terminal_count": 3, "best_terminal_type": 3, "total_capacity_mtpa": 12.0, "any_rail_terminal": 1,
                "logistics_park_count": 2, "best_lp_status": 3, "total_lp_area_acres": 250.0, "any_waterway_lp": 1,
                "max_city_class": 5, "total_population_lakhs": 150.0, "has_airport": 1, "has_rail": 1, "total_signals": 12
            }
        }
    ]

    for loc in ui_locations:
        cursor.execute("""
        INSERT OR REPLACE INTO locations (location_id, name, latitude, longitude, signals_by_type, summary_metrics)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            loc["location_id"], loc["name"], loc["latitude"], loc["longitude"],
            "{}", json.dumps(loc["summary_metrics"])
        ))

    conn.commit()
    print("[db] Database seeding complete.")
