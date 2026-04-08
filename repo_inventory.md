# Repository Inventory (Grounded Snapshot)
**Date:** 2026-04-08 (UTC)

## 1) Top-Level Technical Shape
- Language: Python-first repository.
- Active code roots:
  - `dreamos/` (packaged project root)
  - `src/` (message bus/relay/runtime primitives)
  - `tests/` + `dreamos/tests/`

## 2) File Statistics (Observed)
- Total files: 182
- Python files: 65
- Markdown files: 43
- JSON files: 6

(Counts included repository artifacts present at audit time.)

## 3) Build/Test Metadata
- `dreamos/pyproject.toml`: build system + project metadata + script entrypoint.
- Root `pytest.ini`: test discovery across `tests` and `dreamos/tests`, with audit/phase markers.

## 4) Entrypoint Inventory
- `dreamos` console script -> `dreamos.cli.main:main`
- `python -m dreamos.cli.main`
- `python runtime_demo/main.py`

## 5) Documentation Inventory (High Impact)
- SSOT status log: `00_foundation/PROJECT_STATUS.md`
- Curated root doc: `README_CURATED.md`
- Architecture/project-history docs under `00_foundation/`, `02_architecture/`, `03_execution/`, `99_reference/`.

