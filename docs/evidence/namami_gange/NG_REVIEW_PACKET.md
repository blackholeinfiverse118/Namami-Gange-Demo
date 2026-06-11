# NAMAMI GANGE — REVIEW PACKET
**Sprint:** Dataset Truth Audit + System Mapping
**Auditor:** Nupur Gavane
**Date:** May 28, 2026

> Zero-knowledge handover document. An incoming builder must be able to understand the system immediately from this document.

---

## ENTRY POINT — What Is This System?

**Namami Gange** is a real-time geospatial intelligence platform for the Ganga river basin. It evaluates locations for infrastructure suitability (inland ports, seaplane zones, hub-spoke logistics networks) using real-world datasets from CPCB, CWC, and IWAI.

Key characteristics:
- Fully deterministic — no ML, no randomness
- Every score traceable to a source dataset signal
- Hard vs soft constraint engine — some locations are always REJECTED
- GeoJSON output for map visualization
- Scenario simulation — what-if policy exploration
- REST API via Flask

**Repo:** `Ganga-Basin-Suitability-Intelligence-Final-Convergence`

---

## CORE EXECUTION FLOW

```
data_raw/*.csv
    ↓
data_adapter.py (loads + normalises)
    ↓
location_entity_builder.py (groups signals into location profiles)
    ↓
scoring_engine.py (deterministic weighted scoring)
    ├── constraint_engine.py (HARD → REJECT, SOFT → penalty)
    ├── signal_trace_layer.py (every score traceable to source signal)
    └── explanation_layer.py (human-readable WHY)
    ↓
api.py (Flask REST API)
    ↓
geo_output_builder.py (GeoJSON: baseline + scenario + delta layers)
    ↓
Nikhil's UI / Map Layer
```

---

## LIVE INFRASTRUCTURE (from Shravani)

| Service | Role | Status |
|---|---|---|
| `ng-redis-dedup` | Deduplication | LIVE — No persistence (data lost on restart) |
| `ng-postgres-events` | Event storage | LIVE — connection issues with ng_user |
| `ng-core` | Replay + persistence | RESTARTING — PersistenceStore class missing |

---

## WHAT WAS BUILT

| File | Purpose |
|---|---|
| `NG_DATA_AUDIT_REPORT.md` | What data exists, storage locations, critical findings |
| `ng_data_inventory.csv` | Row-level inventory of all datasets and infrastructure |
| `NG_COVERAGE_MATRIX.md` | Coverage by location, factor, model, and infrastructure |
| `NG_REVIEWER_INTELLIGENCE_REPORT.md` | How a government reviewer (NMCG / Jal Shakti) would evaluate the platform |
| `NG_ADDITION_PLAN.md` | What to add/fix, prioritized P0 to P3 |
| `NG_DATA_READINESS_RISK_REPORT.md` | Where the system will fail, silent risks, readiness score |
| `NG_REVIEW_PACKET.md` | This document |

---

## DATASETS — QUICK REFERENCE

| File | Source | What It Drives |
|---|---|---|
| `cpcb_water_quality_ganga.csv` | CPCB | water_quality factor + extreme_pollution HARD constraint |
| `cwc_river_stations_ganga.csv` | CWC | river_stability + depth critical_depth HARD constraint |
| `iwai_terminals_nw1.csv` | IWAI | terminal_proximity + logistics_access + traffic_potential |
| `logistics_parks_ganga_belt.csv` | IWAI/logistics | logistics_access + hub_spoke model |
| `urban_centers_ganga_basin.csv` | Census | urban_proximity + traffic_potential |

---

## LOCATIONS IN SYSTEM

| Location | River | Inland Port | Key Finding |
|---|---|---|---|
| `patna_river_port` | Ganga (Patna) | HIGH (75.25) | Best scoring location |
| `varanasi_terminal` | Ganga (Varanasi) | MEDIUM (61.6) | Soft: logistics_absence |
| `allahabad_confluence` | Ganga+Yamuna | LOW (44.8) | Soft penalty applied |
| `kanpur_industrial_zone` | Ganga (Kanpur) | REJECTED | HARD: extreme_pollution |
| `farakka_wetland` | Ganga (Farakka) | REJECTED | HARD: wetland + no_env_clearance |
| `sultanganj_node` | Ganga (Sultanganj) | MEDIUM | Soft-constrained |

---

## FAILURE CASES

| Case | What Happens | Source |
|---|---|---|
| Container restart | Redis loses dedup state — all history reset | Shravani confirmed |
| Replay request | ng-core restarting — PersistenceStore missing — replay unavailable | Shravani confirmed |
| Postgres connection drops | Events fail to store | Shravani confirmed |
| Live data query | System cannot answer — static CSVs only | Repo analysis |
| Location not in system | No score returned — only 6 locations covered | Repo analysis |

---

## PROOF — Evidence

| Artifact | Source | Status |
|---|---|---|
| Shravani's direct reply | Shravani Harde | RECEIVED |
| GitHub repo analysis | `data_raw/`, `src/`, `README.md` | CONFIRMED |
| Test results 10/10 | `tests/test_scenarios_simulation.py` | ALL PASS (from repo) |
| API health response | `GET /health` output from README | Documented |

---

## FAQ

**Q: How do I run the system?**
A: `cd src/ && python api.py` — server at `http://localhost:5000`

**Q: Who to contact for data layer issues?**
A: Shravani Harde — data layer owner

**Q: Who owns the UI / map layer?**
A: Nikhil (map consumption) + Chandragupta (UX) — integration not yet started

**Q: What is the most urgent fix?**
A: Three infrastructure fixes must happen first: Redis volume mounts, PersistenceStore class, Postgres connection string. Without these, data is lost on restart and replay is broken.

**Q: Is live data integrated?**
A: No. All 5 datasets are static CSVs. No real-time CPCB or CWC API integration exists yet.

**Q: What is the overall readiness score?**
A: 4/10 — infrastructure issues block operational use despite correct scoring logic.

---

*May 28, 2026 — Nupur Gavane*
