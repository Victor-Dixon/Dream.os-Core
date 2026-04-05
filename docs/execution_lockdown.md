# Execution Lockdown: Bus-Only Enforcement

Date: 2026-04-05

## Entrypoint inventory

Command used:

```bash
rg -n "swarm\.run\(|TaskAdapter\.execute\(|execute_bus_message\(" .
```

Findings:

- `dreamos/core/task_adapter.py`
  - `TaskAdapter.execute(...)` (public choke point, now BusMessage-only).
  - `TaskAdapter.execute_bus_message(...)` (typed helper, BusMessage-only).
- `dreamos/tests/test_swarm.py`
  - direct `swarm.run(...)` calls (internal runtime tests only, now `_internal=True`).
- `src/relay/device_relay.py`
  - routes claimed/running task messages through `TaskAdapter.execute(...)`.

Classification:

- Bus-backed valid path:
  - CLI → `FileTransport.send(BusMessage)` → `DeviceRelay.poll_once()` → `TaskAdapter.execute(BusMessage)` → `SwarmController.execute_message(BusMessage)`.
- Internal-only runtime path:
  - `SwarmController.run(..., _internal=True)` for internal orchestration tests/runtime internals.
- Invalid external bypass:
  - Raw dict/list/str payloads passed to `TaskAdapter.execute`.
  - External calls to `SwarmController.run(...)` without `_internal=True`.

## Public execution path

External callers must submit `BusMessage` instances only.

- Guard: `src/core/execution_guard.py::require_bus_message`.
- Choke point: `dreamos/core/task_adapter.py::TaskAdapter.execute`.
- Runtime boundary: `dreamos/core/swarm.py::SwarmController.execute_message`.

## Forbidden paths

- `TaskAdapter.execute` with raw dict/manual payload.
- `SwarmController.run` from external code without internal flag.

Both fail with `InvalidExecutionPathError`.

## Lifecycle transition rules

Centralized in `src/core/execution_guard.py`:

- `new -> claimed`
- `claimed -> running | expired`
- `running -> complete | failed | expired`
- `complete`, `failed`, `expired` are terminal

Guard function: `validate_transition(current_state, next_state)`.

Wiring:

- `src/relay/claim_logic.py` validates transitions for claim/run/complete/fail.
- `dreamos/core/task_adapter.py` validates running→complete and running→failed result writes.

## Test coverage added

- `tests/test_execution_guard.py`
  - validates BusMessage type checks and transition checks.
- `tests/test_message_only_execution.py`
  - proves raw dict rejection.
  - proves BusMessage execution succeeds.
  - proves direct external `SwarmController.run` bypass is rejected.
