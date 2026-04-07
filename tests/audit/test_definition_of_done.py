"""Audit checks for SSOT Definition of Done enforcement."""

from __future__ import annotations

from pathlib import Path

from scripts.ci.check_definition_of_done import (
    REQUIRED_DOD_IDS,
    REQUIRED_SECTION_TITLE,
    extract_dod_section,
    validate_dod_section,
)

ROOT = Path(__file__).resolve().parents[2]
SSOT_PATH = ROOT / "00_foundation" / "PROJECT_STATUS.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ssot_has_explicit_dod_section() -> None:
    status_text = SSOT_PATH.read_text(encoding="utf-8")
    section = extract_dod_section(status_text)
    assert section is not None, f"Missing '{REQUIRED_SECTION_TITLE}' section."


def test_ssot_dod_section_contains_all_required_ids() -> None:
    status_text = SSOT_PATH.read_text(encoding="utf-8")
    section = extract_dod_section(status_text)
    assert section is not None
    assert validate_dod_section(section) == []


def test_ci_runs_dod_validation_script() -> None:
    ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "python scripts/ci/check_definition_of_done.py" in ci_text


def test_required_dod_ids_are_stable() -> None:
    assert REQUIRED_DOD_IDS == ("DOD-1", "DOD-2", "DOD-3", "DOD-4")


def test_dod_validator_rejects_partial_identifier_matches() -> None:
    section = """
- [x] `DOD-10` — Placeholder criterion.
- [x] `DOD-20` — Placeholder criterion.
- [x] `DOD-30` — Placeholder criterion.
- [x] `DOD-40` — Placeholder criterion.
""".strip()
    errors = validate_dod_section(section)
    assert len(errors) == 4
    for dod_id in REQUIRED_DOD_IDS:
        assert any(dod_id in error for error in errors)


def test_dod_validator_accepts_exact_identifier_matches() -> None:
    section = """
- [x] `DOD-1` — Full suite passes.
- [x] `DOD-2` — Audit suite passes.
- [x] `DOD-3` — SSOT mode passes.
- [x] `DOD-4` — CI DoD check passes.
""".strip()
    assert validate_dod_section(section) == []
