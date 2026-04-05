# Agent Contract (Transport-First)

Agents do not own delivery. They only consume and produce messages under the shared bus contract.

## Responsibilities

1. Parse validated message payload.
2. Execute idempotent unit of work.
3. Return optional response message with `reply_to` set.
4. Never mutate transport state directly.

## Non-Responsibilities

- No direct file movement between bus folders.
- No git pull/push orchestration.
- No lease conflict resolution.

All delivery and ack behavior belongs to relay + transport layers.
