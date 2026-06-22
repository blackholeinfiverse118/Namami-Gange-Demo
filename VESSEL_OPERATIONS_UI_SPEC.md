# Vessel Operations Console UI Specification
## Namami Gange Marine Operations Command Center (MOCC)

This specification defines the UI layout, component behavior, data structures, and user actions for the Vessel Operations Console. This console enables real-time tracking of commercial vessels, barges, and passenger ferries along the National Waterways (NW-1).

---

## 1. Console Interface Layout

The Vessel Operations Console features a split-pane layout: a geospatial vessel tracking sub-map on the left, an interactive list of active transits in the center, and a contextual Vessel Detail panel on the right.

![Vessel Operations Console Mockup](/C:/Users/PIXEL/.gemini/antigravity-ide/brain/f29da9f4-5d17-4113-ae2d-692085a042b3/vessel_console_1782124982684.png)

---

## 2. UI Workspace Elements

### A. Contextual KPI Ribbon
* **Active Transits**: Count of vessels with status `UNDERWAY`.
* **Vessel Safety Alerts**: Count of vessels triggering draft warnings or course deviations.
* **Class Distribution Summary**: Fast sparklines showing the count of Class I through Class VII vessels.

### B. Interactive Transits Directory (Table View)

| Vessel Name | Class | Status | Route (Origin → Dest) | Speed | ETA | Alerts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| MV Ganga-Vahini | Class III | `UNDERWAY` | Varanasi → Patna | 8.2 kts | 2026-06-23 18:30 | None |
| MV Hooghly-Pride | Class V | `MOORED` | Kolkata → Haldia | 0.0 kts | -- | None |
| MV Saryu-Courier | Class I | `UNDERWAY` | Patna → Prayagraj | 6.5 kts | 2026-06-24 09:15 | `DRAFT_WARN` |
| MV Bhagirathi-1 | Class VII | `UNDERWAY` | Haldia → Kolkata | 11.2 kts | 2026-06-22 21:00 | `SPEED_VIOL` |

### C. Contextual Vessel Detail Panel (Right Pane)
When an operator clicks a vessel row, the right panel updates with:
* **Vessel Specifications**: Length overall (LOA), Beam width, Draft (operational and design).
* **Cargo Load State**: Commodity type, tonnage, and percentage utilization.
* **Under-Keel Clearance (UKC) Monitor**: A vertical bar chart comparing the river draft depth (via RIS sensor) and the vessel's current draft depth.
* **Safety Alert Indicators**: Visual warning flags with manual action overrides.

---

## 3. Vessel Class Standards (IWAI Guidelines)

The console categorizes vessels according to IWAI standards for NW-1:

| Vessel Class | Max LOA (m) | Max Beam (m) | Max Draft (m) | Minimum Safe River Depth Required |
| :--- | :--- | :--- | :--- | :--- |
| **Class I** | 45 | 8.0 | 1.2 | 1.5m |
| **Class II** | 60 | 9.0 | 1.5 | 1.8m |
| **Class III** | 80 | 12.0 | 1.8 | 2.2m |
| **Class IV** | 100 | 12.0 | 2.0 | 2.5m |
| **Class V** | 130 | 15.0 | 2.2 | 2.8m |
| **Class VI** | 150 | 18.0 | 2.5 | 3.2m |
| **Class VII** | 170 | 22.0 | 2.8 | 3.5m |

---

## 4. Operational Alert Conditions & Thresholds

The UI generates automatic warnings based on ingested telemetry:

1. **Under-Keel Clearance Warning (`DRAFT_WARN`)**:
   * *Logic*: `(River Depth - Vessel Operational Draft) < 0.4 meters`
   * *UI Output*: Glowing red row outline, blinking hazard icon, detail panel shows water draft vs. vessel draft layout.
2. **Speed Limit Violation (`SPEED_VIOL`)**:
   * *Logic*: `Vessel Speed > Speed Limit Zone` (Standard zone limit: 10 knots; Eco-sensitive zones: 6 knots)
   * *UI Output*: Glowing orange badge on Speed cell.
3. **Course Deviation Warning (`ROUTE_DEV`)**:
   * *Logic*: `Distance from Designated Navigation Channel Corridor > 50 meters`
   * *UI Output*: Vessel path on geospatial map turns red.

---

## 5. API Data Specifications

### A. Fetch Active Transits API Payload
**Endpoint**: `GET /api/vessel/transits`  
**JSON Structure**:
```json
{
  "status": "success",
  "timestamp": "2026-06-22T16:15:00Z",
  "count": 12,
  "transits": [
    {
      "vessel_id": "VES-NW1-088",
      "name": "MV Ganga-Vahini",
      "class": "Class III",
      "status": "UNDERWAY",
      "dimensions": { "loa": 78.5, "beam": 11.8, "current_draft": 1.6 },
      "route": {
        "origin_id": "VNS-TERM",
        "origin_name": "Varanasi Multi-Modal",
        "dest_id": "PAT-TERM",
        "dest_name": "Patna Gaighat",
        "total_distance_km": 240
      },
      "telemetry": {
        "lat": 25.4521,
        "lng": 84.1205,
        "sog_kts": 8.2,
        "cog_deg": 112.5,
        "under_keel_clearance_m": 0.9
      },
      "eta": "2026-06-23T18:30:00Z",
      "alerts": []
    },
    {
      "vessel_id": "VES-NW1-042",
      "name": "MV Saryu-Courier",
      "class": "Class I",
      "status": "UNDERWAY",
      "dimensions": { "loa": 42.0, "beam": 7.5, "current_draft": 1.3 },
      "route": {
        "origin_id": "PAT-TERM",
        "origin_name": "Patna Gaighat",
        "dest_id": "PRY-TERM",
        "dest_name": "Prayagraj Passenger Jetty",
        "total_distance_km": 360
      },
      "telemetry": {
        "lat": 25.5123,
        "lng": 83.2144,
        "sog_kts": 6.5,
        "cog_deg": 284.1,
        "under_keel_clearance_m": 0.2
      },
      "eta": "2026-06-24T09:15:00Z",
      "alerts": ["DRAFT_WARN"]
    }
  ]
}
```

### B. Operator Override Alert Dispatch Payload
**Endpoint**: `POST /api/vessel/override`  
**JSON Structure**:
```json
{
  "operator_id": "OP-331",
  "vessel_id": "VES-NW1-042",
  "override_action": "DISPATCH_SLOW_ADVISORY",
  "override_notes": "Siltation zone detected near Buxar. Instructing vessel to drop speed to 4.0 knots.",
  "timestamp": "2026-06-22T16:16:30Z"
}
```
