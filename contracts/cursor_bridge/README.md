# Cursor Bridge Contracts

These schemas define the lightweight GPT ↔ Cursor bridge payloads promoted from `Victor.os`.

## Files

- `gpt_command_schema.json` — commands sent from GPT/operator layer to Cursor bridge.
- `cursor_feedback_schema.json` — feedback/results returned from Cursor bridge.

## Promotion Notes

Promoted during Dream.OS variant consolidation.

Source variant:

- `~/projects/Victor.os/src/dreamos/integrations/cursor/bridge/schemas/`

Canonical intent:

- Keep bridge payload contracts under `contracts/cursor_bridge/`
- Avoid burying shared contracts under implementation-specific package paths
- Review runtime validators separately before wiring execution
