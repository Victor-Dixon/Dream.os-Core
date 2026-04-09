# SSOT Update Log

## 2026-04-09 — Repo discovery restore + transport hardening

- Status: Completed
- Git: `main` includes `fix: restore repo discovery and add transport validation guard` (confirm current tip with `git log -1 --oneline`).

### Repo discovery and scan goal
- **Configuration:** Optional repo-root `.env.dreamos`, or path override via `DREAMOS_ENV_FILE`. Keys are applied only when not already set in the process environment (see `dreamos/config/settings.py`). Template: `.env.dreamos.example`. Local overrides: copy the example to `.env.dreamos` (gitignored).
- **Discovery semantics:** `find_repos()` in `dreamos/cli/main.py` (and REPL) uses `discover_git_repo_roots` — the configured root is either a single git repo or **immediate child directories** that contain `.git` (aligned with `dreamos scan all --root`, no whole-tree `rglob`).
- **Swarm goal:** Any goal string whose lowercase form contains `projectscanner` decomposes to the `scan` tool (`dreamos/config/goals.py`). Tool implementation: `dreamos/tools/scan_tools.py` → `write_scan_artifacts`. **MetaAgent** carries `scan`; **scan** runs even under default dry-run because it is read-only (`dreamos/core/agent.py`).
- **Verification (local):** `python main.py --list-repos` → expect a positive repo count when `DREAMOS_GITHUB_DIR` points at the directory that contains those repos; `python main.py "run projectscanner on all repos"` → expect matched plan `scan` without decomposer fallback warning.

### Transport kernel hardening
- **Envelope contract:** `src/core/schemas/bus_message.schema.json` (JSON Schema draft-07, `additionalProperties: false` on the root envelope).
- **Validation:** `BusMessage.validate_dict` applies `jsonschema` after existing field checks (`src/core/message.py`). Runtime dependency: `jsonschema` (declared in `dreamos/pyproject.toml`).
- **Pre-routing:** `src/transports/envelope_middleware.py` → `assert_pre_routing_envelope`; invoked from `FileTransport.send` before writing inbox JSON (`src/transports/file_transport.py`).
- **FSM traceability:** `TRANSITION_AUDIT` and `clear_transition_audit()` in `src/core/execution_guard.py`; each allowed `validate_transition` records `from`, `to`, optional `message_id`, optional `source`. Claim/complete/fail paths pass message id and stage name (`src/relay/claim_logic.py`, `dreamos/core/task_adapter.py`).
- **Tests:** `tests/test_execution_guard.py`, `tests/test_message_schema.py`, `tests/test_transport_envelope.py`; autouse audit reset in root `conftest.py`. **pytest:** root `pytest.ini` `minversion` set to `7.4` for compatibility with pytest 7.4.x environments.
- **Verification:** `pytest -q tests dreamos/tests` (or full `pytest -q` per DoD).

### Phase mapping (SSOT)
- **Phase 1 (Comm layer):** Extended with envelope schema enforcement, pre-send transport validation, and FSM transition audit trail (lifecycle still `new → claimed → running → complete|failed`; illegal transitions rejected).
- **Phase 3 (Robustness):** Reinforced by schema + audit + tests above; complements existing execution guard and contract tests.

## 2026-04-08 — Grounded repository audit package + README truth-alignment

- Status: Completed
- Decision: Completed a file/command/output-grounded audit and produced reusable audit artifacts with explicit verdicts.
- Verdicts:
  - Runtime: partially_runnable
  - Tests: test_credible
  - Domain clarity: domain_partial
- Artifacts:
  - `audit_report.md`
  - `run_log.md`
  - `architecture_map.md`
  - `domain_model.md`
  - `test_assessment.md`
  - `prioritized_fix_plan.md`
  - `repo_inventory.md`
  - `truth_matrix.md`
- Reconciliation:
  - Updated `README_CURATED.md` to reflect verified implementation/runtime truth rather than legacy ACP claims.

---

## 2026-04-07 — Definition of Done (DoD) established + CI encoded

- Status: Completed
- Decision: The project now has an explicit SSOT Definition of Done with machine-checked gates.
- DoD criteria (all required for "done"):
  - `DOD-1`: `pytest -q` passes.
  - `DOD-2`: `pytest --audit -q` passes.
  - `DOD-3`: `pytest --ssot-mode -q` passes.
  - `DOD-4`: CI executes `scripts/ci/check_definition_of_done.py` to verify the SSOT DoD section is present and criteria IDs are intact.
- Verification commands:
  - `python scripts/ci/check_definition_of_done.py`
  - `pytest -q tests/audit/test_definition_of_done.py`
  - `pytest --audit -q`
  - `pytest --ssot-mode -q`
  - `pytest -q`

## Definition of Done (SSOT-Enforced)

The work is considered **Done** only when every required criterion below remains true.

- [x] `DOD-1` — Full automated test suite passes (`pytest -q`).
- [x] `DOD-2` — Audit suite passes (`pytest --audit -q`).
- [x] `DOD-3` — SSOT alignment suite passes (`pytest --ssot-mode -q`).
- [x] `DOD-4` — CI includes and passes `python scripts/ci/check_definition_of_done.py`.

---

## 2026-04-07 — SSOT phase status recalibration

- Status: Completed
- Decision: `00_foundation/PROJECT_STATUS.md` is the canonical SSOT for phase status.
- Verification outcome:
  - Phase 3 reliability enhancements: implemented (`enforce_completed_phases` regression lock + chained prerequisites in CI).
  - Phase 3 error handling: implemented (schema validation + execution-guard failure boundaries).
  - True phase states: Phase 1 = COMPLETED, Phase 2 = COMPLETED, Phase 3 = COMPLETED, Phase 4 = COMPLETED.
- Reconciliation:
  - CI phase checks aligned to SSOT statuses.
  - Audit tests changed to derive expectations from SSOT headings (no hardcoded phase state literals).
  - Added SSOT agent rules (`AGENT_AUDIT.md`) and `pytest --ssot-mode` validation mode.

---

## 2026-04-06 — Multiple updates

### Phase 2 runtime implementation
- Status: Completed
- Changes: normalized Phase 2 runtime contracts, message pipeline, command router, inbox listener
- Verification: pytest tests/test_phase2_runtime.py

### Documentation pruning candidate audit  
- Status: Completed
- Changes: repository-wide documentation pruning candidate report
- Artifact: 03_execution/DOCS_PRUNING_CANDIDATES_2026-04-07.md

### SSOT phase-state reconciliation
- Status: Completed
- Changes: reconciled legacy phase sections, marked Phases 2-4 as COMPLETED

---

## 2026-04-06 — Regression lock + phase prerequisite enforcement in CI
- Status: Completed
- Changes: added a completed-phase regression lock job (`enforce_completed_phases`) and chained phase prerequisites in CI so later phase gates only execute after earlier phase success, while still surfacing incomplete phases via SSOT status checks.
- Verification commands: `pytest -q`, `pytest --audit -q`, `python scripts/ci/check_phase_regression.py --phase-result 1=success --phase-result 2=skipped --phase-result 3=skipped --phase-result 4=skipped`

---

## 2026-04-06 — Phase-labeled CI gates tied to SSOT status
- Status: Completed
- Changes: CI now exposes phase-labeled jobs (`Phase#1..Phase#4`) with SSOT status checks, phase-focused test gates, and an explicit audit gate so completion/lack-of-completion is visible directly from CI pass/fail states.
- Verification commands: `pytest -q`, `pytest -q -m phase1`, `pytest --audit -q`

---

## 2026-04-06 — CI/CD test enforcement + goal-aligned audit suite
- Status: Completed
- Changes: added GitHub Actions CI workflow (`pytest -q` + `pytest --audit -q`) and expanded audit tests to verify project-goal evidence coverage across transport, bridge, runtime, and execution-integrity areas.
- Verification commands: `pytest -q`, `pytest --audit -q`

---

## 2026-04-06 — Audit-aligned test structure and quality gates
- Status: Completed
- Changes: added repository-level pytest configuration, deterministic audit/contract/integration markers, `--audit` mode, and audit-structure verification tests.
- Verification command: `pytest --audit`

---

## 2026-04-06 — Systems Audit (Dream.OS swarm architecture)
- Status: Completed
- Scope audited: transport layer, swarm runtime, bridge layer, routing/capabilities, structure, docs, tests, execution integrity, CI/CD.
- Evidence source: repository code/contracts/tests as of 2026-04-06.
- Artifact: `03_execution/SWARM_SYSTEM_AUDIT_2026-04-06.md`

---

## 2026-04-05 — Execution lock-down (bus-only path enforcement)
- Status: Completed
- Changes: added centralized execution/lifecycle guard, hardened TaskAdapter to BusMessage-only input, and added bypass-rejection tests.
- Artifact: `docs/execution_lockdown.md`

---

## 2026-04-05 — Systems Audit (Dream.OS swarm architecture)
- Status: Completed
- Scope audited: transport layer, swarm runtime, bridge layer, routing/capabilities, structure, docs, tests, execution integrity, CI/CD.
- Evidence source: repository code/contracts/tests as of 2026-04-05.
- Artifact: `03_execution/SWARM_SYSTEM_AUDIT_2026-04-05.md`

---

## 2026-04-08 — Repository scope clarification (Agent Cell Phone / SSOT integrity)

- Status: Completed
- Decision: Legacy **Agent Cell Phone** material (PyAutoGUI, coordinate-based GUI layouts, `Agent_CellPhone/`-style file lists) was incorrectly merged into this SSOT. It is **not** part of the verified **Dream.os-Core** tree and must not be read as shipping functionality here. Authoritative scope remains the message-driven swarm runtime under `dreamos/`, `src/`, and `tests/`, consistent with grounded audit verdicts (for example `partially_runnable` / `domain_partial` where applicable).
- Action: Preserved the removed block as archival read-only text in `archive/agent_cell_phone/PROJECT_STATUS_AGENT_CELL_PHONE_ARCHIVED.md` (banner + verbatim body). The **only** phase status headings below are the machine-checked set for this repository (`scripts/ci/check_phase_status.py`, audit tests).
- Pointer: Any future revival of Agent Cell Phone as a product should live in its **own** repo or a clearly named subtree with its own SSOT — not appended to this file.

---

## Phase 1: MVP Comm Layer - COMPLETED

Dream.os-Core: bus message contracts, file/git transport adapters, send/claim/ack lifecycle, and CLI/runtime alignment. **2026-04-09:** JSON Schema for on-disk message envelopes, validation before `FileTransport.send`, and an append-only FSM transition audit on every legal state change. This phase is **not** PyAutoGUI or desktop GUI coordinate automation.

---

## Phase 2: Full Listener Loop - COMPLETED

- **InboxListener Path** — typed bus ingestion, relay poll/claim/ack coverage, schema-aware validation.
- **Command Router** — routing across swarm/tool paths with deterministic guardrail tests.
- **Message Processing Pipeline** — queue-safe transports, execution guard, bus-only execution expectations.

---

## Phase 3: Robustness - COMPLETED

- **Reliability Enhancements** — completed-phase regression lock in CI, chained workflow prerequisites, execution-integrity gates.
- **Error Handling** — contract/schema validation, failure and dead-letter visibility in pipeline and audit tests.
- **2026-04-09** — Bus envelope `jsonschema` validation, illegal transition rejection with `InvalidMessageTransitionError`, and deterministic tests for envelope and FSM audit behavior.

---

## Phase 4: Logging & Debug Panel - COMPLETED

SSOT-driven phase validation in CI, audit modes (`pytest --audit`, `pytest --ssot-mode`), dated artifacts under `03_execution/`, and `docs/execution_lockdown.md`. Operational visibility here means **logs, audits, and CI** — not a PyAutoGUI or coordinate-GUI “debug panel.”

---

**Last Updated:** 2026-04-09  
**Archival (historical, non-SSOT):** `archive/agent_cell_phone/PROJECT_STATUS_AGENT_CELL_PHONE_ARCHIVED.md`

### Next up (process; see also `AGENTS.md`)
- Keep tests green before and after changes (`pytest -q`, `pytest --audit -q`, `pytest --ssot-mode -q` per DoD).
- When GitHub API limits allow, confirm there are no open PRs needing merge; merge or close as appropriate and re-push `main` if needed.
