# NAMAMI GANGE — DATA ADDITION PLAN
**Sprint:** Dataset Truth Audit + System Mapping
**Auditor:** Nupur Gavane
**Date:** May 28, 2026

> Principle: No blind additions. Every item is evidence-based and prioritized by impact.

---

## Priority Legend

| Priority | Criteria |
|---|---|
|  P0 | Blocks correct system operation. Fix immediately. |
|  P1 | Significant gap. Add this week. |
|  P2 | Important for completeness. Next sprint. |
|  P3 | Nice to have. Backlog. |

---

## SECTION 1 — Infrastructure Fixes (Must Do First)

These are not data additions — they are infrastructure gaps that prevent existing data from working correctly.

| # | Fix | Why Critical | Owner | Priority |
|---|---|---|---|---|
| INFRA-001 | Add Redis volume mounts to docker-compose | Data lost on every restart — deduplication broken after restart | Shravani | P0 |
| INFRA-002 | Implement PersistenceStore class in ng-core | Service in restart loop — replay/persistence completely broken | Shravani | P0 |
| INFRA-003 | Fix Postgres ng_user connection string | Event storage intermittently failing | Shravani | P0 |
| INFRA-004 | Begin Chandragupta UI integration | Sir confirmed UI is ready — integration not started | Nupur + Chandragupta | P1 |

---

## SECTION 2 — Data Additions

###  P0 — Critical (Add Immediately)

| # | Item to Add | Source | Why Critical |
|---|---|---|---|
| ADD-001 | Expand location coverage — 20+ additional Ganga basin sites | Field survey / IWAI data | Only 6 locations in entire system — not representative |
| ADD-002 | Confirm environmental data sources — wetland, flood zone, env clearance | MoEF / SEIAA / NRSC | These drive HARD constraints but their source is unconfirmed |

###  P1 — High Priority (This Week)

| # | Item to Add | Source | Why Important |
|---|---|---|---|
| ADD-003 | Dataset version/edition fields on all 5 CSVs | Internal metadata | Cannot detect outdated data without version tracking |
| ADD-004 | CPCB historical data — last 3 years | CPCB open data portal | Water quality is seasonal — point-in-time snapshot may be misleading |
| ADD-005 | CWC flood risk historical data | CWC open data | Flood constraint needs historical context |

### P2 — Medium Priority (Next Sprint)

| # | Item to Add | Source | Notes |
|---|---|---|---|
| ADD-006 | Real-time CPCB API integration | https://cpcb.nic.in / Jal Shakti portal | Replace static CSV with live feed |
| ADD-007 | Real-time CWC river data API | https://cwc.gov.in | Replace static CSV with live feed |
| ADD-008 | IWAI real-time vessel traffic data | IWAI VTS system | Traffic_potential currently static |
| ADD-009 | 50+ additional basin locations | IWAI + district data | Current 6-location coverage is too narrow |

### P3 — Low Priority (Backlog)

| # | Item | Source | Notes |
|---|---|---|---|
| ADD-010 | Satellite imagery overlay | ISRO Bhuvan | Future visual validation layer |
| ADD-011 | Groundwater data | CGWB | Additional environmental factor |
| ADD-012 | Port Authority data | Major Port Trusts | Supplement IWAI terminal data |

---

## SECTION 3 — Schema Gaps

| # | Gap | Impact | Fix | Priority |
|---|---|---|---|---|
| SCHEMA-001 | No `dataset_version` field on any dataset | Cannot detect if data is outdated | Add version + last_updated to all CSV headers | P0 |
| SCHEMA-002 | Environmental data has no confirmed source | HARD constraints may be wrong | Confirm and document source for wetland/flood/clearance data | P0 |
| SCHEMA-003 | No timestamp on Redis events after restart | Events post-restart have no dedup history | Fix Redis persistence first, then add timestamp validation | P0 |

---

## SECTION 4 — Today's P0 Action List

| # | Action | Owner | Deadline |
|---|---|---|---|
| 1 | Add Redis volume mounts | Shravani | Today |
| 2 | Implement PersistenceStore class | Shravani | Today |
| 3 | Fix Postgres connection string | Shravani | Today |
| 4 | Confirm environmental data sources | Nupur + Shravani | Today |
| 5 | Start Chandragupta UI integration | Nupur + Chandragupta | Today |

---

*May 28, 2026*
