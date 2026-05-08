# AutoDream Message FSM Compare

## State Signal Counts

| state | AutoDream count | DreamOS guard count |
|---|---:|---:|
| `new` | 0 | 0 |
| `claimed` | 0 | 0 |
| `running` | 0 | 0 |
| `complete` | 0 | 0 |
| `failed` | 0 | 0 |
| `expired` | 0 | 0 |
| `pending` | 0 | 0 |
| `processing` | 0 | 0 |
| `delivered` | 0 | 0 |
| `ack` | 0 | 0 |
| `retry` | 0 | 0 |

## Recommendation

- Keep `ALLOWED_TRANSITIONS` as canonical SSOT.
- Map AutoDream queue concepts onto DreamOS FSM only through tests.
- Do not import AutoDream queue implementation.