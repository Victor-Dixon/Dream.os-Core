#!/usr/bin/env bash
set -u

CANON="${1:-$HOME/projects/DreamOS}"
shift || true

if [ "$#" -gt 0 ]; then
  VARIANTS=("$@")
else
  VARIANTS=("$HOME/projects/Dream.os" "$HOME/projects/Victor.os")
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="$CANON/_ops/reports/variant_promotions_$STAMP"
mkdir -p "$REPORT_DIR"

rel_files() {
  repo="$1"
  find "$repo" -path "$repo/.git" -prune -o -type f -print 2>/dev/null \
    | sed "s#^$repo/##" \
    | grep -v '^.git/' \
    | sort
}

classify_file() {
  path="$1"

  case "$path" in
    *_ops/reports/*|_ops/reports/*|runtime/tasks/*)
      echo "REFERENCE"
      ;;
    *README*|*.md)
      echo "REFERENCE"
      ;;
    *__pycache__*|*.pyc|*.pyo|.pytest_cache/*)
      echo "DELETE"
      ;;
    archive/*|runtime/*|sandbox/*|cache/*|chrome_profile/*|*/cache/*)
      echo "DELETE"
      ;;
    tests/*|src/tests/*|*/tests/*)
      echo "PROMOTE_TEST"
      ;;
    contracts/*|*/schemas/*|*schema*.json)
      echo "PROMOTE_CONTRACT"
      ;;
    src/*|dreamos/*|core/*|social/*|interfaces/*|config/*|scripts/*|tools/*)
      echo "PROMOTE_REVIEW"
      ;;
    *.py|*.yaml|*.yml|*.json|*.toml|*.ini)
      echo "PROMOTE_REVIEW"
      ;;
    *)
      echo "DEFER"
      ;;
  esac
}

for variant in "${VARIANTS[@]}"; do
  [ -d "$variant" ] || continue

  name="$(basename "$variant")"
  md="$REPORT_DIR/${name}_promotion_manifest.md"
  csv="$REPORT_DIR/${name}_promotion_manifest.tsv"

  canon_list="$(mktemp)"
  variant_list="$(mktemp)"
  exact_overlap="$(mktemp)"
  unique_variant="$(mktemp)"

  rel_files "$CANON" > "$canon_list"
  rel_files "$variant" > "$variant_list"

  comm -12 "$canon_list" "$variant_list" > "$exact_overlap"
  comm -13 "$canon_list" "$variant_list" > "$unique_variant"

  {
    echo "# $name Promotion Manifest"
    echo
    echo "Generated: $(date -Iseconds)"
    echo "Canonical: $CANON"
    echo "Variant: $variant"
    echo
    echo "## Counts"
    echo
    echo '```text'
    echo "canonical_files=$(wc -l < "$canon_list")"
    echo "variant_files=$(wc -l < "$variant_list")"
    echo "exact_path_overlap=$(wc -l < "$exact_overlap")"
    echo "unique_variant_files=$(wc -l < "$unique_variant")"
    echo '```'
    echo
    echo "## Exact Path Overlap"
    echo
    echo '```text'
    sed -n '1,120p' "$exact_overlap"
    echo '```'
    echo
    echo "## Unique Variant Files By Classification"
    echo
    echo '```text'
    while IFS= read -r path; do
      class="$(classify_file "$path")"
      printf "%-18s %s\n" "$class" "$path"
    done < "$unique_variant" | sort
    echo '```'
    echo
    echo "## Promotion Rule"
    echo
    echo "- PROMOTE_CONTRACT: inspect first; likely high-value schema/config."
    echo "- PROMOTE_TEST: import only if it protects canonical behavior."
    echo "- PROMOTE_REVIEW: inspect by lane before copying."
    echo "- REFERENCE: useful context, not copied by default."
    echo "- DELETE: already-pruned or generated/noise category."
    echo "- DEFER: unknown; review only if needed."
  } > "$md"

  {
    echo -e "classification\tpath"
    while IFS= read -r path; do
      class="$(classify_file "$path")"
      echo -e "$class\t$path"
    done < "$unique_variant" | sort
  } > "$csv"

  rm -f "$canon_list" "$variant_list" "$exact_overlap" "$unique_variant"

  echo "WROTE: $md"
  echo "WROTE: $csv"
done

cat > "$REPORT_DIR/README.md" << README
# Variant Promotion Manifests

Generated: $(date -Iseconds)

Canonical:

- $CANON

Variants:

$(printf -- '- %s\n' "${VARIANTS[@]}")

Next step:

1. Review PROMOTE_CONTRACT first.
2. Review PROMOTE_TEST second.
3. Review PROMOTE_REVIEW by functional lane.
4. Do not bulk merge a whole variant.
README

echo "REPORT_DIR=$REPORT_DIR"
find "$REPORT_DIR" -maxdepth 1 -type f -print | sort
