# Agent_Cellphone_docs — Curated Core Package

This package pulls only the documents that directly support rebuilding or extracting the usable core of the Agent Cell Phone system.

## Package layout

- `01_core/` — communication, FSM, and config contracts
- `02_architecture/` — product and technical architecture
- `03_execution/` — roadmap and concrete phase contract
- `04_onboarding/` — onboarding patterns worth preserving
- `99_manifest/` — selection rationale and exclusion notes

## Selection rule

Kept:
- docs that define runtime behavior, protocol, architecture, execution order, or onboarding mechanics

Excluded:
- resume material
- GUI-heavy layers
- derivative summaries when a stronger source doc already exists
- branding/status noise

## Recommended read order

1. `01_core/AGENT_README.md`
2. `01_core/INTER_AGENT_COMMUNICATION_GUIDE.md`
3. `01_core/FSM_STRUCTURE.md`
4. `01_core/CONFIG_STRUCTURE.md`
5. `02_architecture/PRODUCT_REQUIREMENTS_DOCUMENT.md`
6. `02_architecture/TECHNICAL_SPECIFICATIONS.md`
7. `03_execution/PROJECT_ROADMAP.md`
8. `03_execution/IMPLEMENTATION_ROADMAP.md`
9. `03_execution/changes_2025-08-10_phase2-contract.json`
10. `04_onboarding/COMPREHENSIVE_ONBOARDING_SUMMARY.md`

## Intended use

Use this package as the source set for:
- v2 core-kernel extraction
- message schema definition
- FSM/runtime implementation
- repo reconstruction without dragging in non-core noise
