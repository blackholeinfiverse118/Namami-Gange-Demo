"""
navigability_layer.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Layer 3 -- NW5 + Navigability Intelligence

Deterministic scoring for:
  - depth thresholds vs vessel draft
  - vessel class compatibility
  - segment navigability scoring
  - seasonal closure probability
  - navigability confidence index

Covers NW1 (Ganga) and NW5 (Brahmani-Baitarani).
All outputs are proposal-only. No execution authority.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal


# Depth thresholds (metres)
DEPTH_DEEP_WATER        = 5.0
DEPTH_NAVIGABLE         = 3.0
DEPTH_SHALLOW           = 1.5
DEPTH_CRITICAL          = 0.8

# Seasonal closure probability thresholds
SEASONAL_HIGH_CLOSURE   = 0.70
SEASONAL_MODERATE_CLOSURE = 0.40
SEASONAL_LOW_CLOSURE    = 0.15

# Navigability confidence weights
WEIGHT_DEPTH            = 0.45
WEIGHT_SEASONAL         = 0.30
WEIGHT_INFRASTRUCTURE   = 0.25

# National Waterway reference data
NATIONAL_WATERWAYS = {
    "NW1": {
        "name": "National Waterway 1 -- Ganga-Bhagirathi-Hooghly",
        "length_km": 1620,
        "stretch": "Allahabad to Haldia",
        "min_depth_target_m": 3.0,
        "states": ["UP", "Bihar", "Jharkhand", "West Bengal"]
    },
    "NW5": {
        "name": "National Waterway 5 -- Brahmani-Baitarani",
        "length_km": 588,
        "stretch": "Dhamra to Talcher",
        "min_depth_target_m": 2.0,
        "states": ["Odisha"]
    }
}

# Vessel draft compatibility table
# Minimum required depth = draft + 0.5m underkeel clearance
VESSEL_DRAFT_CLEARANCE = {
    "Class-I":   1.0,   # draft 0.5 + 0.5 clearance
    "Class-II":  1.5,   # draft 1.0 + 0.5
    "Class-III": 2.0,   # draft 1.5 + 0.5
    "Class-IV":  2.5,   # draft 2.0 + 0.5
    "Class-V":   3.3,   # draft 2.8 + 0.5
    "Seaplane":  0.8,   # draft 0.3 + 0.5
    "Barge":     1.7,   # draft 1.2 + 0.5
    "Tug":       2.3,   # draft 1.8 + 0.5
    "Ferry":     2.1    # draft 1.6 + 0.5
}

# Month-wise seasonal navigability index for NW1
# 1.0 = fully navigable, 0.0 = closed
NW1_SEASONAL_INDEX = {
    1: 0.85,   # January
    2: 0.80,   # February
    3: 0.75,   # March
    4: 0.65,   # April
    5: 0.55,   # May
    6: 0.40,   # June -- monsoon onset
    7: 0.30,   # July -- peak monsoon
    8: 0.35,   # August
    9: 0.50,   # September
    10: 0.75,  # October
    11: 0.90,  # November
    12: 0.90   # December
}

# Month-wise seasonal index for NW5
NW5_SEASONAL_INDEX = {
    1: 0.80,
    2: 0.75,
    3: 0.65,
    4: 0.55,
    5: 0.45,
    6: 0.35,
    7: 0.25,
    8: 0.30,
    9: 0.55,
    10: 0.80,
    11: 0.85,
    12: 0.85
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def assess_depth_compatibility(
    depth_m: float,
    vessel_class: str
) -> Dict[str, Any]:
    """
    Assesses whether a given water depth is compatible with a vessel class.

    Returns:
        {
            depth_m: float
            vessel_class: str
            required_depth_m: float
            depth_margin_m: float
            compatible: bool
            depth_category: DEEP / NAVIGABLE / SHALLOW / CRITICAL
            score: float 0-100
            reasoning: str
        }
    """
    depth = float(depth_m)
    required = VESSEL_DRAFT_CLEARANCE.get(vessel_class, 2.0)
    margin = round(depth - required, 2)

    if depth >= DEPTH_DEEP_WATER:
        category = "DEEP"
        score = 100.0
    elif depth >= DEPTH_NAVIGABLE:
        category = "NAVIGABLE"
        score = 80.0
    elif depth >= DEPTH_SHALLOW:
        category = "SHALLOW"
        score = 45.0
    elif depth >= DEPTH_CRITICAL:
        category = "CRITICAL"
        score = 15.0
    else:
        category = "CRITICAL"
        score = 0.0

    compatible = margin >= 0

    if not compatible:
        score = 0.0
        reasoning = (
            f"Depth {depth}m insufficient for {vessel_class} "
            f"(requires {required}m). Deficit {abs(margin)}m."
        )
    else:
        reasoning = (
            f"Depth {depth}m compatible with {vessel_class} "
            f"(requires {required}m). Margin {margin}m."
        )

    return {
        "depth_m": depth,
        "vessel_class": vessel_class,
        "required_depth_m": required,
        "depth_margin_m": margin,
        "compatible": compatible,
        "depth_category": category,
        "score": score,
        "reasoning": reasoning
    }


def get_seasonal_closure_probability(
    waterway_id: str,
    month: int
) -> Dict[str, Any]:
    """
    Returns seasonal closure probability for a waterway in a given month.

    Returns:
        {
            waterway_id: str
            month: int
            month_name: str
            navigability_index: float
            closure_probability: float
            risk_level: HIGH / MODERATE / LOW
            operational: bool
            reasoning: str
        }
    """
    ww = waterway_id.upper()
    if ww == "NW1":
        index = NW1_SEASONAL_INDEX.get(month, 0.5)
    elif ww == "NW5":
        index = NW5_SEASONAL_INDEX.get(month, 0.5)
    else:
        index = 0.6  # default for unknown waterways

    closure_prob = round(1.0 - index, 2)
    month_name = MONTH_NAMES.get(month, "Unknown")

    if closure_prob >= SEASONAL_HIGH_CLOSURE:
        risk_level = "HIGH"
        operational = False
        reasoning = (
            f"{ww} in {month_name}: navigability index {index} -- "
            f"high closure probability ({closure_prob}). Operations not recommended."
        )
    elif closure_prob >= SEASONAL_MODERATE_CLOSURE:
        risk_level = "MODERATE"
        operational = True
        reasoning = (
            f"{ww} in {month_name}: navigability index {index} -- "
            f"moderate closure risk ({closure_prob}). Conditional operations feasible."
        )
    else:
        risk_level = "LOW"
        operational = True
        reasoning = (
            f"{ww} in {month_name}: navigability index {index} -- "
            f"low closure risk ({closure_prob}). Normal operations expected."
        )

    return {
        "waterway_id": ww,
        "month": month,
        "month_name": month_name,
        "navigability_index": index,
        "closure_probability": closure_prob,
        "risk_level": risk_level,
        "operational": operational,
        "reasoning": reasoning
    }


def score_segment_navigability(
    segment_id: str,
    waterway_id: str,
    geo_coordinates: List[float],
    depth_m: float,
    vessel_class: str,
    month: int,
    infrastructure_score: float = 70.0,
    source_id: str = "NAVIGABILITY_ENGINE_v1"
) -> Dict[str, Any]:
    """
    Master function -- scores a waterway segment for navigability.
    Combines depth, seasonal, and infrastructure dimensions.

    Returns full navigability assessment with proposal.
    """
    depth_result = assess_depth_compatibility(depth_m, vessel_class)
    seasonal_result = get_seasonal_closure_probability(waterway_id, month)

    # Composite navigability score
    infra_score = max(0.0, min(100.0, float(infrastructure_score)))
    raw_score = (
        depth_result["score"] * WEIGHT_DEPTH +
        seasonal_result["navigability_index"] * 100.0 * WEIGHT_SEASONAL +
        infra_score * WEIGHT_INFRASTRUCTURE
    )
    composite_score = round(max(0.0, min(100.0, raw_score)), 2)

    # Navigability confidence
    confidence = round(
        (depth_result["score"] / 100.0) * 0.5 +
        seasonal_result["navigability_index"] * 0.5,
        2
    )

    # Overall viability
    viable = (
        depth_result["compatible"] and
        seasonal_result["operational"] and
        composite_score >= 30.0
    )

    # Build proposal
    ww_info = NATIONAL_WATERWAYS.get(waterway_id.upper(), {})
    ww_name = ww_info.get("name", waterway_id)

    if viable:
        proposal = (
            f"Segment {segment_id} on {ww_name}: "
            f"{vessel_class} navigation FEASIBLE in {seasonal_result['month_name']}. "
            f"Depth {depth_m}m meets requirement. "
            f"Navigability score: {composite_score}/100. "
            f"Confidence: {confidence}."
        )
    else:
        blockers = []
        if not depth_result["compatible"]:
            blockers.append(
                f"insufficient depth ({depth_m}m vs {depth_result['required_depth_m']}m required)"
            )
        if not seasonal_result["operational"]:
            blockers.append(
                f"seasonal closure risk HIGH in {seasonal_result['month_name']}"
            )
        if composite_score < 30.0:
            blockers.append(f"low composite score ({composite_score})")
        proposal = (
            f"Segment {segment_id} on {ww_name}: "
            f"{vessel_class} navigation NOT FEASIBLE in {seasonal_result['month_name']}. "
            f"Blockers: {'; '.join(blockers)}."
        )

    # Normalized signals
    signals = [
        build_signal(
            signal_type="depth",
            value=depth_m,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="navigability_confidence",
            value=confidence,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="segment_score",
            value=composite_score,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        )
    ]

    return {
        "segment_id": segment_id,
        "waterway_id": waterway_id.upper(),
        "geo_coordinates": geo_coordinates,
        "vessel_class": vessel_class,
        "month": month,
        "month_name": seasonal_result["month_name"],
        "depth_assessment": depth_result,
        "seasonal_assessment": seasonal_result,
        "composite_navigability_score": composite_score,
        "navigability_confidence": confidence,
        "navigation_viable": viable,
        "proposal": proposal,
        "signals": signals
    }


def best_months_for_segment(
    segment_id: str,
    waterway_id: str,
    geo_coordinates: List[float],
    depth_m: float,
    vessel_class: str,
    infrastructure_score: float = 70.0
) -> Dict[str, Any]:
    """
    Finds the best months for navigating a segment with a given vessel class.
    Returns ranked list of months by navigability score.
    """
    monthly_scores = []
    for month in range(1, 13):
        result = score_segment_navigability(
            segment_id=segment_id,
            waterway_id=waterway_id,
            geo_coordinates=geo_coordinates,
            depth_m=depth_m,
            vessel_class=vessel_class,
            month=month,
            infrastructure_score=infrastructure_score
        )
        monthly_scores.append({
            "month": month,
            "month_name": MONTH_NAMES[month],
            "score": result["composite_navigability_score"],
            "viable": result["navigation_viable"]
        })

    ranked = sorted(monthly_scores, key=lambda x: x["score"], reverse=True)
    best_months = [m for m in ranked if m["viable"]]

    return {
        "segment_id": segment_id,
        "vessel_class": vessel_class,
        "best_months": best_months[:6],
        "all_months_ranked": ranked,
        "viable_month_count": len(best_months)
    }


# Self-test
if __name__ == "__main__":
    import json

    print("navigability_layer.py -- Self-Test")
    print("=" * 50)

    # Test 1: Depth compatibility
    r1 = assess_depth_compatibility(3.5, "Class-III")
    print(f"Depth 3.5m for Class-III: compatible={r1['compatible']} "
          f"score={r1['score']} category={r1['depth_category']}")

    r2 = assess_depth_compatibility(1.2, "Class-IV")
    print(f"Depth 1.2m for Class-IV: compatible={r2['compatible']} "
          f"score={r2['score']}")

    print()

    # Test 2: Seasonal closure
    r3 = get_seasonal_closure_probability("NW1", 7)
    print(f"NW1 July: operational={r3['operational']} "
          f"risk={r3['risk_level']} closure_prob={r3['closure_probability']}")

    r4 = get_seasonal_closure_probability("NW1", 11)
    print(f"NW1 November: operational={r4['operational']} "
          f"risk={r4['risk_level']} closure_prob={r4['closure_probability']}")

    print()

    # Test 3: Full segment navigability
    r5 = score_segment_navigability(
        segment_id="NW1_PATNA_SEG_001",
        waterway_id="NW1",
        geo_coordinates=[85.1376, 25.5941],
        depth_m=4.2,
        vessel_class="Class-III",
        month=11
    )
    print(f"Segment: {r5['segment_id']}")
    print(f"Score: {r5['composite_navigability_score']}")
    print(f"Viable: {r5['navigation_viable']}")
    print(f"Proposal: {r5['proposal']}")

    print()

    # Test 4: Best months
    r6 = best_months_for_segment(
        segment_id="NW1_VARANASI_SEG_001",
        waterway_id="NW1",
        geo_coordinates=[82.9739, 25.3176],
        depth_m=3.2,
        vessel_class="Class-III"
    )
    print(f"Best months for Class-III at Varanasi:")
    for m in r6["best_months"][:3]:
        print(f"  {m['month_name']}: score={m['score']}")
    print(f"Total viable months: {r6['viable_month_count']}")