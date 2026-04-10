# Dream.os-Core — Grounded Repository README
**Last Audited:** 2026-04-08 (UTC)  
**SSOT Status File:** `00_foundation/PROJECT_STATUS.md`

## What this repository provably is
This repository currently implements a **Python message-driven swarm execution runtime** composed of:
- `dreamos/`: swarm orchestration, agents, routing, tools, memory abstractions, and CLI.
- `src/`: bus message contracts, relay lifecycle (claim/run/ack), transport adapters, and execution guards.
- `tests/` + `dreamos/tests/`: passing test suites including audit and SSOT modes.

## What runs today (verified)
- Full test suite:
  - `pytest -q`
  - `pytest --audit -q`
  - `pytest --ssot-mode -q`
- Minimal closed-loop pipeline (hard contract + retries):
  - `python run.py --task "demo" --fail-attempts 1 --max-retries 3`
- Runtime demo:
  - `python runtime_demo/main.py`
- CLI info modes:
  - `python -m dreamos.cli.main --list-goals`
  - `python -m dreamos.cli.main --list-tools`

## Installation status
- Packaging metadata exists in `dreamos/pyproject.toml`.
- In this audit environment, `pip install -e ./dreamos` failed due inability to fetch build dependency `setuptools>=68` through configured proxy/network.

## Entrypoints
- Console script: `dreamos` → `dreamos.cli.main:main`
- Module execution: `python -m dreamos.cli.main`
- Demo execution: `python runtime_demo/main.py`

## Audit package (generated)
- `audit_report.md`
- `run_log.md`
- `architecture_map.md`
- `domain_model.md`
- `test_assessment.md`
- `prioritized_fix_plan.md`
- `repo_inventory.md`
- `truth_matrix.md`

## Documentation policy
If a documentation claim conflicts with executable code/tests, treat code/tests as source of truth and reconcile docs to SSOT.

