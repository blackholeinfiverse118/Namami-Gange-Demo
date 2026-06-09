# Proposal Engine Proof
**Project:** NICAI -- Marine Intelligence Spine v1
**Date:** 2026-05-30
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the proposal engine generates deterministic,
confidence-tagged, trace-backed, explainable proposals for all 5
intelligence layer types, with correct priority sorting and provenance.

---

## PROOF 1 -- Proposal Engine Self-Test

**Command run:**
```
cd src
python proposal_engine.py
```

**Terminal output:**
```
proposal_engine.py -- Self-Test
==================================================
Proposal type: NAVIGABILITY
Confidence: 0.85 (HIGH)
Priority: HIGH
Text: Segment NW1_PATNA_001 on NW1 suitable for Class-III vessel during November...
Deterministic: True
ML used: False

Ecological proposal: ECOLOGICAL
Priority: CRITICAL
Conditions: ['No port or tourism infrastructure until remediation',
             'Namami Gange intervention mandatory',
             'Industrial effluent audit required']

Seaplane proposal: Location varanasi_terminal feasible for CONDITIONAL
seaplane landing with last-mile dependency...
Conditions: ['Last-mile connectivity infrastructure required']
Signal count: 5
```

---

## PROOF 2 -- Proposal Engine Test Suite: 35/35 Pass

**Command run:**
```
python tests/test_proposal_engine.py
```

**Results:**
```
Results: 35/35 passed ALL PASS
```

**Key results:**
- TEST A2 -- deterministic=True ml_used=False on all proposals
- TEST H1 -- Same input produces identical proposal text (determinism)
- TEST D2 -- CRITICAL ecological: Namami Gange intervention in conditions
- TEST G3 -- CRITICAL priority sorted first in multi-layer output

---

## Proposal Types Verified

| Type | Example Output | Status |
|---|---|---|
| NAVIGABILITY | "Segment NW1_PATNA_001 suitable for Class-III during November" | PASS |
| CONSTRAINT | "Bridge clearance risk ELEVATED for Class-III draft profile" | PASS |
| ECOLOGICAL | "Ecological stress CRITICAL near kanpur_industrial_zone" | PASS |
| INFRASTRUCTURE | "Patna Port PRIORITY candidate for Sagarmala integration" | PASS |
| CONNECTIVITY | "Location feasible for CONDITIONAL seaplane landing with last-mile dependency" | PASS |

---

## Proposal Contract Verified

Every proposal contains:

| Field | Verified |
|---|---|
| proposal_type | PASS |
| subject | PASS |
| proposal_text | PASS |
| confidence (0.0-1.0) | PASS |
| confidence_label (HIGH/MEDIUM/LOW/UNCERTAIN) | PASS |
| score (0.0-100.0) | PASS |
| priority (CRITICAL/HIGH/MEDIUM/LOW) | PASS |
| source_ids (non-empty list) | PASS |
| contributing_signals (non-empty list) | PASS |
| reasoning (non-empty string) | PASS |
| geo_coordinates | PASS |
| conditions (list, can be empty) | PASS |
| provenance.deterministic = True | PASS |
| provenance.ml_used = False | PASS |

**Conclusion:** Proposal engine operational. All proposals are
confidence-tagged, trace-backed, explainable, and provenance-anchored.
CRITICAL priority proposals sort first. No ML used anywhere in the pipeline.
