"""
test_determinism.py
────────────────────────────────────────────────────────────
NICAI - Namami Gange Intelligence Convergence Sprint
Phase 2 — Deterministic Test Hardening

Runs the same input through the scoring engine 10 times.
Asserts: identical score, level, explanation, trace on every run.
This is the determinism proof required for showcase readiness.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scoring_engine import score_entity, score_all

# ── Test entities (one per suitability outcome) ──────────────────
ENTITY_HIGH = {
    "location_id": "patna_river_port",
    "properties": {
        "river_stability_score": 85,
        "terminal_proximity_score": 80,
        "logistics_access_score": 75,
        "water_quality_index": 55,
        "traffic_potential_score": 80,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 72
    }
}

ENTITY_MEDIUM = {
    "location_id": "hajipur_hub",
    "properties": {
        "river_stability_score": 72,
        "terminal_proximity_score": 68,
        "logistics_access_score": 62,
        "water_quality_index": 58,
        "traffic_potential_score": 65,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 62
    }
}

ENTITY_REJECTED = {
    "location_id": "kanpur_industrial_zone",
    "properties": {
        "river_stability_score": 60,
        "terminal_proximity_score": 65,
        "logistics_access_score": 80,
        "water_quality_index": 18,   # triggers extreme_pollution → REJECTED
        "traffic_potential_score": 75,
        "in_wetland": False,
        "in_flood_zone": False,
        "env_clearance": True,
        "depth_score": 55
    }
}

ALL_ENTITIES = [ENTITY_HIGH, ENTITY_MEDIUM, ENTITY_REJECTED]
RUNS = 10

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


# ── TEST 1: Single entity — 10 runs, score identical ─────────────
def test_single_entity_score_determinism():
    scores = [score_entity(ENTITY_HIGH, "inland_port")["score"] for _ in range(RUNS)]
    all_same = len(set(scores)) == 1
    log(
        f"TEST 1 — Single entity score: {RUNS} runs identical",
        all_same,
        f"all scores = {scores[0]} | unique values = {set(scores)}"
    )
    return all_same


# ── TEST 2: Single entity — 10 runs, level identical ─────────────
def test_single_entity_level_determinism():
    levels = [score_entity(ENTITY_HIGH, "inland_port")["level"] for _ in range(RUNS)]
    all_same = len(set(levels)) == 1
    log(
        f"TEST 2 — Single entity level: {RUNS} runs identical",
        all_same,
        f"all levels = {levels[0]} | unique values = {set(levels)}"
    )
    return all_same


# ── TEST 3: Single entity — 10 runs, explanation identical ───────
def test_single_entity_explanation_determinism():
    explanations = [score_entity(ENTITY_HIGH, "inland_port")["explanation"] for _ in range(RUNS)]
    all_same = len(set(explanations)) == 1
    log(
        f"TEST 3 — Single entity explanation: {RUNS} runs identical",
        all_same,
        f"unique explanation count = {len(set(explanations))}"
    )
    return all_same


# ── TEST 4: Single entity — 10 runs, trace identical ─────────────
def test_single_entity_trace_determinism():
    import json
    traces = [
        json.dumps(score_entity(ENTITY_HIGH, "inland_port")["trace"], sort_keys=True)
        for _ in range(RUNS)
    ]
    all_same = len(set(traces)) == 1
    log(
        f"TEST 4 — Single entity trace: {RUNS} runs identical",
        all_same,
        f"unique trace count = {len(set(traces))}"
    )
    return all_same


# ── TEST 5: REJECTED entity — 10 runs, always REJECTED, score 0 ──
def test_rejected_entity_determinism():
    results = [score_entity(ENTITY_REJECTED, "inland_port") for _ in range(RUNS)]
    scores = [r["score"] for r in results]
    levels = [r["level"] for r in results]
    all_zero = all(s == 0.0 for s in scores)
    all_rejected = all(l == "REJECTED" for l in levels)
    log(
        f"TEST 5 — REJECTED entity: {RUNS} runs always score=0.0 level=REJECTED",
        all_zero and all_rejected,
        f"scores unique={set(scores)} levels unique={set(levels)}"
    )
    return all_zero and all_rejected


# ── TEST 6: Batch run — 10 full score_all runs, all identical ─────
def test_batch_run_determinism():
    import json
    runs = [
        json.dumps(score_all(ALL_ENTITIES, "inland_port"), sort_keys=True)
        for _ in range(RUNS)
    ]
    all_same = len(set(runs)) == 1
    log(
        f"TEST 6 — Batch score_all: {RUNS} runs, all 3 entities identical",
        all_same,
        f"unique batch outputs = {len(set(runs))}"
    )
    return all_same


# ── TEST 7: Cross-model determinism — seaplane model, 10 runs ────
def test_seaplane_model_determinism():
    seaplane_entity = {
        "location_id": "varanasi_terminal",
        "properties": {
            "turbulence_index": 0.25,
            "water_quality_index": 70,
            "traffic_potential_score": 65,
            "urban_proximity_score": 72,
            "env_clearance": True,
            "in_wetland": False,
            "in_flood_zone": False
        }
    }
    scores = [score_entity(seaplane_entity, "seaplane")["score"] for _ in range(RUNS)]
    all_same = len(set(scores)) == 1
    log(
        f"TEST 7 — Seaplane model: {RUNS} runs identical",
        all_same,
        f"score = {scores[0]} | unique = {set(scores)}"
    )
    return all_same


# ── TEST 8: Cross-model determinism — hub_spoke model, 10 runs ───
def test_hub_spoke_model_determinism():
    hub_entity = {
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
    }
    scores = [score_entity(hub_entity, "hub_spoke")["score"] for _ in range(RUNS)]
    all_same = len(set(scores)) == 1
    log(
        f"TEST 8 — Hub-Spoke model: {RUNS} runs identical",
        all_same,
        f"score = {scores[0]} | unique = {set(scores)}"
    )
    return all_same


# ── TEST 9: Scenario weights — 10 runs, identical under custom weights
def test_scenario_weights_determinism():
    custom_weights = {
        "river_stability": 0.10,
        "terminal_proximity": 0.10,
        "logistics_access": 0.50,
        "water_quality": 0.15,
        "traffic_potential": 0.15
    }
    scores = [
        score_entity(ENTITY_MEDIUM, "inland_port", custom_weights=custom_weights)["score"]
        for _ in range(RUNS)
    ]
    all_same = len(set(scores)) == 1
    log(
        f"TEST 9 — Custom weights scenario: {RUNS} runs identical",
        all_same,
        f"score = {scores[0]} | unique = {set(scores)}"
    )
    return all_same


# ── TEST 10: Constraint override — 10 runs, identical with override
def test_override_determinism():
    scores = [
        score_entity(ENTITY_MEDIUM, "inland_port",
                     scenario_overrides=["logistics_absence"])["score"]
        for _ in range(RUNS)
    ]
    all_same = len(set(scores)) == 1
    log(
        f"TEST 10 — Constraint override scenario: {RUNS} runs identical",
        all_same,
        f"score = {scores[0]} | unique = {set(scores)}"
    )
    return all_same


# ── RUNNER ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNICAI — Determinism Test Suite (10-Run Proof)")
    print("=" * 60)
    print(f"Each test runs the engine {RUNS} times on identical input.")
    print(f"All {RUNS} outputs must be identical to pass.\n")

    tests = [
        test_single_entity_score_determinism,
        test_single_entity_level_determinism,
        test_single_entity_explanation_determinism,
        test_single_entity_trace_determinism,
        test_rejected_entity_determinism,
        test_batch_run_determinism,
        test_seaplane_model_determinism,
        test_hub_spoke_model_determinism,
        test_scenario_weights_determinism,
        test_override_determinism,
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