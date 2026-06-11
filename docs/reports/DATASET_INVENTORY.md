# Dataset Inventory

Document Name: DATASET_INVENTORY.md
Version: 1.0
Status: In Review
Prepared By: Nupur Gavane
Project: Namami Gange Demo
Document Type: Inventory Report
Last Updated: 10/06/2026

## Purpose

This document provides a consolidated inventory of datasets currently used within the Namami Gange demonstration environment.

The inventory is derived from the verified dataset registry, audit findings, and suitability intelligence processing pipeline.

## Dataset Summary

| Dataset                    | Source                                     | Primary Usage                                   | Status  |
| -------------------------- | ------------------------------------------ | ----------------------------------------------- | ------- |
| CPCB Water Quality Dataset | Central Pollution Control Board (CPCB)     | Water quality assessment, pollution constraints | Present |
| CWC River Stations Dataset | Central Water Commission (CWC)             | River flow, depth, and stability analysis       | Present |
| IWAI Terminal Dataset      | Inland Waterways Authority of India (IWAI) | Terminal proximity and logistics assessment     | Present |
| Logistics Parks Dataset    | Logistics and infrastructure sources       | Logistics accessibility scoring                 | Present |
| Urban Centers Dataset      | Census and urban development sources       | Market access and traffic potential analysis    | Present |

## Dataset Utilization

### CPCB Water Quality Dataset

Purpose:

* Water quality evaluation
* Environmental suitability assessment
* Pollution constraint detection

Associated Signals:

* CPCB_WQI_v1
* CPCB_POLL_v1

---

### CWC River Stations Dataset

Purpose:

* River stability analysis
* Navigation depth assessment
* Hydrological suitability evaluation

Associated Signals:

* CWC_RIV_STAB_v1
* CWC_DEPTH_v1

---

### IWAI Terminal Dataset

Purpose:

* Terminal proximity scoring
* Logistics accessibility assessment
* Inland waterway suitability evaluation

Associated Signals:

* IWAI_TERM_v1
* IWAI_LOG_v1
* IWAI_TRAF_v1

---

### Logistics Parks Dataset

Purpose:

* Logistics support analysis
* Distribution network evaluation
* Infrastructure accessibility assessment

---

### Urban Centers Dataset

Purpose:

* Population accessibility analysis
* Market access evaluation
* Traffic demand estimation

## Signal Mapping

| Signal ID       | Dataset Source        | Functional Area           |
| --------------- | --------------------- | ------------------------- |
| CWC_RIV_STAB_v1 | CWC River Stations    | River Stability           |
| CPCB_WQI_v1     | CPCB Water Quality    | Water Quality             |
| CWC_DEPTH_v1    | CWC River Stations    | Navigation Depth          |
| IWAI_TERM_v1    | IWAI Terminal Dataset | Terminal Proximity        |
| IWAI_LOG_v1     | IWAI Terminal Dataset | Logistics Access          |
| IWAI_TRAF_v1    | IWAI Terminal Dataset | Traffic Potential         |
| ENV_WETLAND_v1  | Environmental Overlay | Environmental Constraints |
| ENV_FLOOD_v1    | Environmental Overlay | Flood Constraints         |
| ENV_CLEAR_v1    | Environmental Overlay | Clearance Constraints     |
| CPCB_POLL_v1    | CPCB Water Quality    | Pollution Constraints     |

## Data Processing Role

The datasets support the generation of:

* Suitability Scores
* Opportunity Assessment
* Constraint Identification
* Location Intelligence
* Recommendation Generation
* Dashboard Visualization Payloads

The processed outputs are available through the suitability intelligence backend and supporting payload artifacts.

## Current Limitations

### Static Dataset Sources

Current datasets are sourced from repository-managed files and are not continuously synchronized with live external systems.

### Dataset Version Visibility

Dataset version tracking is limited and may be expanded in future iterations.

### Coverage Expansion

Additional geographic coverage and supplementary datasets may improve future intelligence generation capabilities.

## Related Evidence

Supporting evidence is available within:

```text
docs/evidence/namami_gange/
```

including:

* ng_data_inventory.csv
* NG_DATA_AUDIT_REPORT.md
* NG_COVERAGE_MATRIX.md
* NG_DATA_READINESS_RISK_REPORT.md

## Conclusion

The Namami Gange demonstration environment currently utilizes five primary datasets supporting suitability assessment, operational analysis, location intelligence generation, and dashboard visualization workflows.

These datasets form the foundation of the intelligence processing pipeline and provide the inputs required for assessment, scoring, explainability, and recommendation generation.
