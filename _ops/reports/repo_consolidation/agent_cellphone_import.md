# Agent_Cellphone Import

## Source

`~/projects/Agent_Cellphone`

## Destination

`archive/imports/Agent_Cellphone`

## Import Mode

Legacy source archive imported into DreamOS for characterization, salvage, and selective promotion.

## Rules

- DreamOS remains the canonical repo.
- Imported source is preserved under `archive/imports/`.
- Do not directly wire legacy runtime into DreamOS.
- Promote only after tests characterize behavior.
- Historical `agent_workspaces/`, `CONTRACTS/`, `FSM_UPDATES/`, and demo artifacts are evidence, not runtime.

## Promotion Candidates

- `CORE/agent_cell_phone.py`
- `CORE/SECURE_COMMUNICATION_HUB.py`
- `CORE/inter_agent_framework.py`
- `CORE/enhanced_agent_coordination_framework.py`
- `CORE/COLLABORATIVE_EXECUTION_SYSTEM.py`
- `CORE/unified_stall_detection_system.py`
- `CORE/fixed_stall_detection_system.py`
- `agent5_coordination_system.py`

## Next Gate

Create characterization tests in DreamOS before promoting any imported module into active runtime paths.
