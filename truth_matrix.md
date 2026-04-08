# Documentation vs Implementation Truth Matrix
**Date:** 2026-04-08 (UTC)

| Claim Area | Documentation Claim (Summary) | Implementation Reality | Status |
|---|---|---|---|
| Product identity | "Agent Cell Phone" with PyAutoGUI/Cursor GUI ecosystem | Active code is DreamOS swarm + message bus runtime; ACP-specific files referenced in docs are absent in current tree | Contradicted |
| Project status phases | Phase-based SSOT with DoD/test gates | CI/check scripts and audit tests exist and pass; this is supported | Supported |
| Runtime architecture | Message/relay/command pipeline | `src/core`, `src/relay`, `src/transports`, and integration in `dreamos.cli.main` prove this path | Supported |
| Packaging/install | Python package `dreamos` | Metadata exists; install attempt failed in this environment due dependency fetch/proxy issue | Partially supported |
| Test credibility | Claimed robust validation | 123 tests pass, plus audit and ssot subsets pass | Supported |
| Legacy file structure docs | Windows path structures and ACP modules | Many referenced files/dirs do not exist in current repository | Contradicted |

## Notes
- This matrix prioritizes executable and importable code over narrative docs.
- Contradictions should be handled by explicit archival labels and updated top-level guidance.

