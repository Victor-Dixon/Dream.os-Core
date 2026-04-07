"""Validate that SSOT has an explicit, machine-checkable Definition of Done."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_DOD_IDS = ("DOD-1", "DOD-2", "DOD-3", "DOD-4")
REQUIRED_SECTION_TITLE = "## Definition of Done (SSOT-Enforced)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path("00_foundation/PROJECT_STATUS.md"),
        help="Path to the SSOT project status document.",
    )
    return parser.parse_args()


def extract_dod_section(status_text: str) -> str | None:
    if REQUIRED_SECTION_TITLE not in status_text:
        return None
    post_title = status_text.split(REQUIRED_SECTION_TITLE, maxsplit=1)[1]
    section = post_title.split("\n---", maxsplit=1)[0]
    return section.strip()


def validate_dod_section(section_text: str) -> list[str]:
    errors: list[str] = []
    for dod_id in REQUIRED_DOD_IDS:
        pattern = rf"\b{re.escape(dod_id)}\b"
        if not re.search(pattern, section_text):
            errors.append(f"Missing required DoD criteria identifier: {dod_id}")
    return errors


def main() -> int:
    args = parse_args()
    status_text = args.status_file.read_text(encoding="utf-8")
    dod_section = extract_dod_section(status_text)
    if dod_section is None:
        print(f"ERROR: Missing '{REQUIRED_SECTION_TITLE}' section in {args.status_file}")
        return 1

    errors = validate_dod_section(dod_section)
    if errors:
        print("Definition of Done check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Definition of Done check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
