#!/usr/bin/env bash
set -euo pipefail

# Requires:
#   npm install -D wrangler
#   wrangler login
#
# Usage:
#   BUCKET=pupwiki-places ./scripts/upload_r2.sh data-build/places/v1 places/v1

SRC_DIR="${1:-data-build/places/v1}"
R2_PREFIX="${2:-places/v1}"
BUCKET="${BUCKET:-pupwiki-places}"

echo "Uploading $SRC_DIR to R2 bucket $BUCKET at prefix $R2_PREFIX"

find "$SRC_DIR" -type f \( -name "*.json" -o -name "*.json.gz" \) | while read -r file; do
  rel="${file#$SRC_DIR/}"
  key="$R2_PREFIX/$rel"

  if [[ "$file" == *.gz ]]; then
    wrangler r2 object put "$BUCKET/$key" \
      --file "$file" \
      --content-type "application/json; charset=utf-8" \
      --content-encoding "gzip"
  else
    wrangler r2 object put "$BUCKET/$key" \
      --file "$file" \
      --content-type "application/json; charset=utf-8"
  fi
done

echo "Upload complete"
