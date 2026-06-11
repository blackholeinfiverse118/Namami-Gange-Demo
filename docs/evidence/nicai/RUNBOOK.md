# RUNBOOK.md

# NICAI — Operational Runbook

## Purpose

This document explains how to run, validate, replay, and debug the NICAI orchestration system.

This runbook is intended for:

- incoming developers
- reviewers
- testing authorities
- operational auditors
- AIAIC transition engineers

---

# 1. Environment Setup

## Install dependencies

```bash
pip install -r requirements.txt
```

## Start FastAPI server

```bash
uvicorn main:app --reload
```

Default server:

```text
http://127.0.0.1:8000
```

---

# 2. Health Check

## Route

```text
GET /test
```

## Expected Result

```json
{
  "status": "OK",
  "message": "NICAI Task 5 — engine active"
}
```

---

# 3. Canonical Execution Flow

Authoritative execution route:

```text
GET /run
```

This executes:

Signal
→ Validation
→ Intelligence
→ Context Fusion
→ Cluster Aggregation
→ Contract Validation
→ Action Routing
→ Persistence
→ Replay Visibility

---

# 4. Main Execution Validation

## Route

```text
GET /run
```

## Expected Result

Response should contain:

- cluster_result
- action
- total_signals

Replay artifacts should appear inside:

```text
logs/
```

Expected log files:

- validation_logs.json
- anomaly_logs.json
- pattern_logs.json
- contract_logs.json
- action_logs.json

---

# 5. Replay Validation

## Run replay engine

```bash
python replay_engine.py
```

## Input

Provide a valid trace_id.

## Expected Result

Replay reconstruction should contain:

- VALIDATION
- ANALYSIS
- CLUSTER_ANALYSIS
- CONTRACT_VALIDATION
- ACTION

Replay status should be:

```text
COMPLETE
```

---

# 6. Lineage Export Validation

## Run lineage exporter

```bash
python test_lineage_export.py
```

## Expected Result

Export should contain:

- immutable sequence IDs
- trace continuity
- ordered orchestration stages
- replay-safe lineage reconstruction

---

# 7. Replay Divergence Validation

## Run replay divergence test

```bash
python test_divergence_checker.py
```

## Expected Result

System should detect:

- duplicate stages
- replay divergence
- missing stages
- orphan events

---

# 8. Contract Validation Testing

## Run downstream acknowledgment tests

```bash
python test_downstream_acknowledgment.py
```

## Expected Result

System should validate:

- successful acknowledgments
- malformed acknowledgments
- trace mismatches
- orphan acknowledgments

---

# 9. Dashboard Validation

## Route

```text
GET /dashboard
```

## Expected Result

Dashboard should display:

- risk_level
- anomaly_type
- explanation
- recommendation_signal
- trace_id

Dashboard is visualization-only and not the canonical governance route.

---

# 10. Common Failure Areas

| Area | Primary Module |
|---|---|
| replay failures | replay_engine.py |
| persistence issues | bucket_emitter.py |
| contract failures | contract_validator.py |
| intelligence issues | sanskar_engine.py |
| orchestration issues | main.py |
| aggregation issues | cluster_intelligence.py |

---

# 11. Operational Constraints

NICAI intentionally enforces:

- deterministic orchestration
- bounded execution
- replay-safe persistence
- recommendation-only action routing
- contract-first governance

NICAI does NOT:

- autonomously intervene
- self-modify orchestration
- bypass replay governance
- bypass contract validation

---

# 12. Operational Status

Validated capabilities:

- replay reconstruction
- immutable sequencing
- deterministic orchestration
- contextual fusion
- aggregation intelligence
- contract governance
- lineage persistence
- bounded action routing

System state:

OPERATIONALLY_RESILIENT