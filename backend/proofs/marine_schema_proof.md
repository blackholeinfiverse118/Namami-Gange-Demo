# Marine Schema Proof
**Project:** NICAI -- Marine Intelligence Spine v1
**Date:** 2026-05-30
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the Unified Marine Schema normalizes all data correctly,
rejects invalid inputs deterministically, generates provenance hashes, and
produces identical event_ids for identical inputs across runs.

---

## PROOF 1 -- Schema Self-Test

**Command run:**
```
cd src
python marine_schema.py
```

**Terminal output:**
```
marine_schema.py -- Self-Test
==================================================
Valid signal built:
{
  "signal_type": "depth",
  "value": 3.5,
  "geo_coordinates": [82.9739, 25.3176],
  "source_id": "CWC_DEPTH_NW1_v1",
  "confidence_initial": 0.9,
  "timestamp": "2026-05-26T10:00:00",
  "conflict_density": 0.0,
  "event_id": "EVT_62C3106760FE",
  "source_hash": "e0129be33e621c48",
  "extraction_hash": "c23a43d219bb2e8e"
}
Batch: 1 valid, 1 failed
Failed errors: ["signal_type: 'bad_type' not recognized."]
check_schema on valid signal: is_valid=True errors=[]
```

**What this proves:**
- Schema normalizes raw input into 9 required fields
- Auto-generates deterministic event_id (EVT_62C3106760FE same on every run)
- Auto-generates source_hash and extraction_hash for provenance
- Rejects invalid signal_type with clear error message
- check_schema confirms valid signal passes

---

## PROOF 2 -- Marine Schema Test Suite: 28/28 Pass

**Command run:**
```
python tests/test_marine_schema.py
```

**Results:**
```
Results: 28/28 passed ALL PASS
```

**Key results:**
- TEST A4 -- Same input produces same event_id: id1=EVT_D9C5AE425CA6 id2=EVT_D9C5AE425CA6
- TEST A5 -- Hashes deterministic: source_hash match=True
- TEST C2 -- Coordinates outside India bounds caught
- TEST C8 -- Non-dict signal rejected cleanly
- TEST E2 -- Batch mixed: 1 valid, 1 failed correctly separated

---

## Schema Field Reference

| Field | Type | Required | Notes |
|---|---|---|---|
| event_id | string | YES | Auto-generated if missing |
| timestamp | string or None | NO | Defaults to None |
| geo_coordinates | [lon, lat] | YES | India bounds enforced |
| signal_type | string | YES | Must be in VALID_SIGNAL_TYPES |
| value | any | YES | Cannot be None |
| confidence_initial | float 0-1 | YES | Range enforced |
| source_id | string | YES | Non-empty |
| source_hash | string | NO | Auto-generated |
| extraction_hash | string | NO | Auto-generated |
| conflict_density | float 0-1 | YES | Defaults to 0.0 |

**Conclusion:** Unified Marine Schema operational. All data entering the
spine is normalized before analysis. No downstream processing on raw data.
