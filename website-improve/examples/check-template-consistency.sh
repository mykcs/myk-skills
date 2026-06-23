#!/bin/bash
# examples/check-template-consistency.sh
# Template consistency check (per website-improve §A.7 v3.10.0).
# Verify N pages sharing same template have same structural elements.
#
# Usage: bash check-template-consistency.sh <glob-pattern> [template-elements...]
# Example: bash check-template-consistency.sh 'src/pages/{en,zh}/paper/*/slide.astro' \
#            slide-top-accent slide-info-corner kicker takeaway-item
#
# Output: per-file count of each template element, plus diff vs baseline file.

set -e
shopt -s nullglob  # required: expand to empty if no match (avoid literal pattern)
GLOB="${1:?Usage: $0 <glob-pattern> [template-elements...]}"
shift
ELEMENTS=("$@")

if [ ${#ELEMENTS[@]} -eq 0 ]; then
  ELEMENTS=("slide-top-accent" "slide-info-corner" "kicker" "takeaway-item" "accent-bar")
fi

echo "=== Template consistency check (website-improve §A.7 v3.10.0) ==="
echo ""
echo "Files matching: $GLOB"
echo "Elements tracked: ${ELEMENTS[*]}"
echo ""

# Collect per-file element counts
TMP=$(mktemp)
trap "rm -f $TMP" EXIT

# Expand glob into array (eval needed because $GLOB is string variable, not literal glob)
FILES=()
while IFS= read -r f; do
  [ -f "$f" ] && FILES+=("$f")
done < <(eval "ls -1 $GLOB 2>/dev/null")

if [ ${#FILES[@]} -eq 0 ]; then
  echo "ERROR: No files matched glob: $GLOB"
  exit 1
fi

for f in "${FILES[@]}"; do
  printf "%s:\n" "$f" >> "$TMP"
  for elem in "${ELEMENTS[@]}"; do
    count=$(grep -c "$elem" "$f" 2>/dev/null || echo 0)
    printf "  %s: %s\n" "$elem" "$count" >> "$TMP"
  done
  echo "" >> "$TMP"
done

cat "$TMP"

# Detect outliers (count differs > 2x median across files)
echo ""
echo "=== Outlier detection (count > 2x OR < 0.5x median) ==="
for elem in "${ELEMENTS[@]}"; do
  counts=$(grep -A 5 "" "$TMP" | grep -E "^  ${elem}:" | awk '{print $2}' | sort -n)
  median=$(echo "$counts" | awk 'NR==int((NR+1)/2) || NR==int(NR/2) {print; exit}')
  outliers=$(echo "$counts" | awk -v med="$median" 'BEGIN{n=0} {if ($1 > med*2 || $1 < med*0.5) {n++}} END{print n+0}')
  echo "  $elem: median=$median, outliers=$outliers"
done