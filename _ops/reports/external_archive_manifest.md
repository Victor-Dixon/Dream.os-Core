# External Archive Manifest

Legacy import payloads were moved out of the active DreamOS repo tree.

Reason:
- The active repo should contain source, contracts, tests, runtime code, and SSOT docs.
- Imported legacy payloads are salvage/reference material, not active runtime.
- Keeping them inside `archive/imports/` made `tree`, grep, tests, and repo review noisy.

Expected external location:
- `~/projects/DreamOS_external_archive/`

Recovery rule:
- Pull specific files back only through a targeted salvage task.
- Do not bulk restore legacy imports into the active repo.
