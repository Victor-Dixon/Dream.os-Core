# AutoDream Message FSM Compare

## State Signal Counts

| state | AutoDream count | DreamOS guard count |
|---|---:|---:|
| `new` | 1 | 1 |
| `claimed` | 0 | 2 |
| `running` | 4 | 2 |
| `complete` | 2 | 2 |
| `failed` | 20 | 2 |
| `expired` | 15 | 3 |
| `pending` | 14 | 0 |
| `processing` | 18 | 0 |
| `delivered` | 7 | 0 |
| `ack` | 54 | 0 |
| `retry` | 22 | 0 |

## Recommendation

- Keep `ALLOWED_TRANSITIONS` as canonical SSOT.
- Map AutoDream queue concepts onto DreamOS FSM only through tests.
- Do not import AutoDream queue implementation.