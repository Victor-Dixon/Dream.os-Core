#!/usr/bin/env bash
set -u

ROOT="${1:-$HOME/projects}"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$HOME/projects/DreamOS/_ops/reports/variant_cleanup_census_dreamos_only_$STAMP.md"

mkdir -p "$HOME/projects/DreamOS/_ops/reports"

count_files() {
  repo="$1"
  find "$repo" -path "$repo/.git" -prune -o -type f -print 2>/dev/null | wc -l
}

count_dirs() {
  repo="$1"
  find "$repo" -path "$repo/.git" -prune -o -type d -print 2>/dev/null | wc -l
}

count_ext() {
  repo="$1"
  pattern="$2"
  find "$repo" -path "$repo/.git" -prune -o -type f -name "$pattern" -print 2>/dev/null | wc -l
}

count_yaml() {
  repo="$1"
  {
    find "$repo" -path "$repo/.git" -prune -o -type f -name "*.yaml" -print 2>/dev/null
    find "$repo" -path "$repo/.git" -prune -o -type f -name "*.yml" -print 2>/dev/null
  } | wc -l
}

dirty_count() {
  repo="$1"
  git -C "$repo" status --short 2>/dev/null | wc -l
}

top_dirs() {
  repo="$1"
  find "$repo" -path "$repo/.git" -prune -o -type f -print 2>/dev/null \
    | sed "s#^$repo/##" \
    | sed 's#/[^/]*$##' \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -20
}

{
  echo "# DreamOS-Only Variant Cleanup Census"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Root: $ROOT"
  echo
  echo "Excluded: AgentTools, because it is a toolbelt repo, not a Dream.OS variant."
  echo
  echo "## Summary"
  echo
  echo '```text'
  printf "%-24s %-24s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s\n" "repo" "branch" "dirty" "files" "dirs" "pyc" "json" "md" "yaml" "js"
  printf "%-24s %-24s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s\n" "----" "------" "-----" "-----" "----" "---" "----" "--" "----" "--"

  for repo in "$ROOT"/DreamOS "$ROOT"/Dream.os "$ROOT"/Victor.os "$ROOT"/Dream.os-Core "$ROOT"/DreamOS_* "$ROOT"/Dream.os_* "$ROOT"/Dream_*; do
    [ -d "$repo/.git" ] || continue
    name="$(basename "$repo")"
    branch="$(git -C "$repo" branch --show-current 2>/dev/null || echo UNKNOWN)"
    printf "%-24s %-24s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s\n" \
      "$name" \
      "$branch" \
      "$(dirty_count "$repo")" \
      "$(count_files "$repo")" \
      "$(count_dirs "$repo")" \
      "$(count_ext "$repo" "*.pyc")" \
      "$(count_ext "$repo" "*.json")" \
      "$(count_ext "$repo" "*.md")" \
      "$(count_yaml "$repo")" \
      "$(count_ext "$repo" "*.js")"
  done
  echo '```'
  echo

  echo "## Top Directories"
  for repo in "$ROOT"/DreamOS "$ROOT"/Dream.os "$ROOT"/Victor.os "$ROOT"/Dream.os-Core "$ROOT"/DreamOS_* "$ROOT"/Dream.os_* "$ROOT"/Dream_*; do
    [ -d "$repo/.git" ] || continue
    name="$(basename "$repo")"
    echo
    echo "### $name"
    echo '```text'
    top_dirs "$repo"
    echo '```'
  done

  echo
  echo "## Next Rule"
  echo
  echo "Clean only remaining dirty Dream.OS variants. If all are clean, stop pruning and generate promote manifests."
} > "$REPORT"

echo "WROTE: $REPORT"
cat "$REPORT"
