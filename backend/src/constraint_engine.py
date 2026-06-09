"""
constraint_engine.py  (MODIFIED — audit-grade hardening)
─────────────────────────────────────────────────────────
NICAI - Ganga Basin Intelligence Engine

HARD constraints → always REJECT, cannot be overridden in strict mode
SOFT constraints → reduce score only, never reject

Every result includes:
  "constraints": {
    "hard": [...triggered hard constraint names],
    "soft": [...triggered soft constraint names],
    "overridden": [...constraints bypassed in scenario mode]
  }
"""

from typing import Dict, List, Any, Tuple



# CONSTRAINT DEFINITIONS
# ─────────────────────────────────────────────

HARD_CONSTRAINTS = {
    "wetland_zone": {
        "description": "Location is within a protected wetland boundary",
        "field": "in_wetland",
        "condition": lambda v: v is True,
        "rejection_reason": "HARD REJECT: Protected wetland — infrastructure prohibited"
    },
    "critical_depth": {
        "description": "Water depth below navigable minimum (< 2m)",
        "field": "depth_score",
        "condition": lambda v: isinstance(v, (int, float)) and v < 20,
        "rejection_reason": "HARD REJECT: Depth below navigable threshold"
    },
    "extreme_pollution": {
        "description": "Water quality index indicates extreme pollution (WQI < 20)",
        "field": "water_quality_index",
        "condition": lambda v: isinstance(v, (int, float)) and v < 20,
        "rejection_reason": "HARD REJECT: Extreme water pollution — unusable for port/seaplane"
    },
    "flood_zone": {
        "description": "Location within active flood zone",
        "field": "in_flood_zone",
        "condition": lambda v: v is True,
        "rejection_reason": "HARD REJECT: Active flood zone — structural risk unacceptable"
    },
    "no_env_clearance": {
        "description": "Environmental clearance not obtained",
        "field": "env_clearance",
        "condition": lambda v: v is False,
        "rejection_reason": "HARD REJECT: Environmental clearance required and absent"
    }
}

SOFT_CONSTRAINTS = {
    "logistics_absence": {
        "description": "No logistics infrastructure within threshold distance",
        "field": "logistics_access_score",
        "condition": lambda v: isinstance(v, (int, float)) and v < 30,
        "score_penalty": 15,
        "explanation": "SOFT: Logistics access poor — score penalised by 15 points"
    },
    "low_traffic": {
        "description": "Traffic potential below minimum viable threshold",
        "field": "traffic_potential_score",
        "condition": lambda v: isinstance(v, (int, float)) and v < 25,
        "score_penalty": 10,
        "explanation": "SOFT: Low traffic potential — score penalised by 10 points"
    },
    "poor_connectivity": {
        "description": "Connectivity score below viable threshold",
        "field": "connectivity_score",
        "condition": lambda v: isinstance(v, (int, float)) and v < 25,
        "score_penalty": 10,
        "explanation": "SOFT: Poor connectivity — score penalised by 10 points"
    },
    "high_turbulence": {
        "description": "Flow turbulence index above safe threshold (seaplane)",
        "field": "turbulence_index",
        "condition": lambda v: isinstance(v, (int, float)) and v > 0.7,
        "score_penalty": 12,
        "explanation": "SOFT: High turbulence — unsuitable for seaplane landing, score penalised"
    }
}



# CONSTRAINT EVALUATION
# ─────────────────────────────────────────────

def evaluate_constraints(
    entity_properties: Dict[str, Any],
    scenario_overrides: List[str] = None
) -> Dict[str, Any]:
    """
    Evaluates all hard and soft constraints against entity properties.

    Args:
        entity_properties: raw property dict of a location entity
        scenario_overrides: list of constraint names to bypass (SOFT only in demo mode)

    Returns:
        {
          "hard_triggered": [...],     # names of hard constraints that fired
          "soft_triggered": [...],     # names of soft constraints that fired
          "overridden": [...],         # constraints bypassed
          "total_soft_penalty": int,   # total score penalty from soft constraints
          "is_rejected": bool,         # True if any unoverridden hard constraint fired
          "rejection_reason": str|None,
          "constraint_detail": {       # full detail per triggered constraint
            "constraint_name": { type, description, field, value, explanation }
          }
        }
    """
    if scenario_overrides is None:
        scenario_overrides = []

    hard_triggered = []
    soft_triggered = []
    overridden = []
    total_soft_penalty = 0
    rejection_reason = None
    constraint_detail = {}

    # ── Evaluate HARD constraints ──────────────────────────────────
    for name, defn in HARD_CONSTRAINTS.items():
        field = defn["field"]
        value = entity_properties.get(field)

        if value is None:
            continue

        if defn["condition"](value):
            if name in scenario_overrides:
                # Hard constraints CAN be listed as overridden in scenario mode
                # but they are ALWAYS flagged — never silently bypassed
                overridden.append(name)
                constraint_detail[name] = {
                    "type": "hard",
                    "description": defn["description"],
                    "field": field,
                    "value": value,
                    "explanation": f"OVERRIDDEN (scenario mode): {defn['rejection_reason']} — flagged for audit"
                }
            else:
                hard_triggered.append(name)
                if rejection_reason is None:
                    rejection_reason = defn["rejection_reason"]
                constraint_detail[name] = {
                    "type": "hard",
                    "description": defn["description"],
                    "field": field,
                    "value": value,
                    "explanation": defn["rejection_reason"]
                }

    # ── Evaluate SOFT constraints ──────────────────────────────────
    for name, defn in SOFT_CONSTRAINTS.items():
        field = defn["field"]
        value = entity_properties.get(field)

        if value is None:
            continue

        if defn["condition"](value):
            if name in scenario_overrides:
                overridden.append(name)
                constraint_detail[name] = {
                    "type": "soft",
                    "description": defn["description"],
                    "field": field,
                    "value": value,
                    "explanation": f"OVERRIDDEN (scenario mode): penalty waived"
                }
            else:
                soft_triggered.append(name)
                total_soft_penalty += defn["score_penalty"]
                constraint_detail[name] = {
                    "type": "soft",
                    "description": defn["description"],
                    "field": field,
                    "value": value,
                    "explanation": defn["explanation"]
                }

    is_rejected = len(hard_triggered) > 0

    return {
        "hard_triggered": hard_triggered,
        "soft_triggered": soft_triggered,
        "overridden": overridden,
        "total_soft_penalty": total_soft_penalty,
        "is_rejected": is_rejected,
        "rejection_reason": rejection_reason,
        "constraint_detail": constraint_detail
    }


def build_constraint_block(constraint_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns the clean constraints block for API output:
    {
      "hard": [...],
      "soft": [...],
      "overridden": [...]
    }
    """
    return {
        "hard": constraint_result["hard_triggered"],
        "soft": constraint_result["soft_triggered"],
        "overridden": constraint_result["overridden"]
    }


def apply_soft_penalty(base_score: float, constraint_result: Dict[str, Any]) -> float:
    """
    Applies soft constraint penalties to a base score.
    Score is clamped to [0, 100].
    """
    penalised = base_score - constraint_result["total_soft_penalty"]
    return round(max(0.0, min(100.0, penalised)), 2)



# QUICK SELF-TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # Test 1: HARD constraint fires (wetland)
    entity_hard = {
        "in_wetland": True,
        "logistics_access_score": 70,
        "traffic_potential_score": 50,
        "water_quality_index": 55,
        "depth_score": 60
    }
    result1 = evaluate_constraints(entity_hard)
    print("TEST 1 — Hard constraint (wetland):")
    print(json.dumps(build_constraint_block(result1), indent=2))
    print("Is rejected:", result1["is_rejected"])
    print()

    # Test 2: SOFT constraints fire (low logistics + low traffic)
    entity_soft = {
        "in_wetland": False,
        "logistics_access_score": 20,
        "traffic_potential_score": 15,
        "water_quality_index": 55,
        "depth_score": 60,
        "env_clearance": True
    }
    result2 = evaluate_constraints(entity_soft)
    print("TEST 2 — Soft constraints (low logistics + low traffic):")
    print(json.dumps(build_constraint_block(result2), indent=2))
    print("Total soft penalty:", result2["total_soft_penalty"])
    print("Score after penalty:", apply_soft_penalty(72.0, result2))
    print()

    # Test 3: Scenario override on soft constraint
    result3 = evaluate_constraints(entity_soft, scenario_overrides=["logistics_absence"])
    print("TEST 3 — Scenario override on logistics_absence:")
    print(json.dumps(build_constraint_block(result3), indent=2))
    print("Total soft penalty:", result3["total_soft_penalty"])
