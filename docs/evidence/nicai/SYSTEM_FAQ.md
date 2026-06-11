# SYSTEM_FAQ.md

# NICAI — System FAQ

---

# 1. What is NICAI?

NICAI is a bounded deterministic orchestration system for environmental intelligence processing.

The system combines:

- validation
- intelligence execution
- contextual fusion
- aggregation analysis
- contract governance
- replay-safe persistence
- bounded action routing

NICAI is governance-oriented and replay-safe.

---

# 2. What is the canonical execution route?

The authoritative execution route is:

```text
GET /run
```

Located in:

```text
main.py
```

This is the only route executing the full governance-aware orchestration chain.

---

# 3. What is the canonical execution flow?

```text
Signal
→ Validation
→ Intelligence
→ Context Fusion
→ Cluster Aggregation
→ Contract Validation
→ Action Routing
→ Persistence
→ Replay Reconstruction
```

---

# 4. Is NICAI deterministic?

Yes.

NICAI enforces deterministic orchestration through:

- immutable sequence IDs
- bounded escalation logic
- contract validation
- replay reconstruction
- governance-safe routing

---

# 5. Does NICAI support replay reconstruction?

Yes.

Replay reconstruction is implemented through:

- replay_engine.py
- bucket_emitter.py
- lineage_exporter.py

Replay reconstruction validates:

- stage continuity
- immutable ordering
- trace continuity
- replay completeness

---

# 6. Where are replay artifacts stored?

Replay artifacts are stored inside:

```text
logs/
```

Primary replay files:

- validation_logs.json
- anomaly_logs.json
- pattern_logs.json
- contract_logs.json
- action_logs.json

---

# 7. Does NICAI perform autonomous intervention?

No.

NICAI intentionally restricts orchestration to:

- recommendation emission
- escalation routing
- governance-safe bounded actions

NICAI does NOT autonomously execute real-world interventions.

---

# 8. What enforces governance boundaries?

Primary governance modules:

| Module | Responsibility |
|---|---|
| validator.py | ingress governance |
| contract_validator.py | downstream governance |
| replay_engine.py | replay governance |
| failure_handler.py | failure governance |
| bucket_emitter.py | lineage governance |

---

# 9. What performs intelligence processing?

Primary intelligence modules:

| Module | Responsibility |
|---|---|
| sanskar_engine.py | deterministic intelligence |
| integration_orchestrator.py | contextual fusion |
| cluster_intelligence.py | aggregation intelligence |

---

# 10. Why does NICAI use immutable sequence IDs?

Immutable sequence IDs enforce:

- deterministic replay ordering
- lineage continuity
- replay-safe reconstruction
- governance-safe orchestration tracing

Sequence IDs are assigned through:

```text
sequence_manager.py
```

---

# 11. What happens if contract validation fails?

NICAI blocks downstream participation.

Action routing only occurs AFTER successful contract validation.

Invalid orchestration outputs are rejected deterministically.

---

# 12. What happens if replay reconstruction is incomplete?

Replay engine reports:

```text
INCOMPLETE
```

and identifies missing stages.

Replay continuity enforcement is deterministic.

---

# 13. What are the major operational limitations?

Known limitations include:

- filesystem-bound persistence
- no cryptographic lineage integrity
- no distributed replay persistence
- route-driven orchestration
- partially duplicated validation logic
- limited telemetry coverage

See:

```text
KNOWN_LIMITATIONS.md
```

---

# 14. Is NICAI operationally audited?

Yes.

NICAI has been audited for:

- deterministic orchestration
- replay governance
- contract enforcement
- lineage persistence
- contextual fusion
- bounded action routing
- aggregation intelligence

---

# 15. What is NICAI’s current operational state?

Current audited status:

```text
OPERATIONALLY_RESILIENT
```