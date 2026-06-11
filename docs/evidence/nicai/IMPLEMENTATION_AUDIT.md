# validator.py

## Path

validator.py

## Status

EXISTS + INTEGRATED

## Actual Behavior

Performs deterministic signal validation, trace assignment, failure normalization, telemetry propagation, and validation artifact emission.

Acts as the ingress validation gate for NICAI orchestration.

## Core Functions

- generate_trace_id
- validate_output_schema
- build_error
- validate_signal
- validate_batch
- get_validated_signals

## Integration Flow

Signal
→ validate_signal()
→ validation checks
→ trace assignment
→ failure handling
→ telemetry emission
→ orchestration continuation

## Called By

- main.py
- orchestration execution flow

## Output Flows To

- bucket_emitter.py
- telemetry_emitter.py
- failure_handler.py
- replay/governance layers

## Operational Findings

- deterministic trace propagation confirmed
- replay-safe validation confirmed
- governance failure integration confirmed
- telemetry integration confirmed

## Known Limitations

- validate_output_schema currently stubbed
- optional imports may silently hide integration failures
- legacy commented code still exists
- numeric environmental bounds not enforced
- schema versioning not implemented


# integration_orchestrator.py

## Path

integration_orchestrator.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the canonical intelligence fusion orchestration layer between Sanskar reasoning and Nupur contextual intelligence.

Performs deterministic fusion, contextual escalation, explanation enrichment, replay-safe trace propagation, and contract-safe output shaping.

## Core Execution Flow

Signal
→ run_engine(signal)
→ get_context_intelligence(signal)
→ context fusion
→ risk adjustment
→ recommendation escalation
→ trace propagation
→ contract-safe final output

## Called By

- main.py orchestration flow

## Output Flows To

- cluster_intelligence.py
- contract_validator.py
- replay/governance layers

## Operational Findings

- real cross-system orchestration confirmed
- contextual fusion actively modifies risk outputs
- deterministic trace continuity confirmed
- downstream contract shaping confirmed
- replay-safe propagation confirmed

## Known Limitations

- Nupur failures are silently absorbed
- contextual schema validation not enforced
- fusion logic partially hardcoded
- no direct telemetry emission
- no internal replay checkpointing

# sanskar_engine.py

## Path

sanskar_engine.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the primary deterministic intelligence engine of NICAI.

Performs anomaly detection, temporal reasoning, spatial reasoning, deterministic risk escalation, confidence estimation, explanation generation, and recommendation routing.

## Core Execution Flow

process()
→ preprocess()
→ detect_anomaly()
→ analyze_temporal()
→ analyze_spatial()
→ calculate_risk()
→ calculate_confidence()
→ generate_explanation()
→ final output generation

## Called By

- integration_adapter.py
- integration_orchestrator.py

## Output Flows To

- integration_orchestrator.py
- cluster_intelligence.py
- contract_validator.py
- replay/governance layers

## Operational Findings

- deterministic rule-based reasoning confirmed
- multi-signal fusion confirmed
- temporal escalation confirmed
- spatial clustering confirmed
- replay-safe reasoning confirmed
- explainability layer confirmed
- bounded execution confirmed

## Known Limitations

- fully rule-based (non-adaptive)
- thresholds hardcoded
- confidence heuristic only
- no internal schema enforcement
- no replay checkpoint emission
- pattern analysis may overlap cluster_intelligence.py


# cluster_intelligence.py

## Path

cluster_intelligence.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the orchestration-level aggregation intelligence layer.

Performs multi-signal aggregation, temporal escalation analysis, regional spread analysis, composite environmental stress detection, escalation scoring, and replay-safe cluster output generation.

## Core Execution Flow

processed signals
→ cluster aggregation
→ temporal wave analysis
→ regional spread detection
→ composite stress detection
→ escalation scoring
→ recommendation routing
→ replay-safe output

## Called By

- main.py orchestration flow

## Output Flows To

- contract_validator.py
- action_router.py
- replay/governance layers

## Operational Findings

- real orchestration-level aggregation confirmed
- temporal escalation analysis confirmed
- multi-region clustering confirmed
- composite stress detection confirmed
- weighted escalation routing confirmed
- replay-safe trace continuity confirmed

## Known Limitations

- cluster logic partially depends on explanation text parsing
- no structured feature extraction layer
- confidence score static
- no internal telemetry emission
- no internal replay checkpointing
- possible temporal counter reset edge-case

# contract_validator.py

## Path

contract_validator.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the deterministic downstream governance and contract enforcement layer.

Performs required-field validation, enum enforcement, confidence validation, explanation validation, and deterministic contract acceptance/rejection.

## Core Execution Flow

orchestration output
→ type validation
→ required field validation
→ enum validation
→ confidence validation
→ explanation validation
→ deterministic contract verdict

## Called By

- main.py orchestration flow

## Output Flows To

- action_router.py
- replay/governance layers
- downstream participation systems

## Operational Findings

- runtime contract enforcement confirmed
- deterministic rejection behavior confirmed
- replay-safe trace continuity confirmed
- bounded output vocabulary confirmed
- governance-safe validation confirmed

## Known Limitations

- no nested schema validation
- limited strict type enforcement
- no schema versioning
- no direct telemetry emission
- enums hardcoded in module


# replay_engine.py

## Path

replay_engine.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the deterministic replay reconstruction and governance verification layer.

Performs log aggregation, trace filtering, immutable sequence reconstruction, stage verification, and replay integrity validation.

## Core Execution Flow

trace_id
→ log collection
→ trace filtering
→ immutable sequence reconstruction
→ stage verification
→ replay integrity validation
→ replay summary generation

## Called By

- replay_divergence_checker.py
- lineage_exporter.py
- replay validation flows
- operational testing flows

## Output Flows To

- governance layers
- replay verification systems
- lineage export systems
- operational proof flows

## Operational Findings

- deterministic replay reconstruction confirmed
- immutable ordering confirmed
- stage continuity validation confirmed
- replay-safe lineage reconstruction confirmed
- governance-safe replay verification confirmed

## Known Limitations

- replay persistence filesystem-bound
- no cryptographic integrity validation
- partial replay failures may silently degrade visibility
- no direct telemetry emission
- required stages hardcoded
- duplicate-stage detection distributed across modules

# failure_handler.py

## Path

failure_handler.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the centralized governance failure normalization layer.

Performs deterministic failure structuring, replay-visible persistence, severity classification, and bounded orchestration failure handling.

## Core Execution Flow

failure detected
→ build_failure()
→ normalized governance structure
→ replay-safe persistence
→ orchestration continuation

## Called By

- validator.py
- governance failure flows

## Output Flows To

- failure_logs.json
- replay/governance layers

## Operational Findings

- structured governance failures confirmed
- replay-visible failure persistence confirmed
- bounded failure handling confirmed
- deterministic failure normalization confirmed

## Known Limitations

- limited governance taxonomy richness
- no telemetry emission
- no failure deduplication
- no traceback preservation
- no replay checkpoint metadata

# action_router.py

## Path

action_router.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the deterministic operational decision emission layer.

Performs bounded risk-to-action routing, replay-visible action persistence, and deterministic orchestration termination.

## Core Execution Flow

validated orchestration output
→ risk extraction
→ deterministic action mapping
→ replay-safe action persistence
→ operational action emission

## Called By

- main.py orchestration flow

## Output Flows To

- action_logs.json
- replay/governance layers
- downstream operational review systems

## Operational Findings

- deterministic action routing confirmed
- replay-safe action persistence confirmed
- bounded orchestration behavior confirmed
- governance-safe escalation behavior confirmed

## Known Limitations

- routing only risk-level driven
- no configurable policy engine
- no downstream acknowledgment verification
- no internal failure handling
- no telemetry emission

# bucket_emitter.py

## Path

bucket_emitter.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the deterministic persistence and lineage storage layer for NICAI orchestration.

Performs immutable sequence assignment, structured event persistence, replay-safe trace continuity preservation, and governance-compatible lineage storage.

## Core Execution Flow

event emitted
→ sequence_id assignment
→ trace propagation
→ timestamp generation
→ structured lineage packaging
→ persistent append storage
→ replay visibility preservation

## Called By

- validator.py
- failure_handler.py
- action_router.py
- orchestration flows
- governance flows

## Output Flows To

- logs/*.json
- replay_engine.py
- lineage_exporter.py
- governance reconstruction layers

## Operational Findings

- immutable sequence persistence confirmed
- replay-safe lineage storage confirmed
- append-style persistence confirmed
- deterministic event reconstruction confirmed
- governance-compatible trace continuity confirmed

## Known Limitations

- full-file rewrite persistence model
- no concurrency protection
- corruption recovery may lose visibility
- no cryptographic integrity guarantees
- no storage rotation
- persistence failure handling print-only

# integration_adapter.py

## Path

integration_adapter.py

## Status

EXISTS + ACTIVELY INTEGRATED

## Actual Behavior

Acts as the orchestration compatibility and schema translation layer between NICAI orchestration and SanskarEngine intelligence processing.

Performs deterministic input normalization, engine-safe schema mapping, output contract normalization, trace continuity propagation, and bounded failure containment.

## Core Execution Flow

NICAI signal
→ input normalization
→ engine-safe schema mapping
→ SanskarEngine.process()
→ output normalization
→ contract-safe transformation
→ trace continuity propagation
→ orchestration return

## Called By

- integration_orchestrator.py
- API orchestration flows

## Output Flows To

- integration_orchestrator.py
- cluster_intelligence.py
- replay/governance layers

## Operational Findings

- orchestration boundary separation confirmed
- deterministic schema translation confirmed
- contract normalization confirmed
- replay-safe trace continuity confirmed
- bounded failure handling confirmed
- governance-aware reject filtering confirmed

## Known Limitations

- schema validation partial
- input contracts hardcoded
- no direct telemetry emission
- adapter failures not directly governance-persisted
- singleton engine lifecycle model


# main.py

## Path

main.py

## Status

EXISTS + PRIMARY ORCHESTRATION ENTRYPOINT

## Actual Behavior

Acts as the canonical operational execution controller for NICAI.

Coordinates FastAPI routing, validation orchestration, intelligence fusion, aggregation orchestration, contract enforcement, replay persistence, telemetry propagation, dashboard exposure, and operational action routing.

## Canonical Execution Spine

Signal
→ validate_signal()
→ orchestrate_intelligence()
→ analyze_signal_cluster()
→ validate_contract()
→ route_action()
→ emit_bucket_artifact()
→ emit_orchestration_event()
→ replay/governance visibility

## Primary Execution Route

GET /run

This is the authoritative bounded orchestration execution flow.

## Called By

- FastAPI routes
- dashboard execution flows
- operational replay/testing flows

## Output Flows To

- replay_engine.py
- lineage_exporter.py
- action_router.py
- contract_validator.py
- governance telemetry systems

## Operational Findings

- canonical orchestration spine confirmed
- deterministic governance layering confirmed
- replay-safe persistence fully integrated
- contract enforcement correctly gated
- action routing bounded after validation
- orchestration telemetry confirmed

## Known Limitations

- validation logic partially duplicated inside main.py
- multiple partial execution routes exist
- legacy logging remnants remain
- failure governance not fully centralized
- telemetry coverage incomplete
- orchestration remains route-driven instead of centralized service-driven