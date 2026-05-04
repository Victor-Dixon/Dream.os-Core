# Promote Cursor Bridge Contracts

## Decision

Promote the Cursor bridge command/feedback JSON schemas from `Victor.os` into canonical DreamOS contract space.

## Source

- `Victor.os/src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json`
- `Victor.os/src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json`

## Destination

- `contracts/cursor_bridge/gpt_command_schema.json`
- `contracts/cursor_bridge/cursor_feedback_schema.json`

## Reason

These schemas define GPT ↔ Cursor bridge payloads and belong in canonical shared contracts before implementation merge.

## Deferred

- Runtime validators
- Cursor bridge implementation modules
- Product output schema
- MeritChain schema
