# Agent_Cellphone Target Map

## Decision

Agent_Cellphone should not be flattened into one repo.

It should be decomposed across Dream.OS repos by responsibility.

## Target Map

| Agent_Cellphone Area | Target | Action |
|---|---|---|
| `CORE/fixed_stall_detection_system.py` | `DreamOS` first, then maybe `Dream.os-Core` | Prove in active runtime before core promotion |
| `CORE/unified_stall_detection_system.py` | `DreamOS` first, then maybe `Dream.os-Core` | Extract deterministic stall logic |
| `CORE/SECURE_COMMUNICATION_HUB.py` | `Dream.os-Core` | Inspect only for schema/transport guard ideas |
| `CORE/COLLABORATIVE_EXECUTION_SYSTEM.py` | `DreamOS` | Runtime coordination experiment |
| `CORE/enhanced_agent_coordination_framework.py` | `DreamOS` | Runtime coordination experiment |
| `CORE/inter_agent_framework.py` | `DreamOS` / `Dream.os-Core` split | Runtime behavior to DreamOS; envelope rules to Core |
| `advanced_workflows/` | `DreamOS` | Convert to problem examples/workflow templates |
| Discord integrations | `AgentTools` | External adapter/tooling lane |
| GUI launchers/calibration | quarantine | Not core; possible future control-plane adapter |
| `agent_workspaces/` | archive only | Historical evidence, not live state |
| `CONTRACTS/` | archive only or `Dream.os-Core` docs | Evidence for schema decisions |
| `FSM_UPDATES/` | archive only or `Dream.os-Core` docs | Historical FSM evidence, not canonical FSM |
| `PRDs/` | archive/docs | Product reference only |
| `DOCUMENTATION/` | archive/docs | Reference only |

## Revised Import Strategy

1. Archive audit reports only.
2. Do not import full Agent_Cellphone into Dream.os-Core.
3. Promote runtime behavior into `DreamOS` first.
4. Promote only proven invariants into `Dream.os-Core`.
5. Put adapters/integrations into `AgentTools`.
6. Commit every repo boundary decision before code movement.

## Commit Boundary

Recommended first commit:

`docs: define dreamos repo boundaries`
