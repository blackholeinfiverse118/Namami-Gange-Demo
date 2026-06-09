"""
proposal_engine.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Actionable Proposal Engine

Generates deterministic, confidence-tagged, trace-backed,
explainable proposals from all intelligence layers.

Rules (mandatory):
  - Proposal only. Never execution.
  - Every proposal is confidence tagged (0.0 to 1.0)
  - Every proposal is trace backed (source signals listed)
  - Every proposal is explainable (reasoning included)
  - Every proposal is provenance anchored (source_ids listed)
  - No ML. No probabilistic inference. Pure deterministic rules.

Proposal types:
  - NAVIGABILITY: vessel/segment/month suitability
  - CONSTRAINT: bridge/barrage/clearance risk
  - ECOLOGICAL: pollution/stress/turbidity alerts
  - INFRASTRUCTURE: port/terminal/CEZ/MMLP readiness
  - CONNECTIVITY: last-mile/tourism/cargo movement
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any, Dict, List, Optional
from marine_schema import build_signal


# Proposal types
PROPOSAL_TYPE_NAVIGABILITY    = "NAVIGABILITY"
PROPOSAL_TYPE_CONSTRAINT      = "CONSTRAINT"
PROPOSAL_TYPE_ECOLOGICAL      = "ECOLOGICAL"
PROPOSAL_TYPE_INFRASTRUCTURE  = "INFRASTRUCTURE"
PROPOSAL_TYPE_CONNECTIVITY    = "CONNECTIVITY"

VALID_PROPOSAL_TYPES = {
    PROPOSAL_TYPE_NAVIGABILITY,
    PROPOSAL_TYPE_CONSTRAINT,
    PROPOSAL_TYPE_ECOLOGICAL,
    PROPOSAL_TYPE_INFRASTRUCTURE,
    PROPOSAL_TYPE_CONNECTIVITY
}

# Confidence level labels
CONFIDENCE_HIGH     = "HIGH"       # 0.80 - 1.00
CONFIDENCE_MEDIUM   = "MEDIUM"     # 0.55 - 0.79
CONFIDENCE_LOW      = "LOW"        # 0.30 - 0.54
CONFIDENCE_UNCERTAIN = "UNCERTAIN" # 0.00 - 0.29

# Priority levels
PRIORITY_CRITICAL   = "CRITICAL"
PRIORITY_HIGH       = "HIGH"
PRIORITY_MEDIUM     = "MEDIUM"
PRIORITY_LOW        = "LOW"
PRIORITY_INFO       = "INFO"


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.80:
        return CONFIDENCE_HIGH
    elif confidence >= 0.55:
        return CONFIDENCE_MEDIUM
    elif confidence >= 0.30:
        return CONFIDENCE_LOW
    else:
        return CONFIDENCE_UNCERTAIN


def _score_to_priority(score: float) -> str:
    if score >= 75.0:
        return PRIORITY_HIGH
    elif score >= 50.0:
        return PRIORITY_MEDIUM
    elif score >= 25.0:
        return PRIORITY_LOW
    else:
        return PRIORITY_CRITICAL


def build_proposal(
    proposal_type: str,
    subject: str,
    proposal_text: str,
    confidence: float,
    score: float,
    source_ids: List[str],
    contributing_signals: List[str],
    reasoning: str,
    geo_coordinates: List[float],
    priority: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Core proposal builder. All proposals pass through here.

    Returns a fully structured proposal dict:
    {
        proposal_type: str
        subject: str
        proposal_text: str
        confidence: float
        confidence_label: str
        score: float
        priority: str
        source_ids: list
        contributing_signals: list
        reasoning: str
        geo_coordinates: list
        conditions: list
        provenance: dict
        metadata: dict
    }
    """
    if proposal_type not in VALID_PROPOSAL_TYPES:
        proposal_type = PROPOSAL_TYPE_INFO = "INFO"

    conf = max(0.0, min(1.0, float(confidence)))
    sc = max(0.0, min(100.0, float(score)))

    return {
        "proposal_type": proposal_type,
        "subject": subject,
        "proposal_text": proposal_text,
        "confidence": round(conf, 2),
        "confidence_label": _confidence_label(conf),
        "score": round(sc, 2),
        "priority": priority or _score_to_priority(sc),
        "source_ids": source_ids,
        "contributing_signals": contributing_signals,
        "reasoning": reasoning,
        "geo_coordinates": geo_coordinates,
        "conditions": conditions or [],
        "provenance": {
            "source_count": len(source_ids),
            "signal_count": len(contributing_signals),
            "deterministic": True,
            "ml_used": False
        },
        "metadata": metadata or {}
    }


def propose_navigability(
    segment_id: str,
    waterway_id: str,
    vessel_class: str,
    month_name: str,
    composite_score: float,
    depth_m: float,
    confidence: float,
    geo_coordinates: List[float],
    seasonal_risk: str,
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a navigability proposal for a segment/vessel/month combination.

    Example output:
    "Segment NW1_PATNA_001 suitable for Class-III vessel during November."
    """
    viable = composite_score >= 30.0

    if viable:
        text = (
            f"Segment {segment_id} on {waterway_id} suitable for "
            f"{vessel_class} vessel during {month_name}. "
            f"Depth {depth_m}m meets draft requirement. "
            f"Seasonal risk: {seasonal_risk}. "
            f"Navigability score: {composite_score}/100."
        )
    else:
        text = (
            f"Segment {segment_id} on {waterway_id} NOT suitable for "
            f"{vessel_class} vessel during {month_name}. "
            f"Depth {depth_m}m or seasonal conditions insufficient. "
            f"Score: {composite_score}/100."
        )

    reasoning = (
        f"Depth {depth_m}m assessed against {vessel_class} draft requirement. "
        f"Seasonal index for {month_name} applied. "
        f"Composite score {composite_score} determines viability threshold (30.0)."
    )

    return build_proposal(
        proposal_type=PROPOSAL_TYPE_NAVIGABILITY,
        subject=f"{segment_id} / {vessel_class} / {month_name}",
        proposal_text=text,
        confidence=confidence,
        score=composite_score,
        source_ids=source_ids or ["NAVIGABILITY_ENGINE_v1"],
        contributing_signals=["depth", "navigability_confidence", "segment_score"],
        reasoning=reasoning,
        geo_coordinates=geo_coordinates,
        conditions=[] if viable else [
            f"Depth insufficient or seasonal closure risk in {month_name}"
        ]
    )


def propose_bridge_clearance(
    bridge_name: str,
    vessel_class: str,
    clearance_margin_m: float,
    risk_level: str,
    score: float,
    geo_coordinates: List[float],
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a bridge clearance constraint proposal.

    Example output:
    "Bridge clearance risk elevated for draft profile B."
    """
    if risk_level == "SAFE":
        text = (
            f"Bridge {bridge_name}: clearance SAFE for {vessel_class}. "
            f"Margin {clearance_margin_m}m -- no restriction."
        )
        conditions = []
    elif risk_level == "MARGINAL":
        text = (
            f"Bridge {bridge_name}: clearance MARGINAL for {vessel_class}. "
            f"Margin {clearance_margin_m}m -- low tide passage recommended."
        )
        conditions = ["Passage during low tide only", "Tide gauge monitoring required"]
    elif risk_level == "CRITICAL":
        text = (
            f"Bridge clearance risk ELEVATED at {bridge_name} for "
            f"{vessel_class} draft profile. "
            f"Margin {clearance_margin_m}m -- passage not recommended."
        )
        conditions = [
            "Passage not recommended",
            "Use alternative route or smaller vessel class"
        ]
    else:
        text = (
            f"Bridge {bridge_name} BLOCKS {vessel_class}. "
            f"Clearance margin {clearance_margin_m}m -- passage impossible."
        )
        conditions = [
            "Route blocked for this vessel class",
            "Vessel transshipment required"
        ]

    confidence = 0.95 if risk_level in ("SAFE", "BLOCKED") else 0.80

    reasoning = (
        f"Air clearance assessed against {vessel_class} height profile. "
        f"Margin {clearance_margin_m}m classified as {risk_level}. "
        f"Thresholds: SAFE >= 10m, MARGINAL 5-10m, CRITICAL 2-5m, BLOCKED < 0m."
    )

    return build_proposal(
        proposal_type=PROPOSAL_TYPE_CONSTRAINT,
        subject=f"{bridge_name} / {vessel_class}",
        proposal_text=text,
        confidence=confidence,
        score=score,
        source_ids=source_ids or ["BRIDGE_CONSTRAINT_v1", "NHAI_BRIDGE_v1"],
        contributing_signals=["bridge_clearance"],
        reasoning=reasoning,
        geo_coordinates=geo_coordinates,
        conditions=conditions
    )


def propose_ecological_status(
    location_id: str,
    stress_level: str,
    pollution_class: str,
    ecological_score: float,
    nirmal_signal: str,
    aviral_signal: str,
    confidence: float,
    geo_coordinates: List[float],
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates an ecological status proposal.

    Example output:
    "Ecological stress elevated near Node-D."
    """
    if stress_level == "CRITICAL":
        text = (
            f"Ecological stress CRITICAL near {location_id}. "
            f"Pollution class: {pollution_class}. "
            f"Immediate Namami Gange intervention required. "
            f"{nirmal_signal}."
        )
        conditions = [
            "No port or tourism infrastructure until remediation",
            "Namami Gange intervention mandatory",
            "Industrial effluent audit required"
        ]
    elif stress_level == "HIGH":
        text = (
            f"Ecological stress HIGH at {location_id}. "
            f"Pollution class: {pollution_class}. "
            f"Infrastructure development conditional on ecological improvement. "
            f"{nirmal_signal}."
        )
        conditions = [
            "Ecological improvement required before infrastructure approval",
            "Monitoring programme mandatory"
        ]
    elif stress_level == "MODERATE":
        text = (
            f"Ecological stress MODERATE at {location_id}. "
            f"Pollution class: {pollution_class}. "
            f"Conditional development feasible with mitigation. "
            f"{nirmal_signal}."
        )
        conditions = ["Environmental mitigation plan required"]
    else:
        text = (
            f"Ecological integrity ACCEPTABLE at {location_id}. "
            f"Pollution class: {pollution_class}. "
            f"{nirmal_signal}. "
            f"{aviral_signal}."
        )
        conditions = []

    reasoning = (
        f"Ecological stress level {stress_level} derived from pollution score, "
        f"turbidity, and industrial proximity assessment. "
        f"Score {ecological_score}/100."
    )

    return build_proposal(
        proposal_type=PROPOSAL_TYPE_ECOLOGICAL,
        subject=location_id,
        proposal_text=text,
        confidence=confidence,
        score=ecological_score,
        source_ids=source_ids or ["ECOLOGICAL_ENGINE_v1", "CPCB_WQ_v1"],
        contributing_signals=["pollution", "turbidity",
                              "ecological_stress", "industrial_proximity"],
        reasoning=reasoning,
        geo_coordinates=geo_coordinates,
        conditions=conditions
    )


def propose_infrastructure_readiness(
    node_id: str,
    node_type: str,
    composite_score: float,
    multimodal: bool,
    operational_status: str,
    geo_coordinates: List[float],
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates an infrastructure readiness proposal.

    Example output:
    "Jetty cluster C augmentable for tourism / cargo use."
    """
    if multimodal and composite_score >= 75.0:
        text = (
            f"{node_type.replace('_', ' ').title()} {node_id}: "
            f"PRIORITY candidate for Sagarmala / Bharatmala integration. "
            f"Multimodal connectivity confirmed. "
            f"Score {composite_score}/100. Status: {operational_status}."
        )
        conditions = []
    elif composite_score >= 60.0:
        text = (
            f"{node_type.replace('_', ' ').title()} {node_id}: "
            f"VIABLE for infrastructure development. "
            f"Score {composite_score}/100. "
            f"Augmentable for cargo / tourism use pending DPR."
        )
        conditions = ["DPR preparation recommended", "Connectivity gap assessment required"]
    elif composite_score >= 30.0:
        text = (
            f"{node_type.replace('_', ' ').title()} {node_id}: "
            f"CONDITIONAL -- score {composite_score}/100. "
            f"Connectivity investment required before viability. "
            f"Status: {operational_status}."
        )
        conditions = [
            "Road or rail connectivity improvement required",
            "Revisit after infrastructure gap is addressed"
        ]
    else:
        text = (
            f"{node_type.replace('_', ' ').title()} {node_id}: "
            f"NOT VIABLE at this time. Score {composite_score}/100. "
            f"Fundamental connectivity and status barriers present."
        )
        conditions = [
            "Not recommended for near-term development",
            "Requires major connectivity and status improvement"
        ]

    reasoning = (
        f"Infrastructure score {composite_score}/100 computed from "
        f"operational status and multimodal connectivity. "
        f"Multimodal: {multimodal}. Status: {operational_status}."
    )

    return build_proposal(
        proposal_type=PROPOSAL_TYPE_INFRASTRUCTURE,
        subject=f"{node_id} ({node_type})",
        proposal_text=text,
        confidence=0.90,
        score=composite_score,
        source_ids=source_ids or ["INFRA_OVERLAY_v1"],
        contributing_signals=["port_infrastructure", "terminal"],
        reasoning=reasoning,
        geo_coordinates=geo_coordinates,
        conditions=conditions
    )


def propose_seaplane_feasibility(
    location_id: str,
    depth_m: float,
    turbidity_class: str,
    bridge_obstruction: bool,
    ecological_viable: bool,
    last_mile_available: bool,
    geo_coordinates: List[float],
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a seaplane feasibility proposal.

    Example output:
    "Location A feasible for conditional seaplane landing
     with last-mile dependency."
    """
    blockers = []
    conditions = []

    if depth_m < 0.8:
        blockers.append(f"insufficient water depth ({depth_m}m, minimum 0.8m)")
    if turbidity_class in ("HIGH", "CRITICAL"):
        blockers.append(f"turbidity {turbidity_class} restricts visibility")
    if bridge_obstruction:
        blockers.append("bridge obstruction in approach path")
    if not ecological_viable:
        blockers.append("ecological conditions below minimum standard")

    if not blockers and last_mile_available:
        text = (
            f"Location {location_id} FEASIBLE for seaplane landing. "
            f"Depth adequate ({depth_m}m). "
            f"Turbidity acceptable ({turbidity_class}). "
            f"Last-mile connectivity available. "
            f"No bridge obstruction."
        )
        confidence = 0.90
        score = 85.0
    elif not blockers and not last_mile_available:
        text = (
            f"Location {location_id} feasible for CONDITIONAL seaplane landing "
            f"with last-mile dependency. "
            f"Water conditions suitable. "
            f"Last-mile connectivity required for operational viability."
        )
        conditions = ["Last-mile connectivity infrastructure required"]
        confidence = 0.75
        score = 65.0
    else:
        text = (
            f"Location {location_id} NOT feasible for seaplane landing. "
            f"Blockers: {'; '.join(blockers)}."
        )
        conditions = blockers
        confidence = 0.90
        score = 10.0

    reasoning = (
        f"Seaplane feasibility assessed against: depth >= 0.8m, "
        f"turbidity class not HIGH/CRITICAL, no bridge obstruction, "
        f"ecological viability, last-mile availability."
    )

    return build_proposal(
        proposal_type=PROPOSAL_TYPE_CONNECTIVITY,
        subject=f"{location_id} / Seaplane",
        proposal_text=text,
        confidence=confidence,
        score=score,
        source_ids=source_ids or [
            "NAVIGABILITY_ENGINE_v1",
            "ECOLOGICAL_ENGINE_v1",
            "BRIDGE_CONSTRAINT_v1"
        ],
        contributing_signals=[
            "depth", "turbidity", "bridge_clearance",
            "seaplane_feasibility", "last_mile"
        ],
        reasoning=reasoning,
        geo_coordinates=geo_coordinates,
        conditions=conditions
    )


def generate_location_proposals(
    location_id: str,
    geo_coordinates: List[float],
    navigability_result: Optional[Dict] = None,
    ecological_result: Optional[Dict] = None,
    infrastructure_result: Optional[Dict] = None,
    bridge_result: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Generates all applicable proposals for a location from available
    layer results.

    Returns a list of proposals sorted by priority.
    """
    proposals = []

    if navigability_result:
        p = propose_navigability(
            segment_id=location_id,
            waterway_id=navigability_result.get("waterway_id", "NW1"),
            vessel_class=navigability_result.get("vessel_class", "Class-III"),
            month_name=navigability_result.get("month_name", "November"),
            composite_score=navigability_result.get(
                "composite_navigability_score", 0.0),
            depth_m=navigability_result.get(
                "depth_assessment", {}).get("depth_m", 0.0),
            confidence=navigability_result.get("navigability_confidence", 0.5),
            geo_coordinates=geo_coordinates,
            seasonal_risk=navigability_result.get(
                "seasonal_assessment", {}).get("risk_level", "UNKNOWN")
        )
        proposals.append(p)

    if ecological_result:
        p = propose_ecological_status(
            location_id=location_id,
            stress_level=ecological_result.get(
                "stress_assessment", {}).get("stress_level", "UNKNOWN"),
            pollution_class=ecological_result.get(
                "pollution_assessment", {}).get("pollution_class", "UNKNOWN"),
            ecological_score=ecological_result.get(
                "composite_ecological_score", 0.0),
            nirmal_signal=ecological_result.get(
                "pollution_assessment", {}).get("nirmal_signal", ""),
            aviral_signal=ecological_result.get(
                "pollution_assessment", {}).get("aviral_signal", ""),
            confidence=ecological_result.get("confidence", 0.8),
            geo_coordinates=geo_coordinates
        )
        proposals.append(p)

    if infrastructure_result:
        p = propose_infrastructure_readiness(
            node_id=location_id,
            node_type=infrastructure_result.get("node_type", "candidate_location_108"),
            composite_score=infrastructure_result.get("composite_score", 0.0),
            multimodal=infrastructure_result.get("multimodal", False),
            operational_status=infrastructure_result.get(
                "operational_status", "PROPOSED"),
            geo_coordinates=geo_coordinates
        )
        proposals.append(p)

    if bridge_result:
        p = propose_bridge_clearance(
            bridge_name=bridge_result.get("bridge_name", "Unknown Bridge"),
            vessel_class=bridge_result.get("vessel_class", "Class-III"),
            clearance_margin_m=bridge_result.get("clearance_margin_m", 0.0),
            risk_level=bridge_result.get("risk_level", "CRITICAL"),
            score=bridge_result.get("score", 0.0),
            geo_coordinates=geo_coordinates
        )
        proposals.append(p)

    # Sort: CRITICAL first, then by score descending
    priority_order = {
        PRIORITY_CRITICAL: 0,
        PRIORITY_HIGH: 1,
        PRIORITY_MEDIUM: 2,
        PRIORITY_LOW: 3,
        PRIORITY_INFO: 4
    }
    proposals.sort(key=lambda p: (
        priority_order.get(p["priority"], 5),
        -p["score"]
    ))

    return proposals


# Self-test
if __name__ == "__main__":
    import json

    print("proposal_engine.py -- Self-Test")
    print("=" * 50)

    # Test 1: Navigability proposal
    p1 = propose_navigability(
        segment_id="NW1_PATNA_001",
        waterway_id="NW1",
        vessel_class="Class-III",
        month_name="November",
        composite_score=80.5,
        depth_m=4.2,
        confidence=0.85,
        geo_coordinates=[85.1376, 25.5941],
        seasonal_risk="LOW"
    )
    print(f"Proposal type: {p1['proposal_type']}")
    print(f"Confidence: {p1['confidence']} ({p1['confidence_label']})")
    print(f"Priority: {p1['priority']}")
    print(f"Text: {p1['proposal_text'][:80]}")
    print(f"Deterministic: {p1['provenance']['deterministic']}")
    print(f"ML used: {p1['provenance']['ml_used']}")

    print()

    # Test 2: Ecological proposal
    p2 = propose_ecological_status(
        location_id="kanpur_industrial_zone",
        stress_level="CRITICAL",
        pollution_class="CRITICAL",
        ecological_score=0.93,
        nirmal_signal="CRITICAL: Water quality fails all Nirmal Ganga standards",
        aviral_signal="Flow continuity insufficient",
        confidence=0.8,
        geo_coordinates=[80.3319, 26.4499]
    )
    print(f"Ecological proposal: {p2['proposal_type']}")
    print(f"Priority: {p2['priority']}")
    print(f"Conditions: {p2['conditions']}")

    print()

    # Test 3: Seaplane feasibility
    p3 = propose_seaplane_feasibility(
        location_id="varanasi_terminal",
        depth_m=3.5,
        turbidity_class="MODERATE",
        bridge_obstruction=False,
        ecological_viable=True,
        last_mile_available=False,
        geo_coordinates=[82.9739, 25.3176]
    )
    print(f"Seaplane proposal: {p3['proposal_text'][:80]}")
    print(f"Conditions: {p3['conditions']}")
    print(f"Signal count: {p3['provenance']['signal_count']}")
