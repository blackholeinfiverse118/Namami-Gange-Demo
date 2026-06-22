# Review Packet — Marine Operations Command Center
**Document Name:** REVIEW_PACKET.md  
**Version:** 4.0 (Transition Phase Complete)  
**Status:** Approved for Subsystem Integration  
**Prepared By:** Chandragupta Maurya  
**Project:** Namami Gange Marine Operations Command Center (MOCC)  
**Last Updated:** 2026-06-22  

---

## 1. Executive Summary

This review packet documents the architectural transition of the Namami Gange dashboard from a location suitability demo platform into a **Marine Operations Command Center (MOCC)**. The MOCC serves as the master command console for waterway operators, harbor masters, and logistics planners to supervise traffic, cargo flow, River Information Services (RIS), voyage planning, and terminal management.

---

## 2. Command Center Specification Directory

The following design specification files have been created in the workspace root:

1. **[COMMAND_CENTER_INFORMATION_ARCHITECTURE.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/COMMAND_CENTER_INFORMATION_ARCHITECTURE.md)**: Details the unified layout grid, the six specialized operational zones, user roles, and data flow topologies.
2. **[VESSEL_OPERATIONS_UI_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/VESSEL_OPERATIONS_UI_SPEC.md)**: Designs the active vessel tracking list, IWAI vessel class definitions, and safety alert rules (under-keel draft warnings and speed limits).
3. **[CARGO_OPERATIONS_UI_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/CARGO_OPERATIONS_UI_SPEC.md)**: Outlines flow density corridors, commodity type tracking (coal, fly ash, containers), and terminal capacity indices.
4. **[RIS_COMMAND_CENTER_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/RIS_COMMAND_CENTER_SPEC.md)**: Establishes European RIS standard integration (Notice to Mariners, Electronic Ship Reporting, water level gauges, and Farakka locks control).
5. **[VOYAGE_PLANNING_UI_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/VOYAGE_PLANNING_UI_SPEC.md)**: Defines the step-by-step route planning wizard, draft and clearance constraints mapping, and alternate route comparison tools.
6. **[TERMINAL_OPERATIONS_UI_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/TERMINAL_OPERATIONS_UI_SPEC.md)**: Focuses on jetty berths booking Gantt charts, arrival queues, and yard utilization heatmaps.
7. **[NATIONAL_WATERWAYS_GEOSPATIAL_SPEC.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/NATIONAL_WATERWAYS_GEOSPATIAL_SPEC.md)**: Details the GIS mapping layers, GeoJSON feeds, and candidate locations for seaplane water aerodromes.
8. **[MARINE_OPERATIONS_DESIGN_SYSTEM.md](file:///c:/Users/PIXEL/Desktop/namaamai%20gange%203/MARINE_OPERATIONS_DESIGN_SYSTEM.md)**: Defines the dark-theme styling design tokens (HSL colors, fonts) and component APIs for the 8 card primitives.

---

## 3. Integration Stream Architecture

The updated system schema highlights how the integration team's subsystems interact with the MOCC panels:

```mermaid
graph TD
    subgraph Data Sources (Nupur / Shravani)
        AIS[AIS GPS Feeds]
        MDB[Marine MasterDB]
        Gauge[CWC Level Gauges]
        CPCB[CPCB Water Sensors]
    end

    subgraph Analytical Core (Ankita / Shravani)
        RIS_Eng[RIS Alert Processor]
        Voy_Opt[Voyage Optimizer]
        Term_Sch[Terminal Slot Scheduler]
    end

    subgraph Operations Frontend (You / Soham)
        Map[Geospatial Command Layer]
        Vessel[Vessel Console]
        Cargo[Cargo Console]
        Terminal[Terminal Console]
        RIS_Panel[RIS Dashboard]
    end

    AIS --> RIS_Eng
    MDB --> Term_Sch
    Gauge --> RIS_Eng
    CPCB --> RIS_Eng
    
    RIS_Eng --> Map
    RIS_Eng --> RIS_Panel
    RIS_Eng --> Vessel
    
    Term_Sch --> Terminal
    Term_Sch --> Cargo
    
    Voy_Opt --> Map
    Voy_Opt --> Vessel
```

---

## 4. Operational Demo Flows

### A. Real-Time Vessel Safety Flow
1. **Under-Keel Monitoring**: Vessel telemetry reports current draft. CWC gauges report shallow water at Buxar.
2. **Alert Triggered**: System alerts the operator of a draft safety clearance breach (`DRAFT_WARN` < 0.4m).
3. **Dispatch Override**: Operator reviews the lock gate and dredger statuses via the RIS console, then broadcasts a slow-speed advisory.

### B. Cargo Congestion Rerouting Flow
1. **Capacity Overload**: Farakka terminal yard capacity utilization exceeds 90%.
2. **Notification**: The Cargo console highlights Farakka in red and suggests alternate berths upstream.
3. **Reallocation**: Operator opens the cargo reallocation wizard, moves upcoming barge arrivals to Kahalgaon Jetty, and updates the schedules.

### C. Multi-Constraint Voyage Planning Flow
1. **Configuration**: Operator launches the Voyage Wizard, selecting Varanasi MMT to Haldia, using a Class V barge carrying 2,000 tons of fly ash.
2. **Constraint Check**: System validates draft limits and vertical bridge clearance under bridges.
3. **Recommendation**: Planner reviews the optimal route recommendations vs. alternate high-siltation paths.

---

## 5. Design Tokens (Quick Reference)

| Category | Token Name | Hex/HSL Value | Use Case |
| :--- | :--- | :--- | :--- |
| **Theme** | `--deep-navy` | `hsl(222, 47%, 7%)` | Global background |
| **Theme** | `--surface` | `hsl(222, 40%, 12%)` | Panel backgrounds |
| **Status** | `--active-cyan` | `hsl(180, 100%, 45%)` | Normal active state |
| **Status** | `--eco-green` | `hsl(145, 80%, 45%)` | Ecological compliant zones |
| **Status** | `--warn-amber` | `hsl(38, 95%, 55%)` | Warnings (speed limit) |
| **Status** | `--alert-red` | `hsl(355, 85%, 55%)` | Critical safety breaches |