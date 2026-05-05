#!/usr/bin/env bash
set -euo pipefail

CANON="$HOME/projects/DreamOS"
VARIANT="$HOME/projects/AutoDream.Os"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUTDIR="$CANON/_ops/reports/autodream_promotions_$STAMP"
MD="$OUTDIR/AutoDream.Os_promotion_manifest.md"
TSV="$OUTDIR/AutoDream.Os_promotion_manifest.tsv"

mkdir -p "$OUTDIR"

classify() {
  path="$1"

  case "$path" in
    *.pyc|*/__pycache__/*|.pytest_cache/*)
      echo "IGNORE_CACHE"
      ;;
    *_report.md|*_REPORT.md|*REPORT*.md|*SUMMARY*.md|*STATUS*.md|*ANALYSIS*.md|*COMPLETE*.md)
      echo "PROMOTE_REVIEW"
      ;;
    contracts/*|schemas/*|*/schemas/*|*schema*.json|*contract*.json|*contract*.md)
      echo "PROMOTE_CONTRACT"
      ;;
    tests/*|*/tests/*|test_*.py|*_test.py|*.test.tsx)
      echo "PROMOTE_TEST"
      ;;
    config/*|*.yaml|*.yml|*.toml|requirements*.txt|package.json|pytest.ini)
      echo "PROMOTE_CONFIG"
      ;;
    src/*|core/*|tools/*|tools_v2/*|scripts/*|extensions/*|systems/*)
      echo "PROMOTE_REVIEW"
      ;;
    docs/*|swarm_brain/*)
      echo "PROMOTE_DOC_REVIEW"
      ;;
    *)
      echo "PROMOTE_REVIEW"
      ;;
  esac
}

{
  echo -e "class\tpath\tsize_bytes\tsha256"
  cd "$VARIANT"
  find . -path ./.git -prune -o -type f -print \
    | sed 's#^\./##' \
    | sort \
    | while IFS= read -r path; do
        class="$(classify "$path")"
        size="$(wc -c < "$path" | tr -d ' ')"
        sha="$(sha256sum "$path" | awk '{print $1}')"
        echo -e "$class\t$path\t$size\t$sha"
      done
} > "$TSV"

{
  echo "# AutoDream.Os Promotion Manifest"
  echo
  echo "Generated: $(date -Iseconds)"
  echo "Canonical: $CANON"
  echo "Variant: $VARIANT"
  echo
  echo "## Counts By Class"
  echo
  echo '```text'
  cut -f1 "$TSV" | tail -n +2 | sort | uniq -c | sort -nr
  echo '```'
  echo
  echo "## PROMOTE_CONTRACT"
  echo
  echo '```text'
  awk -F '\t' '$1=="PROMOTE_CONTRACT"{print $2}' "$TSV" | sed -n '1,200p'
  echo '```'
  echo
  echo "## PROMOTE_CONFIG"
  echo
  echo '```text'
  awk -F '\t' '$1=="PROMOTE_CONFIG"{print $2}' "$TSV" | sed -n '1,200p'
  echo '```'
  echo
  echo "## PROMOTE_TEST"
  echo
  echo '```text'
  awk -F '\t' '$1=="PROMOTE_TEST"{print $2}' "$TSV" | sed -n '1,240p'
  echo '```'
  echo
  echo "## PROMOTE_REVIEW Top Source Lanes"
  echo
  echo '```text'
  awk -F '\t' '$1=="PROMOTE_REVIEW"{print $2}' "$TSV" \
    | sed 's#/[^/]*$##' \
    | sort \
    | uniq -c \
    | sort -nr \
    | sed -n '1,120p'
  echo '```'
  echo
  echo "## PROMOTE_DOC_REVIEW Top Doc Lanes"
  echo
  echo '```text'
  awk -F '\t' '$1=="PROMOTE_DOC_REVIEW"{print $2}' "$TSV" \
    | sed 's#/[^/]*$##' \
    | sort \
    | uniq -c \
    | sort -nr \
    | sed -n '1,120p'
  echo '```'
  echo
  echo "## Suggested First Merge Lane"
  echo
  echo "Do not bulk-copy. Inspect contracts/config first, then tests, then source lanes."
} > "$MD"

cat > "$OUTDIR/README.md" << EOF_README
# AutoDream.Os Promotion Reports

Generated: $(date -Iseconds)

Files:
- AutoDream.Os_promotion_manifest.md
- AutoDream.Os_promotion_manifest.tsv
EOF_README

echo "WROTE: $MD"
echo "WROTE: $TSV"
echo "REPORT_DIR=$OUTDIR"
sed -n '1,260p' "$MD"
