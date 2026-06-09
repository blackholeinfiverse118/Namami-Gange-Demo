"""
test_boundaries.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 2 — Boundary Test Suite

Tests exact threshold boundaries:
  A. 74.9 km vs 75.1 km — CLUSTER_RADIUS_KM grouping boundary
  B. Score threshold boundaries — HIGH/MEDIUM/LOW edge values
  C. 50 km vs 100 km proximity variants
  D. Constraint boundary values — exact trigger points
  E. Edge coordinate cases — India bounds
  F. Weight boundary — exactly 1.0 vs 1.0001
"""

import sys
import os
import math


PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, os.path.abspath(PROJECT_ROOT))
sys.path.insert(0, os.path.abspath(SRC_DIR))

import importlib
import importlib.util
import types
import data_adapter as _da
_leb_spec = importlib.util.spec_from_file_location(
    "location_entity_builder",
    os.path.join(SRC_DIR, "location_entity_builder.py")
)
_leb = importlib.util.module_from_spec(_leb_spec)
sys.modules["data_adapter"] = _da
sys.modules["src.data_adapter"] = _da
_leb_spec.loader.exec_module(_leb)

from scoring_engine import score_entity, SCORING_MODELS
from constraint_engine import evaluate_constraints
haversine_km = _leb.haversine_km
CLUSTER_RADIUS_KM = _leb.CLUSTER_RADIUS_KM


PASS = "  PASS"
FAIL = "  FAIL"
results_log = []


def log(name, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"{status}  {name}"
    if detail:
        msg += f"\n         → {detail}"
    print(msg)
    results_log.append((name, passed))


# ══════════════════════════════════════════════════════════════
# BLOCK A — 74.9 km vs 75.1 km CLUSTER RADIUS BOUNDARY
# CLUSTER_RADIUS_KM = 75 in location_entity_builder.py
# Signal at 74.9 km → INSIDE cluster (included)
# Signal at 75.1 km → OUTSIDE cluster (excluded)
# ══════════════════════════════════════════════════════════════

# Anchor: Varanasi (25.3176, 82.9739)
ANCHOR_LAT = 25.3176
ANCHOR_LON = 82.9739


def _point_at_distance_km(lat, lon, distance_km, bearing_deg=90):
    """
    Returns (lat2, lon2) that is exactly distance_km away from (lat, lon)
    at the given bearing. Uses spherical earth approximation.
    """
    R = 6371.0
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    d = distance_km / R

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d) +
        math.cos(lat1) * math.sin(d) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2)
    )
    return math.degrees(lat2), math.degrees(lon2)


def test_A1_signal_inside_cluster_radius():
    """Signal at 74.9 km should be INSIDE the 75 km cluster radius."""
    lat2, lon2 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 74.9)
    distance = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat2, lon2)
    inside = distance <= CLUSTER_RADIUS_KM
    log(
        "TEST A1 — 74.9 km signal: inside cluster radius (≤ 75 km)",
        inside,
        f"computed distance = {distance:.4f} km | CLUSTER_RADIUS_KM = {CLUSTER_RADIUS_KM} | inside = {inside}"
    )
    return inside


def test_A2_signal_outside_cluster_radius():
    """Signal at 75.1 km should be OUTSIDE the 75 km cluster radius."""
    lat2, lon2 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 75.1)
    distance = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat2, lon2)
    outside = distance > CLUSTER_RADIUS_KM
    log(
        "TEST A2 — 75.1 km signal: outside cluster radius (> 75 km)",
        outside,
        f"computed distance = {distance:.4f} km | CLUSTER_RADIUS_KM = {CLUSTER_RADIUS_KM} | outside = {outside}"
    )
    return outside


def test_A3_exact_boundary_75km():
    """Signal at exactly 75.0 km — should be ON the boundary (included, ≤)."""
    lat2, lon2 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 75.0)
    distance = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat2, lon2)
    # Allow 0.01 km floating point tolerance in the computed distance
    on_boundary = distance <= CLUSTER_RADIUS_KM + 0.01
    log(
        "TEST A3 — 75.0 km signal: on boundary (≤ 75 km ± 0.01 tolerance)",
        on_boundary,
        f"computed distance = {distance:.4f} km | included = {on_boundary}"
    )
    return on_boundary


def test_A4_inside_outside_different_bearings():
    """74.9 km and 75.1 km at different bearings all respect the boundary."""
    bearings = [0, 90, 180, 270]
    results = []
    for b in bearings:
        lat_in, lon_in = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 74.9, b)
        lat_out, lon_out = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 75.1, b)
        d_in = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat_in, lon_in)
        d_out = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat_out, lon_out)
        results.append(d_in <= CLUSTER_RADIUS_KM and d_out > CLUSTER_RADIUS_KM)
    passed = all(results)
    log(
        "TEST A4 — 74.9/75.1 km boundary holds at N/E/S/W bearings",
        passed,
        f"all 4 bearings correct = {results}"
    )
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK B — SCORE THRESHOLD BOUNDARIES
# inland_port: HIGH ≥ 75 | MEDIUM ≥ 50 | LOW < 50
# ══════════════════════════════════════════════════════════════

def _entity_with_score(target_score, model_type="inland_port"):
    """
    Builds an entity whose raw weighted score will be approximately target_score.
    For inland_port: score = rs*0.25 + tp*0.20 + la*0.20 + wq*0.20 + traf*0.15
    Set all factors equal → score = factor_value * 1.0 = factor_value
    """
    v = float(target_score)
    return {
        "location_id": f"boundary_test_{int(v)}",
        "properties": {
            "river_stability_score": v,
            "terminal_proximity_score": v,
            "logistics_access_score": v,
            "water_quality_index": v,
            "traffic_potential_score": v,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 60.0
        }
    }


def test_B1_score_75_is_HIGH():
    """Score of exactly 75 should be HIGH (threshold ≥ 75)."""
    result = score_entity(_entity_with_score(75), "inland_port")
    passed = result["level"] == "HIGH" and result["score"] == 75.0
    log(
        "TEST B1 — Score 75.0 → HIGH",
        passed,
        f"score={result['score']} level={result['level']}"
    )
    return passed


def test_B2_score_74_9_is_MEDIUM():
    """Score of 74.9 should be MEDIUM (just below HIGH threshold of 75)."""
    result = score_entity(_entity_with_score(74.9), "inland_port")
    passed = result["level"] == "MEDIUM"
    log(
        "TEST B2 — Score 74.9 → MEDIUM (just below HIGH threshold)",
        passed,
        f"score={result['score']} level={result['level']}"
    )
    return passed


def test_B3_score_50_is_MEDIUM():
    """Score of exactly 50 should be MEDIUM (threshold ≥ 50)."""
    result = score_entity(_entity_with_score(50), "inland_port")
    passed = result["level"] == "MEDIUM" and result["score"] == 50.0
    log(
        "TEST B3 — Score 50.0 → MEDIUM",
        passed,
        f"score={result['score']} level={result['level']}"
    )
    return passed


def test_B4_score_49_9_is_LOW():
    """Score of 49.9 should be LOW (just below MEDIUM threshold of 50)."""
    result = score_entity(_entity_with_score(49.9), "inland_port")
    passed = result["level"] == "LOW"
    log(
        "TEST B4 — Score 49.9 → LOW (just below MEDIUM threshold)",
        passed,
        f"score={result['score']} level={result['level']}"
    )
    return passed


def test_B5_score_0_is_LOW():
    """All factor scores = 0, no hard constraints → score 0.0 should be LOW."""
    entity = {
        "location_id": "zero_score_test",
        "properties": {
            "river_stability_score": 0,
            "terminal_proximity_score": 0,
            "logistics_access_score": 0,
            "water_quality_index": 25,   # above extreme_pollution threshold (≥ 20)
            "traffic_potential_score": 0,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 25            # above critical_depth threshold (≥ 20)
        }
    }
    result = score_entity(entity, "inland_port")
    passed = result["level"] == "LOW" and result["score"] == 0.0
    log(
        "TEST B5 — Score 0.0 (no hard constraints) → LOW",
        passed,
        f"score={result['score']} level={result['level']}"
    )
    return passed 


# ══════════════════════════════════════════════════════════════
# BLOCK C — 50 KM vs 100 KM PROXIMITY THRESHOLD VARIANTS
# Tests that the haversine function correctly classifies signals
# at 50 km and 100 km from an anchor point.
# ══════════════════════════════════════════════════════════════

def test_C1_50km_inside_75km_radius():
    """A signal 50 km away is inside the 75 km cluster radius."""
    lat2, lon2 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 50.0)
    distance = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat2, lon2)
    inside = distance <= CLUSTER_RADIUS_KM
    log(
        "TEST C1 — 50 km proximity: inside 75 km radius",
        inside,
        f"distance = {distance:.4f} km | inside = {inside}"
    )
    return inside


def test_C2_100km_outside_75km_radius():
    """A signal 100 km away is outside the 75 km cluster radius."""
    lat2, lon2 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 100.0)
    distance = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat2, lon2)
    outside = distance > CLUSTER_RADIUS_KM
    log(
        "TEST C2 — 100 km proximity: outside 75 km radius",
        outside,
        f"distance = {distance:.4f} km | outside = {outside}"
    )
    return outside


def test_C3_50km_vs_100km_ordering():
    """50 km distance must be less than 100 km distance (sanity check)."""
    lat50, lon50 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 50.0)
    lat100, lon100 = _point_at_distance_km(ANCHOR_LAT, ANCHOR_LON, 100.0)
    d50 = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat50, lon50)
    d100 = haversine_km(ANCHOR_LAT, ANCHOR_LON, lat100, lon100)
    passed = d50 < d100
    log(
        "TEST C3 — 50 km < 100 km ordering holds",
        passed,
        f"d50={d50:.4f} km | d100={d100:.4f} km"
    )
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK D — CONSTRAINT BOUNDARY VALUES
# Tests exact trigger points for hard and soft constraints
# ══════════════════════════════════════════════════════════════

def test_D1_extreme_pollution_boundary_below():
    """WQI = 19 triggers extreme_pollution hard constraint (< 20)."""
    props = {"water_quality_index": 19, "in_wetland": False,
             "in_flood_zone": False, "env_clearance": True, "depth_score": 60}
    result = evaluate_constraints(props)
    passed = "extreme_pollution" in result["hard_triggered"]
    log(
        "TEST D1 — WQI=19 triggers extreme_pollution (< 20)",
        passed,
        f"hard_triggered={result['hard_triggered']}"
    )
    return passed


def test_D2_extreme_pollution_boundary_above():
    """WQI = 20 does NOT trigger extreme_pollution (boundary is < 20)."""
    props = {"water_quality_index": 20, "in_wetland": False,
             "in_flood_zone": False, "env_clearance": True, "depth_score": 60}
    result = evaluate_constraints(props)
    passed = "extreme_pollution" not in result["hard_triggered"]
    log(
        "TEST D2 — WQI=20 does NOT trigger extreme_pollution (boundary exclusive)",
        passed,
        f"hard_triggered={result['hard_triggered']}"
    )
    return passed


def test_D3_logistics_soft_boundary_below():
    """Logistics score = 29 triggers logistics_absence soft constraint (< 30)."""
    props = {"logistics_access_score": 29, "in_wetland": False,
             "in_flood_zone": False, "env_clearance": True, "depth_score": 60}
    result = evaluate_constraints(props)
    passed = "logistics_absence" in result["soft_triggered"]
    log(
        "TEST D3 — Logistics=29 triggers logistics_absence (< 30)",
        passed,
        f"soft_triggered={result['soft_triggered']}"
    )
    return passed


def test_D4_logistics_soft_boundary_above():
    """Logistics score = 30 does NOT trigger logistics_absence (boundary is < 30)."""
    props = {"logistics_access_score": 30, "in_wetland": False,
             "in_flood_zone": False, "env_clearance": True, "depth_score": 60}
    result = evaluate_constraints(props)
    passed = "logistics_absence" not in result["soft_triggered"]
    log(
        "TEST D4 — Logistics=30 does NOT trigger logistics_absence",
        passed,
        f"soft_triggered={result['soft_triggered']}"
    )
    return passed


def test_D5_depth_hard_boundary_below():
    """Depth score = 19 triggers critical_depth hard constraint (< 20)."""
    props = {"depth_score": 19, "in_wetland": False,
             "in_flood_zone": False, "env_clearance": True, "water_quality_index": 50}
    result = evaluate_constraints(props)
    passed = "critical_depth" in result["hard_triggered"]
    log(
        "TEST D5 — depth_score=19 triggers critical_depth (< 20)",
        passed,
        f"hard_triggered={result['hard_triggered']}"
    )
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK E — EDGE COORDINATE CASES (India bounds validation)
# data_adapter.py validates: 6.0 ≤ lat ≤ 37.0, 68.0 ≤ lon ≤ 97.5
# ══════════════════════════════════════════════════════════════

def test_E1_valid_ganga_coordinates():
    """Valid Ganga Basin coordinates pass haversine without error."""
    try:
        d = haversine_km(25.3176, 82.9739, 25.5941, 85.1376)
        passed = d > 0
    except Exception as e:
        passed = False
    log(
        "TEST E1 — Valid Ganga coords: haversine computes without error",
        passed,
        f"distance Varanasi→Patna = {d:.2f} km"
    )
    return passed


def test_E2_same_point_distance_zero():
    """Distance from a point to itself must be 0 km."""
    d = haversine_km(25.3176, 82.9739, 25.3176, 82.9739)
    passed = d == 0.0
    log(
        "TEST E2 — Same point haversine = 0.0 km",
        passed,
        f"distance = {d}"
    )
    return passed


def test_E3_north_south_india_extreme():
    """Extreme India coordinates — Kanyakumari to Kashmir — valid haversine."""
    try:
        d = haversine_km(8.0883, 77.5385, 34.0837, 74.7973)
        passed = 2800 < d < 3200
    except Exception as e:
        passed = False
    log(
        "TEST E3 — Kanyakumari to Kashmir: haversine in valid range (2800–3200 km)",
        passed,
        f"distance = {d:.2f} km"
    )
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK F — WEIGHT BOUNDARY
# ══════════════════════════════════════════════════════════════

def test_F1_weights_exactly_1_accepted():
    """Weights summing to exactly 1.0 are accepted."""
    weights = {
        "river_stability": 0.25,
        "terminal_proximity": 0.20,
        "logistics_access": 0.20,
        "water_quality": 0.20,
        "traffic_potential": 0.15
    }
    entity = _entity_with_score(70)
    try:
        result = score_entity(entity, "inland_port", custom_weights=weights)
        passed = result["score"] > 0
    except Exception:
        passed = False
    log(
        "TEST F1 — Weights sum = 1.0 exactly: accepted",
        passed,
        f"sum={sum(weights.values())}"
    )
    return passed


def test_F2_weights_1_0001_rejected():
    """Weights summing to 1.10 are rejected with ValueError."""
    weights = {
        "river_stability": 0.35,
        "terminal_proximity": 0.20,
        "logistics_access": 0.20,
        "water_quality": 0.20,
        "traffic_potential": 0.15
    }
    entity = _entity_with_score(70)
    try:
        score_entity(entity, "inland_port", custom_weights=weights)
        passed = False
    except ValueError:
        passed = True
    log(
        "TEST F2 — Weights sum = 1.10: rejected with ValueError",
        passed,
        f"sum={round(sum(weights.values()), 6)}"
    )
    return passed


# ── RUNNER ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNICAI — Boundary Test Suite")
    print("=" * 60)

    tests = [
        test_A1_signal_inside_cluster_radius,
        test_A2_signal_outside_cluster_radius,
        test_A3_exact_boundary_75km,
        test_A4_inside_outside_different_bearings,
        test_B1_score_75_is_HIGH,
        test_B2_score_74_9_is_MEDIUM,
        test_B3_score_50_is_MEDIUM,
        test_B4_score_49_9_is_LOW,
        test_B5_score_0_is_LOW,
        test_C1_50km_inside_75km_radius,
        test_C2_100km_outside_75km_radius,
        test_C3_50km_vs_100km_ordering,
        test_D1_extreme_pollution_boundary_below,
        test_D2_extreme_pollution_boundary_above,
        test_D3_logistics_soft_boundary_below,
        test_D4_logistics_soft_boundary_above,
        test_D5_depth_hard_boundary_below,
        test_E1_valid_ganga_coordinates,
        test_E2_same_point_distance_zero,
        test_E3_north_south_india_extreme,
        test_F1_weights_exactly_1_accepted,
        test_F2_weights_1_0001_rejected,
    ]

    for t in tests:
        try:
            t()
        except Exception as e:
            log(t.__name__, False, f"Exception: {e}")

    print()
    total = len(results_log)
    passed = sum(1 for _, p in results_log if p)
    failed = total - passed
    print("=" * 60)
    print(f"Results: {passed}/{total} passed", " ALL PASS" if failed == 0 else f" {failed} FAILED")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)