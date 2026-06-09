"""
scoring_engine.py  (MODIFIED — audit-grade scoring transparency)
─────────────────────────────────────────────────────────────────
NICAI – Ganga Basin Intelligence Engine
DAY 2 · PHASE 2A — Scoring Exposure

Every result now includes:
  "scoring_model": {
    "weights": {...},
    "thresholds": {...},
    "formula": "explicit text"
  }

Integrates with:
  - signal_trace_layer.py   → trace block
  - constraint_engine.py    → constraint block + penalty

Design: deterministic, fully explainable, no ML/randomness.
"""

from typing import Dict, Any, List, Optional
from signal_trace_layer import attach_trace
from constraint_engine import evaluate_constraints, build_constraint_block, apply_soft_penalty


# ─────────────────────────────────────────────
# SCORING MODELS — weights + thresholds
# ─────────────────────────────────────────────

SCORING_MODELS = {
    "inland_port": {
        "weights": {
            "river_stability":    0.25,
            "terminal_proximity": 0.20,
            "logistics_access":   0.20,
            "water_quality":      0.20,
            "traffic_potential":  0.15
        },
        "thresholds": {
            "HIGH":   75,
            "MEDIUM": 50,
            "LOW":    0
        },
        "formula": (
            "score = (river_stability_score × 0.25) + "
            "(terminal_proximity_score × 0.20) + "
            "(logistics_access_score × 0.20) + "
            "(water_quality_index × 0.20) + "
            "(traffic_potential_score × 0.15); "
            "then subtract soft constraint penalties; "
            "clamped to [0, 100]; "
            "HARD constraints → REJECT (score = 0, level = REJECTED)"
        ),
        "field_map": {
            "river_stability":    "river_stability_score",
            "terminal_proximity": "terminal_proximity_score",
            "logistics_access":   "logistics_access_score",
            "water_quality":      "water_quality_index",
            "traffic_potential":  "traffic_potential_score"
        }
    },

    "seaplane": {
        "weights": {
            "turbulence":        0.30,
            "water_quality":     0.25,
            "traffic_density":   0.15,
            "urban_proximity":   0.20,
            "env_clearance_adj": 0.10
        },
        "thresholds": {
            "HIGH":   70,
            "MEDIUM": 45,
            "LOW":    0
        },
        "formula": (
            "score = ((1 - turbulence_index) × 100 × 0.30) + "
            "(water_quality_index × 0.25) + "
            "(traffic_potential_score × 0.15) + "
            "(urban_proximity_score × 0.20) + "
            "(env_clearance_score × 100 × 0.10); "
            "then subtract soft constraint penalties; "
            "clamped to [0, 100]; "
            "HARD constraints → REJECT"
        ),
        "field_map": {
            "turbulence":        "turbulence_index",
            "water_quality":     "water_quality_index",
            "traffic_density":   "traffic_potential_score",
            "urban_proximity":   "urban_proximity_score",
            "env_clearance_adj": "env_clearance"
        }
    },

    "hub_spoke": {
        "weights": {
            "node_proximity":    0.20,
            "logistics_park":    0.25,
            "terminal_density":  0.20,
            "connectivity":      0.20,
            "market_access":     0.15
        },
        "thresholds": {
            "HIGH":   72,
            "MEDIUM": 48,
            "LOW":    0
        },
        "formula": (
            "score = (multi_node_proximity × 0.20) + "
            "(logistics_park_quality × 0.25) + "
            "(terminal_density_score × 0.20) + "
            "(connectivity_score × 0.20) + "
            "(urban_market_access × 0.15); "
            "then subtract soft constraint penalties; "
            "clamped to [0, 100]; "
            "HARD constraints → REJECT"
        ),
        "field_map": {
            "node_proximity":   "multi_node_proximity",
            "logistics_park":   "logistics_park_quality",
            "terminal_density": "terminal_density_score",
            "connectivity":     "connectivity_score",
            "market_access":    "urban_market_access"
        }
    }
}


# ─────────────────────────────────────────────
# LEVEL ASSIGNMENT
# ─────────────────────────────────────────────

def assign_level(score: float, thresholds: Dict[str, int]) -> str:
    if score >= thresholds["HIGH"]:
        return "HIGH"
    elif score >= thresholds["MEDIUM"]:
        return "MEDIUM"
    else:
        return "LOW"


# ─────────────────────────────────────────────
# FACTOR SCORE COMPUTATION
# ─────────────────────────────────────────────

def compute_factor_scores(props: Dict[str, Any], model_type: str) -> Dict[str, float]:
    """
    Returns per-factor raw scores (0–100) for a given entity and model.
    Normalises boolean env_clearance → 100/0.
    Normalises turbulence_index (0–1 inverse) → 0–100.
    """
    model = SCORING_MODELS[model_type]
    field_map = model["field_map"]
    factor_scores = {}

    for factor, field in field_map.items():
        value = props.get(field)
        if value is None:
            factor_scores[factor] = 0.0
            continue

        # Special normalisations
        if field in ("env_clearance",):
            factor_scores[factor] = 100.0 if value else 0.0
        elif field in ("turbulence_index", "flow_turbulence_index"):
            # Inverse: low turbulence → high score
            factor_scores[factor] = round((1.0 - float(value)) * 100.0, 2)
        else:
            factor_scores[factor] = float(value)

    return factor_scores


def compute_weighted_score(factor_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Applies weights to factor scores. Returns raw weighted sum (0–100).
    """
    total = 0.0
    for factor, weight in weights.items():
        total += factor_scores.get(factor, 0.0) * weight
    return round(total, 2)


# ─────────────────────────────────────────────
# EXPLANATION GENERATOR
# ─────────────────────────────────────────────

def build_explanation(
    factor_scores: Dict[str, float],
    weights: Dict[str, float],
    constraint_result: Dict[str, Any],
    final_score: float,
    level: str,
    model_type: str
) -> str:
    """
    Generates a human-readable explanation of how the score was reached.
    """
    lines = [f"Model: {model_type.replace('_', ' ').title()} | Level: {level} | Score: {final_score}"]

    lines.append("Factor contributions:")
    for factor, weight in weights.items():
        fs = factor_scores.get(factor, 0.0)
        contribution = round(fs * weight, 2)
        lines.append(f"  {factor}: {fs} × {weight} = {contribution}")

    if constraint_result["soft_triggered"]:
        lines.append(f"Soft constraint penalties: -{constraint_result['total_soft_penalty']} pts")
        for name in constraint_result["soft_triggered"]:
            lines.append(f"  • {name}")

    if constraint_result["hard_triggered"]:
        lines.append(f"HARD CONSTRAINTS TRIGGERED → REJECTED")
        for name in constraint_result["hard_triggered"]:
            lines.append(f"  ✗ {name}: {constraint_result['constraint_detail'][name]['explanation']}")

    if constraint_result["overridden"]:
        lines.append(f"Overridden in scenario (flagged for audit):")
        for name in constraint_result["overridden"]:
            lines.append(f"  ⚠ {name}")

    return " | ".join(lines)


# ─────────────────────────────────────────────
# MAIN SCORE FUNCTION
# ─────────────────────────────────────────────

def score_entity(
    entity: Dict[str, Any],
    model_type: str,
    custom_weights: Optional[Dict[str, float]] = None,
    scenario_overrides: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Scores a single location entity.

    Args:
        entity: dict with "location_id" and "properties" keys
        model_type: one of "inland_port", "seaplane", "hub_spoke"
        custom_weights: optional weight overrides (must sum to 1.0)
        scenario_overrides: constraint names to bypass in scenario mode

    Returns:
        Full scored result with trace, constraints, scoring_model, explanation.
    """
    if model_type not in SCORING_MODELS:
        raise ValueError(f"Unknown model_type: {model_type}. Must be one of {list(SCORING_MODELS.keys())}")

    # ── Input schema resolution ───────────────────────────────────
    # Supports two input formats:
    #   1. API input:      entity["properties"] → pre-normalised scoring fields
    #   2. Internal input: entity["summary_metrics"] → raw dataset fields
    #      (produced by location_entity_builder.py from real CSVs)
    # This keeps the engine as single source of truth for both paths.

    if "properties" in entity:
        # API / demo / test input — already in scoring field format
        props = entity["properties"]

    elif "summary_metrics" in entity:
        # Internal entity from location_entity_builder — translate raw metrics
        sm = entity["summary_metrics"]

        # Normalisation rules (deterministic, no ML):
        #   flow_stability_code: 0–4 scale → multiply × 25 → 0–100
        #   terminal_count: count → multiply × 20, capped at 100
        #   logistics_park_count: count → multiply × 20, capped at 100
        #   avg_bod_mg_l: BOD (lower = better) → 100 − (BOD × 5), clamped 0–100
        #   total_population_lakhs: demand proxy → multiply × 2, capped at 100
        #   turbulence_index: 0–1 (lower = better, already normalised)
        #   env_sensitivity_code: 1=low, 2=medium, 3=high sensitivity
        #     clearance granted if sensitivity code <= 2
        #   has_rail: 0/1 boolean → connectivity score (50 pts if present)
        #   nav_depth_m: metres → multiply × 10, capped at 100

        props = {
            # ── Inland port fields ──────────────────────────────
            "river_stability_score":    min(100.0, sm.get("flow_stability_code", 0) * 25.0),
            "terminal_proximity_score": min(100.0, sm.get("terminal_count", 0) * 20.0),
            "logistics_access_score":   min(100.0, sm.get("logistics_park_count", 0) * 20.0),
            "water_quality_index":      max(0.0, min(100.0, 100.0 - sm.get("avg_bod_mg_l", 0) * 5.0)),
            "traffic_potential_score":  min(100.0, sm.get("total_population_lakhs", 0) * 2.0),
            "depth_score":              min(100.0, sm.get("nav_depth_m", 0) * 10.0),

            # ── Constraint fields ───────────────────────────────
            "in_wetland":    sm.get("in_wetland", False),
            "in_flood_zone": sm.get("in_flood_zone", False),
            "env_clearance": sm.get("env_sensitivity_code", 3) <= 2,

            # ── Seaplane fields ─────────────────────────────────
            "turbulence_index":      sm.get("turbulence_index",
                                        max(0.0, 1.0 - sm.get("flow_stability_code", 0) / 4.0)),
            "urban_proximity_score": min(100.0, sm.get("total_population_lakhs", 0) * 2.0),

            # ── Hub-spoke fields ────────────────────────────────
            "multi_node_proximity":   min(100.0,
                                        (sm.get("terminal_count", 0) + sm.get("logistics_park_count", 0)) * 10.0),
            "logistics_park_quality": min(100.0, sm.get("logistics_park_count", 0) * 20.0),
            "terminal_density_score": min(100.0, sm.get("terminal_count", 0) * 20.0),
            "connectivity_score":     sm.get("has_rail", 0) * 50.0 +
                                      min(50.0, sm.get("logistics_park_count", 0) * 10.0),
            "urban_market_access":    min(100.0, sm.get("total_population_lakhs", 0) * 2.0),
        }

    else:
        # Flat dict — treat as props directly (legacy / fallback)
        props = entity

    location_id = entity.get("location_id") or props.get("location_id", "unknown")

    model_def = SCORING_MODELS[model_type]
    weights = custom_weights if custom_weights else model_def["weights"]
    thresholds = model_def["thresholds"]

    # Validate weights sum to 1.0
    weight_sum = round(sum(weights.values()), 4)
    if abs(weight_sum - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0. Got: {weight_sum}")

    # ── Step 1: Evaluate constraints ─────────────────────────────
    constraint_result = evaluate_constraints(props, scenario_overrides or [])

    # ── Step 2: Compute factor scores ────────────────────────────
    factor_scores = compute_factor_scores(props, model_type)

    # ── Step 3: Compute weighted score ───────────────────────────
    raw_score = compute_weighted_score(factor_scores, weights)

    # ── Step 4: Apply soft penalties ─────────────────────────────
    penalised_score = apply_soft_penalty(raw_score, constraint_result)

    # ── Step 5: Hard constraint → REJECT ─────────────────────────
    if constraint_result["is_rejected"]:
        final_score = 0.0
        level = "REJECTED"
    else:
        final_score = penalised_score
        level = assign_level(final_score, thresholds)

    # ── Step 6: Build explanation ─────────────────────────────────
    explanation = build_explanation(
        factor_scores, weights, constraint_result, final_score, level, model_type
    )

    # ── Step 7: Assemble result ───────────────────────────────────
    result = {
        "location_id": location_id,
        "model_type": model_type,
        "score": final_score,
        "level": level,
        "factor_scores": factor_scores,
        "constraints": build_constraint_block(constraint_result),
        "scoring_model": {
            "weights": weights,
            "thresholds": thresholds,
            "formula": model_def["formula"]
        },
        "explanation": explanation
    }

    # ── Step 8: Attach signal trace ───────────────────────────────
    result = attach_trace(result, props, model_type)

    return result


def score_all(
    entities: List[Dict[str, Any]],
    model_type: str,
    custom_weights: Optional[Dict[str, float]] = None,
    scenario_overrides: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Scores a list of entities. Returns list of full scored results.
    """
    return [score_entity(e, model_type, custom_weights, scenario_overrides) for e in entities]


# ─────────────────────────────────────────────
# QUICK SELF-TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    entities = [
        {
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
                "pollution_index": 45
            }
        },
        {
            "location_id": "patna_wetland_site",
            "properties": {
                "river_stability_score": 80,
                "terminal_proximity_score": 70,
                "logistics_access_score": 65,
                "water_quality_index": 55,
                "traffic_potential_score": 60,
                "in_wetland": True,   # → HARD REJECT
                "in_flood_zone": False,
                "env_clearance": True
            }
        }
    ]

    results = score_all(entities, "inland_port")
    for r in results:
        print(json.dumps(r, indent=2))
        print("─" * 60)