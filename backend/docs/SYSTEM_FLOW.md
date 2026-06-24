# System Flow

## Runtime Intelligence Flow

Dataset Source
    ↓
Refresh Manager
    ↓
Refresh Registry
    ↓
Refresh Audit Log
    ↓
Source Health Service
    ↓
Health Calculations
    ↓
Runtime APIs
    ↓
Frontend Runtime Views

---

## Components

### Refresh Manager

Responsible for:

- Dataset refresh execution
- Refresh timestamps
- Refresh version tracking
- Refresh history generation

---

### Source Health Service

Responsible for:

- Freshness scoring
- Health assessment
- Confidence degradation tracking
- Source reachability evaluation

---

### Runtime APIs

Endpoints:

- /dataset-health
- /dataset-freshness
- /source-status
- /intelligence-health

---

## Operational Goal

Provide continuously observable marine intelligence runtime status without requiring direct code inspection.