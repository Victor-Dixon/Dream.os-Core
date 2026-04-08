# Architecture Map (Grounded)
**Date:** 2026-04-08 (UTC)

## 1) High-Level Components
1. **Orchestration Layer (`dreamos/`)**
   - Agent model, swarm controller, routing policy, tool registry, memory/RAG abstractions.
2. **Execution Transport Layer (`src/`)**
   - Bus message schema, execution guardrails, relay claim/ack state transitions, filesystem transport.
3. **Integration Boundary**
   - `dreamos.cli.main` composes both layers (builds swarm, wraps with `TaskAdapter`, dispatches via `DeviceRelay` over `FileTransport`).

## 2) Dependency Direction (Observed)
- `dreamos` depends on `src` for execution guard + bus messaging contracts in multiple places.
- `src/relay/device_relay.py` also imports `dreamos.core.task_adapter.TaskAdapter`.

This creates a **bidirectional package coupling** (`dreamos <-> src`) at runtime integration points.

## 3) Entrypoints
- Packaged CLI entrypoint: `dreamos.cli.main:main`.
- Module entrypoint: `python -m dreamos.cli.main`.
- Demo runtime entrypoint: `python runtime_demo/main.py`.

## 4) Runtime Flow (Task Path)
1. CLI parses goal + repo context.
2. CLI constructs `BusMessage(type="task")`.
3. `FileTransport.send` writes message to node inbox.
4. `DeviceRelay.poll_once` receives, claims, marks running.
5. `TaskAdapter.execute` enforces bus-message-only execution.
6. `SwarmController.execute_message/run` decomposes goal into tool steps and executes per repo.
7. Relay marks complete/failure and acks to complete queue.

## 5) Primary Architectural Risk
- Mixed historical repository documents and mixed package roots increase ambiguity.
- Bidirectional coupling between `dreamos` and `src` can complicate packaging boundaries and long-term modularity.

