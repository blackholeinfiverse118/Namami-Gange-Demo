"""
scenario_model.py

Defines the scenario input schema and validation logic.
This is the simulation control layer.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


# ── Default weights used by the baseline engine ──────────────────────────────
DEFAULT_WEIGHTS = {
    "river_stability":       0.20,
    "terminal_proximity":    0.20,
    "logistics_access":      0.20,
    "water_quality":         0.20,
    "traffic_potential":     0.20,
}

# All valid constraint keys that can be overridden in scenario mode
VALID_CONSTRAINT_KEYS = [
    "wetlands",
    "flood_zone",
    "environmental_clearance",
    "water_quality_threshold",
    "turbulence_limit",
]


@dataclass
class ScenarioModifications:
    """
    All possible modifications a scenario can apply.
    Every field is optional — unset fields fall back to baseline defaults.
    """
    exclude_zones: List[str] = field(default_factory=list)
    # e.g. ["wetlands", "flood_zone"]

    priority_weights: Dict[str, float] = field(default_factory=dict)
    # e.g. {"logistics_access": 0.50, "water_quality": 0.10, ...}
    # Must sum to 1.0 if provided

    distance_thresholds: Dict[str, float] = field(default_factory=dict)
    # e.g. {"terminal_proximity_km": 30.0}

    traffic_conditions: Dict[str, Any] = field(default_factory=dict)
    # e.g. {"congestion_factor": 0.8}

    environmental_override: bool = False
    # If True, environmental hard-rejects are downgraded to warnings in scenario mode


@dataclass
class ScenarioInput:
    """
    Full scenario input — what the POST /simulate endpoint receives.
    """
    scenario_id: str
    description: str
    modifications: ScenarioModifications = field(default_factory=ScenarioModifications)

    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "description": self.description,
            "modifications": {
                "exclude_zones": self.modifications.exclude_zones,
                "priority_weights": self.modifications.priority_weights,
                "distance_thresholds": self.modifications.distance_thresholds,
                "traffic_conditions": self.modifications.traffic_conditions,
                "environmental_override": self.modifications.environmental_override,
            }
        }


# ── Validation ────────────────────────────────────────────────────────────────

class ScenarioValidationError(Exception):
    pass


def validate_scenario(scenario: ScenarioInput) -> None:
    """
    Validates a scenario input. Raises ScenarioValidationError on failure.
    This is called before any simulation run — bad input never reaches the engine.
    """
    if not scenario.scenario_id or not scenario.scenario_id.strip():
        raise ScenarioValidationError("scenario_id must not be empty.")

    weights = scenario.modifications.priority_weights
    if weights:
        total = round(sum(weights.values()), 6)
        if abs(total - 1.0) > 0.001:
            raise ScenarioValidationError(
                f"priority_weights must sum to 1.0. Got {total:.4f}. "
                f"Difference: {abs(total - 1.0):.4f}"
            )
        for key, val in weights.items():
            if val < 0:
                raise ScenarioValidationError(
                    f"Weight for '{key}' is negative ({val}). All weights must be >= 0."
                )

    for zone in scenario.modifications.exclude_zones:
        if zone not in VALID_CONSTRAINT_KEYS:
            raise ScenarioValidationError(
                f"Unknown exclude_zone: '{zone}'. "
                f"Valid options: {VALID_CONSTRAINT_KEYS}"
            )


def parse_scenario_from_dict(data: dict) -> ScenarioInput:
    """
    Parses a raw dict (from JSON request body) into a ScenarioInput object.
    """
    mods_raw = data.get("modifications", {})
    mods = ScenarioModifications(
        exclude_zones=mods_raw.get("exclude_zones", []),
        priority_weights=mods_raw.get("priority_weights", {}),
        distance_thresholds=mods_raw.get("distance_thresholds", {}),
        traffic_conditions=mods_raw.get("traffic_conditions", {}),
        environmental_override=mods_raw.get("environmental_override", False),
    )
    return ScenarioInput(
        scenario_id=data.get("scenario_id", "unnamed"),
        description=data.get("description", ""),
        modifications=mods,
    )
