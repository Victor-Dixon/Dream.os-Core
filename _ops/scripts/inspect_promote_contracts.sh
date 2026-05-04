#!/usr/bin/env bash
set -u

CANON="$HOME/projects/DreamOS"
DREAM_OS="$HOME/projects/Dream.os"
VICTOR_OS="$HOME/projects/Victor.os"

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$CANON/_ops/reports/promote_contracts_inspection_$STAMP.md"

mkdir -p "$CANON/_ops/reports"

inspect_pair() {
  label="$1"
  variant="$2"
  path="$3"

  echo "## $label"
  echo
  echo "variant_path=$variant/$path"
  echo "canonical_same_path=$CANON/$path"
  echo

  echo '```text'
  if [ -f "$variant/$path" ]; then
    echo "variant_exists=yes"
    wc -l "$variant/$path" 2>/dev/null || true
    sha256sum "$variant/$path" 2>/dev/null || true
  else
    echo "variant_exists=no"
  fi

  if [ -f "$CANON/$path" ]; then
    echo "canonical_same_path_exists=yes"
    wc -l "$CANON/$path" 2>/dev/null || true
    sha256sum "$CANON/$path" 2>/dev/null || true
  else
    echo "canonical_same_path_exists=no"
  fi
  echo '```'
  echo

  echo "### Variant preview"
  echo
  echo '```text'
  if [ -f "$variant/$path" ]; then
    sed -n '1,80p' "$variant/$path"
  fi
  echo '```'
  echo

  echo "### Same-path diff if canonical exists"
  echo
  echo '```diff'
  if [ -f "$variant/$path" ] && [ -f "$CANON/$path" ]; then
    diff -u "$CANON/$path" "$variant/$path" | sed -n '1,160p' || true
  else
    echo "NO_SAME_PATH_DIFF"
  fi
  echo '```'
  echo
}

{
  echo "# PROMOTE_CONTRACT Inspection"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Canonical: $CANON"
  echo

  inspect_pair "Dream.os merit chain schema" "$DREAM_OS" "core/schemas/merit_chain_schema.json"

  inspect_pair "Victor.os product output schema" "$VICTOR_OS" "src/dreamos/core/tasks/schemas/product_output_schema.py"
  inspect_pair "Victor.os cursor feedback schema" "$VICTOR_OS" "src/dreamos/integrations/cursor/bridge/schemas/cursor_feedback_schema.json"
  inspect_pair "Victor.os gpt command schema" "$VICTOR_OS" "src/dreamos/integrations/cursor/bridge/schemas/gpt_command_schema.json"

  echo "# Suggested First Merge Lane"
  echo
  echo "Do not bulk-copy. Promote contracts one at a time under canonical paths after deciding ownership."
} > "$REPORT"

echo "WROTE: $REPORT"
cat "$REPORT"
