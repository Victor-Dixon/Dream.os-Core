# Agent_Cellphone Import Archive

This directory preserves the Agent_Cellphone flatten audit as non-runtime migration evidence.

## Source

- Source repo: `~/projects/Agent_Cellphone`
- Import type: flatten audit / salvage classification
- Runtime status: archived only

## Rules

- Do not wire `agent_workspaces/` into Dream.os-Core runtime.
- Do not treat historical inbox/outbox JSON as live bus state.
- Do not replace Dream.os-Core canonical message schema.
- Do not promote coordinate-calibration or GUI-click automation into the core kernel.
- Promote only tested primitives through normal Dream.os-Core modules.

## Current Read

Agent_Cellphone contains useful swarm-era concepts, but most of the repo is historical evidence.

Primary salvage candidates:

- Stall detection
- Collaborative execution coordination
- Secure communication guard concepts
- Knowledge-management patterns
- Advanced workflow templates

Primary archive-only material:

- `agent_workspaces/`
- `CONTRACTS/`
- `FSM_UPDATES/`
- `DEMOS/`
- legacy PRDs and documentation
