# Terminal Operations Console UI Specification
## Namami Gange Marine Operations Command Center (MOCC)

This document specifies the interface layout, scheduling algorithms, and API payloads for the Terminal Operations Console. This console enables terminal administrators and port superintendents to schedule berths, monitor jetty utilization, and manage vessel arrivals.

---

## 1. Console Interface Layout

The Terminal Operations Console contains a high-density operational grid: a Gantt-style Jetty Booking timeline at the top, a Terminal Slot Scheduling calendar in the center, and a Terminal Utilization and Arrival list at the bottom.

![Terminal Operations Console Mockup](/C:/Users/PIXEL/.gemini/antigravity-ide/brain/f29da9f4-5d17-4113-ae2d-692085a042b3/terminal_console_1782125028506.png)

---

## 2. Core Scheduling Components

### A. Jetty Booking Gantt Timeline
* **Visual Representation**: Horizontal bars representing booked durations for individual berths (Berth 1, Berth 2, Berth 3).
* **Interactions**: Drag-and-drop bars to re-allocate berth timings, click a bar to view loading manifests.
* **Color States**:
  * **Cyan (Loading / Active)**: Vessel currently docked and actively loading/unloading.
  * **Amber (Reserved / Scheduled)**: Confirmed booking.
  * **Red (Overrun / Delayed)**: Vessel has exceeded its slot allocation time.

### B. Vessel Arrivals Queue
Tracks vessels approaching terminal limits:
* **Pre-Arrival Notification**: Triggered when a vessel crosses the 5km geofence radius.
* **Pilotage Assignment**: Button to assign a pilot to guide the incoming vessel to its designated berth.

| Vessel Name | Status | Est. Arrival (ETA) | Assigned Berth | Cargo Type | Pilot Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MV Ganga-Vahini** | Approaching (3km) | 2026-06-22 18:30 | Berth 1 | Fly Ash | `BOARDED` |
| **MV Saryu-Courier**| Anchored (Outer) | 2026-06-22 19:45 | Berth 3 | Grain Bulk | `PENDING` |
| **MV Kashi-Pride**  | En Route (12km)  | 2026-06-23 04:00 | Berth 2 | Containers | `NOT_ASSIGNED`|

### C. Terminal Utilization Heatmap & KPIs
* **KPI Metrics**:
  * *Avg Turnaround Time*: Core metric measuring hours from dock to undock.
  * *Crane Utilization Rate*: Operational percentage of shore-based loading cranes.
  * *Yard Saturation*: Bar chart showing volume stored compared to capacity limits.
* **Congestion Heatmap**: Displays terminal utilization levels over a rolling 24-hour cycle to highlight bottleneck hours (usually shifts matching truck arrivals).

---

## 3. Slot Reservation Collision Logic

The UI incorporates automatic validation to prevent double-booking:
1. **Overlap Check**: If a booking is scheduled for `Berth X` that overlaps with an existing reservation, the slot turns bright red.
2. **Draft Alignment**: Checks the vessel's loaded draft against the berth's dredge limit. (e.g., MV Class VII cannot be booked at Berth 3 if Berth 3's maximum depth is only 2.0m).

---

## 4. API Data Specifications

### A. Create Jetty Booking / Slot Reservation
**Endpoint**: `POST /api/terminal/booking`  
**JSON Payload**:
```json
{
  "booking_id": "BKG-2026-099",
  "terminal_id": "TERM-VNS-MMT",
  "berth_id": "BERTH-01",
  "vessel_id": "VES-NW1-088",
  "cargo_manifest": {
    "commodity": "FLY_ASH",
    "target_volume_tons": 1500
  },
  "scheduled_arrival": "2026-06-22T18:30:00Z",
  "scheduled_departure": "2026-06-23T06:30:00Z"
}
```

### B. Fetch Terminal Capacity & Utilization
**Endpoint**: `GET /api/terminal/utilization`  
**JSON Structure**:
```json
{
  "status": "success",
  "timestamp": "2026-06-22T16:30:00Z",
  "terminals": [
    {
      "terminal_id": "TERM-VNS-MMT",
      "name": "Varanasi Multi-Modal Terminal",
      "total_berths": 3,
      "active_berths_count": 2,
      "yard_capacity_tons": 50000,
      "yard_utilized_tons": 27000,
      "crane_operational_count": 4,
      "crane_total_count": 4,
      "congestion_level": "LOW",
      "hourly_utilization_profile": [40, 45, 50, 75, 80, 85, 70, 60, 50, 45, 40, 40]
    },
    {
      "terminal_id": "TERM-PAT-GAI",
      "name": "Patna Gaighat Terminal",
      "total_berths": 2,
      "active_berths_count": 2,
      "yard_capacity_tons": 30000,
      "yard_utilized_tons": 24600,
      "crane_operational_count": 2,
      "crane_total_count": 3,
      "congestion_level": "HIGH",
      "hourly_utilization_profile": [60, 70, 80, 90, 95, 95, 90, 85, 80, 75, 70, 65]
    }
  ]
}
```
