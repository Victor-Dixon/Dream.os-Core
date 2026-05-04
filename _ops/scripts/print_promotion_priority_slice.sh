#!/usr/bin/env bash
set -u

REPORT_DIR="${1:-$(ls -td _ops/reports/variant_promotions_* | head -1)}"

echo "# Promotion Priority Slice"
echo "report_dir=$REPORT_DIR"
echo

for manifest in "$REPORT_DIR"/*_promotion_manifest.tsv; do
  [ -f "$manifest" ] || continue
  name="$(basename "$manifest" _promotion_manifest.tsv)"

  echo "## $name"
  echo
  echo "### PROMOTE_CONTRACT"
  grep '^PROMOTE_CONTRACT	' "$manifest" | sed 's/^/ - /' | head -80 || true
  echo

  echo "### PROMOTE_TEST"
  grep '^PROMOTE_TEST	' "$manifest" | sed 's/^/ - /' | head -80 || true
  echo

  echo "### PROMOTE_REVIEW top source lanes"
  grep '^PROMOTE_REVIEW	' "$manifest" \
    | awk -F '\t' '{print $2}' \
    | cut -d/ -f1-3 \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -40
  echo
done

echo "## Git State"
git status --short
