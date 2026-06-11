# KNOWN_LIMITATIONS.md

# NICAI — Known Operational Limitations

## Purpose

This document identifies known operational, architectural, replay, governance, and scalability limitations within NICAI.

These limitations are intentionally documented to reduce operational ambiguity and improve inheritance readiness.

---

# 1. Filesystem-Bound Persistence

NICAI replay persistence currently depends on:

```text
logs/*.json
```

Limitations:

- no distributed persistence
- no database-backed replay storage
- no persistence replication
- local filesystem dependency

Impact:

Large-scale orchestration durability is limited.

---

# 2. Full-File Rewrite Persistence Model

bucket_emitter.py rewrites entire log files during persistence updates.

Limitations:

- reduced scalability
- performance degradation under high event volume
- increased corruption risk during concurrent writes

Impact:

Current persistence model is suitable for bounded operational environments only.

---

# 3. No Cryptographic Lineage Integrity

Replay artifacts currently do NOT include:

- cryptographic hashes
- signatures
- tamper validation
- immutable audit signatures

Impact:

Replay ordering is deterministic, but artifact authenticity is not cryptographically guaranteed.

---

# 4. No Concurrency Protection

Persistence layer currently lacks:

- file locking
- transactional writes
- atomic append guarantees

Impact:

Concurrent orchestration execution may introduce persistence race conditions.

---

# 5. Route-Driven Orchestration

NICAI orchestration is primarily coordinated through:

```text
main.py
```

Limitations:

- no centralized orchestration service class
- partial orchestration routes coexist
- execution discipline depends on canonical route usage

Canonical route:

```text
GET /run
```

---

# 6. Partial Validation Duplication

Validation logic currently exists in both:

- validator.py
- main.py validate_signal()

Impact:

Validation responsibilities are partially duplicated.

Future consolidation recommended.

---

# 7. Limited Telemetry Coverage

Operational telemetry exists through:

```text
orchestration_telemetry.py
```

Limitations:

- not all routes emit telemetry
- dashboard execution partially untracked
- replay diagnostics telemetry incomplete

Impact:

Operational observability is functional but not comprehensive.

---

# 8. Static Governance Enums

Contract governance currently uses hardcoded enums.

Examples:

- risk levels
- recommendation signals
- temporal contexts

Impact:

Policy evolution requires code modification.

---

# 9. Simplified Action Routing

action_router.py currently routes primarily through:

```text
risk_level
```

Limitations:

- no policy engine
- no dynamic orchestration policies
- limited contextual action routing

Impact:

Action routing intentionally remains bounded and simplified.

---

# 10. No Autonomous Intervention

NICAI intentionally restricts execution to:

- recommendation emission
- escalation routing
- governance-safe orchestration

NICAI does NOT:

- autonomously intervene
- self-modify orchestration
- execute uncontrolled actions

This limitation is intentional.

---

# 11. Replay Governance Distributed Across Modules

Replay governance responsibilities are distributed across:

- replay_engine.py
- replay_divergence_checker.py
- lineage_exporter.py
- bucket_emitter.py

Impact:

Replay governance is operationally functional but not fully centralized.

---

# 12. Cluster Intelligence Uses Partial Text Parsing

cluster_intelligence.py partially depends on explanation text parsing.

Example:

```python
"pollution" in explanation_text
```

Impact:

Future explanation-format changes may affect aggregation behavior.

---

# 13. Dashboard Is Visualization-Only

/dashboard route provides:

- visualization
- trace visibility
- operational inspection

It is NOT:

- the canonical orchestration route
- governance-authoritative
- replay-authoritative

Canonical route remains:

```text
GET /run
```

---

# 14. Current Operational Position

NICAI is operationally coherent and governance-aware, but intentionally bounded.

The system prioritizes:

- deterministic execution
- replay safety
- governance visibility
- bounded orchestration

over:

- autonomous complexity
- uncontrolled scaling
- dynamic self-modification

---

# Final Limitation Statement

NICAI is intentionally designed as a bounded deterministic orchestration system.

The current implementation prioritizes:

- operational clarity
- replay-safe governance
- deterministic orchestration
- bounded execution behavior

over aggressive scalability or autonomous execution complexity.