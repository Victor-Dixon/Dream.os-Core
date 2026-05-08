# AutoDream Message Queue Semantic Audit

## Sources

## src/core/message_queue.py

- chars: 18058

### Signals

- pending: 12
- processing: 17
- failed: 9
- delivered: 7
- lock: 0
- ack: 15
- retry: 9
- schema: 0
- bus: 0
- persist: 30

## src/core/message_queue_persistence.py

- chars: 17281

### Signals

- pending: 2
- processing: 1
- failed: 11
- delivered: 0
- lock: 17
- ack: 38
- retry: 13
- schema: 0
- bus: 1
- persist: 7

## src/domain/ports/message_bus.py

- chars: 3581

### Signals

- pending: 0
- processing: 0
- failed: 0
- delivered: 0
- lock: 0
- ack: 1
- retry: 0
- schema: 0
- bus: 9
- persist: 0

## Recommendation

- Treat AutoDream queue as a reference implementation only.
- Compare lifecycle states to canonical DreamOS message FSM before promotion.
- Prefer compatibility tests over implementation import.