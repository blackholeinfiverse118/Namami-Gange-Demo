# NAMAMI GANGE — DATA READINESS AND RISK REPORT
**Sprint:** Dataset Truth Audit + System Mapping
**Auditor:** Nupur Gavane
**Date:** May 28, 2026

---

## 1. Assessment Objective

Determine whether current data and infrastructure can support Namami Gange's core use cases correctly. Identify where the system will fail, give wrong answers, or fail silently.

---

## 2. Capability Assessment

### 2.1 Core Scoring Readiness

| Scenario | Ready? | Risk | Evidence |
|---|---|---|---|
| Score a location for Inland Port | YES | LOW | All 5 factors available, scoring deterministic |
| Score a location for Seaplane | YES | MEDIUM | env_clearance source unconfirmed |
| Score a location for Hub-Spoke | YES | LOW | All factors available |
| Run what-if scenario simulation | YES | LOW | Scenario engine working |
| Multi-scenario comparison | YES | LOW | Sensitivity engine working |
| Replay a past incident | NO | CRITICAL | ng-core restarting — PersistenceStore broken |
| Get live water quality | NO | CRITICAL | Static CSV only — no live CPCB feed |
| Get live flood risk | NO | CRITICAL | Static CSV only — no live CWC feed |
| Deduplicate signals across restart | NO | CRITICAL | Redis has no persistence |

---

### 2.2 Integration Readiness

| Integration | Ready? | Risk | Notes |
|---|---|---|---|
| Nikhil (Map / UI) — GeoJSON consumption | YES | LOW | GeoJSON output confirmed working |
| Chandragupta (UX) — interaction layer | NOT STARTED | HIGH | UI ready per sir but not integrated |
| Ankita Prajapati (Validation) | PARTIAL | MEDIUM | Signal registry and dataset registry ready |
| Tester (Functional Validation) | YES | LOW | 10/10 test suite passing |

---

## 3. High-Risk Failure Points

| ID | Failure | Trigger | Impact | Fix |
|---|---|---|---|---|
| FAIL-001 | System restart loses all dedup state | Redis restart (no volume mounts) | Duplicate signals processed as new — corrupted event history | Add Redis volume mounts |
| FAIL-002 | Replay unavailable | ng-core in restart loop | Operator cannot replay past incidents | Implement PersistenceStore class |
| FAIL-003 | Event storage fails | Postgres connection issue | Events not stored — data loss | Fix ng_user connection string |
| FAIL-004 | Wrong HARD constraint applied | Environmental data source unconfirmed | Location incorrectly REJECTED or incorrectly ACCEPTED | Confirm environmental data sources |
| FAIL-005 | Stale data used for scoring | Static CSV with no version tracking | Score based on outdated water quality / flood data | Add version tracking + live feeds |

---

## 4. Silent Correctness Risks

These are the most dangerous — the system gives an answer confidently but it may be wrong.

| ID | Risk | How It Happens | Detection |
|---|---|---|---|
| SILENT-001 | Water quality score based on stale data | CPCB CSV has no date — could be months old | Add dataset timestamp + staleness check |
| SILENT-002 | Flood constraint not triggered when it should be | CWC flood data is static — doesn't reflect current monsoon | Add real-time CWC integration |
| SILENT-003 | Hard constraint applied based on unverified source | Environmental overlay source unclear | Verify and document all constraint data sources |
| SILENT-004 | Duplicate signal processed after restart | Redis loses dedup state on restart | Add Redis persistence |

---

## 5. Overall Readiness Score

| Dimension | Score (1–10) | Notes |
|---|---|---|
| Scoring Accuracy (static) | 8/10 | Deterministic + traceable on static data |
| Live Data Readiness | 2/10 | No live feeds integrated |
| Infrastructure Stability | 3/10 | Redis + ng-core + Postgres all have issues |
| Replay Capability | 1/10 | ng-core broken |
| Integration Readiness | 5/10 | GeoJSON ready, Chandragupta not started |
| OVERALL | 4/10 | Infrastructure issues block operational use |

---

## 6. Priority Fix List

| Priority | Fix | Fixes Which Risks |
|---|---|---|
| P0 | Add Redis volume mounts | FAIL-001, SILENT-004 |
| P0 | Implement PersistenceStore | FAIL-002 |
| P0 | Fix Postgres connection | FAIL-003 |
| P1 | Confirm environmental data sources | FAIL-004, SILENT-003 |
| P1 | Add dataset version/timestamp tracking | SILENT-001, SILENT-002 |
| P1 | Begin Chandragupta UI integration | Integration gap |
| P2 | Integrate live CPCB API | SILENT-001 |
| P2 | Integrate live CWC flood data | SILENT-002, FAIL-005 |

---

*May 28, 2026 — Built from Shravani's direct reply + repo analysis*
