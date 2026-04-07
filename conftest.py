"""Pytest configuration for audit-aligned and phase-aware test structure."""

from __future__ import annotations

from pathlib import Path

import pytest


AUDIT_TEST_FILES = {
    "test_message_schema.py",
    "test_execution_guard.py",
    "test_message_only_execution.py",
    "test_message_to_swarm_execution.py",
    "test_claim_and_ack.py",
    "test_git_transport.py",
    "test_audit_suite_structure.py",
    "test_phase_regression_gate.py",
}

CONTRACT_TEST_FILES = {
    "test_message_schema.py",
    "test_execution_guard.py",
    "test_message_only_execution.py",
    "test_audit_suite_structure.py",
    "test_phase_regression_gate.py",
}

INTEGRATION_TEST_FILES = {
    "test_message_to_swarm_execution.py",
    "test_claim_and_ack.py",
    "test_git_transport.py",
}


PHASE_TEST_FILES = {
    "phase1": {
        "test_message_schema.py",
        "test_execution_guard.py",
        "test_message_only_execution.py",
        "test_message_to_swarm_execution.py",
        "test_claim_and_ack.py",
        "test_git_transport.py",
        "test_agent.py",
        "test_memory.py",
        "test_routing.py",
        "test_swarm.py",
        "test_tools.py",
        "test_audit_suite_structure.py",
        "test_phase_regression_gate.py",
    }
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--audit",
        action="store_true",
        default=False,
        help="Run only audit-focused tests.",
    )
    parser.addoption(
        "--ssot-mode",
        action="store_true",
        default=False,
        help="Run only tests that validate SSOT/documentation alignment.",
    )


def _path_name(item: pytest.Item) -> str:
    return Path(str(item.fspath)).name


def _add_default_markers(item: pytest.Item) -> None:
    name = _path_name(item)
    test_path = Path(str(item.fspath))

    if "dreamos/tests" in test_path.as_posix():
        item.add_marker(pytest.mark.unit)

    if name in AUDIT_TEST_FILES:
        item.add_marker(pytest.mark.audit)

    if name in CONTRACT_TEST_FILES:
        item.add_marker(pytest.mark.contract)

    if name in INTEGRATION_TEST_FILES:
        item.add_marker(pytest.mark.integration)

    for phase, files in PHASE_TEST_FILES.items():
        if name in files:
            item.add_marker(getattr(pytest.mark, phase))


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    audit_only = config.getoption("--audit")
    ssot_mode = config.getoption("--ssot-mode")

    for item in items:
        _add_default_markers(item)

    if not audit_only and not ssot_mode:
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        if ssot_mode and (item.get_closest_marker("audit") or item.get_closest_marker("contract")):
            selected.append(item)
        elif audit_only and item.get_closest_marker("audit"):
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
