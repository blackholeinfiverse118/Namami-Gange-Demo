"""
weight_engine.py
----------------
Handles weight adjustment for scenario simulations.

Rules (enforced, not optional):
  - Weights must sum to 1.0 (tolerance: 0.001)
  - No weight may be negative
  - If no custom weights provided, DEFAULT_WEIGHTS are used
"""

from scenario_model import DEFAULT_WEIGHTS
from typing import Dict


class WeightValidationError(Exception):
    pass


def resolve_weights(custom_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Returns the final weights to use for a scoring run.
    - If custom_weights is empty/None → returns DEFAULT_WEIGHTS (baseline)
    - If custom_weights is provided → validates and returns them

    """
    if not custom_weights:
        return dict(DEFAULT_WEIGHTS)

    _validate_weights(custom_weights)
    return dict(custom_weights)


def _validate_weights(weights: Dict[str, float]) -> None:
    if not weights:
        raise WeightValidationError("Weights dict is empty.")

    for key, val in weights.items():
        if not isinstance(val, (int, float)):
            raise WeightValidationError(f"Weight for '{key}' is not numeric: {val}")
        if val < 0:
            raise WeightValidationError(
                f"Weight for '{key}' is negative ({val}). Weights must be >= 0."
            )

    total = round(sum(weights.values()), 6)
    if abs(total - 1.0) > 0.001:
        raise WeightValidationError(
            f"Weights must sum to 1.0. Got {total:.6f}. "
            f"Adjust your weights so they sum to exactly 1.0."
        )


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Force-normalizes weights to sum to 1.0.
    """
    total = sum(weights.values())
    if total == 0:
        raise WeightValidationError("Cannot normalize weights that all sum to 0.")
    return {k: round(v / total, 6) for k, v in weights.items()}


def apply_weight_to_factors(factor_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Computes weighted composite score from individual factor scores.

    Args:
        factor_scores: e.g. {"logistics_access": 80, "water_quality": 60, ...}
        weights: e.g. {"logistics_access": 0.50, "water_quality": 0.10, ...}

    Returns:
        Weighted score (float, 0-100)

    """
    resolved = resolve_weights(weights)
    total_score = 0.0
    applied_weight = 0.0

    for factor, weight in resolved.items():
        score = factor_scores.get(factor, 0.0)
        total_score += score * weight
        applied_weight += weight

    # If weights don't cover all factors (partial weight set), renormalize
    if applied_weight > 0 and abs(applied_weight - 1.0) > 0.01:
        total_score = total_score / applied_weight

    return round(total_score, 4)


def explain_weight_changes(
    baseline_weights: Dict[str, float],
    scenario_weights: Dict[str, float]
) -> list:
    """
    Returns a list of human-readable strings explaining how weights changed
    between baseline and scenario.
    """
    explanations = []
    all_keys = set(list(baseline_weights.keys()) + list(scenario_weights.keys()))

    for key in sorted(all_keys):
        old = baseline_weights.get(key, 0.0)
        new = scenario_weights.get(key, 0.0)
        diff = round(new - old, 4)
        if abs(diff) > 0.001:
            direction = "increased" if diff > 0 else "decreased"
            explanations.append(
                f"Weight for '{key}' {direction} from {old:.2f} to {new:.2f} "
                f"(delta: {'+' if diff > 0 else ''}{diff:.4f})"
            )

    return explanations if explanations else ["No weight changes from baseline."]
