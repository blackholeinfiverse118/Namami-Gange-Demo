# Integration Surface Definitions v2
**Project:** NICAI -- Marine Intelligence Spine v1
**Date:** 2026-05-30
**Author:** Nupur Gavane -- Build Lead
**Version:** 2.0 (Sprint 5 -- Marine Intelligence Spine)
**Status:** ACTIVE

---

## What Changed from v1

v1 defined contracts for: Shravani, Ankita, Nikhil, Tester.
v2 adds: Nupur to Chandragupta contract (the sovereign control surface).
All v1 contracts remain in force. This document adds the new contract only.

For v1 contracts see: integration_surface.md

---

## NEW CONTRACT -- NUPUR TO CHANDRAGUPTA
### Nupur Gavane (Marine Intelligence Spine) -> Chandragupta (Sovereign Control Surface)

### What Chandragupta Is

Chandragupta is the sovereign operational control surface. It is the
frontend dashboard that government decision-makers use to query the
intelligence spine, view the GIS map, read proposals, and make
infrastructure decisions. It consumes the backend truth. It does NOT
replicate backend logic.

### What the Spine Delivers to Chandragupta

**1. GeoJSON Overlays (5 layers)**

All delivered via GET /digital-depth

```
Layer 1 -- Physical:    depth, flow, discharge
Layer 2 -- Ecological:  pollution, turbidity, stress
Layer 3 -- Economic:    cargo, CEZ, MMLP, tourism
Layer 4 -- Policy:      restricted zones, compliance, project areas
Layer 5 -- Infrastructure: ports, terminals, waterways, bridges, barrages
```

Each layer is a GeoJSON FeatureCollection. Each feature has:
- geo_coordinates [longitude, latitude] WGS84
- score (float 0-100)
- status (layer-specific string)
- color (hex code for map marker)
- reasoning (string for tooltip)

**2. Navigability Intelligence**

Delivered via GET /navigability

Query parameters:
- waterway: NW1 or NW5
- vessel_class: Class-I through Class-V, Seaplane, Barge, Ferry
- month: 1-12

Returns: segment-by-segment viability, scores, proposals, confidence.

**3. Ecological Intelligence**

Delivered via GET /ecology

Query parameters:
- stress_level: LOW, MODERATE, HIGH, CRITICAL
- location_id: specific location

Returns: pollution class, turbidity class, Nirmal Ganga signal,
Aviral Ganga signal, ecological viability, stress level.

**4. Infrastructure Overlay**

Delivered via GET /infrastructure-overlay

Query parameters:
- type: major_port, inland_terminal, hub_spoke_node, cez_cluster, etc.
- candidates: true -- includes 108 candidate locations

Returns: GeoJSON FeatureCollection of all infrastructure nodes.

**5. Actionable Proposals**

Delivered via GET /proposal-engine

Query parameters:
- location_id (required)
- vessel_class
- month

Returns: priority-sorted list of proposals for a location.
Each proposal has: proposal_type, proposal_text, confidence,
confidence_label, priority, conditions, source_ids,
contributing_signals, reasoning, provenance.

**6. Marine Signals**

Delivered via GET /marine-signals

Query parameters:
- signal_type: depth, discharge, pollution, bridge_clearance, etc.
- source_id: CWC_v1, CPCB_v1, IWAI_v1, etc.

Returns: normalized marine schema signals with provenance hashes.

**7. System Health**

Delivered via GET /marine-health

Returns: operational status, available layers, endpoints, deterministic=True.

### API Base URL

Development: http://localhost:5000
All endpoints return JSON. All responses are contract-compliant.

### What Chandragupta Must NOT Do

- Must NOT replicate scoring logic in the frontend
- Must NOT hardcode scores, levels, or proposals
- Must NOT modify GeoJSON before rendering
- Must NOT make infrastructure recommendations outside what the spine proposes
- Must NOT present proposals as decisions -- they are proposals only

### What Chandragupta Must Do

- Call the spine API for all intelligence data
- Display proposals with their confidence labels and conditions
- Show the Nirmal Ganga and Aviral Ganga signals as part of ecological view
- Render all 5 GIS layers with the color maps provided by the spine
- Show proposal conditions as mandatory context alongside the proposal text
- Never show a proposal without its confidence label

### GeoJSON Color Reference for Chandragupta

Physical layer:
```
FLOOD:    #8b0000  (dark red)
HIGH:     #cc3300  (red-orange)
NORMAL:   #2ecc71  (green)
LOW:      #f39c12  (amber)
DEEP:     #1a6eb5  (dark blue)
NAVIGABLE:#4a9fd4  (medium blue)
SHALLOW:  #89c4e1  (light blue)
CRITICAL: #d4e9f7  (very light blue)
```

Ecological layer:
```
EXCELLENT: #27ae60  (dark green)
GOOD:      #2ecc71  (green)
MODERATE:  #f39c12  (amber)
POOR:      #e74c3c  (red)
CRITICAL:  #7f0000  (dark red)
```

Infrastructure layer:
```
OPERATIONAL:       #2ecc71  (green)
UNDER_DEVELOPMENT: #f39c12  (amber)
PROPOSED:          #95a5a6  (grey)
BLOCKED:           #e74c3c  (red)
```

### Failure Handling

| API Failure | Chandragupta Behaviour |
|---|---|
| API returns 500 | Show "Intelligence spine temporarily unavailable" |
| API unreachable | Show "Engine offline -- cached data may be shown" |
| Empty results | Show "No data available for this filter" |
| Unknown location_id | Show "Location not found in spine" |

### Topology Feeds

The spine provides topology feeds via /digital-depth for GIS rendering.
Chandragupta should load all 5 layers on initialization and refresh
on user filter changes. Layer switching (Physical/Ecological/etc.)
should be handled client-side using the already-loaded layer data.

### Realtime-Ready Contracts

The current spine is not real-time (batch computation on request).
The API contract is designed to be realtime-ready:
- All signals have timestamps
- All signals have source_hash and extraction_hash
- Conflict density tracks data freshness
- The append-only truth store supports incremental updates

When real-time data feeds are connected, the API responses will
update automatically without any frontend contract changes.

---

## Summary -- All Active Integration Contracts

| Contract | Version | Status |
|---|---|---|
| Shravani -> Nupur (Data) | v1 | ACTIVE |
| Ankita -> Nupur (Validation) | v1 | ACTIVE |
| Nupur -> Nikhil (Visualization) | v1 | ACTIVE |
| Nupur -> Tester (Test) | v1 | ACTIVE |
| Nupur -> Chandragupta (Control Surface) | v2 NEW | ACTIVE |

All contracts are enforced by code. No contract is trust-based.
