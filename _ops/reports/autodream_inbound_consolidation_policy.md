# AutoDream Inbound Consolidation Policy

source_repo: AutoDream.Os
canonical_repo: DreamOS
status: ACCEPT_BY_GOVERNED_PROMOTION_ONLY

## Policy

DreamOS may receive AutoDream concepts only through small verified lanes.

## Required Gate

Each inbound change needs:

1. source path
2. target path
3. classification
4. rationale
5. tests
6. commit

## Forbidden

- bulk copy
- overwrite canonical contracts
- import generated data
- import stale runtime artifacts
