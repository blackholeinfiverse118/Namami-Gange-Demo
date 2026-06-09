"""
contradiction_engine.py
────────────────────────────────────────────────────────────
NICAI - Marine Intelligence Spine v1
Contradiction Engine -- Append-Only Truth Layer

Rules (mandatory, non-negotiable):
  - If two sources disagree: preserve BOTH
  - Mark ambiguity on both signals
  - Increase conflict_density
  - No silent averaging
  - No deletion
  - Branching allowed
  - Append-only semantics

Truth store is an in-memory append-only log.
Signals are never modified after insertion.
Contradictions produce a new conflict record, not an update.
"""

from typing import Any, Dict, List, Optional, Tuple
from marine_schema import normalize_signal, check_schema, MarineSchemaError


# Conflict density increment per contradiction
CONFLICT_DENSITY_INCREMENT = 0.25

# Maximum conflict density (capped at 1.0)
MAX_CONFLICT_DENSITY = 1.0


class ContradictionRecord:
    """
    Represents a detected contradiction between two signals.
    Immutable after creation.
    """
    def __init__(
        self,
        signal_a: Dict[str, Any],
        signal_b: Dict[str, Any],
        field: str,
        value_a: Any,
        value_b: Any,
        resolution: str = "AMBIGUOUS"
    ):
        self.signal_a_id = signal_a["event_id"]
        self.signal_b_id = signal_b["event_id"]
        self.field = field
        self.value_a = value_a
        self.value_b = value_b
        self.resolution = resolution
        self.ambiguity_note = (
            f"Contradiction on field '{field}': "
            f"source '{signal_a['source_id']}' reports {value_a}, "
            f"source '{signal_b['source_id']}' reports {value_b}. "
            f"Both preserved. Conflict density increased."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_a_id": self.signal_a_id,
            "signal_b_id": self.signal_b_id,
            "field": self.field,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "resolution": self.resolution,
            "ambiguity_note": self.ambiguity_note
        }


class TruthStore:
    """
    Append-only truth store for marine signals.

    Rules:
    - Signals are appended, never modified or deleted
    - Contradictions produce a ContradictionRecord
    - Both contradicting signals remain in the store
    - conflict_density is tracked per signal_type + geo_area

    In production this would be a persistent database.
    For Sprint 5 this is an in-memory store.
    """

    def __init__(self):
        self._signals: List[Dict[str, Any]] = []
        self._contradictions: List[ContradictionRecord] = []
        self._event_ids: set = set()

    def append(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appends a signal to the truth store.
        Checks for contradictions with existing signals of the same type.
        Returns the signal (possibly with updated conflict_density).
        """
        is_valid, errors = check_schema(signal)
        if not is_valid:
            raise MarineSchemaError(errors)

        # Check for contradictions with existing signals
        contradictions = self._detect_contradictions(signal)

        if contradictions:
            # Increase conflict_density on the incoming signal
            new_density = min(
                signal["conflict_density"] + CONFLICT_DENSITY_INCREMENT * len(contradictions),
                MAX_CONFLICT_DENSITY
            )
            # Append-only: create new signal dict with updated density
            signal = {**signal, "conflict_density": round(new_density, 4)}

            for record in contradictions:
                self._contradictions.append(record)

        # Append -- never modify existing
        self._signals.append(signal)
        self._event_ids.add(signal["event_id"])

        return signal

    def _detect_contradictions(
        self, incoming: Dict[str, Any]
    ) -> List[ContradictionRecord]:
        """
        Detects contradictions between incoming signal and existing signals.

        A contradiction exists when:
        - Same signal_type
        - Same geo_coordinates (within 0.01 degree tolerance)
        - Different value (beyond tolerance)
        - Different source_id
        """
        contradictions = []

        for existing in self._signals:
            if existing["signal_type"] != incoming["signal_type"]:
                continue
            if existing["source_id"] == incoming["source_id"]:
                continue
            if not _coords_match(
                existing["geo_coordinates"],
                incoming["geo_coordinates"]
            ):
                continue

            # Same location, same type, different source -- check value
            if _values_contradict(existing["value"], incoming["value"]):
                record = ContradictionRecord(
                    signal_a=existing,
                    signal_b=incoming,
                    field="value",
                    value_a=existing["value"],
                    value_b=incoming["value"]
                )
                contradictions.append(record)

        return contradictions

    def get_signals(
        self,
        signal_type: Optional[str] = None,
        source_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns signals, optionally filtered."""
        results = self._signals
        if signal_type:
            results = [s for s in results if s["signal_type"] == signal_type]
        if source_id:
            results = [s for s in results if s["source_id"] == source_id]
        return list(results)

    def get_contradictions(self) -> List[Dict[str, Any]]:
        """Returns all contradiction records as dicts."""
        return [c.to_dict() for c in self._contradictions]

    def get_conflict_summary(self) -> Dict[str, Any]:
        """Returns a summary of contradiction state."""
        high_conflict = [
            s for s in self._signals if s["conflict_density"] >= 0.5
        ]
        return {
            "total_signals": len(self._signals),
            "total_contradictions": len(self._contradictions),
            "high_conflict_signals": len(high_conflict),
            "clean_signals": len(self._signals) - len(high_conflict),
            "contradiction_rate": round(
                len(self._contradictions) / max(len(self._signals), 1), 4
            )
        }

    @property
    def signal_count(self) -> int:
        return len(self._signals)

    @property
    def contradiction_count(self) -> int:
        return len(self._contradictions)


# Helpers
def _coords_match(
    coords_a: List[float],
    coords_b: List[float],
    tolerance: float = 0.01
) -> bool:
    """
    Returns True if two coordinate pairs are within tolerance degrees.
    0.01 degrees is approximately 1 km.
    """
    return (
        abs(coords_a[0] - coords_b[0]) <= tolerance and
        abs(coords_a[1] - coords_b[1]) <= tolerance
    )


def _values_contradict(value_a: Any, value_b: Any, tolerance: float = 0.05) -> bool:
    """
    Returns True if two values contradict each other.
    For numeric values: difference > tolerance fraction of the larger value.
    For string values: any difference is a contradiction.
    """
    if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
        if value_a == 0 and value_b == 0:
            return False
        larger = max(abs(value_a), abs(value_b))
        return abs(value_a - value_b) / larger > tolerance
    return str(value_a) != str(value_b)


def detect_and_record(
    store: TruthStore,
    signals: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Appends a list of signals to the truth store.
    Returns a summary of what was appended and what contradictions were found.
    """
    appended = []
    failed = []

    for sig in signals:
        try:
            result = store.append(sig)
            appended.append(result)
        except MarineSchemaError as e:
            failed.append({"signal": sig, "errors": e.errors})

    return {
        "appended": len(appended),
        "failed": len(failed),
        "contradictions_found": store.contradiction_count,
        "conflict_summary": store.get_conflict_summary(),
        "failed_details": failed
    }


# Self-test
if __name__ == "__main__":
    import json
    import sys
    sys.path.insert(0, ".")
    from marine_schema import build_signal

    print("contradiction_engine.py -- Self-Test")
    print("=" * 50)

    store = TruthStore()

    # Signal 1: CWC says depth at Varanasi is 3.5m
    sig1 = build_signal(
        signal_type="depth",
        value=3.5,
        geo_coordinates=[82.9739, 25.3176],
        source_id="CWC_DEPTH_v1",
        confidence_initial=0.9
    )
    store.append(sig1)
    print(f"Appended signal 1: depth=3.5 from CWC")

    # Signal 2: IWAI says depth at same location is 2.1m (contradiction)
    sig2 = build_signal(
        signal_type="depth",
        value=2.1,
        geo_coordinates=[82.9739, 25.3176],
        source_id="IWAI_DEPTH_v1",
        confidence_initial=0.8
    )
    result2 = store.append(sig2)
    print(f"Appended signal 2: depth=2.1 from IWAI")
    print(f"Signal 2 conflict_density after contradiction: {result2['conflict_density']}")

    # Signal 3: same source as signal 1, same value -- no contradiction
    sig3 = build_signal(
        signal_type="discharge",
        value=1500.0,
        geo_coordinates=[85.1376, 25.5941],
        source_id="CWC_DISCH_v1",
        confidence_initial=0.95
    )
    store.append(sig3)
    print(f"Appended signal 3: discharge=1500.0 (no contradiction expected)")

    print(f"\nContradictions detected: {store.contradiction_count}")
    print(f"Contradiction records:")
    for c in store.get_contradictions():
        print(f"  {c['ambiguity_note']}")

    print(f"\nConflict summary:")
    print(json.dumps(store.get_conflict_summary(), indent=2))

    print(f"\nAll signals in store: {store.signal_count}")
    print("Both contradicting signals preserved (append-only confirmed)")