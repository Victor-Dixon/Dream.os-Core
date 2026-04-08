# Prioritized Fix Plan
**Date:** 2026-04-08 (UTC)

## Priority 0 (Immediate)
1. **Stabilize install path in constrained environments**
   - Provide offline/air-gapped install guidance or lockfile/wheelhouse strategy.
   - Add explicit troubleshooting for proxy constraints and build deps.

2. **Truth-align top-level documentation**
   - Keep README and foundation docs aligned to currently runnable components.
   - Flag archival/legacy ACP claims as historical.

## Priority 1 (High)
3. **Reduce cross-root coupling (`dreamos` <-> `src`)**
   - Define clear ownership boundary (e.g., promote `src` runtime primitives into package namespace or extract shared kernel package).

4. **Promote architecture contract doc from observed code**
   - Capture current runtime task flow, status transitions, and transport contracts as canonical architecture doc.

## Priority 2 (Medium)
5. **Entry-point robustness checks**
   - Add smoke tests for `python -m dreamos.cli.main --list-goals` and demo runtime.

6. **Deprecation labeling**
   - Annotate stale/historical documents with clear status banners to prevent operator confusion.

## Priority 3 (Lower)
7. **Repository hygiene automation**
   - Add CI lint that detects references to non-existent paths in top-level docs.

