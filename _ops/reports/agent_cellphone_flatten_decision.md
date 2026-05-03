# Agent_Cellphone Flatten Decision

## Decision

Agent_Cellphone will be flattened into Dream.os-Core as an archive-first salvage import.

It is not a direct runtime merge.

## Promote Candidates

| Source Area | Decision | Target |
|---|---|---|
| `CORE/fixed_stall_detection_system.py` | Inspect and port deterministic logic | Dream.os-Core runtime guard/tests |
| `CORE/unified_stall_detection_system.py` | Inspect and port deterministic logic | Dream.os-Core runtime guard/tests |
| `CORE/COLLABORATIVE_EXECUTION_SYSTEM.py` | Conceptual salvage only | Existing planner/dispatcher/runtime |
| `CORE/enhanced_agent_coordination_framework.py` | Conceptual salvage only | Existing swarm coordination layer |
| `CORE/SECURE_COMMUNICATION_HUB.py` | Contract/security concept review | Existing canonical message validation |
| `advanced_workflows/` | Convert useful flows to examples/tests | Problem JSON/workflow docs |

## Archive Only

| Source Area | Reason |
|---|---|
| `agent_workspaces/` | Historical runtime mailboxes; not live state |
| `CONTRACTS/` | Historical handoff evidence |
| `FSM_UPDATES/` | Historical state records; not canonical FSM |
| `DEMOS/` | Reference behavior only |
| `DOCUMENTATION/` | Doctrine/reference |
| `PRDs/` | Product/reference material |

## Quarantine

| Source Area | Reason |
|---|---|
| coordinate calibration scripts | GUI/coordinate automation is brittle and belongs outside core |
| launchers | Old activation wrappers likely duplicate current CLI |
| ad hoc debug scripts | Not kernel material |

## Guardrails

- Dream.os-Core remains canonical schema owner.
- No competing message envelope enters runtime.
- No historical JSON enters active bus state.
- Tests are required before promotion.
- Runtime changes must preserve existing public imports.

## Next Step

Promote stall detection first because it is high-value, bounded, and testable.
