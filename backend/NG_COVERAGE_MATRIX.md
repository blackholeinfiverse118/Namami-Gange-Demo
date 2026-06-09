# NAMAMI GANGE — COVERAGE MATRIX
**Sprint:** Dataset Truth Audit + System Mapping
**Auditor:** Nupur Gavane
**Date:** May 28, 2026

---

## How to Read This Matrix

| Symbol | Meaning |
|---|---|
| CONFIRMED | Full coverage — data present and scoring works |
| PARTIAL | Data present but gaps or quality issues |
| MISSING | No data |
| CRITICAL | Critical risk |
| HIGH | High risk |
| MEDIUM | Medium risk |
| LOW | Low risk |

---

## SECTION A — Location Coverage

| Location | River | Models Scored | Inland Port | Seaplane | Hub-Spoke | Data Quality | Risk |
|---|---|---|---|---|---|---|---|
| `patna_river_port` | Ganga (Patna) | All 3 | HIGH (75.25) | CONFIRMED | CONFIRMED | Good | LOW |
| `varanasi_terminal` | Ganga (Varanasi) | All 3 | MEDIUM (61.6) | CONFIRMED | CONFIRMED | Good | MEDIUM |
| `allahabad_confluence` | Ganga+Yamuna | All 3 | LOW (44.8) | CONFIRMED | CONFIRMED | Good | MEDIUM |
| `kanpur_industrial_zone` | Ganga (Kanpur) | All 3 | REJECTED | REJECTED | REJECTED | Good | LOW (correctly rejected) |
| `farakka_wetland` | Ganga (Farakka) | All 3 | REJECTED | REJECTED | REJECTED | Good | LOW (correctly rejected) |
| `sultanganj_node` | Ganga (Sultanganj) | Partial | MEDIUM | CONFIRMED | CONFIRMED | Good | MEDIUM |

**Coverage:** 6 locations out of hundreds of potential Ganga basin sites.

---

## SECTION B — Factor Coverage by Dataset

| Factor | Dataset Source | Coverage Status | Quality | Risk |
|---|---|---|---|---|
| river_stability | CWC river stations | COVERED | Static only | HIGH — seasonal changes not captured |
| water_quality | CPCB water quality | COVERED | Static only | HIGH — pollution levels change |
| terminal_proximity | IWAI terminals NW1 | COVERED | Stable | LOW |
| logistics_access | IWAI + logistics parks | COVERED | Stable | LOW |
| traffic_potential | IWAI terminals | COVERED | Static only | MEDIUM |
| urban_proximity | Urban centers | COVERED | Stable | LOW |
| flow_turbulence | CWC river stations | COVERED | Static only | HIGH |
| env_clearance | Environmental overlay | PARTIAL | Source unclear | HIGH |
| wetland_zone | Environmental overlay | PARTIAL | Source unclear | CRITICAL — HARD constraint |
| flood_zone | Environmental overlay | PARTIAL | Source unclear | CRITICAL — HARD constraint |

---

## SECTION C — Model Coverage

| Model | Factors Required | Factors Available | Coverage | Can Score? |
|---|---|---|---|---|
| Inland Port | river_stability, terminal_proximity, logistics_access, water_quality, traffic_potential | All 5 | 5/5 | YES |
| Seaplane | flow_turbulence, water_surface_quality, traffic_density, urban_proximity, env_clearance | 4/5 (env_clearance partial) | 4.5/5 | YES (with caveat) |
| Hub-Spoke | multi_node_proximity, logistics_park_quality, terminal_density, connectivity, urban_market_access | All 5 | 5/5 | YES |

---

## SECTION D — Infrastructure Coverage

| Service | Data It Holds | Current Status | Can System Function Without It? |
|---|---|---|---|
| Redis dedup | Deduplication state | LIVE but no persistence | Yes but duplicate signals pass through on restart |
| Postgres events | Event history | Connection issues | PARTIAL — new events may fail to store |
| ng-core | Replay + persistence | RESTARTING | NO — replay unavailable |

---

## SECTION E — Can the System Answer Correctly?

| Question | Can Answer? | Confidence | Risk |
|---|---|---|---|
| "Score this location for inland port" | YES | High | LOW |
| "Why was Kanpur rejected?" | YES | High | LOW |
| "What's the water quality today?" | NO | None | CRITICAL — static data only |
| "Is there a flood risk right now?" | NO | None | CRITICAL — static data only |
| "Replay last week's incident" | NO | None | CRITICAL — ng-core down |
| "Run a what-if scenario" | YES | High | LOW |
| "Compare 3 scenarios" | YES | High | LOW |

---

## SECTION F — Gap Summary

| Type | Total Expected | Present | Partial | Missing |
|---|---|---|---|---|
| Core datasets | 5 | 5 | 0 | 0 |
| Infrastructure services | 3 | 1 fully working | 2 degraded | 0 |
| Live data feeds | 5 | 0 | 0 | 5 |
| Locations in system | ~100+ ideal | 6 | 0 | ~94+ |
| Environmental data sources | 3 | 0 confirmed | 3 | 0 |

---

*May 28, 2026 — Built from Shravani's direct reply + repo analysis*
