# Voyage Planning UI Specification
## Namami Gange Marine Operations Command Center (MOCC)

This document defines the UI layout, workflow, constraint verification engines, and API specifications for the Voyage Planning Console. This console allows logistics coordinators to draft, analyze, and optimize voyages across National Waterway-1.

---

## 1. Console Interface Layout

The Voyage Planning screen utilizes a structured wizard interface on the left, a dynamic navigational routing map in the center, and a comprehensive Route Analytics panel on the right.

![Voyage Planning UI Mockup](/C:/Users/PIXEL/.gemini/antigravity-ide/brain/f29da9f4-5d17-4113-ae2d-692085a042b3/voyage_planner_1782125012271.png)

---

## 2. Dynamic Planning Workflow

The operator configures a new voyage through a 4-step progressive wizard:

```
[ Step 1: Terminals ] ---> [ Step 2: Vessel Select ] ---> [ Step 3: Cargo Details ] ---> [ Step 4: Run Analytics ]
```

### Step 1: Select Terminals (Origin & Destination)
* **Input**: Searchable dropdowns connecting to the terminal registry (e.g., Origin: *Varanasi MMT*, Destination: *Haldia Port*).
* **Interactions**: Map automatically displays the base straight-line waterway path and highlights key intermediate stations.

### Step 2: Select Vessel
* **Input**: Dropdown of active or idle vessels from the Marine MasterDB.
* **UI Feedback**: Selecting a vessel dynamically imports its length, width, and draft parameters, comparing them against current channel limits.

### Step 3: Cargo Details
* **Input**: Select commodity type (e.g., Fly Ash) and input tonnage.
* **UI Feedback**: System calculates the expected operational draft of the vessel under load:
  * `Loaded Draft = Vessel Light Draft + (Cargo Tonnage / Tons-Per-Centimeter Immersion)`

### Step 4: Run Optimization & Path Assessment
* **Action**: Operator clicks "OPTIMIZE ROUTE".
* **UI Output**: System queries the Voyage Engine, highlighting the optimal pathway, any alternate routing corridors, and active constraints.

---

## 3. Constraint-Constrained Routing Engine

The panel on the right displays validation results across three constraint categories:

### A. Draft Constraints (Water Depth)
* **Check**: Compares `Loaded Draft` against CWC sensor depths in all intermediate segments.
* **UI Feedback**: Blinking warning badge if safety clearance is less than 0.4 meters (e.g., "Critical Draft Bottleneck: Buxar Segment (Depth: 2.1m, Loaded Draft: 1.9m)").

### B. Vertical Clearance (Bridges & Transmission Lines)
* **Check**: Compares `Vessel Mast Height` against the air drafts of bridges along the path based on live river stage measurements.
* **UI Feedback**: Warning badge if clearances are compromised:
  * `Air Draft = Bridge Underside Elevation - Current River Level`

### C. Environmental & Ecological Restrictions
* **Check**: Flags if the path intersects protected zones (e.g., Vikramshila Gangetic Dolphin Sanctuary).
* **UI Feedback**: Warning icon displaying mandatory speed reductions (e.g., "Eco-Zone: Limit Speed to 6 Knots").

---

## 4. Alternate Path Analysis

The console displays comparative metrics for alternate routes:

| Route Option | Distance (km) | Est. Duration | Lock Wait Times | Risk Score | Recommended? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Path A (Deep Channel)** | 620 | 54 Hours | 3.5 Hours (Farakka) | 12% | **YES (Recommended)**|
| **Path B (Shallow Bypass)**| 580 | 62 Hours | 0.0 Hours | 48% (Siltation risk)| **NO** |

---

## 5. API Data Specifications

### A. Voyage Optimization Request
**Endpoint**: `POST /api/voyage/optimize`  
**JSON Payload**:
```json
{
  "origin_terminal_id": "VNS-TERM",
  "dest_terminal_id": "HAL-TERM",
  "vessel_id": "VES-NW1-088",
  "cargo": {
    "commodity": "FLY_ASH",
    "tonnage": 1800
  },
  "safety_margins": {
    "min_under_keel_clearance_m": 0.4,
    "min_air_draft_m": 1.0
  }
}
```

### B. Voyage Optimization Response
**Endpoint**: `POST /api/voyage/optimize` (Response)  
**JSON Structure**:
```json
{
  "status": "success",
  "calculation_time_ms": 142,
  "voyage_plan": {
    "recommended_path": {
      "path_id": "PATH-VNS-HAL-A",
      "distance_km": 612.4,
      "estimated_duration_hours": 52.5,
      "fuel_consumption_liters": 4800,
      "lock_wait_estimated_mins": 210,
      "risk_profile": {
        "overall_risk_level": "LOW",
        "siltation_risk_percent": 15.0,
        "eco_zones_crossed": ["Dolphin Sanctuary Varanasi"]
      },
      "segments": [
        {
          "segment_name": "Varanasi to Patna",
          "min_depth_found_m": 3.1,
          "clearance_check": "PASS",
          "speed_limit_kts": 8.0
        },
        {
          "segment_name": "Patna to Farakka",
          "min_depth_found_m": 2.6,
          "clearance_check": "PASS",
          "speed_limit_kts": 8.0
        }
      ]
    },
    "alternate_paths": [
      {
        "path_id": "PATH-VNS-HAL-B",
        "distance_km": 595.0,
        "estimated_duration_hours": 60.2,
        "lock_wait_estimated_mins": 0,
        "risk_profile": {
          "overall_risk_level": "HIGH",
          "siltation_risk_percent": 74.0,
          "eco_zones_crossed": []
        }
      }
    ]
  }
}
```
