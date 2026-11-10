#!/usr/bin/env bash
# Pack platform ZIP: solution.py + psb_*.py + requirements.txt (no .env / vendor / node_modules).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-"$ROOT/dist/psb_submission.zip"}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$(dirname "$OUT")" "$TMP/pack"
cp "$ROOT/solution.py" "$ROOT/requirements.txt" "$TMP/pack/"
cp "$ROOT"/psb_*.py "$TMP/pack/"

# Drop any accidental caches if present
rm -rf "$TMP/pack/__pycache__" "$TMP/pack"/*.pyc 2>/dev/null || true

rm -f "$OUT"
(
  cd "$TMP/pack"
  zip -9 -r "$OUT" solution.py requirements.txt psb_*.py >/dev/null
)

SIZE="$(wc -c < "$OUT" | tr -d ' ')"
MAX=$((128 * 1024 * 1024))
echo "Wrote $OUT ($SIZE bytes)"
echo "Contents:"
unzip -l "$OUT"
if (( SIZE > MAX )); then
  echo "ERROR: ZIP exceeds 128MB ($SIZE > $MAX)" >&2
  exit 1
fi
echo "OK: under 128MB. Upload manually if needed — this script does not submit."
