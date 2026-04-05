# Agent Cellphone — Curated Docs Pack

This package contains only the documents with direct value for extracting a clean Dream.OS / Agent Cellphone v2 core.

## Included

### 00_foundation
- `README.md` — Repo entrypoint and highest-level system framing.
- `PRODUCT_REQUIREMENTS_DOCUMENT.md` — Primary product intent, scope, features, and operating model.
- `TECHNICAL_SPECIFICATIONS.md` — Most concrete technical design doc; stronger than summary variants.
- `IMPLEMENTATION_ROADMAP.md` — Sequenced build order for reconstructing the system cleanly.
- `PROJECT_REQUIREMENTS_ANALYSIS.md` — Requirements decomposition that can inform v2 extraction decisions.
- `PROJECT_STATUS.md` — Snapshot of what was claimed complete vs pending in v1.

### 01_runtime_core
- `INTER_AGENT_COMMUNICATION_GUIDE.md` — Core communication protocol concepts for agent-to-agent routing.
- `INTER_AGENT_FRAMEWORK_SUMMARY.md` — Compact framing of the inter-agent framework; useful as companion context.
- `FSM_STRUCTURE.md` — Closest thing to an execution-state contract; high-value for runtime rebuild.
- `AutonomousModes.md` — Operational mode model for task progression and autonomy behavior.
- `AGENT_RESCUE_SYSTEM.md` — Recovery and anti-stall concepts worth preserving.
- `CONFIG_STRUCTURE.md` — Canonical configuration structure after cleanup; useful for v2 settings design.
- `PROJECT_FOCUS_CONFIGURATION.md` — Useful if preserving dynamic project routing without hardcoding.
- `AGENT_README.md` — Practical communication/self-prompting behavior guide tied to ACP workflows.

### 02_onboarding_ops
- `ONBOARDING_SYSTEM_IMPROVEMENTS.md` — Best single onboarding doc; replaces multiple overlapping onboarding summaries.

### 99_reference
- `FINAL_PROJECT_STRUCTURE.md` — Reference-only snapshot of intended organized layout.
- `PROJECT_STRUCTURE.md` — Reference-only snapshot of earlier 'cursor bridge' structure/claims.

## Excluded on Purpose

- **GUI docs:** Deferred until a stable backend/runtime exists.
- **Resume/interview docs:** Not relevant to Dream.OS v2 extraction.
- **Branding/update summaries:** Low engineering value for rebuild.
- **Duplicate onboarding summaries:** Superseded by ONBOARDING_SYSTEM_IMPROVEMENTS.md.
- **Spec/summary duplicates:** Kept full specs, dropped summaries.

## Packaging Notes

- Foldered by rebuild function, not original repo layout.
- `99_reference/` is context-only and should not drive implementation contracts.
