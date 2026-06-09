# GeoJSON Output Proof
**Project:** NICAI -- Namami Gange Intelligence Convergence Sprint
**Date:** 2026-05-26
**Author:** Nupur Gavane -- Build Lead
**Status:** VERIFIED

---

## What This Proves

This document proves the intelligence engine produces valid, map-ready GeoJSON
output from real scored results. The GeoJSON is consumed directly by the
visualization layer (Nikhil) for map rendering. Every feature contains all
required properties: score, level, color, delta, reasoning, constraints, and
trace summary.

---

## Command Run

```
cd src
python geo_output_builder.py
```

---

## GeoJSON Baseline Layer Output

Two locations scored and output as GeoJSON FeatureCollection:

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "layer_type": "baseline",
    "model_type": "inland_port",
    "feature_count": 2,
    "legend": [
      { "label": "HIGH",     "color": "#2ecc71", "description": "Score >= threshold -- suitable" },
      { "label": "MEDIUM",   "color": "#f39c12", "description": "Score in mid-range -- conditionally suitable" },
      { "label": "LOW",      "color": "#e74c3c", "description": "Score below threshold -- not recommended" },
      { "label": "REJECTED", "color": "#7f8c8d", "description": "Hard constraint triggered -- infrastructure prohibited" }
    ]
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [82.9739, 25.3176]
      },
      "properties": {
        "location_id": "varanasi_terminal",
        "model_type": "inland_port",
        "score": 73.75,
        "level": "MEDIUM",
        "color": "#f39c12",
        "delta": null,
        "reasoning": "Level: MEDIUM | Score: 73.75 | Key factors: flood_constraint, wetland_constraint, env_clearance",
        "constraints": { "hard": [], "soft": [], "overridden": [] },
        "scoring_model": {
          "weights": {
            "river_stability": 0.25, "terminal_proximity": 0.2,
            "logistics_access": 0.2, "water_quality": 0.2, "traffic_potential": 0.15
          },
          "thresholds": { "HIGH": 75, "MEDIUM": 50, "LOW": 0 },
          "formula": "score = weighted sum of factor scores minus soft penalties; HARD constraints -> REJECT"
        },
        "trace_summary": {
          "contributing_signals": [
            "CPCB_WQI_v1", "CWC_DEPTH_v1", "CWC_RIV_STAB_v1",
            "ENV_CLEAR_v1", "ENV_FLOOD_v1", "ENV_WETLAND_v1",
            "IWAI_LOG_v1", "IWAI_TERM_v1", "IWAI_TRAF_v1"
          ]
        }
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [85.1376, 25.5941]
      },
      "properties": {
        "location_id": "patna_river_port",
        "model_type": "inland_port",
        "score": 75.25,
        "level": "HIGH",
        "color": "#2ecc71",
        "delta": null,
        "reasoning": "Level: HIGH | Score: 75.25 | Key factors: flood_constraint, wetland_constraint, env_clearance",
        "constraints": { "hard": [], "soft": [], "overridden": [] },
        "trace_summary": {
          "contributing_signals": [
            "CPCB_WQI_v1", "CWC_DEPTH_v1", "CWC_RIV_STAB_v1",
            "ENV_CLEAR_v1", "ENV_FLOOD_v1", "ENV_WETLAND_v1",
            "IWAI_LOG_v1", "IWAI_TERM_v1", "IWAI_TRAF_v1"
          ]
        }
      }
    }
  ]
}
```

---

## Legend Structure Output

```json
{
  "level_legend": [
    { "label": "HIGH",     "color": "#2ecc71", "description": "Score >= threshold -- suitable" },
    { "label": "MEDIUM",   "color": "#f39c12", "description": "Score in mid-range -- conditionally suitable" },
    { "label": "LOW",      "color": "#e74c3c", "description": "Score below threshold -- not recommended" },
    { "label": "REJECTED", "color": "#7f8c8d", "description": "Hard constraint triggered -- infrastructure prohibited" }
  ],
  "delta_legend": [
    { "label": "IMPROVED",  "color": "#1abc9c", "description": "Score increased under scenario" },
    { "label": "DECLINED",  "color": "#e67e22", "description": "Score decreased under scenario" },
    { "label": "UNCHANGED", "color": "#95a5a6", "description": "Score unchanged under scenario" }
  ],
  "color_reference": {
    "HIGH":      "#2ecc71",
    "MEDIUM":    "#f39c12",
    "LOW":       "#e74c3c",
    "REJECTED":  "#7f8c8d",
    "IMPROVED":  "#1abc9c",
    "DECLINED":  "#e67e22",
    "UNCHANGED": "#95a5a6"
  }
}
```

---

## GeoJSON Contract Verification

Every feature in the output contains all required properties for map consumption:

| Required Property | Present | Value (Varanasi) | Value (Patna) |
|---|---|---|---|
| location_id | YES | varanasi_terminal | patna_river_port |
| model_type | YES | inland_port | inland_port |
| score | YES | 73.75 | 75.25 |
| level | YES | MEDIUM | HIGH |
| color | YES | #f39c12 (amber) | #2ecc71 (green) |
| delta | YES | null (baseline) | null (baseline) |
| reasoning | YES | present | present |
| constraints | YES | hard=[], soft=[], overridden=[] | hard=[], soft=[], overridden=[] |
| trace_summary | YES | 9 signals | 9 signals |
| geometry.coordinates | YES | [82.9739, 25.3176] | [85.1376, 25.5941] |

---

## Three-Layer Architecture

The geo_output_builder.py produces three layers for map visualization:

| Layer | Purpose | Color basis |
|---|---|---|
| baseline | Initial map render -- scores without scenario | Level color (HIGH=green, MEDIUM=amber, LOW=red, REJECTED=grey) |
| scenario | Scores under modified weights/constraints | Level color |
| delta | Change visualization between baseline and scenario | Direction color (IMPROVED=teal, DECLINED=orange, UNCHANGED=grey) |

The baseline layer was verified in this proof run.
Scenario and delta layers are generated via POST /simulate endpoint.

---

## Coordinate Verification

Both output coordinates are verified Ganga Basin locations:

| Location | Longitude | Latitude | City |
|---|---|---|---|
| varanasi_terminal | 82.9739 | 25.3176 | Varanasi, Uttar Pradesh |
| patna_river_port | 85.1376 | 25.5941 | Patna, Bihar |

Both coordinates fall within India bounding box (lat 6.0-37.0, lon 68.0-97.5).
Both are valid Ganga Basin locations on National Waterway 1 (NW-1).

---

## Summary

| Verification | Result |
|---|---|
| GeoJSON produced without errors | PASS |
| FeatureCollection format valid | PASS |
| All required properties present | PASS |
| Coordinates are real Ganga Basin locations | PASS |
| Color mapping matches level | PASS |
| Legend structure complete | PASS |
| Signal trace included in each feature | PASS |
| Constraint block included in each feature | PASS |

**Conclusion:** The engine produces valid, map-ready GeoJSON output.
The output is ready for direct consumption by the visualization layer.
No mock data. Real coordinates, real scores, real signal traces.
