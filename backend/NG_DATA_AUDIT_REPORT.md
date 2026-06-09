# NAMAMI GANGE — DATA AUDIT REPORT
**Sprint:** Dataset Truth Audit + System Mapping
**Auditor:** Nupur Gavane
**Date:** May 28, 2026
**Status:** SUBSTANTIALLY COMPLETE — Evidence-based

---

## 1. Audit Objective

Establish factual ground truth about what data actually exists in the Namami Gange system.
No assumptions. Evidence only.

---

## 2. Storage Locations — CONFIRMED (from Shravani)

| Location | Type | Address / Path | Status | Role |
|---|---|---|---|---|
| `ng-redis-dedup` | Redis | Container: ng-redis-dedup | LIVE | Deduplication layer |
| `ng-postgres-events` | PostgreSQL | DB: `namami_gange`, owner: `ng_user` | PARTIAL | Events database |
| `ng-core` | Persistence service | Container: ng-core | RESTARTING | Replay + persistence |
| `data_raw/` | Flat CSV files | Repo: `data_raw/*.csv` | CONFIRMED | Raw source datasets |

**Critical notes:**
- Redis has NO volume mounts — data is lost on container restart
- ng-core is restarting due to missing `PersistenceStore` class
- Postgres connection string for `ng_user` has issues being resolved

---

## 3. Dataset Inventory — CONFIRMED

### Status Legend

| Status | Meaning |
|---|---|
| PRESENT | Confirmed in repo |
| PARTIAL | Exists but quality/completeness unclear |
| MISSING | Not found |
| PLANNED | On roadmap |

---

### 3.1 Core Datasets (`data_raw/`)

| Dataset | Source | Contents | Status | Notes |
|---|---|---|---|---|
| `cpcb_water_quality_ganga.csv` | CPCB (Central Pollution Control Board) | Water quality index readings across Ganga monitoring stations | PRESENT | Key input for water_quality + extreme_pollution constraint |
| `cwc_river_stations_ganga.csv` | CWC (Central Water Commission) | River station data — flow, depth, stability | PRESENT | Key input for river_stability + depth constraint |
| `iwai_terminals_nw1.csv` | IWAI (Inland Waterways Authority) | Terminal locations + logistics on NW1 | PRESENT | Key input for terminal_proximity + logistics_access |
| `logistics_parks_ganga_belt.csv` | IWAI / logistics sources | Logistics park locations + quality scores | PRESENT | Key input for logistics_access + hub_spoke model |
| `urban_centers_ganga_basin.csv` | Census / urban data | Urban coordinates, population, market access | PRESENT | Key input for urban_proximity + traffic_potential |

**Total core datasets: 5/5 PRESENT**

---

### 3.2 Signal Registry (Derived from Datasets)

Every score is traceable to these signal IDs:

| Signal ID | Source Dataset | Factor Driven |
|---|---|---|
| `CWC_RIV_STAB_v1` | cwc_river_stations_ganga.csv | river_stability |
| `CPCB_WQI_v1` | cpcb_water_quality_ganga.csv | water_quality |
| `CWC_DEPTH_v1` | cwc_river_stations_ganga.csv | depth / critical_depth constraint |
| `IWAI_TERM_v1` | iwai_terminals_nw1.csv | terminal_proximity |
| `IWAI_LOG_v1` | iwai_terminals_nw1.csv | logistics_access |
| `IWAI_TRAF_v1` | iwai_terminals_nw1.csv | traffic_potential |
| `ENV_WETLAND_v1` | Environmental overlay | wetland_zone constraint |
| `ENV_FLOOD_v1` | Environmental overlay | flood_zone constraint |
| `ENV_CLEAR_v1` | Environmental overlay | env_clearance constraint |
| `CPCB_POLL_v1` | cpcb_water_quality_ganga.csv | extreme_pollution constraint |

---

### 3.3 What Is Missing / Not Confirmed

| Item | Status | Impact |
|---|---|---|
| Real-time CPCB API feed | MISSING | System uses static CSV only — no live water quality updates |
| Real-time CWC flood data | MISSING | Flood constraint uses static data |
| Historical dataset versions | MISSING | No version/edition tracking — cannot detect outdated data |
| Location coverage beyond 6 sites | MISSING | Ganga basin has 100s of potential sites — very narrow coverage |
| Environmental clearance database | PARTIAL | Used as constraint but source unclear |
| IWAI real-time traffic data | MISSING | Traffic scores from static CSV |

---

## 4. Infrastructure Health Summary

| Component | Status | Severity | Fix Required |
|---|---|---|---|
| Redis data persistence | NO VOLUME MOUNTS | CRITICAL | Add volume mounts to docker-compose |
| ng-core PersistenceStore | CLASS MISSING | CRITICAL | Implement PersistenceStore class |
| Postgres connection | ISSUES | HIGH | Fix ng_user connection string |
| Redis deduplication | LIVE | OK | Working but data lost on restart |
| Postgres events DB | LIVE | MEDIUM | Running but connection intermittent |

---

## 5. Edition / Currency Status

| Dataset | Last Known Update | Current? | Risk |
|---|---|---|---|
| CPCB water quality | Unknown — static CSV | Unknown | HIGH — water quality changes seasonally |
| CWC river stations | Unknown — static CSV | Unknown | HIGH — river conditions change |
| IWAI terminals | Unknown — static CSV | Unknown | MEDIUM — terminals relatively stable |
| Logistics parks | Unknown — static CSV | Unknown | MEDIUM |
| Urban centers | Unknown — static CSV | Unknown | LOW — urban data changes slowly |

---

## 6. Critical Findings

| # | Finding | Severity | Evidence |
|---|---|---|---|
| FIND-001 | Redis data lost on restart — no volume mounts | CRITICAL | Shravani direct confirmation |
| FIND-002 | ng-core PersistenceStore class missing — service restarting | CRITICAL | Shravani direct confirmation |
| FIND-003 | Postgres connection unstable | HIGH | Shravani direct confirmation |
| FIND-004 | Only 6 locations in entire system | HIGH | Repo analysis |
| FIND-005 | All 5 datasets are static CSVs — no live feeds | HIGH | Repo analysis |
| FIND-006 | No dataset version tracking | MEDIUM | No version fields found |
| FIND-007 | Chandragupta UI ready but not integrated | HIGH | Sir's message |

---

## 7. Overall Health Score

| Dimension | Score (1–5) | Evidence |
|---|---|---|
| Data Completeness | 3/5 | 5 datasets present but static only |
| Data Currency | 2/5 | No version tracking, no live feeds |
| Infrastructure Stability | 2/5 | Redis + ng-core + Postgres all have issues |
| Location Coverage | 2/5 | Only 6 locations in the basin |
| Retrieval Readiness | 3/5 | API working, scoring deterministic |

---

## 8. Evidence Artifacts

| Artifact | Source | Status |
|---|---|---|
| Shravani's direct reply | Shravani Harde | RECEIVED |
| `data_raw/` folder contents | GitHub repo | CONFIRMED |
| `src/signal_trace_layer.py` | GitHub repo | CONFIRMED |
| README.md | GitHub repo | CONFIRMED |

---

*All findings are evidence-based. No assumptions.*
*May 28, 2026*
