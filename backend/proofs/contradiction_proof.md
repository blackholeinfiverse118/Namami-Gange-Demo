# Contradiction Engine Proof
**Project:** NICAI -- Marine Intelligence Spine v1
**Date:** 2026-05-30
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the contradiction engine preserves both conflicting
signals (append-only), increases conflict density correctly, never silently
averages conflicting values, and marks all contradictions as AMBIGUOUS.

---

## PROOF 1 -- Contradiction Engine Self-Test

**Command run:**
```
cd src
python contradiction_engine.py
```

**Terminal output:**
```
contradiction_engine.py -- Self-Test
==================================================
Appended signal 1: depth=3.5 from CWC
Appended signal 2: depth=2.1 from IWAI
Signal 2 conflict_density after contradiction: 0.25
Appended signal 3: discharge=1500.0 (no contradiction expected)
Contradictions detected: 1
Contradiction records:
  Contradiction on field 'value': source 'CWC_DEPTH_v1' reports 3.5,
  source 'IWAI_DEPTH_v1' reports 2.1. Both preserved. Conflict density increased.
Conflict summary:
{
  "total_signals": 3,
  "total_contradictions": 1,
  "high_conflict_signals": 0,
  "clean_signals": 3,
  "contradiction_rate": 0.3333
}
All signals in store: 3
Both contradicting signals preserved (append-only confirmed)
```

---

## PROOF 2 -- Contradiction Test Suite: 24/24 Pass

**Command run:**
```
python tests/test_contradictions.py
```

**Results:**
```
Results: 24/24 passed ALL PASS
```

**Key results:**
- TEST A5 -- Contradiction record preserves both values: value_a=3.5 value_b=2.1
- TEST A6 -- Resolution is AMBIGUOUS (not resolved, not averaged)
- TEST B1 -- Both signals preserved: signal_count=2
- TEST B2 -- Store grows monotonically: counts=[1,2,3,4,5]
- TEST B3 -- Original signal not modified after contradiction
- TEST C1 -- Conflict density increases: conflict_density=0.25
- TEST C2 -- Conflict density capped at 1.0

---

## Append-Only Truth Rules Verified

| Rule | Verified |
|---|---|
| Both contradicting signals preserved in store | PASS |
| No signal deleted after contradiction | PASS |
| No silent averaging of conflicting values | PASS |
| Contradiction resolution marked AMBIGUOUS | PASS |
| Conflict density increments by 0.25 per contradiction | PASS |
| Conflict density capped at 1.0 | PASS |
| Clean signals keep conflict_density = 0.0 | PASS |
| Same-source signals do not trigger contradiction | PASS |
| Different-location signals do not trigger contradiction | PASS |

**Conclusion:** Append-only truth semantics confirmed. Both CWC (3.5m) and
IWAI (2.1m) depth readings are preserved in the store. Neither is deleted.
The system surfaces the ambiguity for human review rather than hiding it.
