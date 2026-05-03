# DreamOS Repo Boundaries

## Decision

This repository is the canonical DreamOS repo.

Former name:

- `Dream.os-Core`

Canonical name:

- `DreamOS`

## Repo Roles

| Repo | Role | Owns | Does Not Own |
|---|---|---|---|
| `DreamOS` | Canonical kernel + active runtime spine | message schema, FSM lifecycle, transport guard, deterministic runtime primitives, problem execution model, migration decisions | raw legacy mailboxes, GUI coordinate automation, random untested imports |
| `AgentTools` | Toolbelt / adapters / control plane | MCP adapters, safe tool execution, tools_v2, repo tools, web/API adapters, operator UX | canonical DreamOS schema/FSM ownership |
| `Agent_Cellphone` | Legacy salvage source | historical coordination patterns and evidence | live runtime state, direct imports |
| legacy `~/DreamOS` | Prototype source | old runtime loop material for audit/import | canonical repo identity |

## Import Rules

1. No blind folder flattening.
2. Every import declares source, target lane, and rejection lane.
3. Runtime state is never imported as live state.
4. Historical inbox/outbox files remain archive evidence only.
5. Runtime code lands behind tests.
6. Core contracts remain canonical in this repo.
7. Adapter/control-plane features go to AgentTools.
8. GUI coordinate automation is quarantined unless explicitly isolated as an adapter.

## Current Migration

- `Dream.os-Core` has been renamed to `DreamOS`.
- Legacy `~/DreamOS` must be audited before import.
- Agent_Cellphone remains source-only until each salvage lane is assigned.
