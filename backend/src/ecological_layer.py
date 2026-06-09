"""
ecological_layer.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Layer 4 -- Ecological Integrity Intelligence

Deterministic scoring for:
  - pollution hotspot classification
  - turbidity levels and navigation impact
  - ecological stress index
  - industrial proximity risk
  - Aviral Ganga (flow continuity) signal support
  - Nirmal Ganga (water cleanliness) signal support

All outputs are proposal-only. No execution authority.
All inputs must be normalized Marine Schema signals.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal


# Pollution thresholds (WQI -- Water Quality Index, 0-100)
WQI_EXCELLENT       = 90.0
WQI_GOOD            = 70.0
WQI_MODERATE        = 50.0
WQI_POOR            = 30.0
# Below 30 = VERY POOR / CRITICAL

# BOD thresholds (mg/L) -- Biochemical Oxygen Demand
BOD_ACCEPTABLE      = 3.0
BOD_MODERATE        = 6.0
BOD_HIGH            = 10.0

# DO thresholds (mg/L) -- Dissolved Oxygen
DO_EXCELLENT        = 8.0
DO_GOOD             = 6.0
DO_ACCEPTABLE       = 4.0
DO_CRITICAL         = 2.0

# Turbidity thresholds (NTU)
TURBIDITY_CLEAR         = 10.0
TURBIDITY_MODERATE      = 50.0
TURBIDITY_HIGH          = 150.0
TURBIDITY_CRITICAL      = 500.0

# Industrial proximity risk (km)
INDUSTRY_CRITICAL_KM    = 2.0
INDUSTRY_HIGH_KM        = 5.0
INDUSTRY_MODERATE_KM    = 10.0

# Ecological stress thresholds
STRESS_CRITICAL     = 80.0
STRESS_HIGH         = 60.0
STRESS_MODERATE     = 40.0


def classify_pollution(
    wqi: float,
    bod_mg_l: float,
    do_mg_l: float
) -> Dict[str, Any]:
    """
    Classifies water pollution level from WQI, BOD, and DO readings.

    Returns:
        {
            pollution_class: EXCELLENT / GOOD / MODERATE / POOR / CRITICAL
            wqi_score: float
            bod_score: float
            do_score: float
            composite_pollution_score: float 0-100
            aviral_signal: str -- flow continuity implication
            nirmal_signal: str -- water cleanliness implication
            navigation_impact: str
            reasoning: str
        }
    """
    wqi = float(wqi)
    bod = float(bod_mg_l)
    do = float(do_mg_l)

    # WQI score (0-100, higher = better)
    wqi_score = max(0.0, min(100.0, wqi))

    # BOD score (inverted -- lower BOD = higher score)
    if bod <= BOD_ACCEPTABLE:
        bod_score = 100.0
    elif bod <= BOD_MODERATE:
        bod_score = 70.0
    elif bod <= BOD_HIGH:
        bod_score = 40.0
    else:
        bod_score = 10.0

    # DO score (higher DO = higher score)
    if do >= DO_EXCELLENT:
        do_score = 100.0
    elif do >= DO_GOOD:
        do_score = 80.0
    elif do >= DO_ACCEPTABLE:
        do_score = 50.0
    elif do >= DO_CRITICAL:
        do_score = 20.0
    else:
        do_score = 0.0

    composite = round(
        wqi_score * 0.50 +
        bod_score * 0.25 +
        do_score * 0.25,
        2
    )

    if composite >= WQI_EXCELLENT:
        pollution_class = "EXCELLENT"
        nirmal_signal = "Nirmal Ganga -- water quality meets Class A standard"
        navigation_impact = "No navigation restriction from water quality"
    elif composite >= WQI_GOOD:
        pollution_class = "GOOD"
        nirmal_signal = "Nirmal Ganga -- water quality acceptable for most uses"
        navigation_impact = "Minor water quality concern -- monitoring recommended"
    elif composite >= WQI_MODERATE:
        pollution_class = "MODERATE"
        nirmal_signal = "Nirmal Ganga target not met -- improvement needed"
        navigation_impact = "Moderate water quality -- vessel hull protection advised"
    elif composite >= WQI_POOR:
        pollution_class = "POOR"
        nirmal_signal = "Nirmal Ganga target significantly unmet -- intervention required"
        navigation_impact = "Poor water quality -- corrosion risk to vessel infrastructure"
    else:
        pollution_class = "CRITICAL"
        nirmal_signal = "CRITICAL: Water quality fails all Nirmal Ganga standards"
        navigation_impact = "CRITICAL: Water unusable for port or vessel operations"

    aviral_signal = (
        "Aviral Ganga -- flow continuity supports natural self-purification"
        if pollution_class in ("EXCELLENT", "GOOD")
        else "Aviral Ganga -- flow continuity insufficient to offset pollution load"
    )

    reasoning = (
        f"Pollution class: {pollution_class} | "
        f"Composite score: {composite}/100 | "
        f"WQI: {wqi} | BOD: {bod} mg/L | DO: {do} mg/L"
    )

    return {
        "pollution_class": pollution_class,
        "wqi_score": wqi_score,
        "bod_score": bod_score,
        "do_score": do_score,
        "composite_pollution_score": composite,
        "aviral_signal": aviral_signal,
        "nirmal_signal": nirmal_signal,
        "navigation_impact": navigation_impact,
        "reasoning": reasoning
    }


def assess_turbidity(turbidity_ntu: float) -> Dict[str, Any]:
    """
    Assesses turbidity level and its impact on navigation and ecology.

    Returns:
        {
            turbidity_ntu: float
            turbidity_class: CLEAR / MODERATE / HIGH / CRITICAL
            score: float 0-100
            seaplane_impact: str
            dredging_indicator: bool
            reasoning: str
        }
    """
    t = float(turbidity_ntu)

    if t <= TURBIDITY_CLEAR:
        tclass = "CLEAR"
        score = 100.0
        seaplane_impact = "No turbidity restriction for seaplane operations"
        dredging = False
    elif t <= TURBIDITY_MODERATE:
        tclass = "MODERATE"
        score = 75.0
        seaplane_impact = "Moderate turbidity -- seaplane visibility acceptable"
        dredging = False
    elif t <= TURBIDITY_HIGH:
        tclass = "HIGH"
        score = 40.0
        seaplane_impact = "High turbidity -- seaplane landing restricted"
        dredging = True
    elif t <= TURBIDITY_CRITICAL:
        tclass = "CRITICAL"
        score = 15.0
        seaplane_impact = "Critical turbidity -- seaplane operations not feasible"
        dredging = True
    else:
        tclass = "CRITICAL"
        score = 5.0
        seaplane_impact = "Extreme turbidity -- all water-dependent operations suspended"
        dredging = True

    reasoning = (
        f"Turbidity {t} NTU -- class: {tclass} | "
        f"Score: {score}/100 | "
        f"Dredging indicator: {dredging}"
    )

    return {
        "turbidity_ntu": t,
        "turbidity_class": tclass,
        "score": score,
        "seaplane_impact": seaplane_impact,
        "dredging_indicator": dredging,
        "reasoning": reasoning
    }


def assess_industrial_proximity(
    nearest_industry_km: float,
    industry_type: str = "general"
) -> Dict[str, Any]:
    """
    Assesses ecological risk from nearby industrial activity.

    Returns:
        {
            nearest_industry_km: float
            industry_type: str
            risk_level: CRITICAL / HIGH / MODERATE / LOW
            score: float 0-100
            effluent_risk: bool
            proposal: str
        }
    """
    d = float(nearest_industry_km)

    if d <= INDUSTRY_CRITICAL_KM:
        risk_level = "CRITICAL"
        score = 5.0
        effluent_risk = True
        proposal = (
            f"Industrial zone {d}km away -- CRITICAL proximity risk. "
            f"Effluent discharge likely affecting water quality. "
            f"Site not suitable for port or tourism infrastructure without remediation."
        )
    elif d <= INDUSTRY_HIGH_KM:
        risk_level = "HIGH"
        score = 25.0
        effluent_risk = True
        proposal = (
            f"Industrial zone {d}km away -- HIGH proximity risk. "
            f"Effluent monitoring required. "
            f"Conditional suitability pending pollution audit."
        )
    elif d <= INDUSTRY_MODERATE_KM:
        risk_level = "MODERATE"
        score = 65.0
        effluent_risk = False
        proposal = (
            f"Industrial zone {d}km away -- MODERATE proximity. "
            f"Routine monitoring sufficient. "
            f"No immediate restriction on infrastructure development."
        )
    else:
        risk_level = "LOW"
        score = 95.0
        effluent_risk = False
        proposal = (
            f"No significant industrial activity within {d}km -- "
            f"LOW ecological risk from industrial proximity."
        )

    return {
        "nearest_industry_km": d,
        "industry_type": industry_type,
        "risk_level": risk_level,
        "score": score,
        "effluent_risk": effluent_risk,
        "proposal": proposal
    }


def compute_ecological_stress_index(
    pollution_score: float,
    turbidity_score: float,
    industrial_proximity_score: float,
    flow_disruption: bool = False
) -> Dict[str, Any]:
    """
    Computes composite ecological stress index for a location.

    Returns:
        {
            stress_index: float 0-100 (higher = more stressed)
            stress_level: CRITICAL / HIGH / MODERATE / LOW
            ecological_viability: bool
            score: float 0-100 (inverted -- higher = healthier)
            reasoning: str
        }
    """
    # Stress = inverse of health scores, weighted
    health_score = round(
        pollution_score * 0.45 +
        turbidity_score * 0.30 +
        industrial_proximity_score * 0.25,
        2
    )

    flow_penalty = 10.0 if flow_disruption else 0.0
    health_score = max(0.0, health_score - flow_penalty)
    stress_index = round(100.0 - health_score, 2)

    if stress_index >= STRESS_CRITICAL:
        stress_level = "CRITICAL"
        ecological_viability = False
    elif stress_index >= STRESS_HIGH:
        stress_level = "HIGH"
        ecological_viability = False
    elif stress_index >= STRESS_MODERATE:
        stress_level = "MODERATE"
        ecological_viability = True
    else:
        stress_level = "LOW"
        ecological_viability = True

    reasoning = (
        f"Ecological stress index: {stress_index}/100 | "
        f"Level: {stress_level} | "
        f"Health score: {health_score}/100 | "
        f"Flow disruption penalty: {flow_penalty}"
    )

    return {
        "stress_index": stress_index,
        "stress_level": stress_level,
        "ecological_viability": ecological_viability,
        "score": round(health_score, 2),
        "reasoning": reasoning
    }


def score_ecological_integrity(
    location_id: str,
    geo_coordinates: List[float],
    wqi: float,
    bod_mg_l: float,
    do_mg_l: float,
    turbidity_ntu: float,
    nearest_industry_km: float,
    industry_type: str = "general",
    flow_disruption: bool = False,
    source_id: str = "ECOLOGICAL_ENGINE_v1"
) -> Dict[str, Any]:
    """
    Master function -- full ecological integrity assessment for a location.

    Returns complete ecological score with proposals and normalized signals.
    """
    pollution_result = classify_pollution(wqi, bod_mg_l, do_mg_l)
    turbidity_result = assess_turbidity(turbidity_ntu)
    industrial_result = assess_industrial_proximity(
        nearest_industry_km, industry_type
    )
    stress_result = compute_ecological_stress_index(
        pollution_result["composite_pollution_score"],
        turbidity_result["score"],
        industrial_result["score"],
        flow_disruption
    )

    confidence = round(
        0.9 - (0.1 if flow_disruption else 0.0) -
        (0.1 if industrial_result["effluent_risk"] else 0.0),
        2
    )

    proposal = (
        f"Location {location_id} -- Ecological integrity: "
        f"{stress_result['stress_level']} stress | "
        f"Pollution: {pollution_result['pollution_class']} | "
        f"Turbidity: {turbidity_result['turbidity_class']} | "
        f"Industrial risk: {industrial_result['risk_level']} | "
        f"{pollution_result['nirmal_signal']}"
    )

    signals = [
        build_signal(
            signal_type="pollution",
            value=pollution_result["composite_pollution_score"],
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="turbidity",
            value=turbidity_ntu,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="ecological_stress",
            value=stress_result["stress_index"],
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        ),
        build_signal(
            signal_type="industrial_proximity",
            value=nearest_industry_km,
            geo_coordinates=geo_coordinates,
            source_id=source_id,
            confidence_initial=confidence
        )
    ]

    return {
        "location_id": location_id,
        "geo_coordinates": geo_coordinates,
        "pollution_assessment": pollution_result,
        "turbidity_assessment": turbidity_result,
        "industrial_assessment": industrial_result,
        "stress_assessment": stress_result,
        "composite_ecological_score": stress_result["score"],
        "ecological_viability": stress_result["ecological_viability"],
        "confidence": confidence,
        "proposal": proposal,
        "signals": signals
    }


# Self-test
if __name__ == "__main__":
    import json

    print("ecological_layer.py -- Self-Test")
    print("=" * 50)

    # Test 1: Clean location (Patna -- relatively good water quality)
    result1 = score_ecological_integrity(
        location_id="patna_river_port",
        geo_coordinates=[85.1376, 25.5941],
        wqi=65.0,
        bod_mg_l=2.5,
        do_mg_l=7.2,
        turbidity_ntu=35.0,
        nearest_industry_km=8.5,
        industry_type="light_manufacturing"
    )
    print(f"Location: {result1['location_id']}")
    print(f"Ecological score: {result1['composite_ecological_score']}")
    print(f"Stress level: {result1['stress_assessment']['stress_level']}")
    print(f"Ecological viability: {result1['ecological_viability']}")
    print(f"Nirmal signal: {result1['pollution_assessment']['nirmal_signal']}")
    print(f"Signals produced: {len(result1['signals'])}")

    print()

    # Test 2: Polluted location (Kanpur industrial zone)
    result2 = score_ecological_integrity(
        location_id="kanpur_industrial_zone",
        geo_coordinates=[80.3319, 26.4499],
        wqi=18.0,
        bod_mg_l=15.0,
        do_mg_l=1.5,
        turbidity_ntu=320.0,
        nearest_industry_km=0.8,
        industry_type="leather_tannery",
        flow_disruption=True
    )
    print(f"Location: {result2['location_id']}")
    print(f"Ecological score: {result2['composite_ecological_score']}")
    print(f"Stress level: {result2['stress_assessment']['stress_level']}")
    print(f"Pollution class: {result2['pollution_assessment']['pollution_class']}")
    print(f"Proposal: {result2['proposal']}")