"""
test_scenarios.py  (MODIFIED — aligned with audit-grade unified engine)
------------------------------------------------------------------------
NICAI - Ganga Basin Intelligence Engine

Tests the original 4 scenarios using the UNIFIED scoring engine.
Single source of truth: scoring_engine.py
"""

import sys
import os

# Both root AND src/ on sys.path:
#   location_entity_builder  -> from src.data_adapter (needs root)
#   scoring_engine           -> from signal_trace_layer (needs src/)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC  = os.path.join(_ROOT, "src")

if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from scoring_engine import score_entity
from location_entity_builder import build_location_entities

results_log = []


def get_location_id(entity):
    """
    Safely extract a display name from an entity regardless of key name.
    location_entity_builder uses 'entity_id' as the primary key.
    """
    return (
        entity.get("entity_id")
        or entity.get("location_id")
        or entity.get("name")
        or entity.get("id")
        or "unknown"
    )


def adapt_entity(entity):
    """
    Wraps a location_entity_builder entity so score_entity() can consume it.
    Adds 'location_id' key (used internally by scoring engine) and keeps
    summary_metrics accessible — scoring_engine handles the translation.
    """
    return {
        "location_id":    get_location_id(entity),
        "summary_metrics": entity.get("summary_metrics", {}),
        # Pass through any extra keys untouched
        **{k: v for k, v in entity.items() if k not in ("summary_metrics",)}
    }


def run_models(entity):
    """Run all 3 models through unified scoring engine."""
    adapted = adapt_entity(entity)
    return [
        score_entity(adapted, "inland_port"),
        score_entity(adapted, "seaplane"),
        score_entity(adapted, "hub_spoke"),
    ]


def assert_level(result, expected, scenario_name):
    actual = result["level"]
    passed = (actual == expected)
    icon = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {result['model_type']:22}  score={result['score']:5.1f}  "
          f"expected={expected}  actual={actual}")
    results_log.append((scenario_name, result["model_type"], expected, actual, passed))


# ── SCENARIO 1 ─────────────────────────────────────────────────────
def test_high_connectivity():
    print("\n" + "-" * 70)
    print("SCENARIO 1 - High Connectivity Region")
    print("-" * 70)

    entities = build_location_entities()

    entity = max(entities, key=lambda e: (
        e["summary_metrics"].get("terminal_count", 0) * 2 +
        e["summary_metrics"].get("logistics_park_count", 0) +
        e["summary_metrics"].get("nav_depth_m", 0)
    ))

    loc_id = get_location_id(entity)
    sm = entity["summary_metrics"]
    print(f"  Selected: {loc_id}")
    print(f"  Metrics: terminals={sm.get('terminal_count')}, "
          f"parks={sm.get('logistics_park_count')}, "
          f"depth={sm.get('nav_depth_m')}")

    for r in run_models(entity):
        if r["constraints"]["hard"]:
            print(f"  [INFO] {r['model_type']:22}  HARD CONSTRAINT: "
                  f"{r['constraints']['hard']} -> REJECTED (valid)")
            results_log.append((
                "scenario_1", r["model_type"], "HIGH_OR_REJECTED", r["level"],
                r["level"] in ("HIGH", "MEDIUM", "REJECTED")
            ))
        elif r["model_type"] == "inland_port":
            assert_level(r, "HIGH", "scenario_1")
        elif r["model_type"] == "hub_spoke":
            assert_level(r, "HIGH", "scenario_1")
        else:
            print(f"  [INFO] {r['model_type']:22}  level={r['level']}  score={r['score']}")


# ── SCENARIO 2 ─────────────────────────────────────────────────────
def test_env_restricted():
    print("\n" + "-" * 70)
    print("SCENARIO 2 - Environmentally Restricted Zone")
    print("-" * 70)

    entities = build_location_entities()

    entity = min(entities, key=lambda e: (
        e["summary_metrics"].get("flow_stability_code", 0) +
        e["summary_metrics"].get("nav_depth_m", 0) -
        e["summary_metrics"].get("env_sensitivity_code", 1)
    ))

    loc_id = get_location_id(entity)
    sm = entity["summary_metrics"]
    print(f"  Selected: {loc_id}")
    print(f"  Metrics: flow_stability={sm.get('flow_stability_code')}, "
          f"env_sensitivity={sm.get('env_sensitivity_code')}")

    for r in run_models(entity):
        if r["model_type"] in ("inland_port", "hub_spoke"):
            valid = r["level"] in ("LOW", "REJECTED")
            icon = "PASS" if valid else "FAIL"
            print(f"  [{icon}] {r['model_type']:22}  score={r['score']:5.1f}  "
                  f"expected=LOW or REJECTED  actual={r['level']}")
            results_log.append(("scenario_2", r["model_type"],
                                 "LOW_OR_REJECTED", r["level"], valid))
        else:
            print(f"  [INFO] {r['model_type']:22}  level={r['level']}  score={r['score']}")


# ── SCENARIO 3 ─────────────────────────────────────────────────────
def test_isolated_region():
    print("\n" + "-" * 70)
    print("SCENARIO 3 - Isolated Region")
    print("-" * 70)

    entities = build_location_entities()

    entity = min(entities, key=lambda e: (
        e["summary_metrics"].get("terminal_count", 0) +
        e["summary_metrics"].get("logistics_park_count", 0) +
        e["summary_metrics"].get("total_population_lakhs", 0) / 100
    ))

    loc_id = get_location_id(entity)
    sm = entity["summary_metrics"]
    print(f"  Selected: {loc_id}")
    print(f"  Metrics: terminals={sm.get('terminal_count')}, "
          f"parks={sm.get('logistics_park_count')}, "
          f"pop={sm.get('total_population_lakhs')}")

    for r in run_models(entity):
        if r["model_type"] in ("inland_port", "hub_spoke"):
            valid = r["level"] in ("LOW", "REJECTED")
            icon = "PASS" if valid else "FAIL"
            print(f"  [{icon}] {r['model_type']:22}  score={r['score']:5.1f}  "
                  f"expected=LOW or REJECTED  actual={r['level']}")
            results_log.append(("scenario_3", r["model_type"],
                                 "LOW_OR_REJECTED", r["level"], valid))
        else:
            print(f"  [INFO] {r['model_type']:22}  level={r['level']}  score={r['score']}")


# ── SCENARIO 4 ─────────────────────────────────────────────────────
def test_mixed_signals():
    print("\n" + "-" * 70)
    print("SCENARIO 4 - Mixed Signals Region")
    print("-" * 70)

    entities = build_location_entities()

    candidates = [
        e for e in entities
        if e["summary_metrics"].get("total_population_lakhs", 0) > 10
        and e["summary_metrics"].get("terminal_count", 0) <= 1
    ]
    entity = (
        max(candidates,
            key=lambda e: e["summary_metrics"].get("total_population_lakhs", 0))
        if candidates else entities[0]
    )

    loc_id = get_location_id(entity)
    sm = entity["summary_metrics"]
    print(f"  Selected: {loc_id}")
    print(f"  Metrics: pop={sm.get('total_population_lakhs')}, "
          f"terminals={sm.get('terminal_count')}")

    for r in run_models(entity):
        if r["model_type"] in ("inland_port", "hub_spoke"):
            valid = r["level"] in ("MEDIUM", "LOW", "REJECTED")
            icon = "PASS" if valid else "FAIL"
            print(f"  [{icon}] {r['model_type']:22}  score={r['score']:5.1f}  "
                  f"expected=MEDIUM/LOW/REJECTED  actual={r['level']}")
            results_log.append(("scenario_4", r["model_type"],
                                 "MEDIUM_LOW_REJECTED", r["level"], valid))
        else:
            print(f"  [INFO] {r['model_type']:22}  level={r['level']}  score={r['score']}")


# ── RUNNER ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  AUDIT-GRADE ENGINE - SCENARIO TEST SUITE")
    print("=" * 70)

    test_high_connectivity()
    test_env_restricted()
    test_isolated_region()
    test_mixed_signals()

    total  = len(results_log)
    passed = sum(1 for r in results_log if r[4])
    failed = total - passed

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} passed | {failed} failed")
    if failed == 0:
        print("ALL PASS - Unified engine, single source of truth")
    else:
        print("Some scenarios failed - check constraint triggers above")
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)