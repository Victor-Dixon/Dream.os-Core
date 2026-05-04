#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="_ops/reports/cleanup_intel_$STAMP.md"

mkdir -p _ops/reports

all_files() {
  find . -path ./.git -prune -o -type f -print
}

all_dirs() {
  find . -path ./.git -prune -o -type d -print
}

{
  echo "# DreamOS Cleanup Intelligence Report"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Repo: $(pwd)"
  echo
  echo "## Git State"
  echo '```text'
  git branch --show-current || true
  git status --short || true
  echo '```'
  echo

  echo "## File Counts"
  echo '```text'
  echo "files_total=$(all_files | wc -l)"
  echo "dirs_total=$(all_dirs | wc -l)"
  echo "pycache_dirs=$(all_dirs | grep '/__pycache__$' | wc -l)"
  echo "pyc_files=$(all_files | grep '\.pyc$' | wc -l)"
  echo "json_files=$(all_files | grep '\.json$' | wc -l)"
  echo "md_files=$(all_files | grep '\.md$' | wc -l)"
  echo "yaml_files=$(all_files | grep -E '\.ya?ml$' | wc -l)"
  echo "js_files=$(all_files | grep '\.js$' | wc -l)"
  echo "html_files=$(all_files | grep '\.html$' | wc -l)"
  echo "tsx_files=$(all_files | grep '\.tsx$' | wc -l)"
  echo '```'
  echo

  echo "## Top Extensions"
  echo '```text'
  all_files | awk '
    {
      n=$0
      sub(/^.*\//,"",n)
      if (n !~ /\./) ext="<none>"
      else { ext=n; sub(/^.*\./,".",ext) }
      count[ext]++
    }
    END {
      for (e in count) print count[e], e
    }
  ' | sort -nr | head -40
  echo '```'
  echo

  echo "## Largest Directories"
  echo '```text'
  all_files | sed 's#/[^/]*$##' | sort | uniq -c | sort -nr | head -80
  echo '```'
  echo

  echo "## JSON / MD Hotspots"
  echo '```text'
  all_files | grep -E '\.(json|md)$' | sed 's#/[^/]*$##' | sort | uniq -c | sort -nr | head -80 || true
  echo '```'
  echo

  echo "## YAML / JS / HTML / TSX Hotspots"
  echo '```text'
  all_files | grep -E '\.(yaml|yml|js|html|tsx)$' | sed 's#/[^/]*$##' | sort | uniq -c | sort -nr | head -80 || true
  echo '```'
  echo

  echo "## Generated Cache"
  echo '```text'
  all_dirs | grep '/__pycache__$' | head -120 || true
  all_files | grep '\.pyc$' | head -120 || true
  echo '```'
  echo

  echo "## Candidate Legacy Paths"
  echo '```text'
  all_files | grep -E '/(archive|duplicates|orphan|runtime|sandbox|vendor|examples|snapshots|test_migration)/' | head -200 || true
  echo '```'
  echo

  echo "## Preserve Candidates"
  echo '```text'
  all_files | grep -E '(/schemas/|/config/|schema.*\.json$|pyproject\.toml$|pytest\.ini$|requirements(\.dev)?\.txt$)' | sort | head -200 || true
  echo '```'
  echo

  echo "## Suggested Next Lane"
  echo
  echo "Paste this report back. Next cleanup should target one largest generated or duplicate category only."
} > "$REPORT"

echo "WROTE: $REPORT"
sed -n '1,260p' "$REPORT"
