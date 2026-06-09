"""
marine_schema.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Unified Marine Schema -- Normalization Layer

ALL data entering the Marine Intelligence Spine must pass
through this schema before any downstream analysis.

No analysis before normalization. This is mandatory.

Schema fields (minimum required):
    event_id          -- unique identifier for this signal event
    timestamp         -- ISO 8601 string or None
    geo_coordinates   -- [longitude, latitude] list
    signal_type       -- category of signal
    value             -- numeric or string value
    confidence_initial -- float 0.0 to 1.0
    source_id         -- dataset/source identifier
    source_hash       -- hash of source for provenance
    extraction_hash   -- hash of extracted value for audit
    conflict_density  -- float 0.0 to 1.0 (increases on contradiction)

Valid signal types:
    river_flow, discharge, sediment, seasonal_variation,
    barrage_influence, river_continuity,
    bridge_clearance, navigational_clearance, vessel_obstruction,
    depth, vessel_draft, segment_score, seasonal_closure,
    pollution, turbidity, ecological_stress, industrial_proximity,
    port_infrastructure, terminal, jetty, waterway,
    cargo_movement, passenger_movement, seaplane_feasibility,
    tourism_node, logistics_access, last_mile
"""

import hashlib
import uuid
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


# Valid signal types across all 6 intelligence layers
VALID_SIGNAL_TYPES = {
    # Layer 1 -- River Flow
    "river_flow", "discharge", "sediment", "seasonal_variation",
    "barrage_influence", "river_continuity", "flow_disruption",
    # Layer 2 -- Barrage + Bridge
    "bridge_clearance", "navigational_clearance", "vessel_obstruction",
    "barrage_interruption", "seaplane_obstruction", "flow_redistribution",
    # Layer 3 -- Navigability
    "depth", "vessel_draft", "segment_score",
    "seasonal_closure", "navigability_confidence",
    # Layer 4 -- Ecological
    "pollution", "turbidity", "ecological_stress",
    "industrial_proximity", "aviral_signal", "nirmal_signal",
    # Layer 5 -- Infrastructure
    "port_infrastructure", "terminal", "jetty", "waterway",
    "cez_cluster", "mmlp_cluster", "tourism_node",
    "hub_spoke_overlay", "candidate_location",
    # Layer 6 -- Business / Connectivity
    "cargo_movement", "passenger_movement", "seaplane_feasibility",
    "tourism_connectivity", "logistics_access", "last_mile",
    "ppp_opportunity",
}

# India bounding box
LAT_MIN, LAT_MAX = 6.0, 37.0
LON_MIN, LON_MAX = 68.0, 97.5


class MarineSchemaError(Exception):
    """Raised when a signal fails schema normalization."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(
            f"Marine schema violation -- {len(errors)} error(s):\n" +
            "\n".join(f"  [{i+1}] {e}" for i, e in enumerate(errors))
        )


# Hash helpers
def _hash_value(value: Any) -> str:
    """Deterministic SHA256 hash of any value."""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _generate_event_id(source_id: str, signal_type: str, value: Any) -> str:
    """Generates a deterministic event_id from source + type + value."""
    raw = f"{source_id}::{signal_type}::{value}"
    return "EVT_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12].upper()


# Field validators
def _validate_event_id(data: Dict, errors: List[str]):
    val = data.get("event_id")
    if val is None:
        errors.append("event_id: missing (required)")
    elif not isinstance(val, str) or val.strip() == "":
        errors.append("event_id: must be non-empty string")


def _validate_geo_coordinates(data: Dict, errors: List[str]):
    coords = data.get("geo_coordinates")
    if coords is None:
        errors.append("geo_coordinates: missing (required)")
        return
    if not isinstance(coords, (list, tuple)) or len(coords) != 2:
        errors.append("geo_coordinates: must be [longitude, latitude] list of length 2")
        return
    lon, lat = coords[0], coords[1]
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        errors.append("geo_coordinates: longitude and latitude must be numeric")
        return
    if not (LON_MIN <= float(lon) <= LON_MAX):
        errors.append(
            f"geo_coordinates: longitude {lon} out of India bounds [{LON_MIN}, {LON_MAX}]"
        )
    if not (LAT_MIN <= float(lat) <= LAT_MAX):
        errors.append(
            f"geo_coordinates: latitude {lat} out of India bounds [{LAT_MIN}, {LAT_MAX}]"
        )


def _validate_signal_type(data: Dict, errors: List[str]):
    val = data.get("signal_type")
    if val is None:
        errors.append("signal_type: missing (required)")
    elif val not in VALID_SIGNAL_TYPES:
        errors.append(
            f"signal_type: '{val}' not recognized. "
            f"Must be one of {sorted(VALID_SIGNAL_TYPES)}"
        )


def _validate_value(data: Dict, errors: List[str]):
    val = data.get("value")
    if val is None:
        errors.append("value: missing (required)")


def _validate_confidence(data: Dict, errors: List[str]):
    val = data.get("confidence_initial")
    if val is None:
        errors.append("confidence_initial: missing (required)")
    elif isinstance(val, bool) or not isinstance(val, (int, float)):
        errors.append(
            f"confidence_initial: must be numeric float, got {type(val).__name__}"
        )
    elif not (0.0 <= float(val) <= 1.0):
        errors.append(
            f"confidence_initial: {val} out of valid range [0.0, 1.0]"
        )


def _validate_source_id(data: Dict, errors: List[str]):
    val = data.get("source_id")
    if val is None:
        errors.append("source_id: missing (required)")
    elif not isinstance(val, str) or val.strip() == "":
        errors.append("source_id: must be non-empty string")


def _validate_conflict_density(data: Dict, errors: List[str]):
    val = data.get("conflict_density")
    if val is None:
        errors.append("conflict_density: missing (required)")
    elif isinstance(val, bool) or not isinstance(val, (int, float)):
        errors.append(
            f"conflict_density: must be numeric float, got {type(val).__name__}"
        )
    elif not (0.0 <= float(val) <= 1.0):
        errors.append(
            f"conflict_density: {val} out of valid range [0.0, 1.0]"
        )


# Main schema functions
def check_schema(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a signal dict against the Unified Marine Schema.
    Returns (is_valid, errors).
    Does NOT raise.
    """
    if not isinstance(signal, dict):
        return False, [f"Signal must be a dict, got {type(signal).__name__}"]

    errors: List[str] = []
    _validate_event_id(signal, errors)
    _validate_geo_coordinates(signal, errors)
    _validate_signal_type(signal, errors)
    _validate_value(signal, errors)
    _validate_confidence(signal, errors)
    _validate_source_id(signal, errors)
    _validate_conflict_density(signal, errors)

    return len(errors) == 0, errors


def normalize_signal(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a raw input dict into a fully compliant Marine Schema signal.

    If event_id is missing, generates one deterministically.
    If timestamp is missing, sets to None.
    If source_hash / extraction_hash are missing, computes them.
    If conflict_density is missing, defaults to 0.0.

    Raises MarineSchemaError if the result still fails validation
    after normalization attempts.
    """
    signal = dict(raw)

    # Auto-generate event_id if missing
    if not signal.get("event_id"):
        signal["event_id"] = _generate_event_id(
            signal.get("source_id", "unknown"),
            signal.get("signal_type", "unknown"),
            signal.get("value", "")
        )

    # Default timestamp to None if missing
    if "timestamp" not in signal:
        signal["timestamp"] = None

    # Compute source_hash if missing
    if not signal.get("source_hash"):
        signal["source_hash"] = _hash_value(signal.get("source_id", ""))

    # Compute extraction_hash if missing
    if not signal.get("extraction_hash"):
        signal["extraction_hash"] = _hash_value(
            str(signal.get("value", "")) + str(signal.get("source_id", ""))
        )

    # Default conflict_density to 0.0 if missing
    if signal.get("conflict_density") is None:
        signal["conflict_density"] = 0.0

    # Final validation
    is_valid, errors = check_schema(signal)
    if not is_valid:
        raise MarineSchemaError(errors)

    return signal


def normalize_batch(raw_signals: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
    """
    Normalizes a list of raw signals.
    Returns (valid_signals, failed_signals).
    Failed signals have a 'schema_errors' key added.
    """
    valid = []
    failed = []
    for raw in raw_signals:
        try:
            normalized = normalize_signal(raw)
            valid.append(normalized)
        except MarineSchemaError as e:
            failed.append({**raw, "schema_errors": e.errors})
    return valid, failed


def build_signal(
    signal_type: str,
    value: Any,
    geo_coordinates: List[float],
    source_id: str,
    confidence_initial: float = 1.0,
    timestamp: Optional[str] = None,
    conflict_density: float = 0.0,
    **extra_fields
) -> Dict[str, Any]:
    """
    Convenience builder -- constructs and normalizes a signal in one call.

    Usage:
        sig = build_signal(
            signal_type="depth",
            value=3.5,
            geo_coordinates=[82.97, 25.31],
            source_id="CWC_DEPTH_v1",
            confidence_initial=0.9
        )
    """
    raw = {
        "signal_type": signal_type,
        "value": value,
        "geo_coordinates": geo_coordinates,
        "source_id": source_id,
        "confidence_initial": confidence_initial,
        "timestamp": timestamp,
        "conflict_density": conflict_density,
        **extra_fields
    }
    return normalize_signal(raw)


# Self-test
if __name__ == "__main__":
    import json

    print("marine_schema.py -- Self-Test")
    print("=" * 50)

    # Valid signal
    sig = build_signal(
        signal_type="depth",
        value=3.5,
        geo_coordinates=[82.9739, 25.3176],
        source_id="CWC_DEPTH_NW1_v1",
        confidence_initial=0.9,
        timestamp="2026-05-26T10:00:00"
    )
    print("Valid signal built:")
    print(json.dumps(sig, indent=2))

    # Batch normalization
    raw_batch = [
        {
            "signal_type": "discharge",
            "value": 1500.0,
            "geo_coordinates": [85.1376, 25.5941],
            "source_id": "CWC_DISCH_v1",
            "confidence_initial": 0.85
        },
        {
            "signal_type": "bad_type",    # invalid
            "value": 99,
            "geo_coordinates": [85.1376, 25.5941],
            "source_id": "TEST",
            "confidence_initial": 0.5
        }
    ]
    valid, failed = normalize_batch(raw_batch)
    print(f"\nBatch: {len(valid)} valid, {len(failed)} failed")
    print(f"Failed errors: {failed[0]['schema_errors']}")

    # check_schema test
    is_valid, errors = check_schema(sig)
    print(f"\ncheck_schema on valid signal: is_valid={is_valid} errors={errors}")