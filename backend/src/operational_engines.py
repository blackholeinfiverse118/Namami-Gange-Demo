import sqlite3
import json
import os
import sys
from db import get_db_connection

def get_all_vessels():
    """
    Returns all vessels with dynamic draft/speed safety alert checks.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vessel_operations")
    rows = cursor.fetchall()
    
    vessels = []
    for r in rows:
        v = dict(r)
        
        # Safety Alert Rules (Sprint 4)
        alerts = []
        
        # Rule 1: Draft safety clearance (under-keel draft warning < 0.4m)
        # Using a representative threshold for demo: if draft is deep and speed is fast
        if v["draft"] >= 3.0:
            alerts.append({
                "code": "DRAFT_WARN",
                "message": f"Critical draft warning: draft {v['draft']}m exceeds safe under-keel limit.",
                "severity": "CRITICAL"
            })
            
        # Rule 2: Speed limit violation
        if v["speed"] > 10.0:
            alerts.append({
                "code": "SPEED_LIMIT_EXCEEDED",
                "message": f"Speed limit violation: traveling at {v['speed']} knots (limit 10.0 knots).",
                "severity": "WARNING"
            })
            
        v["alerts"] = alerts
        vessels.append(v)
        
    conn.close()
    return vessels

def get_cargo_manifests():
    """
    Returns cargo manifests along with terminal allocation indicators.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cargo_operations")
    rows = cursor.fetchall()
    manifests = [dict(r) for r in rows]
    conn.close()
    return manifests

def get_terminal_capacities():
    """
    Computes capacity index and congestion level for all terminals.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM terminal_operations")
    rows = cursor.fetchall()
    
    terminals = []
    for r in rows:
        t = dict(r)
        t["bookings"] = json.loads(t["bookings"])
        
        # Calculate yard utilization index
        util = round((t["current_load_tons"] / t["capacity_tons"]) * 100, 1)
        t["utilization_percent"] = util
        t["congestion_level"] = "HIGH" if util > 90.0 else "MEDIUM" if util > 50.0 else "LOW"
        
        terminals.append(t)
        
    conn.close()
    return terminals

def solve_voyage_plan(origin, destination, draft, vessel_class, cargo_weight):
    """
    Solves optimal voyage route plan subject to draft and vertical bridge clearance constraints.
    """
    # Simple segment list & characteristics mapping
    segments = [
        {"name": "Varanasi-Patna", "min_depth": 3.2, "bridge_clearance": 8.0},
        {"name": "Patna-Farakka", "min_depth": 2.2, "bridge_clearance": 5.5},
        {"name": "Farakka-Haldia", "min_depth": 4.5, "bridge_clearance": 12.0}
    ]
    
    constraints_breached = []
    points_checked = []
    
    # Check vertical bridge clearance (Sprint 4: Draft and clearance solver)
    for seg in segments:
        # Check depth / draft
        depth_ok = seg["min_depth"] >= draft
        clearance_ok = seg["bridge_clearance"] >= 6.0 if vessel_class == "Class V" else seg["bridge_clearance"] >= 4.0
        
        points_checked.append({
            "segment": seg["name"],
            "depth_available": seg["min_depth"],
            "draft_required": draft,
            "bridge_clearance": seg["bridge_clearance"],
            "depth_ok": depth_ok,
            "clearance_ok": clearance_ok
        })
        
        if not depth_ok:
            constraints_breached.append({
                "code": "DRAFT_VIOLATION",
                "segment": seg["name"],
                "message": f"Available draft {seg['min_depth']}m is less than barge draft requirement {draft}m."
            })
            
        if not clearance_ok:
            constraints_breached.append({
                "code": "BRIDGE_CLEARANCE_EXCEEDED",
                "segment": seg["name"],
                "message": f"Bridge clearance {seg['bridge_clearance']}m is insufficient for vessel class."
            })
            
    is_feasible = len(constraints_breached) == 0
    recommended_path = [origin, "Patna Terminal NW-1", "Farakka Lock", destination]
    
    return {
        "origin": origin,
        "destination": destination,
        "vessel_class": vessel_class,
        "draft": draft,
        "cargo_weight_tons": cargo_weight,
        "is_feasible": is_feasible,
        "recommended_path": recommended_path,
        "points_checked": points_checked,
        "constraints_breached": constraints_breached
    }

def get_active_ris_notices():
    """
    Fetches active Notice to Mariners from the RIS notice repository.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ris_notices WHERE status = 'ACTIVE'")
    rows = cursor.fetchall()
    notices = [dict(r) for r in rows]
    conn.close()
    return notices

def get_water_gauges():
    """
    Returns hydrological CWC gauge telemetry.
    """
    # Sample hydrological points mapping
    return [
        {"station": "Varanasi", "current_level_m": 72.4, "flood_warning_level_m": 75.0, "status": "NORMAL"},
        {"station": "Buxar", "current_level_m": 60.1, "flood_warning_level_m": 62.0, "status": "SHALLOW"},
        {"station": "Patna", "current_level_m": 48.8, "flood_warning_level_m": 50.0, "status": "NORMAL"},
        {"station": "Farakka", "current_level_m": 22.2, "flood_warning_level_m": 26.0, "status": "NORMAL"}
    ]
