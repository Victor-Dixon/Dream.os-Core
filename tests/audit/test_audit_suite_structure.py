"""Audit-oriented checks for SSOT alignment, CI gates, and phase coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SSOT_PATH = ROOT / "00_foundation" / "PROJECT_STATUS.md"
LATEST_AUDIT_ARTIFACT = ROOT / "03_execution" / "SWARM_SYSTEM_AUDIT_2026-04-06.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

PROJECT_GOAL_EVIDENCE: dict[str, list[Path]] = {
    "transport-layer": [
        ROOT / "tests" / "test_message_schema.py",
        ROOT / "tests" / "test_claim_and_ack.py",
        ROOT / "tests" / "test_git_transport.py",
    ],
    "bridge-layer": [
        ROOT / "tests" / "test_message_to_swarm_execution.py",
        ROOT / "tests" / "test_message_only_execution.py",
    ],
    "execution-integrity": [
        ROOT / "tests" / "test_execution_guard.py",
        ROOT / "docs" / "execution_lockdown.md",
    ],
    "swarm-runtime": [
        ROOT / "dreamos" / "tests" / "test_swarm.py",
        ROOT / "dreamos" / "tests" / "test_agent.py",
    ],
}

PHASE_JOB_LABELS = [
    "Phase#1: MVP Comm Layer",
    "Phase#2: Full Listener Loop",
    "Phase#3: Robustness",
    "Phase#4: Logging & Debug Panel",
]


@pytest.mark.audit
@pytest.mark.phase1
def test_ssot_document_exists() -> None:
    assert SSOT_PATH.exists(), "SSOT document must exist for auditability."


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ssot_mentions_latest_audit_artifact() -> None:
    status_text = SSOT_PATH.read_text(encoding="utf-8")
    assert "SWARM_SYSTEM_AUDIT_2026-04-06.md" in status_text


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_latest_audit_artifact_exists() -> None:
    assert LATEST_AUDIT_ARTIFACT.exists(), "Latest audit artifact should be present."


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_workflow_exists_for_quality_gates() -> None:
    assert CI_WORKFLOW.exists(), "CI workflow must exist to enforce quality gates."


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_runs_full_and_audit_test_commands() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "pytest -q" in ci_text
    assert "pytest --audit -q" in ci_text


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_has_phase_labeled_jobs() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    for label in PHASE_JOB_LABELS:
        assert label in ci_text, f"Missing CI phase job label: {label}"


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_phase_jobs_check_ssot_status() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/ci/check_phase_status.py --phase 1 --expected COMPLETED" in ci_text
    assert "scripts/ci/check_phase_status.py --phase 2 --expected COMPLETED" in ci_text
    assert "scripts/ci/check_phase_status.py --phase 3 --expected IN PROGRESS" in ci_text
    assert "scripts/ci/check_phase_status.py --phase 4 --expected FUTURE" in ci_text


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
@pytest.mark.parametrize("goal_area", sorted(PROJECT_GOAL_EVIDENCE))
def test_project_goal_evidence_exists(goal_area: str) -> None:
    missing = [path for path in PROJECT_GOAL_EVIDENCE[goal_area] if not path.exists()]
    assert not missing, f"Goal area '{goal_area}' is missing evidence files: {missing}"


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_has_completed_phase_regression_lock() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert 'name: "Completed Phase Regression Lock"' in ci_text
    assert 'python scripts/ci/check_phase_regression.py' in ci_text


@pytest.mark.audit
@pytest.mark.contract
@pytest.mark.phase1
def test_ci_phase_prerequisites_are_chained() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert 'needs: [phase1_mvp_comm_layer]' in ci_text
    assert 'needs: [phase2_full_listener_loop]' in ci_text
    assert 'needs: [phase3_robustness]' in ci_text
