"""
scenario_runner.py

Main orchestrator for the Scenario Simulation Layer.

It calls the existing scoring engine without modifying it,
applies scenario modifications through the new layer,
and returns structured sensitivity + comparison results.

"""

import json
import sys
import os

# Adding the src directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenario_model import (
    ScenarioInput,
    ScenarioModifications,
    DEFAULT_WEIGHTS,
    validate_scenario,
    parse_scenario_from_dict,
)
from weight_engine import (
    resolve_weights,
    apply_weight_to_factors,
    explain_weight_changes,
)
from constraint_engine import (
    evaluate_constraints,
    explain_constraint_changes,
    CONSTRAINT_MODE_STRICT,
    CONSTRAINT_MODE_SCENARIO,
)
from sensitivity_engine import analyse_sensitivity, compare_scenarios
from geo_output_builder import build_geo_output


def run_baseline(locations: list) -> dict:
    """
    Runs the baseline scoring — strict constraints, default weights.
    
    """
    return _score_locations(
        locations=locations,
        mode=CONSTRAINT_MODE_STRICT,
        weights=DEFAULT_WEIGHTS,
        exclude_zones=[],
        environmental_override=False,
    )


def run_scenario(locations: list, scenario: ScenarioInput) -> dict:
    """
    Runs a scenario simulation — with modifications from the scenario input.
    All runs are clearly flagged as SCENARIO MODE.
    """
    validate_scenario(scenario)

    mods = scenario.modifications
    weights = resolve_weights(mods.priority_weights) if mods.priority_weights else DEFAULT_WEIGHTS

    return _score_locations(
        locations=locations,
        mode=CONSTRAINT_MODE_SCENARIO,
        weights=weights,
        exclude_zones=mods.exclude_zones,
        environmental_override=mods.environmental_override,
    )


def _score_locations(
    locations: list,
    mode: str,
    weights: dict,
    exclude_zones: list,
    environmental_override: bool,
) -> dict:
    """
    Internal scoring loop.
    Calls constraint_engine and weight_engine
    """
    results = {}

    for loc in locations:
        loc_id = _get_location_id(loc)
        props   = loc.get("properties", loc)

        # Step 1: Evaluate constraints
        constraint_result = evaluate_constraints(
            location=loc,
            mode=mode,
            exclude_zones=exclude_zones,
            environmental_override=environmental_override,
        )

        # Step 2: If hard reject in this mode → score = 0
        if constraint_result["hard_reject"]:
            results[loc_id] = {
                "location_id":      loc_id,
                "score":            0.0,
                "level":            "REJECTED",
                "constraint_result": constraint_result,
                "factor_scores":    {},
                "weights_used":     weights,
                "mode":             "SCENARIO" if mode == CONSTRAINT_MODE_SCENARIO else "STRICT",
                "scenario_flag":    constraint_result["scenario_flag"],
            }
            continue

        # Step 3: Compute factor scores from location properties
        factor_scores = _extract_factor_scores(props)

        # Step 4: Apply weights
        composite_score = apply_weight_to_factors(factor_scores, weights)

        # Step 5: Classify level
        level = _classify_level(composite_score)

        results[loc_id] = {
            "location_id":       loc_id,
            "score":             composite_score,
            "level":             level,
            "constraint_result": constraint_result,
            "factor_scores":     factor_scores,
            "weights_used":      weights,
            "mode":              "SCENARIO" if mode == CONSTRAINT_MODE_SCENARIO else "STRICT",
            "scenario_flag":     constraint_result["scenario_flag"],
        }

    return results


def _extract_factor_scores(props: dict) -> dict:
    """
    Extracts individual factor scores (0-100) from location properties.
    Maps the raw data fields to the weight engine's factor keys.
    Handles missing values gracefully with 0.0 default.
    """
    return {
        "river_stability":    float(props.get("river_stability_score",    props.get("river_stability",    0.0))),
        "terminal_proximity": float(props.get("terminal_proximity_score", props.get("terminal_proximity", 0.0))),
        "logistics_access":   float(props.get("logistics_access_score",   props.get("logistics_access",   0.0))),
        "water_quality":      float(props.get("water_quality_score",      props.get("water_quality_index",0.0))),
        "traffic_potential":  float(props.get("traffic_potential_score",  props.get("traffic_potential",  0.0))),
    }


def _classify_level(score: float) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 45:
        return "MEDIUM"
    else:
        return "LOW"


def _get_location_id(loc: dict) -> str:
    props = loc.get("properties", loc)
    return str(
        props.get("location_id") or
        props.get("id") or
        props.get("name") or
        loc.get("id", "unknown")
    )


# ── Full simulation pipeline ──────────────────────────────────────────────────

def simulate(
    locations: list,
    scenario: ScenarioInput,
) -> dict:
    """
    Runs the full simulation pipeline for a single scenario.
    Returns baseline + scenario results + delta analysis + geo output.

    """
    # 1. Baseline
    baseline_results = run_baseline(locations)

    # 2. Scenario
    scenario_results = run_scenario(locations, scenario)

    # 3. Sensitivity analysis per location
    delta_analysis = []
    for loc_id in baseline_results:
        baseline_score = baseline_results[loc_id]["score"]
        scenario_score = scenario_results.get(loc_id, {}).get("score", baseline_score)

        # Explain WHY
        baseline_weights = DEFAULT_WEIGHTS
        scenario_weights = (
            scenario.modifications.priority_weights or DEFAULT_WEIGHTS
        )
        weight_explanations = explain_weight_changes(baseline_weights, scenario_weights)

        b_constraint = baseline_results[loc_id]["constraint_result"]
        s_constraint = scenario_results.get(loc_id, {}).get("constraint_result", b_constraint)
        constraint_explanations = explain_constraint_changes(b_constraint, s_constraint)

        delta_entry = analyse_sensitivity(
            location_id=loc_id,
            baseline_score=baseline_score,
            scenario_score=scenario_score,
            scenario_id=scenario.scenario_id,
            factor_changes=weight_explanations,
            constraint_changes=constraint_explanations,
        )
        delta_analysis.append(delta_entry)

    # 4. Geo output
    geo_output = build_geo_output(locations, baseline_results, scenario_results, delta_analysis)

    return {
        "scenario_id":      scenario.scenario_id,
        "description":      scenario.description,
        "scenario_mode":    True,
        "baseline_results": baseline_results,
        "scenario_results": scenario_results,
        "delta_analysis":   delta_analysis,
        "geo_output":       geo_output,
    }


def simulate_multiple(
    locations: list,
    scenarios: list,   # list of ScenarioInput
) -> dict:
    """
    Runs multiple scenario simulations and produces a comparison.
    
    """
    all_simulation_results = []
    all_delta_results = []

    for scenario in scenarios:
        result = simulate(locations, scenario)
        all_simulation_results.append(result)
        all_delta_results.extend(result["delta_analysis"])

    comparison = compare_scenarios(all_delta_results)

    return {
        "simulations":  all_simulation_results,
        "comparison":   comparison,
    }
