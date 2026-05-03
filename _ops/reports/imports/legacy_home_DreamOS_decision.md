# Legacy ~/DreamOS Import Decision

## Decision

The old `~/DreamOS` folder is a legacy runtime/prototype source.

It is not the canonical repo.

## Canonical Repo

`~/projects/DreamOS`

## Import Strategy

1. Archive inventory first.
2. Inspect runtime loop files.
3. Compare against canonical DreamOS CLI/runtime.
4. Promote only missing useful behavior.
5. Preserve old problem/run examples as reference data, not active state.

## Initial Target Lanes

| Legacy Area | Lane |
|---|---|
| `main.py` | inspect before promote |
| `core/` | inspect before promote |
| `agents/` | inspect before promote |
| `problems/` | archive examples, possibly promote sample problem JSON |
| `runs/` | archive only |
| `memory/` | archive only unless specific decisions are curated |
