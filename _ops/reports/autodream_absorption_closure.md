# AutoDream Absorption Closure

AutoDream.Os is no longer present as a standalone local repo.

DreamOS will keep the existing salvage trail as the canonical absorption record and will not retain a hard runtime or test dependency on `$HOME/projects/AutoDream.Os`.

Preserved artifacts:

- `_ops/reports/autodream_inbound_consolidation_policy.md`
- `_ops/reports/autodream_message_queue_semantic_audit.md`
- `_ops/reports/autodream_message_fsm_compare.md`
- `runtime/tasks/autodream_*`

Boundary:

- Map AutoDream queue concepts onto DreamOS FSM only through tests.
- Do not import AutoDream queue implementation.
- Promote only small verified lanes.
