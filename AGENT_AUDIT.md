# AGENT_AUDIT.md

## SSOT Audit Rules (Mandatory)

1. Always read phase status from `00_foundation/PROJECT_STATUS.md`.
2. Never hardcode phase expectations in tests.
3. Use `pytest --ssot-mode` to validate documentation and SSOT alignment.

## Implementation Guidance

- CI checks must derive expected phase status from the SSOT source (`PROJECT_STATUS.md`).
- Any new phase status logic should consume SSOT headings, not duplicated constants.
- If phase status is changed, update SSOT first, then tests/CI assertions derived from it.
