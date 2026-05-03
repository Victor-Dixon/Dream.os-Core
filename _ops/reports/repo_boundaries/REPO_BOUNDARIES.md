# Dream.OS Repo Boundaries

## Purpose

This document prevents Dream.OS repo drift.

No repo import, flatten, archive, promotion, or salvage operation is allowed until the target repo role is declared here.

## Canonical Repos

| Repo | Role | Owns | Does Not Own |
|---|---|---|---|
| `DreamOS` | Active runtime / execution loop | problem runs, local orchestration experiments, Termux runner, active loop behavior | canonical schemas, long-term contracts, external toolbelt |
| `Dream.os-Core` | Core kernel / contract authority | message schema, FSM lifecycle, transition guards, transport validation, runtime invariants | legacy mailboxes, GUI coordinate automation, random workflow experiments |
| `AgentTools` | Toolbelt / adapters / external control plane | MCP adapters, tools_v2, repo tools, web/API control surfaces, operator UX | canonical message schema, core FSM ownership |
| `Agent_Cellphone` | Legacy salvage source | historical coordination patterns, stall detection ideas, old agent workspace evidence | live runtime state, canonical schema, direct imports |

## Import Rules

1. Every external repo import must declare:
   - source repo
   - target repo
   - import type
   - promotion lane
   - rejection/quarantine lane

2. Runtime state is never imported directly.
   - No historical inboxes.
   - No old outboxes.
   - No processed queues.
   - No stale agent workspaces.

3. Dream.os-Core only accepts:
   - schemas
   - FSM/transport guards
   - deterministic runtime primitives
   - tests
   - architectural decisions
   - archived evidence clearly marked non-runtime

4. DreamOS accepts:
   - active loop experiments
   - problem JSON examples
   - local runner improvements
   - execution flow experiments

5. AgentTools accepts:
   - adapters
   - CLI tools
   - MCP/API bridges
   - safe execution wrappers
   - dashboard/control-plane features

6. Agent_Cellphone remains source-only unless explicitly retired.

## Current Decision

Agent_Cellphone flatten is paused.

Before continuing, classify whether each salvage item belongs in:

- `DreamOS`
- `Dream.os-Core`
- `AgentTools`
- archive only
- quarantine

## Active Risk

The current risk is repo identity collapse.

Do not continue importing Agent_Cellphone into Dream.os-Core until the target boundary decision is committed.
