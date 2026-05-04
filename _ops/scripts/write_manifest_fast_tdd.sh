#!/usr/bin/env bash
set -euo pipefail

mkdir -p docs/agents runtime/tasks

cat > docs/agents/DREAM_OS_CORE_MANIFEST_v3.md << 'MANIFEST'
# Dream.OS Core Manifest v3.1

## Core Doctrine

- Fast, strategic, closure-first execution.
- No "in progress" without a closure path.
- "Done" means committed, verified, or formally deferred with a task artifact.
- Every action must sharpen Dream.OS.
- Drift, hesitation, and overcomplexity are pruned.
- Full swarm orchestration is default.
- Git commits are mandatory for closed code or repo-structure lanes.

## Dual Mode

### Vibe Mode

Use for high-momentum execution.

Required response shape:

1. COMMAND SHAPE
2. COPY
3. VERIFY
4. TASK FILE
5. CLOSURE

### Forge Mode

Use for architecture, risky refactors, unclear repo state, or destructive cleanup.

Required behavior:

- Classify before destructive action.
- Preserve canonical source unless proven stale.
- Use one focused lane per commit.
- Expand only after the current closure gate passes.

## Fast TDD Command-Shape Protocol

Operate in Fast TDD Command-Shape mode:

- Teach the command pattern first.
- Ship paste-ready heredoc bash.
- Verify with a targeted gate.
- Write YAML prompts as real runtime/tasks/*.yaml artifacts.
- Close with one commit-ready lane.

Agents must provide executable workflow, not inert instructions.

## Command Shape Fields

Every execution lane must begin with:

- TARGET: what path, category, module, or system is being changed.
- ACTION: what operation will be performed.
- VERIFY: what test, count, lint, or inspection proves success.
- COMMIT: the exact commit message for this lane.

## Swarm Response Protocol v3.1

- COMMAND SHAPE = operator-learning scaffold.
- COPY = executable code, shell, config, or file writes.
- VERIFY = exact targeted verification commands.
- TASK FILE = paste-ready command that writes a real task artifact.
- CLOSURE = final lane state, commit message, and next step only if needed.

No inert YAML.

If YAML is provided, it must be written through paste-ready bash into runtime/tasks/*.yaml.

## Code Response Format

Format code responses as bash commands using heredoc syntax:

cat > filename << 'EOF_INNER'
content
EOF_INNER

Rules:

- Include setup commands before cat blocks.
- Every file gets its own cat block.
- Use quoted EOF markers.
- End with the execution command.
- No vague manual-edit instructions.

## TDD / Verification Rules

Fast does not mean reckless.

- Use targeted tests before full-suite tests.
- If code changes, run the closest relevant test.
- If repo structure changes, run a targeted smoke test, file counts, git status, and git diff stat.
- If pruning:
  - generated cache gets deleted
  - duplicate promoted code gets deleted
  - salvageable legacy code moves outside the repo
  - active source, schemas, configs, and tests are preserved unless proven stale

## Cleanup Classification Rules

- __pycache__, *.pyc, .pytest_cache: delete
- duplicate promoted code: delete
- vendored payload already owned elsewhere: delete
- salvageable legacy source: move outside repo
- old runtime logs/reports: move outside repo or delete if generated
- active schemas/configs/tests: preserve unless proven stale
- docs/specs/plans: externalize unless canonical

## Definition of Done

A lane is done only when:

1. Code changed, targeted verification passed, and commit is ready or complete.
2. Cleanup changed tree shape, counts improved, targeted verification passed, and commit is ready or complete.
3. Work is blocked, blocker is concrete, and a real task artifact exists for the next lane.

## Anti-Drift Rules

Forbidden:

- Long commentary without executable commands.
- Inert YAML that is not written to a file.
- Full-suite test spam before a targeted gate.
- Multiple unrelated changes in one commit.
- Repo-local quarantine when the goal is reducing repo size.
- Deleting possible source without classification.
- Continuing after closure is achieved.
MANIFEST

cat > runtime/tasks/update_manifest_fast_tdd_command_shape.yaml << 'TASK'
task: "Update Dream.OS Core Manifest with Fast TDD Command-Shape protocol"
actions_taken:
  - "Promote command-shape learning scaffold into the manifest"
  - "Require paste-ready heredoc bash for code-producing responses"
  - "Require targeted verification gates before closure"
  - "Require YAML prompts to be written as real runtime/tasks/*.yaml artifacts"
  - "Define cleanup classification rules"
verify:
  - "test -f docs/agents/DREAM_OS_CORE_MANIFEST_v3.md"
  - "grep -q 'Fast TDD Command-Shape Protocol' docs/agents/DREAM_OS_CORE_MANIFEST_v3.md"
  - "grep -q 'No inert YAML' docs/agents/DREAM_OS_CORE_MANIFEST_v3.md"
  - "test -f runtime/tasks/update_manifest_fast_tdd_command_shape.yaml"
commit_message: "docs: update manifest with fast TDD command-shape protocol"
status: "pending"
TASK

grep -n "Fast TDD Command-Shape Protocol" docs/agents/DREAM_OS_CORE_MANIFEST_v3.md
grep -n "No inert YAML" docs/agents/DREAM_OS_CORE_MANIFEST_v3.md
test -f runtime/tasks/update_manifest_fast_tdd_command_shape.yaml

git status --short
