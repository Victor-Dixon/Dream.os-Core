# Dream.OS Systems Audit (Evidence-Only)

Audit date: 2026-04-05 (UTC)
Repository: /workspace/Dream.os-Core
Method: file/code/test/config inspection with zero-assumption rule.

Area: Transport Layer (Message Bus)
Status: Proven
Evidence:

* `contracts/message_schema.json` (required message fields including `status`, `lease_owner`, `transport`, `required_capabilities`, `assigned_to`, `result`, `error`).
* `contracts/state_machine.md` (states and allowed transitions).
* `src/core/message.py` (`BusMessage` schema validation and JSON persistence helpers).
* `src/transports/base.py` (`Transport` interface for `send`, `receive`, `ack`).
* `src/transports/file_transport.py` (filesystem transport persistence + claim/ack file moves).
* `src/transports/git_transport.py` (git-backed transport sync after send/ack).
* `src/relay/claim_logic.py` (claim/running/complete/failed mutation helpers).

Gaps:

* State transition enforcement is documented and helper-based, but no centralized transition guard function was found that rejects illegal transition sequences globally.

---

Area: Swarm Runtime (Execution Engine)
Status: Proven
Evidence:

* `dreamos/core/agent.py` (`BaseAgent`, `CognitiveAgent`, bidding/execution abstractions).
* `dreamos/core/swarm.py` (`SwarmController` orchestration, negotiation, parallel step execution).
* `dreamos/plans/decomposer.py` (goal decomposition/planning layer).
* `dreamos/tools/base.py` (`BaseTool`, `ToolRegistry`, standardized tool interface).
* `dreamos/core/memory.py` (`Memory`, `VectorMemory`, `KnowledgeGraph`, `RAGEngine` components).

Gaps:

* None proven as missing for the required runtime components listed in this audit.

---

Area: Bridge Layer (Message → Execution Binding)
Status: Proven
Evidence:

* `dreamos/core/task_adapter.py` (`TaskAdapter.execute_bus_message` maps message to swarm execution and writes status/result/error).
* `src/relay/device_relay.py` (`DeviceRelay._handle` invokes task adapter for `task` messages and persists completion).
* `dreamos/cli/main.py` (CLI enqueues `BusMessage` then triggers relay poll; completion is read from bus storage).
* `tests/test_message_to_swarm_execution.py` (validated message→adapter→swarm→message result flow).

Gaps:

* None proven as missing for required bridge responsibilities.

---

Area: Routing & Capability Resolution
Status: Proven
Evidence:

* `contracts/message_schema.json` (`required_capabilities`, `routing_hints`, `assigned_to`).
* `dreamos/core/routing.py` (`RoutingPolicy`, capability filtering, node scoring, `NodeProfile`).
* `dreamos/core/message_router.py` (routing decision attached back to message).
* `dreamos/core/swarm.py` (`route_score` includes memory and capability-weighted scoring).
* `dreamos/tests/test_routing.py` (tests for capability mismatch rejection and routing success).

Gaps:

* No dynamic node discovery mechanism was found; node population appears caller-provided or static helper-based.

---

Area: Project Structure
Status: Partial
Evidence:

* Runtime/transport split exists in `dreamos/` and `src/` packages.
* Contracts are separated under `contracts/`.
* Planning and tools are separated (`dreamos/plans/`, `dreamos/tools/`).
* Top-level docs and phase folders are present (`00_foundation/`, `03_execution/`, `99_reference/`).

Gaps:

* Expected domains named in audit rubric (`core/`, `tools/`, `plans/`, `config/`, `transport/`) are not all present as top-level peer directories; equivalent domains are split across `dreamos/` and `src/`.

---

Area: Documentation
Status: Proven
Evidence:

* `dreamos/README.md` (runtime usage and architecture overview).
* `README_CURATED.md` (curated documentation map).
* `contracts/message_schema.json` and `contracts/state_machine.md` (message contract and lifecycle docs).
* `contracts/folder_layout.md` (execution/transport flow via inbox/claimed/complete conventions).

Gaps:

* No single architecture document was found that unifies transport + runtime + bridge in one authoritative diagram/spec.

---

Area: Tests
Status: Proven
Evidence:

* `tests/test_message_schema.py` (schema and status validations).
* `tests/test_claim_and_ack.py` (claim/ack file movement and response flow).
* `tests/test_message_to_swarm_execution.py` (message-driven swarm execution binding).
* `dreamos/tests/test_routing.py` (routing and capability checks).
* `dreamos/tests/test_swarm.py` (swarm orchestration behaviors).
* Command output: `pytest -q` passed with `78 passed`.

Gaps:

* No explicit distributed multi-node network test harness (beyond local filesystem relay simulation) was found.

---

Area: Execution Integrity (CRITICAL)
Status: Partial
Evidence:

* Bridge path exists: `dreamos/core/task_adapter.py` and `src/relay/device_relay.py` execute through bus messages.
* CLI path in `dreamos/cli/main.py` sends a bus message and consumes bus completion.
* Search evidence (`rg -n "swarm\\.run\\(") found runtime invocations in:
  * `dreamos/core/task_adapter.py` (adapter-owned)
  * `dreamos/tests/test_swarm.py` (tests)

Gaps:

* `TaskAdapter.execute` accepts generic dict input and calls `swarm.run` without requiring `BusMessage`; this exposes a non-bus execution entrypoint in bridge code.

---

Area: CI/CD
Status: Missing
Evidence:

* Repository scan found no `.github/workflows/` directory.
* No CI pipeline config file was identified during file inventory.

Gaps:

* No automated CI workflow proven for test/lint/validation execution.

---

## Final Summary

### Proven Working

* Message schema, persistence primitives, and filesystem/git transports.
* Swarm runtime abstractions (agents, orchestration, planning, tools, memory).
* Bridge adapter path from bus message to execution and message result persistence.
* Capability-based routing with node profiles and scoring.
* Test suites covering schema, relay, routing, and swarm behaviors.

### Partially Implemented

* Execution integrity is mostly message-driven but still exposes one non-bus execution entrypoint (`TaskAdapter.execute`).
* Project domain separation exists but is split across `dreamos/` and `src/` instead of strict top-level domain folders.

### Missing / Critical Risks

* No CI/CD automation configuration proven.
* No centralized global transition enforcement function proven for lifecycle invalid-transition rejection.

## Final Verdict

⚠️ Partial swarm (local-only or unbound)

Why (evidence-only):

* Swarm runtime, transport, and bridge components are implemented and tested in-repo.
* However, CI/CD automation is missing, and execution integrity is not strictly bus-only due to a callable non-bus adapter entrypoint.
* Transport demonstrations and tests are local filesystem/git-repo based; no independently proven distributed network runtime was found in this audit.
