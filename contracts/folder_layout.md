# Agent Bus Folder Layout (SSOT)

```text
agent-bus/
  inbox/
    desktop/
    laptop/
    android/
  outbox/
  claimed/
  complete/
  failed/
  logs/
```

## Rules

- Sender writes `*.json` into `inbox/<target-node>/`.
- Relay claims by moving file into `claimed/<node>__<message_id>.json`.
- Relay acknowledges by moving claimed file into `complete/<node>__<message_id>.json`.
- Failures are moved into `failed/` with same naming.
- Relays may append operation lines to `logs/<node>.log`.

## Idempotency

- Message ID is globally unique UUID.
- Claim and ack are move operations; repeated calls should fail fast instead of duplicating state.
- A message in `complete/` is immutable terminal evidence.
