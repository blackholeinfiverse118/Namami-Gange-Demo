"""
test_api.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 2 — API Test Suite

Tests all Flask API endpoints:
  A. GET /health
  B. GET /locations
  C. GET /results
  D. POST /analyze-location — valid request
  E. POST /analyze-location — bad requests (missing fields, invalid model)
  F. GET /results — query param filtering
  G. Error handler responses (404, 405)

REQUIRES: API server running on http://localhost:5000
Start with: cd src && python api.py
"""

import sys
import json
import requests

BASE_URL = "http://localhost:5000"

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


def check_server():
    """Verify server is running before tests begin."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ── Clean entity for POST requests ───────────────────────────
VALID_ENTITY = {
    "entity": {
        "location_id": "varanasi_terminal",
        "properties": {
            "river_stability_score": 78,
            "terminal_proximity_score": 85,
            "logistics_access_score": 70,
            "water_quality_index": 60,
            "traffic_potential_score": 75,
            "in_wetland": False,
            "in_flood_zone": False,
            "env_clearance": True,
            "depth_score": 65
        }
    },
    "model_type": "inland_port"
}


# ══════════════════════════════════════════════════════════════
# BLOCK A — GET /health
# ══════════════════════════════════════════════════════════════

def test_A1_health_returns_200():
    """GET /health → 200 OK."""
    r = requests.get(f"{BASE_URL}/health")
    passed = r.status_code == 200
    log("TEST A1 — GET /health: returns 200", passed,
        f"status={r.status_code}")
    return passed


def test_A2_health_response_fields():
    """GET /health → response has required fields."""
    r = requests.get(f"{BASE_URL}/health").json()
    required = ["status", "entities_loaded", "models_available", "determinism", "ml_used"]
    missing = [f for f in required if f not in r]
    passed = len(missing) == 0
    log("TEST A2 — GET /health: all required fields present", passed,
        f"missing={missing} | status={r.get('status')} | ml_used={r.get('ml_used')}")
    return passed


def test_A3_health_ml_false():
    """GET /health → ml_used must be False (deterministic system)."""
    r = requests.get(f"{BASE_URL}/health").json()
    passed = r.get("ml_used") is False
    log("TEST A3 — GET /health: ml_used=False confirmed", passed,
        f"ml_used={r.get('ml_used')}")
    return passed


def test_A4_health_determinism_guaranteed():
    """GET /health → determinism field must be 'guaranteed'."""
    r = requests.get(f"{BASE_URL}/health").json()
    passed = r.get("determinism") == "guaranteed"
    log("TEST A4 — GET /health: determinism='guaranteed'", passed,
        f"determinism={r.get('determinism')}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK B — GET /locations
# ══════════════════════════════════════════════════════════════

def test_B1_locations_returns_200():
    """GET /locations → 200 OK."""
    r = requests.get(f"{BASE_URL}/locations")
    passed = r.status_code == 200
    log("TEST B1 — GET /locations: returns 200", passed,
        f"status={r.status_code}")
    return passed


def test_B2_locations_has_count_and_list():
    """GET /locations → response has 'count' and 'locations' fields."""
    r = requests.get(f"{BASE_URL}/locations").json()
    passed = "count" in r and "locations" in r and isinstance(r["locations"], list)
    log("TEST B2 — GET /locations: has count + locations list", passed,
        f"count={r.get('count')} locations_type={type(r.get('locations')).__name__}")
    return passed


def test_B3_locations_count_matches_list():
    """GET /locations → count field matches actual list length."""
    r = requests.get(f"{BASE_URL}/locations").json()
    passed = r.get("count") == len(r.get("locations", []))
    log("TEST B3 — GET /locations: count matches list length", passed,
        f"count={r.get('count')} list_len={len(r.get('locations', []))}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK C — GET /results
# ══════════════════════════════════════════════════════════════

def test_C1_results_returns_200():
    """GET /results → 200 OK."""
    r = requests.get(f"{BASE_URL}/results")
    passed = r.status_code == 200
    log("TEST C1 — GET /results: returns 200", passed,
        f"status={r.status_code}")
    return passed


def test_C2_results_contract_fields():
    """GET /results → every result has all contract fields."""
    r = requests.get(f"{BASE_URL}/results").json()
    required = ["location_id", "model_type", "score", "level",
                "trace", "constraints", "explanation", "scoring_model"]
    results = r.get("results", [])
    if not results:
        log("TEST C2 — GET /results: contract fields present", False, "No results returned")
        return False
    missing_per_result = []
    for res in results:
        missing = [f for f in required if f not in res]
        if missing:
            missing_per_result.append((res.get("location_id"), missing))
    passed = len(missing_per_result) == 0
    log("TEST C2 — GET /results: all contract fields present in every result", passed,
        f"checked {len(results)} results | missing={missing_per_result}")
    return passed


def test_C3_results_scores_are_numbers():
    """GET /results → all scores are numeric."""
    r = requests.get(f"{BASE_URL}/results").json()
    results = r.get("results", [])
    non_numeric = [res["location_id"] for res in results
                   if not isinstance(res.get("score"), (int, float))]
    passed = len(non_numeric) == 0
    log("TEST C3 — GET /results: all scores are numeric", passed,
        f"non-numeric scores at: {non_numeric}")
    return passed


def test_C4_results_levels_valid():
    """GET /results → all levels are valid values."""
    valid_levels = {"HIGH", "MEDIUM", "LOW", "REJECTED"}
    r = requests.get(f"{BASE_URL}/results").json()
    results = r.get("results", [])
    invalid = [res["location_id"] for res in results
               if res.get("level") not in valid_levels]
    passed = len(invalid) == 0
    log("TEST C4 — GET /results: all levels are valid (HIGH/MEDIUM/LOW/REJECTED)", passed,
        f"invalid levels at: {invalid}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK D — POST /analyze-location VALID REQUESTS
# ══════════════════════════════════════════════════════════════

def test_D1_analyze_valid_request():
    """POST /analyze-location with valid entity → 200 + scored result."""
    r = requests.post(f"{BASE_URL}/analyze-location", json=VALID_ENTITY)
    passed = r.status_code == 200
    log("TEST D1 — POST /analyze-location: valid request → 200", passed,
        f"status={r.status_code}")
    return passed


def test_D2_analyze_response_contract():
    """POST /analyze-location → response has all contract fields."""
    r = requests.post(f"{BASE_URL}/analyze-location", json=VALID_ENTITY).json()
    required = ["location_id", "model_type", "score", "level",
                "trace", "constraints", "explanation", "scoring_model"]
    missing = [f for f in required if f not in r]
    passed = len(missing) == 0
    log("TEST D2 — POST /analyze-location: all contract fields present", passed,
        f"missing={missing} | score={r.get('score')} level={r.get('level')}")
    return passed


def test_D3_analyze_deterministic_repeated():
    """POST /analyze-location → same request twice gives identical score."""
    r1 = requests.post(f"{BASE_URL}/analyze-location", json=VALID_ENTITY).json()
    r2 = requests.post(f"{BASE_URL}/analyze-location", json=VALID_ENTITY).json()
    passed = r1.get("score") == r2.get("score") and r1.get("level") == r2.get("level")
    log("TEST D3 — POST /analyze-location: deterministic (2 identical requests)", passed,
        f"run1={r1.get('score')} run2={r2.get('score')}")
    return passed


def test_D4_analyze_rejected_entity():
    """POST /analyze-location with wetland entity → REJECTED."""
    rejected_entity = {
        "entity": {
            "location_id": "farakka_wetland",
            "properties": {
                "river_stability_score": 74,
                "terminal_proximity_score": 60,
                "logistics_access_score": 45,
                "water_quality_index": 48,
                "traffic_potential_score": 40,
                "in_wetland": True,
                "in_flood_zone": False,
                "env_clearance": False,
                "depth_score": 60
            }
        },
        "model_type": "inland_port"
    }
    r = requests.post(f"{BASE_URL}/analyze-location", json=rejected_entity).json()
    passed = r.get("level") == "REJECTED" and r.get("score") == 0.0
    log("TEST D4 — POST /analyze-location: wetland entity → REJECTED score=0", passed,
        f"level={r.get('level')} score={r.get('score')}")
    return passed


def test_D5_analyze_all_three_models():
    """POST /analyze-location works for all 3 model types."""
    models = {
        "inland_port": VALID_ENTITY,
        "seaplane": {
            "entity": {
                "location_id": "varanasi_seaplane",
                "properties": {
                    "turbulence_index": 0.25,
                    "water_quality_index": 70,
                    "traffic_potential_score": 65,
                    "urban_proximity_score": 72,
                    "env_clearance": True,
                    "in_wetland": False,
                    "in_flood_zone": False
                }
            },
            "model_type": "seaplane"
        },
        "hub_spoke": {
            "entity": {
                "location_id": "hajipur_hub",
                "properties": {
                    "multi_node_proximity": 70,
                    "logistics_park_quality": 65,
                    "terminal_density_score": 60,
                    "connectivity_score": 68,
                    "urban_market_access": 72,
                    "in_wetland": False,
                    "in_flood_zone": False,
                    "env_clearance": True
                }
            },
            "model_type": "hub_spoke"
        }
    }
    all_passed = True
    details = []
    for model, payload in models.items():
        r = requests.post(f"{BASE_URL}/analyze-location", json=payload)
        ok = r.status_code == 200 and r.json().get("model_type") == model
        details.append(f"{model}={r.status_code}")
        if not ok:
            all_passed = False
    log("TEST D5 — POST /analyze-location: all 3 models work", all_passed,
        " | ".join(details))
    return all_passed


# ══════════════════════════════════════════════════════════════
# BLOCK E — POST /analyze-location BAD REQUESTS
# ══════════════════════════════════════════════════════════════

def test_E1_missing_entity_field():
    """POST /analyze-location with no 'entity' field → 400 error."""
    r = requests.post(f"{BASE_URL}/analyze-location",
                      json={"model_type": "inland_port"})
    passed = r.status_code == 400
    log("TEST E1 — POST /analyze-location: missing 'entity' → 400", passed,
        f"status={r.status_code} body={r.json().get('error','')[:60]}")
    return passed


def test_E2_unknown_model_type():
    """POST /analyze-location with unknown model_type → 400 error."""
    bad_payload = {**VALID_ENTITY, "model_type": "nonexistent_model"}
    r = requests.post(f"{BASE_URL}/analyze-location", json=bad_payload)
    passed = r.status_code == 400
    log("TEST E2 — POST /analyze-location: unknown model_type → 400", passed,
        f"status={r.status_code} error={r.json().get('error','')[:60]}")
    return passed


def test_E3_empty_json_body():
    """POST /analyze-location with empty JSON body → 400 error."""
    r = requests.post(f"{BASE_URL}/analyze-location", json={})
    passed = r.status_code == 400
    log("TEST E3 — POST /analyze-location: empty JSON body → 400", passed,
        f"status={r.status_code}")
    return passed


def test_E4_non_json_body():
    """POST /analyze-location with plain text body → 400 error."""
    r = requests.post(
        f"{BASE_URL}/analyze-location",
        data="this is not json",
        headers={"Content-Type": "text/plain"}
    )
    passed = r.status_code == 400
    log("TEST E4 — POST /analyze-location: non-JSON body → 400", passed,
        f"status={r.status_code}")
    return passed


def test_E5_missing_model_type_defaults():
    """POST /analyze-location with no model_type → defaults to inland_port."""
    payload = {"entity": VALID_ENTITY["entity"]}
    r = requests.post(f"{BASE_URL}/analyze-location", json=payload)
    passed = r.status_code == 200 and r.json().get("model_type") == "inland_port"
    log("TEST E5 — POST /analyze-location: missing model_type → defaults to inland_port", passed,
        f"status={r.status_code} model_type={r.json().get('model_type')}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK F — GET /results QUERY PARAM FILTERING
# ══════════════════════════════════════════════════════════════

def test_F1_filter_by_model():
    """GET /results?model=seaplane → all results are seaplane model."""
    r = requests.get(f"{BASE_URL}/results?model=seaplane").json()
    results = r.get("results", [])
    all_seaplane = all(res.get("model_type") == "seaplane" for res in results)
    passed = r.get("model_type") == "seaplane" and all_seaplane
    log("TEST F1 — GET /results?model=seaplane: all results are seaplane", passed,
        f"count={len(results)} all_seaplane={all_seaplane}")
    return passed


def test_F2_filter_by_level():
    """GET /results?level=REJECTED → all returned results are REJECTED."""
    r = requests.get(f"{BASE_URL}/results?level=REJECTED").json()
    results = r.get("results", [])
    all_rejected = all(res.get("level") == "REJECTED" for res in results)
    passed = all_rejected
    log("TEST F2 — GET /results?level=REJECTED: all results are REJECTED", passed,
        f"count={len(results)} all_rejected={all_rejected}")
    return passed


def test_F3_filter_by_location_id():
    """GET /results?location_id=varanasi_terminal → only that location."""
    r = requests.get(f"{BASE_URL}/results?location_id=varanasi_terminal").json()
    results = r.get("results", [])
    all_varanasi = all(res.get("location_id") == "varanasi_terminal" for res in results)
    passed = len(results) >= 1 and all_varanasi
    log("TEST F3 — GET /results?location_id=varanasi_terminal: filtered correctly", passed,
        f"count={len(results)} all_match={all_varanasi}")
    return passed


# ══════════════════════════════════════════════════════════════
# BLOCK G — ERROR HANDLERS
# ══════════════════════════════════════════════════════════════

def test_G1_404_unknown_endpoint():
    """GET /nonexistent → 404 with error message."""
    r = requests.get(f"{BASE_URL}/nonexistent_endpoint_xyz")
    passed = r.status_code == 404
    log("TEST G1 — GET /nonexistent: returns 404", passed,
        f"status={r.status_code}")
    return passed


def test_G2_405_wrong_method():
    """POST /health → 405 Method Not Allowed."""
    r = requests.post(f"{BASE_URL}/health", json={})
    passed = r.status_code == 405
    log("TEST G2 — POST /health: returns 405 Method Not Allowed", passed,
        f"status={r.status_code}")
    return passed


# ── RUNNER ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNICAI — API Test Suite")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print()

    if not check_server():
        print("  ERROR: API server not running.")
        print("  Start it with: cd src && python api.py")
        print("  Then re-run this test file.")
        sys.exit(1)

    print("  Server is running. Starting tests...\n")

    tests = [
        test_A1_health_returns_200,
        test_A2_health_response_fields,
        test_A3_health_ml_false,
        test_A4_health_determinism_guaranteed,
        test_B1_locations_returns_200,
        test_B2_locations_has_count_and_list,
        test_B3_locations_count_matches_list,
        test_C1_results_returns_200,
        test_C2_results_contract_fields,
        test_C3_results_scores_are_numbers,
        test_C4_results_levels_valid,
        test_D1_analyze_valid_request,
        test_D2_analyze_response_contract,
        test_D3_analyze_deterministic_repeated,
        test_D4_analyze_rejected_entity,
        test_D5_analyze_all_three_models,
        test_E1_missing_entity_field,
        test_E2_unknown_model_type,
        test_E3_empty_json_body,
        test_E4_non_json_body,
        test_E5_missing_model_type_defaults,
        test_F1_filter_by_model,
        test_F2_filter_by_level,
        test_F3_filter_by_location_id,
        test_G1_404_unknown_endpoint,
        test_G2_405_wrong_method,
    ]

    for t in tests:
        try:
            t()
        except requests.exceptions.ConnectionError:
            log(t.__name__, False, "Connection refused — is the server still running?")
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