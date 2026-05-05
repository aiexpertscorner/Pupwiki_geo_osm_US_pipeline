#!/usr/bin/env bash
set -euo pipefail
BUILD_DIR="${1:-data-build/places/v1}"
BUCKET="${R2_BUCKET:-pupwiki-places}"
PREFIX="${R2_PREFIX:-places/v1}"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "Install Wrangler first: npm i -g wrangler"
  exit 1
fi

find "$BUILD_DIR" -type f \( -name '*.json' -o -name '*.json.gz' -o -name '*.json.br' \) -print0 | while IFS= read -r -d '' file; do
  rel="${file#$BUILD_DIR/}"
  key="$PREFIX/$rel"
  content_type="application/json; charset=utf-8"
  cache="public, max-age=31536000, immutable"
  if [[ "$rel" == "manifest.json" || "$rel" == "page-manifest.json" || "$rel" == search* ]]; then
    cache="public, max-age=3600, stale-while-revalidate=86400"
  fi
  extra=()
  if [[ "$file" == *.gz ]]; then extra+=(--content-encoding gzip); fi
  if [[ "$file" == *.br ]]; then extra+=(--content-encoding br); fi
  wrangler r2 object put "$BUCKET/$key" --file "$file" --content-type "$content_type" --cache-control "$cache" "${extra[@]}"
done
