"""
river_flow_layer.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Layer 1 -- River Flow Intelligence

Deterministic scoring for:
  - discharge levels (low / normal / high / flood)
  - seasonal variation risk
  - sediment load indicators
  - flow disruption detection
  - barrage influence scoring
  - river continuity signals

All inputs must be normalized Marine Schema signals.
All outputs are deterministic -- same input, same output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal, normalize_signal, VALID_SIGNAL_TYPES


# Thresholds -- all deterministic constants
# Discharge thresholds (cumecs)
DISCHARGE_FLOOD_THRESHOLD    = 50000.0
DISCHARGE_HIGH_THRESHOLD     = 20000.0
DISCHARGE_NORMAL_THRESHOLD   = 5000.0
DISCHARGE_LOW_THRESHOLD      = 500.0

# Sediment thresholds (mg/L)
SEDIMENT_CRITICAL_THRESHOLD  = 5000.0
SEDIMENT_HIGH_THRESHOLD      = 2000.0
SEDIMENT_MODERATE_THRESHOLD  = 500.0

# Seasonal variation risk (monsoon/lean ratio)
SEASONAL_CV_HIGH_RISK        = 50.0
SEASONAL_CV_MODERATE_RISK    = 20.0

# Flow disruption score penalty
FLOW_DISRUPTION_PENALTY      = 25.0

# Barrage influence score reduction
BARRAGE_INFLUENCE_REDUCTION  = 20.0

# Navigation safety thresholds
NAVIGATION_SAFE_DISCHARGE_MIN  = 500.0
NAVIGATION_SAFE_DISCHARGE_MAX  = 20000.0


# Discharge classification
def classify_discharge(discharge_cumecs: float) -> Dict[str, Any]:
    """
    Classifies discharge level and returns navigation safety assessment.

    Returns:
        {
            level: FLOOD / HIGH / NORMAL / LOW / CRITICAL_LOW
            navigation_safe: bool
            score: float 0-100
            reasoning: str
        }
    """
    d = float(discharge_cumecs)

    if d >= DISCHARGE_FLOOD_THRESHOLD:
        return {
            "level": "FLOOD",
            "navigation_safe": False,
            "score": 0.0,
            "reasoning": (
                f"Discharge {d} cumecs exceeds flood threshold "
                f"{DISCHARGE_FLOOD_THRESHOLD} -- navigation unsafe"
            )
        }
    elif d >= DISCHARGE_HIGH_THRESHOLD:
        return {
            "level": "HIGH",
            "navigation_safe": False,
            "score": 30.0,
            "reasoning": (
                f"Discharge {d} cumecs above high threshold "
                f"{DISCHARGE_HIGH_THRESHOLD} -- navigation restricted"
            )
        }
    elif d >= DISCHARGE_NORMAL_THRESHOLD:
        return {
            "level": "NORMAL",
            "navigation_safe": True,
            "score": 85.0,
            "reasoning": (
                f"Discharge {d} cumecs within normal range -- navigation suitable"
            )
        }
    elif d >= DISCHARGE_LOW_THRESHOLD:
        return {
            "level": "LOW",
            "navigation_safe": True,
            "score": 60.0,
            "reasoning": (
                f"Discharge {d} cumecs in low range -- shallow draft vessels only"
            )
        }
    else:
        return {
            "level": "CRITICAL_LOW",
            "navigation_safe": False,
            "score": 10.0,
            "reasoning": (
                f"Discharge {d} cumecs critically low -- navigation not viable"
            )
        }


def classify_sediment(sediment_mg_l: float) -> Dict[str, Any]:
    """
    Classifies sediment load and returns infrastructure risk.

    Returns:
        {
            level: CRITICAL / HIGH / MODERATE / LOW
            dredging_required: bool
            score: float 0-100
            reasoning: str
        }
    """
    s = float(sediment_mg_l)

    if s >= SEDIMENT_CRITICAL_THRESHOLD:
        return {
            "level": "CRITICAL",
            "dredging_required": True,
            "score": 5.0,
            "reasoning": (
                f"Sediment {s} mg/L exceeds critical threshold "
                f"{SEDIMENT_CRITICAL_THRESHOLD} -- dredging essential"
            )
        }
    elif s >= SEDIMENT_HIGH_THRESHOLD:
        return {
            "level": "HIGH",
            "dredging_required": True,
            "score": 30.0,
            "reasoning": (
                f"Sediment {s} mg/L high -- dredging required for port operations"
            )
        }
    elif s >= SEDIMENT_MODERATE_THRESHOLD:
        return {
            "level": "MODERATE",
            "dredging_required": False,
            "score": 65.0,
            "reasoning": (
                f"Sediment {s} mg/L moderate -- monitoring recommended"
            )
        }
    else:
        return {
            "level": "LOW",
            "dredging_required": False,
            "score": 95.0,
            "reasoning": (
                f"Sediment {s} mg/L low -- suitable for port and terminal operations"
            )
        }


def assess_seasonal_variation(
    monsoon_discharge: float,
    lean_discharge: float
) -> Dict[str, Any]:
    """
    Assesses seasonal variation risk using monsoon/lean discharge ratio.
    High ratio = high seasonal variability = operational risk.

    Returns:
        {
            cv_proxy: float
            risk_level: HIGH / MODERATE / LOW
            score: float 0-100
            operational_months: list of safe month descriptions
            reasoning: str
        }
    """
    lean = max(float(lean_discharge), 1.0)
    cv = round(float(monsoon_discharge) / lean, 2)

    if cv >= SEASONAL_CV_HIGH_RISK:
        return {
            "cv_proxy": cv,
            "risk_level": "HIGH",
            "score": 20.0,
            "operational_months": ["November", "December", "January", "February", "March"],
            "reasoning": (
                f"Monsoon/lean ratio {cv} indicates extreme seasonal variation -- "
                f"operations restricted to lean season (Nov-Mar)"
            )
        }
    elif cv >= SEASONAL_CV_MODERATE_RISK:
        return {
            "cv_proxy": cv,
            "risk_level": "MODERATE",
            "score": 55.0,
            "operational_months": [
                "October", "November", "December",
                "January", "February", "March", "April"
            ],
            "reasoning": (
                f"Monsoon/lean ratio {cv} indicates moderate seasonal variation -- "
                f"operations feasible Oct-Apr with monitoring"
            )
        }
    else:
        return {
            "cv_proxy": cv,
            "risk_level": "LOW",
            "score": 90.0,
            "operational_months": [
                "January", "February", "March", "April", "May",
                "September", "October", "November", "December"
            ],
            "reasoning": (
                f"Monsoon/lean ratio {cv} indicates stable flow -- "
                f"year-round operations feasible outside peak monsoon"
            )
        }


def assess_barrage_influence(
    upstream_discharge: float,
    downstream_discharge: float,
    barrage_name: str = "Unknown Barrage"
) -> Dict[str, Any]:
    """
    Assesses how a barrage affects navigability by comparing
    upstream vs downstream discharge.

    Returns:
        {
            influence_level: SEVERE / MODERATE / MINOR / NONE
            flow_reduction_pct: float
            navigation_impact: str
            score: float 0-100
            reasoning: str
        }
    """
    upstream = max(float(upstream_discharge), 1.0)
    downstream = float(downstream_discharge)
    reduction_pct = round(max(0.0, (upstream - downstream) / upstream * 100), 2)

    if reduction_pct >= 60.0:
        return {
            "influence_level": "SEVERE",
            "flow_reduction_pct": reduction_pct,
            "navigation_impact": "BLOCKED",
            "score": 5.0,
            "reasoning": (
                f"{barrage_name} reduces flow by {reduction_pct}% -- "
                f"navigation severely impacted, vessel passage likely blocked"
            )
        }
    elif reduction_pct >= 30.0:
        return {
            "influence_level": "MODERATE",
            "flow_reduction_pct": reduction_pct,
            "navigation_impact": "RESTRICTED",
            "score": 40.0,
            "reasoning": (
                f"{barrage_name} reduces flow by {reduction_pct}% -- "
                f"navigation restricted, shallow draft vessels only"
            )
        }
    elif reduction_pct >= 10.0:
        return {
            "influence_level": "MINOR",
            "flow_reduction_pct": reduction_pct,
            "navigation_impact": "MINOR_RESTRICTION",
            "score": 75.0,
            "reasoning": (
                f"{barrage_name} reduces flow by {reduction_pct}% -- "
                f"minor navigation impact, monitoring recommended"
            )
        }
    else:
        return {
            "influence_level": "NONE",
            "flow_reduction_pct": reduction_pct,
            "navigation_impact": "UNAFFECTED",
            "score": 95.0,
            "reasoning": (
                f"{barrage_name} has negligible flow reduction ({reduction_pct}%) -- "
                f"navigation unaffected"
            )
        }


def score_river_segment(
    segment_id: str,
    geo_coordinates: List[float],
    discharge_cumecs: float,
    sediment_mg_l: float,
    monsoon_discharge: float,
    lean_discharge: float,
    has_flow_disruption: bool = False,
    barrage_upstream: bool = False,
    barrage_upstream_discharge: Optional[float] = None,
    source_id: str = "RIVER_FLOW_ENGINE_v1"
) -> Dict[str, Any]:
    """
    Master function -- scores a river segment across all flow intelligence
    dimensions and returns a unified result.

    Returns:
        {
            segment_id: str
            geo_coordinates: list
            discharge_assessment: dict
            sediment_assessment: dict
            seasonal_assessment: dict
            barrage_assessment: dict or None
            composite_flow_score: float 0-100
            navigation_viable: bool
            confidence: float
            reasoning: str
            signals: list of normalized marine schema signals
        }
    """
    discharge_result = classify_discharge(discharge_cumecs)
    sediment_result = classify_sediment(sediment_mg_l)
    seasonal_result = assess_seasonal_variation(monsoon_discharge, lean_discharge)

    barrage_result = None
    barrage_penalty = 0.0
    if barrage_upstream and barrage_upstream_discharge is not None:
        barrage_result = assess_barrage_influence(
            barrage_upstream_discharge, discharge_cumecs
        )
        if barrage_result["influence_level"] in ("SEVERE", "MODERATE"):
            barrage_penalty = BARRAGE_INFLUENCE_REDUCTION

    disruption_penalty = FLOW_DISRUPTION_PENALTY if has_flow_disruption else 0.0

    # Composite score: weighted average minus penalties
    raw_score = (
        discharge_result["score"] * 0.40 +
        sediment_result["score"] * 0.25 +
        seasonal_result["score"] * 0.35
    )
    composite_score = round(
        max(0.0, min(100.0, raw_score - barrage_penalty - disruption_penalty)),
        2
    )

    navigation_viable = (
        discharge_result["navigation_safe"] and
        composite_score >= 30.0 and
        not (barrage_result and barrage_result["navigation_impact"] == "BLOCKED")
    )

    confidence = round(
        1.0 - (0.1 * (1 if has_flow_disruption else 0)) -
        (0.15 if barrage_upstream else 0.0),
        2
    )

    reasoning = (
        f"Segment {segment_id} | Flow score: {composite_score}/100 | "
        f"Discharge: {discharge_result['level']} | "
        f"Sediment: {sediment_result['level']} | "
        f"Seasonal risk: {seasonal_result['risk_level']} | "
        f"Navigation viable: {navigation_viable}"
    )

    # Build normalized signals for the truth store
    signals = [
        build_signal(
            signal_type="discharge",
            value=discharge_cumecs,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="sediment",
            value=sediment_mg_l,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="river_flow",
            value=composite_score,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        )
    ]

    return {
        "segment_id": segment_id,
        "geo_coordinates": geo_coordinates,
        "discharge_assessment": discharge_result,
        "sediment_assessment": sediment_result,
        "seasonal_assessment": seasonal_result,
        "barrage_assessment": barrage_result,
        "composite_flow_score": composite_score,
        "navigation_viable": navigation_viable,
        "confidence": confidence,
        "reasoning": reasoning,
        "signals": signals
    }


# Self-test
if __name__ == "__main__":
    import json

    print("river_flow_layer.py -- Self-Test")
    print("=" * 50)

    # Test 1: Normal navigable segment
    result1 = score_river_segment(
        segment_id="NW1_VARANASI_001",
        geo_coordinates=[82.9739, 25.3176],
        discharge_cumecs=8000.0,
        sediment_mg_l=400.0,
        monsoon_discharge=45000.0,
        lean_discharge=2500.0
    )
    print(f"Segment: {result1['segment_id']}")
    print(f"Composite flow score: {result1['composite_flow_score']}")
    print(f"Navigation viable: {result1['navigation_viable']}")
    print(f"Reasoning: {result1['reasoning']}")

    print()

    # Test 2: Segment with barrage influence
    result2 = score_river_segment(
        segment_id="NW1_FARAKKA_001",
        geo_coordinates=[87.9186, 24.8119],
        discharge_cumecs=3000.0,
        sediment_mg_l=2500.0,
        monsoon_discharge=60000.0,
        lean_discharge=800.0,
        barrage_upstream=True,
        barrage_upstream_discharge=10000.0
    )
    print(f"Segment: {result2['segment_id']}")
    print(f"Composite flow score: {result2['composite_flow_score']}")
    print(f"Navigation viable: {result2['navigation_viable']}")
    print(f"Barrage influence: {result2['barrage_assessment']['influence_level']}")
    print(f"Signals produced: {len(result2['signals'])}")