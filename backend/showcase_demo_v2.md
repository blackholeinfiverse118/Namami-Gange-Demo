# Showcase Demo v2 -- Marine Intelligence Spine v1
**Project:** NICAI -- Marine Intelligence Spine v1
**Date:** 2026-05-30
**Author:** Nupur Gavane -- Build Lead
**Status:** RUNNABLE -- every step below executes against live code

---

## What This Demo Shows

This document is the complete showcase walkthrough for the Marine
Intelligence Spine v1. It demonstrates the system has evolved from
a suitability scoring engine into a bounded sovereign marine-river
operational intelligence backbone converging Namami Gange + Sagarmala
+ Bharatmala.

Every command is real and runnable. Nothing is pre-recorded or mocked.

---

## Pre-Demo Setup

Ensure you are in the project root:
```
cd C:\Ganga-Basin-Suitability-Intelligence-Final-Convergence
```

Start the API (Terminal 1):
```
cd src
python api.py
```

Expected output:
```
NICAI API -- Starting on http://localhost:5000
```

---

## STEP 1 -- Verify the Spine is Alive

**Command (Terminal 2):**
```
curl http://localhost:5000/marine-health
```

**Expected response:**
```json
{
  "status": "operational",
  "spine_version": "v1",
  "layers_available": ["physical", "ecological", "economic", "policy", "infrastructure"],
  "endpoints": ["GET /marine-signals", "GET /infrastructure-overlay",
                "GET /navigability", "GET /ecology",
                "GET /proposal-engine", "GET /digital-depth"],
  "deterministic": true,
  "ml_used": false
}
```

**What this proves:**
- Marine Intelligence Spine v1 is live
- 5 GIS layers available
- 6 new endpoints operational
- deterministic=true, ml_used=false

---

## STEP 2 -- Ecological Intelligence (Namami Gange Layer)

**What this shows:** Ecological stress assessment for Ganga Basin locations
supporting Nirmal Ganga (clean water) and Aviral Ganga (uninterrupted flow)
goals.

**Command:**
```
curl http://localhost:5000/ecology
```

**Key outputs:**
- Patna: ecological_viability=true, stress=LOW,
  "Nirmal Ganga -- water quality acceptable for most uses"
- Kanpur: ecological_viability=false, stress=CRITICAL,
  "CRITICAL: Water quality fails all Nirmal Ganga standards"

**What this shows:**
- Kanpur identified as critical intervention point for Namami Gange
- Patna cleared for infrastructure development
- Nirmal Ganga signal present on every ecological result
- Aviral Ganga signal present on every ecological result

---

## STEP 3 -- Navigability Intelligence (NW1/NW5 Layer)

**What this shows:** Vessel class and seasonal navigability for National
Waterway 1.

**Command:**
```
curl "http://localhost:5000/navigability?vessel_class=Class-III&month=11"
```

**What this shows:**
- 3 segments scored for Class-III vessel in November
- Seasonal closure probability calculated per segment
- Proposals generated: "Segment X suitable/NOT suitable for Class-III
  during November"
- Confidence tags on every result

---

## STEP 4 -- Infrastructure Overlay (Sagarmala Layer)

**What this shows:** All infrastructure nodes scored for connectivity
and operational readiness.

**Command:**
```
curl http://localhost:5000/infrastructure-overlay
```

**With 108 candidate locations:**
```
curl "http://localhost:5000/infrastructure-overlay?candidates=true"
```

**What this shows:**
- Patna Port: MULTIMODAL, score=100 -- priority Sagarmala candidate
- Hajipur Hub: partial connectivity -- rail investment needed
- 108 candidate locations scaffold available for DPR planning

---

## STEP 5 -- Proposal Engine (Multi-Layer Intelligence)

**What this shows:** All proposals for a location, sorted by priority,
confidence-tagged, trace-backed.

**Command:**
```
curl "http://localhost:5000/proposal-engine?location_id=patna_river_port&vessel_class=Class-III&month=11"
```

**Sample proposal output:**
```json
{
  "proposal_type": "NAVIGABILITY",
  "proposal_text": "Segment suitable for Class-III during November...",
  "confidence": 0.85,
  "confidence_label": "HIGH",
  "priority": "HIGH",
  "provenance": { "deterministic": true, "ml_used": false },
  "conditions": []
}
```

**What this shows:**
- Proposals for navigability, ecological, and infrastructure all in one call
- CRITICAL priority proposals sorted first
- Every proposal has confidence label, conditions, source_ids
- provenance.deterministic=true, provenance.ml_used=false on every proposal

---

## STEP 6 -- Digital Depth / 5-Layer GIS

**What this shows:** The complete 5-layer GIS structure for Chandragupta.

**Summary view:**
```
curl "http://localhost:5000/digital-depth?summary=true"
```

**Single layer view:**
```
curl "http://localhost:5000/digital-depth?layer=ecological"
```

**What this shows:**
- All 5 layers (physical, ecological, economic, policy, infrastructure)
- Each layer is a GeoJSON FeatureCollection
- Real coordinates, scores, colors, reasoning on every feature
- Ready for Chandragupta map rendering

---

## STEP 7 -- Marine Signals (Provenance Layer)

**What this shows:** All normalized marine schema signals with
provenance hashes.

**Command:**
```
curl "http://localhost:5000/marine-signals?signal_type=pollution"
```

**What this shows:**
- Every signal has event_id, source_hash, extraction_hash
- Conflict density tracks data quality
- All signals validated against Unified Marine Schema
- Append-only provenance trail

---

## STEP 8 -- Run Full Test Suite

**Command:**
```
python tests/test_marine_schema.py
python tests/test_contradictions.py
python tests/test_bridge_barrage_constraints.py
python tests/test_navigability.py
python tests/test_proposal_engine.py
python tests/test_overlay_contracts.py
```

**Expected results:**
```
Results: 28/28 passed ALL PASS
Results: 24/24 passed ALL PASS
Results: 31/31 passed ALL PASS
Results: 36/36 passed ALL PASS
Results: 35/35 passed ALL PASS
Results: 35/35 passed ALL PASS
```

Sprint 5 new tests: 189. Combined with Sprint 4: 283 tests, all pass.

---

## Complete Demo Flow Summary

```
STEP 1   GET /marine-health          -> Spine live, 5 layers, ml_used=false
STEP 2   GET /ecology                -> Nirmal/Aviral Ganga signals, Kanpur CRITICAL
STEP 3   GET /navigability           -> Class-III NW1 November assessment
STEP 4   GET /infrastructure-overlay -> Patna MULTIMODAL, 108 candidates
STEP 5   GET /proposal-engine        -> Priority-sorted, confidence-tagged proposals
STEP 6   GET /digital-depth          -> 5-layer GIS for Chandragupta
STEP 7   GET /marine-signals         -> Provenance trail for all signals
STEP 8   All test suites             -> 283 tests, ALL PASS
```

---

## Key Messages for Reviewers

1. This is not a suitability engine anymore. It is a bounded sovereign
   marine-river operational intelligence backbone converging Namami Gange,
   Sagarmala, and Bharatmala.

2. The Unified Marine Schema ensures no data enters the spine without
   normalization and provenance tracking.

3. The Contradiction Engine preserves conflicting source data -- it never
   silently averages. Both CWC and IWAI readings are kept.

4. The Proposal Engine outputs are proposal-only. They are confidence-tagged,
   trace-backed, and explainable. They are not decisions.

5. All 5 GIS layers are ready for Chandragupta consumption. Color maps,
   coordinates, and reasoning fields are all provided.

6. 283 tests passing. Zero failures. No ML anywhere.
