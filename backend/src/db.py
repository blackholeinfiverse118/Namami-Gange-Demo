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

    # Converged Operational Database Schema (Sprint 9)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vessel_operations (
        vessel_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        draft REAL,
        latitude REAL,
        longitude REAL,
        speed REAL,
        heading REAL,
        status TEXT,
        last_update TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargo_operations (
        manifest_id TEXT PRIMARY KEY,
        vessel_id TEXT,
        commodity_type TEXT,
        volume_tons REAL,
        source_terminal TEXT,
        dest_terminal TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voyage_plans (
        voyage_id TEXT PRIMARY KEY,
        vessel_id TEXT,
        origin TEXT,
        destination TEXT,
        route_path TEXT,
        current_segment TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ris_notices (
        notice_id TEXT PRIMARY KEY,
        type TEXT,
        description TEXT,
        severity TEXT,
        status TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS terminal_operations (
        jetty_id TEXT PRIMARY KEY,
        name TEXT,
        capacity_tons REAL,
        current_load_tons REAL,
        queue_length INTEGER,
        bookings TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_ledger (
        event_id TEXT PRIMARY KEY,
        correlation_id TEXT,
        trace_id TEXT,
        timestamp TEXT,
        event_type TEXT,
        payload TEXT,
        audit_hash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS national_waterways (
    waterway_id TEXT PRIMARY KEY,
    name TEXT,
    national_waterway TEXT,
    river_system TEXT,
    total_length_km REAL,
    operational_status TEXT,
    states_covered TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waterway_segments (
    segment_id TEXT PRIMARY KEY,
    waterway_id TEXT,
    segment_name TEXT,
    start_location TEXT,
    end_location TEXT,
    navigable_depth REAL,
    bridge_clearance REAL,
    lock_available INTEGER,
    operational_status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS river_locks (
    lock_id TEXT PRIMARY KEY,
    name TEXT,
    waterway_id TEXT,
    location TEXT,
    operational_status TEXT,
    max_vessel_length REAL,
    max_draft REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bridge_clearances (
    bridge_id TEXT PRIMARY KEY,
    bridge_name TEXT,
    waterway_id TEXT,
    vertical_clearance REAL,
    horizontal_clearance REAL,
    navigation_restriction TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fleet_registry (
    vessel_id TEXT PRIMARY KEY,
    operator_name TEXT,
    vessel_class TEXT,
    propulsion_type TEXT,
    registration_status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waterway_operators (
    operator_id TEXT PRIMARY KEY,
    organization_name TEXT,
    operator_type TEXT,
    headquarters TEXT,
    operational_region TEXT
    )
    """)

    conn.commit()

    # Check if we need to seed
    cursor.execute("SELECT COUNT(*) FROM datasets")
    if cursor.fetchone()[0] == 0:
        seed_db(conn)
    else:
        print("[db] Database already seeded.")

    seed_phase2_masterdb(conn)
    
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

    # Seed Vessel Operations
    vessels = [
        ("vessel_001", "Ganga Sovereign", "Cargo Barge", 2.8, 25.3176, 82.9739, 8.2, 90.0, "TRANSIT", "10:30:00"),
        ("vessel_002", "Bhagirathi Pioneer", "Class V Barge", 3.4, 25.6112, 85.1444, 7.5, 120.0, "LOADING", "10:31:00"),
        ("vessel_003", "Alaknanda Explorer", "Eco Patrol", 1.2, 25.4358, 81.8463, 12.0, 45.0, "PATROL", "10:29:00"),
        ("vessel_004", "Hooghly Carrier", "Fly-Ash Barge", 4.2, 22.5726, 88.3639, 6.8, 270.0, "TRANSIT", "10:32:00"),
        ("vessel_005", "Dolphin Guardian", "Survey Vessel", 1.1, 24.8119, 87.9186, 9.0, 180.0, "SURVEY", "10:28:00")
    ]
    for v in vessels:
        cursor.execute("""
        INSERT OR REPLACE INTO vessel_operations (vessel_id, name, type, draft, latitude, longitude, speed, heading, status, last_update)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, v)

    # Seed Cargo Operations
    cargoes = [
        ("mnf_101", "vessel_001", "Containers", 1500.0, "Varanasi Corridor NW-1", "Haldia-Kolkata Port Grid", "TRANSIT"),
        ("mnf_102", "vessel_002", "Fly Ash", 2200.0, "Patna Terminal NW-1", "Haldia-Kolkata Port Grid", "LOADING"),
        ("mnf_103", "vessel_004", "Coal", 3000.0, "Haldia-Kolkata Port Grid", "Patna Terminal NW-1", "TRANSIT")
    ]
    for c in cargoes:
        cursor.execute("""
        INSERT OR REPLACE INTO cargo_operations (manifest_id, vessel_id, commodity_type, volume_tons, source_terminal, dest_terminal, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, c)

    # Seed Voyage Plans
    voyages = [
        ("voy_201", "vessel_001", "Varanasi Corridor NW-1", "Haldia-Kolkata Port Grid", "Varanasi-Patna-Farakka-Haldia", "Patna", "ACTIVE"),
        ("voy_202", "vessel_002", "Patna Terminal NW-1", "Haldia-Kolkata Port Grid", "Patna-Munger-Farakka-Kolkata", "Patna", "ACTIVE")
    ]
    for vy in voyages:
        cursor.execute("""
        INSERT OR REPLACE INTO voyage_plans (voyage_id, vessel_id, origin, destination, route_path, current_segment, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, vy)

    # Seed RIS Notices
    notices = [
        ("ntc_301", "RESTRICTION", "Navigation restriction near Jajmau (Kanpur) - High pollution alert.", "Medium", "ACTIVE", "10:00:00"),
        ("ntc_302", "MAINTENANCE", "Farakka Barrage Lock 2 undergoing inspection; expected delay 4 hrs.", "High", "ACTIVE", "09:45:00"),
        ("ntc_303", "SHALLOW_ALERT", "Shallow draft alert near Buxar NW-1: available draft 1.9m.", "Critical", "ACTIVE", "10:15:00")
    ]
    for n in notices:
        cursor.execute("""
        INSERT OR REPLACE INTO ris_notices (notice_id, type, description, severity, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, n)

    # Seed Terminal Operations
    terminals = [
        ("varanasi_terminal", "Varanasi Corridor NW-1", 10000.0, 3500.0, 1, json.dumps([{"vessel_id": "vessel_001", "eta": "14:00"}])),
        ("patna_river_port", "Patna Terminal NW-1", 8000.0, 5200.0, 2, json.dumps([{"vessel_id": "vessel_002", "eta": "16:30"}])),
        ("allahabad_confluence", "Prayagraj Sangam Confluence", 3000.0, 450.0, 0, json.dumps([])),
        ("kanpur_industrial_zone", "Kanpur Industrial Reach", 4000.0, 1200.0, 0, json.dumps([])),
        ("farakka_wetland", "Farakka Ecological Reach", 5000.0, 4600.0, 4, json.dumps([])),
        ("kolkata", "Haldia-Kolkata Port Grid", 25000.0, 18000.0, 5, json.dumps([{"vessel_id": "vessel_004", "eta": "18:00"}]))
    ]
    for t in terminals:
        cursor.execute("""
        INSERT OR REPLACE INTO terminal_operations (jetty_id, name, capacity_tons, current_load_tons, queue_length, bookings)
        VALUES (?, ?, ?, ?, ?, ?)
        """, t)

    # Seed National Waterways

    waterways = [

        (
            "NW1",
            "Ganga-Bhagirathi-Hooghly",
            "National Waterway-1",
            "Ganga",
            1620,
            "Operational",
            "Uttar Pradesh, Bihar, Jharkhand, West Bengal"
        ),

        (
            "NW2",
            "Brahmaputra",
            "National Waterway-2",
            "Brahmaputra",
            891,
            "Operational",
            "Assam"
        ),

        (
            "NW3",
            "West Coast Canal",
            "National Waterway-3",
            "West Coast Canal",
            205,
            "Operational",
            "Kerala"
        ),

        (
            "NW4",
            "Godavari-Krishna",
            "National Waterway-4",
            "Godavari",
            1078,
            "Development",
            "Andhra Pradesh, Tamil Nadu"
        ),

        (
            "NW5",
            "East Coast Canal",
            "National Waterway-5",
            "Brahmani",
            588,
            "Development",
            "Odisha, West Bengal"
        )

    ]

    for w in waterways:

        cursor.execute("""

        INSERT OR REPLACE INTO national_waterways

        VALUES (?, ?, ?, ?, ?, ?, ?)

        """, w)

    # Seed Waterway Segments

    segments = [

        (
            "SEG001",
            "NW1",
            "Varanasi-Patna",
            "Varanasi",
            "Patna",
            3.0,
            9.5,
            0,
            "Operational"
        ),

        (
            "SEG002",
            "NW1",
            "Patna-Farakka",
            "Patna",
            "Farakka",
            2.8,
            8.8,
            1,
            "Operational"
        ),

        (
            "SEG003",
            "NW1",
            "Farakka-Haldia",
            "Farakka",
            "Haldia",
            3.2,
            12.0,
            1,
            "Operational"
        ),

        (
            "SEG004",
            "NW2",
            "Dhubri-Guwahati",
            "Dhubri",
            "Guwahati",
            2.5,
            10.0,
            0,
            "Operational"
        ),

        (
            "SEG005",
            "NW3",
            "Kollam-Kochi",
            "Kollam",
            "Kochi",
            2.2,
            8.0,
            0,
            "Operational"
        )

    ]

    for seg in segments:

        cursor.execute("""

        INSERT OR REPLACE INTO waterway_segments

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, seg)

    # Seed River Locks

    locks = [

        (
            "LOCK001",
            "Farakka Navigation Lock",
            "NW1",
            "Farakka",
            "Operational",
            230,
            3.5
        ),

        (
            "LOCK002",
            "Kottapuram Lock",
            "NW3",
            "Kottapuram",
            "Operational",
            110,
            2.5
        ),

        (
            "LOCK003",
            "Buckingham Canal Lock",
            "NW4",
            "Vijayawada",
            "Maintenance",
            120,
            2.2
        )

    ]

    for lock in locks:

        cursor.execute("""

        INSERT OR REPLACE INTO river_locks

        VALUES (?, ?, ?, ?, ?, ?, ?)

        """, lock)

    # Seed Bridge Clearances

    bridges = [

        (
            "BR001",
            "Rajendra Setu",
            "NW1",
            10.5,
            120.0,
            "No restriction"
        ),

        (
            "BR002",
            "Vivekananda Setu",
            "NW1",
            8.5,
            95.0,
            "High water level restriction during monsoon"
        ),

        (
            "BR003",
            "Saraighat Bridge",
            "NW2",
            12.0,
            150.0,
            "No restriction"
        ),

        (
            "BR004",
            "Kochi Canal Bridge",
            "NW3",
            6.0,
            45.0,
            "Small vessels only"
        )

    ]

    for bridge in bridges:

        cursor.execute("""

        INSERT OR REPLACE INTO bridge_clearances

        VALUES (?, ?, ?, ?, ?, ?)

        """, bridge)

    # Seed Fleet Registry

    fleet = [

        (
            "vessel_001",
            "IWAI Logistics",
            "Cargo Barge",
            "Diesel",
            "Active"
        ),

        (
            "vessel_002",
            "National Waterways Logistics",
            "Class V Cargo Vessel",
            "Diesel",
            "Active"
        ),

        (
            "vessel_003",
            "Inland Survey Division",
            "Survey Vessel",
            "Hybrid",
            "Active"
        ),

        (
            "vessel_004",
            "Eastern River Transport",
            "Bulk Cargo Vessel",
            "Diesel",
            "Active"
        ),

        (
            "vessel_005",
            "River Conservation Authority",
            "Patrol Vessel",
            "Electric Hybrid",
            "Active"
        )

    ]

    for vessel in fleet:

        cursor.execute("""

        INSERT OR REPLACE INTO fleet_registry

        VALUES (?, ?, ?, ?, ?)

        """, vessel)

    # Seed Waterway Operators

    operators = [

        (
            "OP001",
            "Inland Waterways Authority of India",
            "Government",
            "Noida",
            "National"
        ),

        (
            "OP002",
            "National Waterways Logistics",
            "Private Logistics",
            "Kolkata",
            "Eastern India"
        ),

        (
            "OP003",
            "Assam River Transport Corporation",
            "State Transport",
            "Guwahati",
            "North East"
        ),

        (
            "OP004",
            "Kerala Water Transport Department",
            "State Government",
            "Kochi",
            "Kerala"
        ),

        (
            "OP005",
            "Eastern Inland Cargo Services",
            "Private Operator",
            "Patna",
            "Ganga Basin"
        )

    ]

    for operator in operators:

        cursor.execute("""

        INSERT OR REPLACE INTO waterway_operators

        VALUES (?, ?, ?, ?, ?)

        """, operator)

    conn.commit()
    print("[db] Database seeding complete.")


def seed_phase2_masterdb(conn):

    cursor = conn.cursor()

    print("[db] Checking Phase 2 Marine MasterDB data...")

    print("[db] Seeding Phase 2 National Marine MasterDB...")

    # -------------------------
    # National Waterways
    # -------------------------

    waterways = [

        (
            "NW1",
            "Ganga–Bhagirathi–Hooghly",
            "National Waterway-1",
            "Ganga",
            1620,
            "Operational",
            "Uttar Pradesh, Bihar, Jharkhand, West Bengal"
        ),

        (
            "NW2",
            "Brahmaputra",
            "National Waterway-2",
            "Brahmaputra",
            891,
            "Operational",
            "Assam"
        ),

        (
            "NW3",
            "West Coast Canal",
            "National Waterway-3",
            "West Coast Canal",
            205,
            "Operational",
            "Kerala"
        ),

        (
            "NW4",
            "Godavari–Krishna",
            "National Waterway-4",
            "Godavari",
            1078,
            "Development",
            "Andhra Pradesh, Tamil Nadu"
        ),

        (
            "NW5",
            "East Coast Canal",
            "National Waterway-5",
            "Brahmani",
            588,
            "Development",
            "Odisha, West Bengal"
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM national_waterways")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO national_waterways VALUES (?,?,?,?,?,?,?)",
            waterways
        )


    # -------------------------
    # Waterway Segments
    # -------------------------

    segments = [

        (
            "SEG001",
            "NW1",
            "Varanasi–Patna",
            "Varanasi",
            "Patna",
            3.0,
            9.5,
            0,
            "Operational"
        ),

        (
            "SEG002",
            "NW1",
            "Patna–Farakka",
            "Patna",
            "Farakka",
            2.8,
            8.8,
            1,
            "Operational"
        ),

        (
            "SEG003",
            "NW1",
            "Farakka–Haldia",
            "Farakka",
            "Haldia",
            3.2,
            12.0,
            1,
            "Operational"
        ),

        (
            "SEG004",
            "NW2",
            "Dhubri–Guwahati",
            "Dhubri",
            "Guwahati",
            2.5,
            10.0,
            0,
            "Operational"
        ),

        (
            "SEG005",
            "NW3",
            "Kollam–Kochi",
            "Kollam",
            "Kochi",
            2.2,
            8.0,
            0,
            "Operational"
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM waterway_segments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO waterway_segments VALUES (?,?,?,?,?,?,?,?,?)",
            segments
        )

    # -------------------------
    # River Locks
    # -------------------------

    locks = [

        (
            "LOCK001",
            "Farakka Navigation Lock",
            "NW1",
            "Farakka",
            "Operational",
            230,
            3.5
        ),

        (
            "LOCK002",
            "Kottapuram Lock",
            "NW3",
            "Kottapuram",
            "Operational",
            110,
            2.5
        ),

        (
            "LOCK003",
            "Buckingham Canal Lock",
            "NW4",
            "Vijayawada",
            "Maintenance",
            120,
            2.2
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM river_locks")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO river_locks VALUES (?,?,?,?,?,?,?)",
            locks
        )

    # -------------------------
    # Bridge Clearances
    # -------------------------

    bridges = [

        (
            "BR001",
            "Rajendra Setu",
            "NW1",
            10.5,
            120.0,
            "No restriction"
        ),

        (
            "BR002",
            "Vivekananda Setu",
            "NW1",
            8.5,
            95.0,
            "High water level restriction during monsoon"
        ),

        (
            "BR003",
            "Saraighat Bridge",
            "NW2",
            12.0,
            150.0,
            "No restriction"
        ),

        (
            "BR004",
            "Kochi Canal Bridge",
            "NW3",
            6.0,
            45.0,
            "Small vessels only"
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM bridge_clearances")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO bridge_clearances VALUES (?,?,?,?,?,?)",
            bridges
        )

    # -------------------------
    # Fleet Registry
    # -------------------------

    fleet = [

        (
            "vessel_001",
            "IWAI Logistics",
            "Cargo Barge",
            "Diesel",
            "Active"
        ),

        (
            "vessel_002",
            "National Waterways Logistics",
            "Class V Cargo Vessel",
            "Diesel",
            "Active"
        ),

        (
            "vessel_003",
            "Inland Survey Division",
            "Survey Vessel",
            "Hybrid",
            "Active"
        ),

        (
            "vessel_004",
            "Eastern River Transport",
            "Bulk Cargo Vessel",
            "Diesel",
            "Active"
        ),

        (
            "vessel_005",
            "River Conservation Authority",
            "Patrol Vessel",
            "Electric Hybrid",
            "Active"
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM fleet_registry")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO fleet_registry VALUES (?,?,?,?,?)",
            fleet
        )

    # -------------------------
    # Waterway Operators
    # -------------------------

    operators = [

        (
            "OP001",
            "Inland Waterways Authority of India",
            "Government",
            "Noida",
            "National"
        ),

        (
            "OP002",
            "National Waterways Logistics",
            "Private Logistics",
            "Kolkata",
            "Eastern India"
        ),

        (
            "OP003",
            "Assam River Transport Corporation",
            "State Transport",
            "Guwahati",
            "North East"
        ),

        (
            "OP004",
            "Kerala Water Transport Department",
            "State Government",
            "Kochi",
            "Kerala"
        ),

        (
            "OP005",
            "Eastern Inland Cargo Services",
            "Private Operator",
            "Patna",
            "Ganga Basin"
        )

    ]

    cursor.execute("SELECT COUNT(*) FROM waterway_operators")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT OR REPLACE INTO waterway_operators VALUES (?,?,?,?,?)",
            operators
        )
    

    conn.commit()

    print("[db] Phase 2 MasterDB seeded.")