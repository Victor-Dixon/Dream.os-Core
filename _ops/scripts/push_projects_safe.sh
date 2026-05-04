#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$HOME/projects}"
MODE="${2:-dry-run}"
ALLOW_FILE="${3:-.dreamos_push_allowlist}"

REPORT_DIR="_ops/reports"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$REPORT_DIR/push_projects_safe_$STAMP.md"

mkdir -p "$REPORT_DIR"

cat > "$REPORT" << REPORT_EOF
# DreamOS Safe Multi-Repo Push Report

Generated: $(date -Iseconds)

Root: \`$ROOT\`
Mode: \`$MODE\`
Allowlist: \`$ALLOW_FILE\`

## Rules

- Dry-run is default.
- Repos must be explicitly allowlisted.
- Dirty repos are blocked.
- Repos without upstream are blocked.
- Live push requires mode: \`live\`.

## Results

REPORT_EOF

if [ "$MODE" != "dry-run" ] && [ "$MODE" != "live" ]; then
  echo "ERROR: mode must be dry-run or live" | tee -a "$REPORT"
  exit 2
fi

cd "$ROOT"

if [ ! -f "$ALLOW_FILE" ]; then
  cat > "$ALLOW_FILE" << ALLOW_EOF
# One repo directory name per line.
# Example:
# DreamOS
# Dream.os-Core
# AgentTools
ALLOW_EOF
  echo "Created allowlist: $ROOT/$ALLOW_FILE"
  echo "Add repo directory names, then rerun."
  echo "- Created missing allowlist: \`$ROOT/$ALLOW_FILE\`" >> "$REPORT"
  exit 0
fi

is_allowed() {
  local repo_name="$1"
  grep -Fxq "$repo_name" "$ALLOW_FILE"
}

for gitdir in "$ROOT"/*/.git; do
  [ -d "$gitdir" ] || continue

  repo="$(dirname "$gitdir")"
  repo_name="$(basename "$repo")"

  if ! is_allowed "$repo_name"; then
    echo "- SKIP \`$repo_name\`: not allowlisted" >> "$REPORT"
    continue
  fi

  cd "$repo"

  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo UNKNOWN)"
  status="$(git status --short)"

  if [ -n "$status" ]; then
    echo "- BLOCK \`$repo_name\`: dirty working tree on branch \`$branch\`" >> "$REPORT"
    echo '```text' >> "$REPORT"
    git status --short >> "$REPORT"
    echo '```' >> "$REPORT"
    cd "$ROOT"
    continue
  fi

  upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  if [ -z "$upstream" ]; then
    echo "- BLOCK \`$repo_name\`: no upstream configured for branch \`$branch\`" >> "$REPORT"
    cd "$ROOT"
    continue
  fi

  ahead="$(git rev-list --count "${upstream}..HEAD" 2>/dev/null || echo 0)"
  behind="$(git rev-list --count "HEAD..${upstream}" 2>/dev/null || echo 0)"

  if [ "$behind" != "0" ]; then
    echo "- BLOCK \`$repo_name\`: branch \`$branch\` is behind \`$upstream\` by $behind commits" >> "$REPORT"
    cd "$ROOT"
    continue
  fi

  if [ "$ahead" = "0" ]; then
    echo "- OK \`$repo_name\`: nothing to push on \`$branch\`" >> "$REPORT"
    cd "$ROOT"
    continue
  fi

  if [ "$MODE" = "dry-run" ]; then
    echo "- DRY-RUN \`$repo_name\`: would push $ahead commit(s) from \`$branch\` to \`$upstream\`" >> "$REPORT"
  else
    git push
    echo "- PUSHED \`$repo_name\`: pushed $ahead commit(s) from \`$branch\` to \`$upstream\`" >> "$REPORT"
  fi

  cd "$ROOT"
done

cd - >/dev/null 2>&1 || true

echo "WROTE: $REPORT"
cat "$REPORT"
