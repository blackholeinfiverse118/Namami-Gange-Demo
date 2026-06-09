"""
sensitivity_engine.py

Sensitivity analysis and multi-scenario comparison.

Computes:
  - Per-location delta between baseline and scenario scores
  - Impact classification: INCREASE / DECREASE / NO CHANGE
  - Multi-scenario comparison: best, worst, most sensitive
  - Full explanation of why the score changed
"""

from typing import List, Dict, Any, Optional


# ── Delta threshold ───────────────────────────────────────────────────────────
# Scores on this system range 0–100.
# A delta of ±0.5 represents a half-point change on a 100-point scale.
# Changes smaller than this are considered floating-point noise from weight
# redistribution rather than a meaningful policy signal.
# This threshold is intentionally conservative — it means the system reports
# "NO CHANGE" only when the modification had negligible real-world effect.
# To make the system more or less sensitive, adjust this value:
#   Lower (e.g. 0.1) → reports more changes as INCREASE/DECREASE
#   Higher (e.g. 2.0) → only reports large structural shifts
DELTA_THRESHOLD = 0.5   # on a 0–100 scale


def analyse_sensitivity(
    location_id: str,
    baseline_score: float,
    scenario_score: float,
    scenario_id: str,
    factor_changes: Optional[List[str]] = None,
    constraint_changes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Computes sensitivity result for a single location across one scenario.
    """
    delta = round(scenario_score - baseline_score, 4)

    if delta > DELTA_THRESHOLD:
        impact = "INCREASE"
    elif delta < -DELTA_THRESHOLD:
        impact = "DECREASE"
    else:
        impact = "NO CHANGE"

    explanation = _build_explanation(
        delta, impact, factor_changes or [], constraint_changes or []
    )

    return {
        "location_id": location_id,
        "scenario_id": scenario_id,
        "baseline_score": round(baseline_score, 4),
        "scenario_score": round(scenario_score, 4),
        "delta": delta,
        "impact": impact,
        "explanation": explanation,
        "factor_changes": factor_changes or [],
        "constraint_changes": constraint_changes or [],
    }


def _build_explanation(
    delta: float,
    impact: str,
    factor_changes: List[str],
    constraint_changes: List[str],
) -> str:
    """
    Builds the WHY explanation for a sensitivity result.
    Answers: why did the score change, which factor caused it,
    and how did constraints affect the outcome.
    """
    parts = []

    if impact == "NO CHANGE":
        return (
            f"Score is stable (delta {delta:+.2f} is within the ±{DELTA_THRESHOLD} "
            "no-change threshold). No significant factors changed in this scenario."
        )

    direction = "increased" if delta > 0 else "decreased"
    parts.append(f"Score {direction} by {abs(delta):.2f} points.")

    if factor_changes:
        parts.append("Weight changes: " + "; ".join(factor_changes))

    if constraint_changes:
        parts.append("Constraint changes: " + "; ".join(constraint_changes))

    if not factor_changes and not constraint_changes:
        parts.append("Score shift due to scenario modifications (see scenario config).")

    return " ".join(parts)


# ── Multi-scenario comparison (Phase 5) ──────────────────────────────────────

def compare_scenarios(all_sensitivity_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compares results across multiple scenarios.
    Returns best scenario, worst scenario, and most sensitive location.
    """
    if not all_sensitivity_results:
        return {"error": "No results to compare."}

    scenario_ids = list({r["scenario_id"] for r in all_sensitivity_results})
    location_ids = list({r["location_id"] for r in all_sensitivity_results})

    # Per-scenario: average delta
    scenario_avg_delta = {}
    for sid in scenario_ids:
        deltas = [r["delta"] for r in all_sensitivity_results if r["scenario_id"] == sid]
        scenario_avg_delta[sid] = round(sum(deltas) / len(deltas), 4) if deltas else 0.0

    best_scenario_id  = max(scenario_avg_delta, key=scenario_avg_delta.get)
    worst_scenario_id = min(scenario_avg_delta, key=scenario_avg_delta.get)

    # Per-location: max absolute delta across all scenarios
    location_max_delta = {}
    for lid in location_ids:
        deltas = [abs(r["delta"]) for r in all_sensitivity_results if r["location_id"] == lid]
        location_max_delta[lid] = round(max(deltas), 4) if deltas else 0.0

    most_sensitive_location_id = max(location_max_delta, key=location_max_delta.get)

    # Retrieve representative results
    best_result = next(
        r for r in all_sensitivity_results if r["scenario_id"] == best_scenario_id
    )
    worst_result = next(
        r for r in all_sensitivity_results if r["scenario_id"] == worst_scenario_id
    )
    sensitive_result = next(
        r for r in all_sensitivity_results if r["location_id"] == most_sensitive_location_id
    )

    # Summary tables
    scenario_summary = [
        {
            "scenario_id": sid,
            "avg_delta": scenario_avg_delta[sid],
            "location_count": len([r for r in all_sensitivity_results if r["scenario_id"] == sid]),
        }
        for sid in sorted(scenario_ids)
    ]

    location_summary = [
        {
            "location_id": lid,
            "max_abs_delta": location_max_delta[lid],
            "sensitivity_rank": i + 1,
        }
        for i, lid in enumerate(
            sorted(location_ids, key=lambda l: location_max_delta[l], reverse=True)
        )
    ]

    return {
        "total_scenarios": len(scenario_ids),
        "total_locations": len(location_ids),
        "best_scenario": {
            "scenario_id": best_scenario_id,
            "avg_delta": scenario_avg_delta[best_scenario_id],
            "sample_result": best_result,
        },
        "worst_scenario": {
            "scenario_id": worst_scenario_id,
            "avg_delta": scenario_avg_delta[worst_scenario_id],
            "sample_result": worst_result,
        },
        "most_sensitive_location": {
            "location_id": most_sensitive_location_id,
            "max_abs_delta": location_max_delta[most_sensitive_location_id],
            "sample_result": sensitive_result,
        },
        "scenario_summary": scenario_summary,
        "location_summary": location_summary,
    }