"""
barrage_bridge_layer.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Layer 2 -- Barrage and Bridge Constraint Intelligence

Deterministic operational constraints for:
  - bridge air clearance vs vessel height
  - barrage navigational lock availability
  - vessel movement interruption logic
  - seaplane obstruction awareness
  - navigational clearance scoring

All results are deterministic -- same input, same output.
All outputs are proposal-only. No execution authority.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal


# Clearance thresholds (metres)
BRIDGE_SAFE_CLEARANCE_M       = 10.0
BRIDGE_MARGINAL_CLEARANCE_M   = 5.0
BRIDGE_CRITICAL_CLEARANCE_M   = 2.0

# Vessel class height profiles (metres above waterline)
VESSEL_CLASS_HEIGHTS = {
    "Class-I":   2.5,
    "Class-II":  3.5,
    "Class-III": 4.5,
    "Class-IV":  6.0,
    "Class-V":   8.0,
    "Seaplane":  4.0,
    "Barge":     3.0,
    "Tug":       4.5,
    "Ferry":     5.5
}

# Vessel draft profiles (metres below waterline)
VESSEL_CLASS_DRAFTS = {
    "Class-I":   0.5,
    "Class-II":  1.0,
    "Class-III": 1.5,
    "Class-IV":  2.0,
    "Class-V":   2.8,
    "Seaplane":  0.3,
    "Barge":     1.2,
    "Tug":       1.8,
    "Ferry":     1.6
}

# Barrage lock availability scores
LOCK_STATUS_SCORES = {
    "OPERATIONAL":      90.0,
    "SEASONAL":         55.0,
    "UNDER_REPAIR":     10.0,
    "DECOMMISSIONED":   0.0,
    "NONE":             0.0
}

# Known Ganga Basin barrages reference data
GANGA_BARRAGES = {
    "farakka_barrage": {
        "name": "Farakka Barrage",
        "geo_coordinates": [87.9186, 24.8119],
        "lock_status": "OPERATIONAL",
        "lock_width_m": 18.0,
        "lock_length_m": 91.5,
        "navigational_pass": True,
        "source_id": "IWAI_BARRAGE_v1"
    },
    "bansagar_barrage": {
        "name": "Bansagar Barrage",
        "geo_coordinates": [81.2833, 24.1833],
        "lock_status": "NONE",
        "lock_width_m": 0.0,
        "lock_length_m": 0.0,
        "navigational_pass": False,
        "source_id": "IWAI_BARRAGE_v1"
    },
    "tehri_dam": {
        "name": "Tehri Dam",
        "geo_coordinates": [78.4806, 30.3773],
        "lock_status": "NONE",
        "lock_width_m": 0.0,
        "lock_length_m": 0.0,
        "navigational_pass": False,
        "source_id": "IWAI_BARRAGE_v1"
    }
}

# Known Ganga Basin bridges reference data
GANGA_BRIDGES = {
    "mahatma_gandhi_setu": {
        "name": "Mahatma Gandhi Setu, Patna",
        "geo_coordinates": [85.1376, 25.5941],
        "air_clearance_m": 12.5,
        "span_width_m": 120.0,
        "source_id": "NHAI_BRIDGE_v1"
    },
    "ganga_bridge_varanasi": {
        "name": "Malviya Bridge, Varanasi",
        "geo_coordinates": [82.9739, 25.3176],
        "air_clearance_m": 8.5,
        "span_width_m": 80.0,
        "source_id": "NHAI_BRIDGE_v1"
    },
    "rajmahal_bridge": {
        "name": "Rajmahal Bridge",
        "geo_coordinates": [87.8299, 25.0445],
        "air_clearance_m": 6.2,
        "span_width_m": 60.0,
        "source_id": "NHAI_BRIDGE_v1"
    }
}


def assess_bridge_clearance(
    bridge_name: str,
    air_clearance_m: float,
    vessel_class: str,
    geo_coordinates: List[float],
    source_id: str = "BRIDGE_CONSTRAINT_v1"
) -> Dict[str, Any]:
    """
    Assesses whether a vessel class can safely pass under a bridge.

    Returns:
        {
            bridge_name: str
            vessel_class: str
            air_clearance_m: float
            vessel_height_m: float
            clearance_margin_m: float
            passage_safe: bool
            risk_level: SAFE / MARGINAL / CRITICAL / BLOCKED
            score: float 0-100
            seaplane_risk: bool
            proposal: str
            signal: dict (normalized marine schema signal)
        }
    """
    vessel_height = VESSEL_CLASS_HEIGHTS.get(vessel_class, 4.0)
    clearance = float(air_clearance_m)
    margin = round(clearance - vessel_height, 2)

    if margin >= BRIDGE_SAFE_CLEARANCE_M:
        risk_level = "SAFE"
        passage_safe = True
        score = 95.0
        proposal = (
            f"Bridge {bridge_name} safe for {vessel_class} passage. "
            f"Clearance margin {margin}m -- no restriction."
        )
    elif margin >= BRIDGE_MARGINAL_CLEARANCE_M:
        risk_level = "MARGINAL"
        passage_safe = True
        score = 60.0
        proposal = (
            f"Bridge {bridge_name} marginal for {vessel_class}. "
            f"Clearance margin {margin}m -- low tide passage recommended."
        )
    elif margin >= BRIDGE_CRITICAL_CLEARANCE_M:
        risk_level = "CRITICAL"
        passage_safe = False
        score = 20.0
        proposal = (
            f"Bridge {bridge_name} critical risk for {vessel_class}. "
            f"Clearance margin {margin}m -- passage not recommended."
        )
    elif margin >= 0:
        risk_level = "CRITICAL"
        passage_safe = False
        score = 10.0
        proposal = (
            f"Bridge {bridge_name} critical risk for {vessel_class}. "
            f"Clearance margin {margin}m -- passage not recommended."
        )
    else:
        risk_level = "BLOCKED"
        passage_safe = False
        score = 0.0
        proposal = (
            f"Bridge {bridge_name} BLOCKS {vessel_class}. "
            f"Vessel height {vessel_height}m exceeds clearance {clearance}m by {abs(margin)}m."
        )

    seaplane_risk = (
        vessel_class == "Seaplane" and risk_level in ("CRITICAL", "BLOCKED")
    )

    signal = build_signal(
        signal_type="bridge_clearance",
        value=round(margin, 2),
        geo_coordinates=geo_coordinates,
        source_id=source_id,
        confidence_initial=0.95
    )

    return {
        "bridge_name": bridge_name,
        "vessel_class": vessel_class,
        "air_clearance_m": clearance,
        "vessel_height_m": vessel_height,
        "clearance_margin_m": margin,
        "passage_safe": passage_safe,
        "risk_level": risk_level,
        "score": score,
        "seaplane_risk": seaplane_risk,
        "proposal": proposal,
        "signal": signal
    }


def assess_barrage_passage(
    barrage_id: str,
    vessel_class: str,
    geo_coordinates: List[float],
    lock_status: Optional[str] = None,
    lock_width_m: Optional[float] = None,
    lock_length_m: Optional[float] = None,
    source_id: str = "BARRAGE_CONSTRAINT_v1"
) -> Dict[str, Any]:
    """
    Assesses whether a vessel can pass through a barrage lock.

    Returns:
        {
            barrage_id: str
            vessel_class: str
            lock_status: str
            lock_compatible: bool
            score: float 0-100
            interruption_level: NONE / MINOR / MODERATE / SEVERE / TOTAL
            proposal: str
            signal: dict
        }
    """
    # Use reference data if available
    ref = GANGA_BARRAGES.get(barrage_id, {})
    status = lock_status or ref.get("lock_status", "NONE")
    width = lock_width_m or ref.get("lock_width_m", 0.0)
    length = lock_length_m or ref.get("lock_length_m", 0.0)
    navigational_pass = ref.get("navigational_pass", False)

    base_score = LOCK_STATUS_SCORES.get(status, 0.0)

    # Check vessel fit in lock
    lock_compatible = False
    if status in ("OPERATIONAL", "SEASONAL") and width > 0 and length > 0:
        # Approximate vessel dimensions from class
        vessel_width = VESSEL_CLASS_DRAFTS.get(vessel_class, 1.5) * 3.0
        lock_compatible = (width >= vessel_width * 2.0)

    if not navigational_pass and status == "NONE":
        interruption_level = "TOTAL"
        score = 0.0
        proposal = (
            f"Barrage {barrage_id} has no navigational lock -- "
            f"{vessel_class} passage completely blocked. "
            f"Vessel must be transported overland."
        )
    elif status == "DECOMMISSIONED":
        interruption_level = "TOTAL"
        score = 0.0
        proposal = (
            f"Barrage {barrage_id} lock decommissioned -- "
            f"navigation route interrupted."
        )
    elif status == "UNDER_REPAIR":
        interruption_level = "SEVERE"
        score = 10.0
        proposal = (
            f"Barrage {barrage_id} lock under repair -- "
            f"{vessel_class} passage suspended. Check repair schedule."
        )
    elif status == "SEASONAL":
        interruption_level = "MODERATE"
        score = 55.0
        proposal = (
            f"Barrage {barrage_id} lock seasonal -- "
            f"{vessel_class} passage feasible during operational season only."
        )
    elif lock_compatible:
        interruption_level = "NONE"
        score = base_score
        proposal = (
            f"Barrage {barrage_id} lock compatible with {vessel_class}. "
            f"Lock width {width}m, length {length}m -- passage feasible."
        )
    else:
        interruption_level = "MODERATE"
        score = 40.0
        proposal = (
            f"Barrage {barrage_id} lock dimensions may not suit {vessel_class}. "
            f"Verify lock width {width}m against vessel beam."
        )

    signal = build_signal(
        signal_type="barrage_interruption",
        value=score,
        geo_coordinates=geo_coordinates,
        source_id=source_id,
        confidence_initial=0.9
    )

    return {
        "barrage_id": barrage_id,
        "vessel_class": vessel_class,
        "lock_status": status,
        "lock_compatible": lock_compatible,
        "score": score,
        "interruption_level": interruption_level,
        "proposal": proposal,
        "signal": signal
    }


def score_corridor_constraints(
    corridor_id: str,
    bridges: List[Dict[str, Any]],
    barrages: List[Dict[str, Any]],
    vessel_class: str
) -> Dict[str, Any]:
    """
    Scores an entire river corridor for a given vessel class
    by evaluating all bridges and barrages along the route.

    bridges: list of dicts with bridge_name, air_clearance_m, geo_coordinates
    barrages: list of dicts with barrage_id, geo_coordinates

    Returns composite corridor constraint score and proposals.
    """
    bridge_results = []
    barrage_results = []

    for b in bridges:
        result = assess_bridge_clearance(
            bridge_name=b["bridge_name"],
            air_clearance_m=b["air_clearance_m"],
            geo_coordinates=b["geo_coordinates"],
            vessel_class=vessel_class
        )
        bridge_results.append(result)

    for bar in barrages:
        result = assess_barrage_passage(
            barrage_id=bar["barrage_id"],
            vessel_class=vessel_class,
            geo_coordinates=bar["geo_coordinates"]
        )
        barrage_results.append(result)

    all_scores = (
        [r["score"] for r in bridge_results] +
        [r["score"] for r in barrage_results]
    )

    if not all_scores:
        composite_score = 100.0
    else:
        composite_score = round(min(all_scores), 2)

    blocked = any(
        r["risk_level"] == "BLOCKED" for r in bridge_results
    ) or any(
        r["interruption_level"] == "TOTAL" for r in barrage_results
    )

    proposals = (
        [r["proposal"] for r in bridge_results] +
        [r["proposal"] for r in barrage_results]
    )

    return {
        "corridor_id": corridor_id,
        "vessel_class": vessel_class,
        "composite_constraint_score": composite_score,
        "corridor_passable": not blocked,
        "bridge_count": len(bridge_results),
        "barrage_count": len(barrage_results),
        "bridge_results": bridge_results,
        "barrage_results": barrage_results,
        "proposals": proposals
    }


# Self-test
if __name__ == "__main__":
    import json

    print("barrage_bridge_layer.py -- Self-Test")
    print("=" * 50)

    # Test 1: Bridge clearance for Class-III vessel
    result1 = assess_bridge_clearance(
        bridge_name="Malviya Bridge, Varanasi",
        air_clearance_m=8.5,
        vessel_class="Class-III",
        geo_coordinates=[82.9739, 25.3176]
    )
    print(f"Bridge: {result1['bridge_name']}")
    print(f"Vessel: {result1['vessel_class']} (height {result1['vessel_height_m']}m)")
    print(f"Clearance margin: {result1['clearance_margin_m']}m")
    print(f"Risk level: {result1['risk_level']}")
    print(f"Proposal: {result1['proposal']}")

    print()

    # Test 2: Barrage passage for Farakka
    result2 = assess_barrage_passage(
        barrage_id="farakka_barrage",
        vessel_class="Class-III",
        geo_coordinates=[87.9186, 24.8119]
    )
    print(f"Barrage: {result2['barrage_id']}")
    print(f"Lock status: {result2['lock_status']}")
    print(f"Interruption level: {result2['interruption_level']}")
    print(f"Proposal: {result2['proposal']}")

    print()

    # Test 3: Corridor scoring
    result3 = score_corridor_constraints(
        corridor_id="NW1_ALLAHABAD_PATNA",
        bridges=[
            {
                "bridge_name": "Malviya Bridge",
                "air_clearance_m": 8.5,
                "geo_coordinates": [82.9739, 25.3176]
            }
        ],
        barrages=[
            {
                "barrage_id": "farakka_barrage",
                "geo_coordinates": [87.9186, 24.8119]
            }
        ],
        vessel_class="Class-III"
    )
    print(f"Corridor: {result3['corridor_id']}")
    print(f"Vessel class: {result3['vessel_class']}")
    print(f"Composite constraint score: {result3['composite_constraint_score']}")
    print(f"Corridor passable: {result3['corridor_passable']}")