# RIS Command Center Operations Specification
## Namami Gange Marine Operations Command Center (MOCC)

This document specifies the operational design, interface protocols, and safety warning frameworks for the River Information Services (RIS) Command Center. This center implements standard features inspired by the European RIS framework (Rhine RIS, Danube RIS) tailored for National Waterway-1 (Ganga-Bhagirathi-Hooghly river system).

---

## 1. RIS Standard Alignment

To support safe inland navigation, this console conforms to the four core pillars of the European RIS standards:
1. **Inland ECDIS**: Electronic Chart Display and Information Systems showing bathymetric depths, fairways, and lock coordinates.
2. **Notices to Skippers (NtS / NtM)**: Standardized digital notifications covering waterway blocks, weather, and water level changes.
3. **Electronic Ship Reporting (ERI)**: Digital voyage notifications detailing passenger lists, toxic cargo manifests, and ship properties.
4. **Vessel Tracking & Tracing (Inland AIS)**: Shore-based transponder receivers showing heading, speed over ground, and operational status.

---

## 2. UI Workspace Layout & Widgets

The RIS interface displays safety-critical, real-time hydrological and operational alerts in a high-density matrix.

### A. Water Levels & Hydrological Gauges (Real-Time)
Provides a live view of water level variations from CWC gauge stations compared to established chart datums:

| Gauge Station | River Mile (km) | Current Level (m) | Chart Datum (m) | Safety Margin (m) | Trend |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kanpur (U/S)** | 1,020 | +1.8 | +2.0 | -0.2 (Critical) | `FALLING ↘` |
| **Prayagraj Sangam**| 910 | +2.4 | +2.2 | +0.2 (Low Water)| `STABLE →` |
| **Varanasi MMT** | 790 | +3.8 | +3.0 | +0.8 (Optimal) | `RISING ↗` |
| **Patna Sahib** | 560 | +3.2 | +2.8 | +0.4 (Optimal) | `STABLE →` |
| **Farakka Pool** | 310 | +4.9 | +4.0 | +0.9 (Optimal) | `RISING ↗` |

### B. Notice to Mariners (NtM) / Notices to Skippers (NtS)
Digital bulletin board with 1-click broadcast capabilities:
* **Warning IDs**: Code structures based on European standard (e.g., `IN-NW1-NtM-2026-088`).
* **Categorizations**: `WATERWAY_BLOCK`, `WEATHER_WARN`, `DREDGER_OPERATING`, `SHAL_RESTRICT`.
* **Urgency Levels**: `IMMEDIATE` (Red blinking alert), `URGENT` (Amber alert), `ROUTINE` (Info gray).

### C. Lock & Gate Control Status
Enables operators to monitor transit schedules at key lock structures (such as Farakka Lock):
* **Farakka Lock Chamber #1**:
  * *Gate State*: `CLOSED`
  * *Water Level Differential*: `0.85m`
  * *Lock Queue*: 3 barges waiting (MV Hooghly-Pride, MV Ganga-Carrier, MV Prayag-Express)
  * *Operational Mode*: `AUTOMATIC_SCADA`
* **Farakka Lock Chamber #2**:
  * *Gate State*: `OPENING`
  * *Water Level Differential*: `0.05m`
  * *Active Transit*: MV Saryu-Courier
  * *Operational Mode*: `MANUAL_OVERRIDE`

### D. Navigation Restrictions Index
Displays live parameters regarding channel limitations:
* **Vertical Bridge Clearance**: Live sensor measurements of bridge structures (e.g., Mahatma Gandhi Setu, Patna) to prevent super-structure collisions.
* **Shoal Formations**: Siltation alerts detailing localized sandbars (e.g., near Kahalgaon, Bihar).

---

## 3. Standard Notice to Mariners (NtM) JSON Schema

The system broadcasts all navigation warnings using a JSON format compatible with European NtS XML schemas:

**Endpoint**: `POST /api/ris/notice/publish`  
**JSON Payload**:
```json
{
  "message_id": "IN-NW1-NtS-2212",
  "issuer": "IWAI RIS Varanasi Branch",
  "issue_date": "2026-06-22T16:25:00Z",
  "validity": {
    "start_date": "2026-06-22T18:00:00Z",
    "end_date": "2026-06-25T18:00:00Z"
  },
  "waterway_section": {
    "waterway": "NW-1",
    "start_km": 720,
    "end_km": 740,
    "direction": "ALL"
  },
  "notice_type": "DREDGING_NOTICE",
  "urgency": "URGENT",
  "description": "Dredger 'Ganga-Silt-04' operating in mid-channel. Safe passage corridor shifted 30m south. Max speed limit 4 knots for all vessels Class III and above.",
  "channel_restrictions": {
    "max_draft_m": 1.9,
    "max_speed_kts": 4.0,
    "vertical_clearance_limit_m": null
  }
}
```

---

## 4. Hydrological Status Ingestion Feed

**Endpoint**: `GET /api/ris/hydro/status`  
**JSON Payload**:
```json
{
  "status": "success",
  "timestamp": "2026-06-22T16:26:00Z",
  "gauge_readings": [
    {
      "station_id": "STN-CWC-VNS",
      "station_name": "Varanasi CWC Gauge",
      "water_level_m": 3.82,
      "discharge_rate_cumecs": 1420.5,
      "flow_velocity_mps": 1.25,
      "siltation_index": "LOW",
      "water_temperature_c": 28.5
    },
    {
      "station_id": "STN-CWC-KAN",
      "station_name": "Kanpur Downstream CWC",
      "water_level_m": 1.84,
      "discharge_rate_cumecs": 450.2,
      "flow_velocity_mps": 0.82,
      "siltation_index": "HIGH_WARNING",
      "water_temperature_c": 29.1
    }
  ]
}
```
