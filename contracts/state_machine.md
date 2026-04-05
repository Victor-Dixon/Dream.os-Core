# Message Lifecycle State Machine (SSOT)

## States

- `new`
- `claimed`
- `running`
- `complete`
- `failed`
- `expired`

## Valid Transitions

- `new -> claimed`
- `claimed -> running`
- `running -> complete`
- `running -> failed`
- `claimed -> expired`
- `running -> expired`

## Invariants

- `complete`, `failed`, and `expired` are terminal.
- `lease_owner` is required when status is `claimed` or `running`.
- `lease_expires_at` must be null for `new` and `complete`.
