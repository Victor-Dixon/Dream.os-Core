# Documentation Pruning Candidates Report (2026-04-07)

## Scope
This report identifies documentation files that are likely redundant or stale and are candidates for removal or consolidation. It is a **suspected-candidates list only** (no removals performed).

## Method Used
1. Enumerated all `*.md` files in the repository.
2. Computed SHA-256 hashes to detect exact duplicate content.
3. Grouped docs by domain/folder and flagged overlap patterns.
4. Marked each item with a confidence level and a safe action.

## High-Confidence Candidates (Exact Duplicates)
These files are byte-for-byte identical and can typically be reduced to one canonical copy plus links.

### 1) Implementation roadmap duplicates
- `00_foundation/IMPLEMENTATION_ROADMAP.md`
- `03_execution/IMPLEMENTATION_ROADMAP.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep one canonical roadmap (suggest `00_foundation/`) and replace the other with a short pointer.

### 2) Product requirements duplicates
- `00_foundation/PRODUCT_REQUIREMENTS_DOCUMENT.md`
- `02_architecture/PRODUCT_REQUIREMENTS_DOCUMENT.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep only one canonical PRD in `00_foundation/`.

### 3) Technical specifications duplicates
- `00_foundation/TECHNICAL_SPECIFICATIONS.md`
- `02_architecture/TECHNICAL_SPECIFICATIONS.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep `00_foundation/TECHNICAL_SPECIFICATIONS.md`, convert the other to reference-only.

### 4) Foundation/Core README duplicates
- `00_foundation/README.md`
- `01_core/README.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep one README and cross-link from the secondary location.

### 5) Core vs runtime_core duplicates (4 docs)
- `01_core/AGENT_README.md` == `01_runtime_core/AGENT_README.md`
- `01_core/CONFIG_STRUCTURE.md` == `01_runtime_core/CONFIG_STRUCTURE.md`
- `01_core/FSM_STRUCTURE.md` == `01_runtime_core/FSM_STRUCTURE.md`
- `01_core/INTER_AGENT_COMMUNICATION_GUIDE.md` == `01_runtime_core/INTER_AGENT_COMMUNICATION_GUIDE.md`
- Evidence: identical SHA-256 content hash for each pair.
- Recommendation: choose either `01_core/` or `01_runtime_core/` as canonical and de-duplicate the mirrored set.

### 6) Final project structure duplicates
- `02_architecture/FINAL_PROJECT_STRUCTURE.md`
- `99_reference/FINAL_PROJECT_STRUCTURE.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep one canonical copy in `99_reference/` (or `02_architecture/`) and link from the other.

### 7) Onboarding improvements duplicates
- `02_onboarding_ops/ONBOARDING_SYSTEM_IMPROVEMENTS.md`
- `04_onboarding/ONBOARDING_SYSTEM_IMPROVEMENTS.md`
- Evidence: identical SHA-256 content hash.
- Recommendation: keep one canonical onboarding improvements doc and archive the duplicate path.

## Medium-Confidence Candidates (Likely Overlap, Needs Human Confirmation)
These are not verified as exact duplicates in this pass, but likely overlap by naming/scope.

1. `README_CURATED.md` and `00_index/README_CURATED.md`
   - Action: run content diff and keep only one canonical index entry point.

2. `03_execution/PROJECT_ROADMAP.md` vs `00_foundation/IMPLEMENTATION_ROADMAP.md`
   - Action: check if one supersedes the other; if yes, archive legacy roadmap.

3. `01_runtime_core/INTER_AGENT_FRAMEWORK_SUMMARY.md` vs core communication docs
   - Action: verify if this is unique synthesis or redundant summary.

## Proposed Safe Pruning Plan (No Breaking Changes)
1. Pick a canonical location policy:
   - Requirements/spec/status in `00_foundation/`
   - Historical snapshots in `99_reference/`
2. For each duplicate pair, keep canonical file and replace duplicate with:
   - 3-5 line pointer explaining canonical path, or
   - symlink (if repo policy allows).
3. Run CI (`pytest -q` and `pytest --audit -q`) after each batch.
4. Update `00_foundation/PROJECT_STATUS.md` SSOT log with each de-duplication batch.

## Commands Used (Evidence)
- `find . -maxdepth 3 -type f \( -name '*.md' -o -name '*.markdown' \) | sort`
- Python SHA-256 duplicate scan across `**/*.md`.

## Output
- Candidate set produced for review. No files removed in this task.
