# Agent_Cellphone Import Cleanup

## Purpose

Trim stale legacy runtime artifacts from the DreamOS import while preserving source, docs, PRDs, onboarding material, and promotable modules.

## Removed

- Agent inbox/outbox message dumps
- Agent processed FSM/message queues
- Global queue snapshots
- CONTRACTS JSON update dumps
- FSM_UPDATES JSON dumps
- Generated demo JSON outputs
- Runtime status/state/task JSON files

## Preserved

- `CORE/`
- `DOCUMENTATION/`
- `PRDs/`
- `LAUNCHERS/`
- `advanced_workflows/`
- `agent_workspaces/onboarding/`
- Python source files
- Markdown planning/protocol files

## Rule

DreamOS should ingest behavior through characterization tests, not by preserving stale message/event dumps.
