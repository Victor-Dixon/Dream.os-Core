# Repository Grounded Audit Report
**Project:** Dream.os-Core  
**Audit Date:** 2026-04-08 (UTC)  
**Auditor:** GPT-5.3-Codex  
**SSOT Reference:** `00_foundation/PROJECT_STATUS.md`

## 1) Scope and Method
This audit was performed from repository code, executable commands, and observed outputs. Documentation claims were treated as hypotheses and verified against implementation.

## 2) Final Verdict
- **Runtime verdict:** **partially_runnable**
- **Test verdict:** **test_credible**
- **Domain verdict:** **domain_partial**

## 3) Fact / Inference / Unknown Separation
### Facts
- The codebase is primarily Python and contains two active code roots: `dreamos/` and `src/`.
- Packaging metadata defines project `dreamos` with console script `dreamos = dreamos.cli.main:main`.
- Runtime demo executes successfully via `python runtime_demo/main.py`.
- Full tests pass: `pytest -q` reports `123 passed`.
- Audit suite and SSOT mode also pass.
- Editable install failed in this environment because pip could not fetch build dependency `setuptools>=68` (proxy/network path failure).

### Inferences
- The operational implementation appears to be a **hybrid architecture** where `dreamos` orchestration uses `src` bus/relay/message transport primitives.
- The repository is runnable for local module execution and tests, but not fully installable in this environment due to dependency fetch constraints.

### Unknowns
- Whether editable installation succeeds in a network-permissive environment.
- Whether legacy "Agent Cell Phone" GUI/runtime claims are still externally deployed elsewhere.

## 4) Stack, Setup Path, Entrypoints, and Test Path
See `architecture_map.md`, `repo_inventory.md`, and `test_assessment.md` for evidence-backed detail.

## 5) Documentation Truthfulness Summary
- Several top-level and foundation docs claim a much larger ACP GUI/Cursor automation system than the code currently present.
- Current implementation truth is centered on DreamOS swarm orchestration + message bus relay + transport + CI/audit enforcement.
- A grounded README update has been provided in `README_CURATED.md`.

## 6) Prioritized Recommendations
See `prioritized_fix_plan.md`.

## 7) Audit Artifacts
- `run_log.md`
- `architecture_map.md`
- `domain_model.md`
- `test_assessment.md`
- `prioritized_fix_plan.md`
- `repo_inventory.md`
- `truth_matrix.md`

