# Cargo Operations Console UI Specification
## Namami Gange Marine Operations Command Center (MOCC)

This specification defines the UI layout, data models, interaction patterns, and alert indicators for the Cargo Operations Console. The Cargo Operations Console allows logistics planners to optimize cargo corridors, track terminal freight capacities, and minimize congestion.

---

## 1. Console Interface Layout

The Cargo Operations Console provides a logistics-focused interface that overlays cargo flow densities directly onto the National Waterway-1 grid. The interface consists of a corridor flow density map, a cargo type throughput breakdown, a terminal allocation index, and a bottleneck list.

![Cargo Operations Console Mockup](/C:/Users/PIXEL/.gemini/antigravity-ide/brain/f29da9f4-5d17-4113-ae2d-692085a042b3/cargo_console_1782124997875.png)

---

## 2. UI Workspace Elements

### A. Core Navigation Corridors (Flow Density Map)
* **Visual Layer**: Overlays color-coded cargo bands along NW-1 sectors representing volume intensity:
  * **Cyan (Active/Optimal Flow)**: Sector operating under 60% capacity.
  * **Amber (Heavy Flow)**: Sector operating at 60% to 85% capacity.
  * **Magenta (Bottleneck/Congestion)**: Sector operating above 85% capacity or suffering terminal queues.
* **Corridor High-Level Overview**:
  * *Haldia-Kolkata Corridor*: Deepest draft, high-density container and coal traffic.
  * *Patna-Varanasi Corridor*: Medium draft, high-density fly ash and agricultural bulk traffic.
  * *Varanasi-Prayagraj Corridor*: Shallow draft, seasonal low-volume bulk and passenger ferry traffic.

### B. Cargo Type & Volume Dashboard
Displays real-time cargo breakdowns using nested donut charts and bar metrics:
* **Containers (TEU)**: Integrated logistics, finished goods, manufactured exports.
* **Coal & Minerals (MT)**: Bulk inputs feeding power plants along the riverbank (e.g. NTPC Farakka, Kahalgaon).
* **Fly Ash (MT)**: Crucial return bulk cargo shipped upstream from coal power plants.
* **Agricultural Bulk & Fertilizer (MT)**: High-demand food grains and fertilizers serving Eastern UP and Bihar.

### C. Terminal Allocation Monitor

This widget displays the allocation and queue status across primary terminals:

| Terminal Name | Assigned Vessels | Daily Throughput (MT) | Yard Capacity | Utilization % | Congestion Index |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Varanasi MMT** | 3 Underway / 2 Docked | 12,500 | 50,000 MT | 54% | `LOW` |
| **Patna Sahib / Gaighat** | 1 Underway / 3 Docked | 8,800 | 30,000 MT | 82% | `MODERATE` |
| **Farakka Jetty** | 4 Underway / 1 Docked | 15,200 | 40,000 MT | 91% | `CRITICAL ⚠` |
| **Haldia Container Port**| 7 Underway / 4 Docked | 42,000 | 120,000 MT | 68% | `MODERATE` |

### D. Congestion Indicators & Alert States
1. **Yard Saturation Warning (`YARD_SAT`)**:
   * *Trigger*: Terminal Yard Storage Utilization > 85%
   * *UI Output*: Red flashing border on the Terminal Card; priority recommendation popup.
2. **Barge Wait Queue Alert (`QUEUE_WAIT`)**:
   * *Trigger*: Vessel wait time at anchorage to dock > 12 hours
   * *UI Output*: Highlighted badge on Terminal list table.

---

## 3. Bottleneck Resolution Workflows

When terminal congestion or draft limits create bottlenecks, the UI triggers a dynamic **Bottleneck Resolution Dialog**:
1. **Detect**: System flags Farakka Jetty queue limit exceeded.
2. **Analyze**: Dialog displays alternate discharge terminals (e.g., Kahalgaon Jetty or Rajmahal Wharf).
3. **Execute**: Planner clicks "REALLOCATE CARGO FLOW" to dispatch a route change directive to incoming Class III and V vessels.

---

## 4. API Data Specifications

### A. Fetch Cargo Corridors API Payload
**Endpoint**: `GET /api/cargo/corridors`  
**JSON Structure**:
```json
{
  "status": "success",
  "timestamp": "2026-06-22T16:20:00Z",
  "corridors": [
    {
      "corridor_id": "CORR-HAL-KOL",
      "name": "Haldia-Kolkata Port Belt",
      "active_vessels_count": 14,
      "daily_volume_tons": 58000,
      "congestion_status": "MODERATE",
      "primary_commodities": ["Containers", "Coal"]
    },
    {
      "corridor_id": "CORR-VNS-PAT",
      "name": "Varanasi-Patna Flyash Belt",
      "active_vessels_count": 8,
      "daily_volume_tons": 21300,
      "congestion_status": "CRITICAL",
      "primary_commodities": ["Fly Ash", "Agri-Bulk"]
    }
  ]
}
```

### B. Create Cargo Allocation / Reallocation Request
**Endpoint**: `POST /api/cargo/reallocate`  
**JSON Structure**:
```json
{
  "planner_id": "PLAN-712",
  "original_terminal_id": "TERM-FARAKKA",
  "target_terminal_id": "TERM-KAHALGAON",
  "affected_vessel_ids": ["VES-NW1-088", "VES-NW1-094"],
  "reallocation_reason": "Farakka yard utilization at 91% capacity. Rerouting dry bulk upstream.",
  "timestamp": "2026-06-22T16:21:45Z"
}
```
