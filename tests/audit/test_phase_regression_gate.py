"""Tests for completed-phase regression protection logic."""

from __future__ import annotations

from scripts.ci.check_phase_regression import (
    parse_completed_phases,
    parse_phase_results,
    verify_completed_phases,
)


def test_parse_completed_phases_reads_ssot_headings() -> None:
    text = """
## ✅ Phase 1: MVP Comm Layer - COMPLETED
## 🔄 Phase 2: Full Listener Loop - IN PROGRESS
## 🔮 Phase 3: Robustness - FUTURE
"""
    assert parse_completed_phases(text) == {1}


def test_verify_completed_phases_accepts_success_for_completed_phase() -> None:
    completed = {1}
    results = {1: "success", 2: "failure"}
    assert verify_completed_phases(completed, results) == []


def test_verify_completed_phases_rejects_failed_completed_phase() -> None:
    completed = {1, 2}
    results = {1: "success", 2: "failure"}
    errors = verify_completed_phases(completed, results)
    assert len(errors) == 1
    assert "Phase 2" in errors[0]


def test_parse_phase_results_parses_key_value_pairs() -> None:
    parsed = parse_phase_results(["1=success", "2=failure"])
    assert parsed == {1: "success", 2: "failure"}
