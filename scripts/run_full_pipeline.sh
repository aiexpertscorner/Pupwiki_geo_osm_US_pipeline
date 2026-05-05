#!/usr/bin/env bash
set -euo pipefail

PBF="${PUPWIKI_OSM_PBF:-data-raw/osm/google-drive/us-latest.osm.pbf}"
VERSION="${PUPWIKI_PLACES_VERSION:-v1}"
BUILD="data-build/places/${VERSION}"

python -m pupwiki_geo.cli init

if [[ ! -f "$PBF" ]]; then
  echo "Missing OSM PBF at $PBF"
  echo "Download with: python -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY"
  exit 1
fi

python -m pupwiki_geo.cli extract-osm --pbf "$PBF" --out data-work/osm/us-dog-pois.ndjson
python -m pupwiki_geo.cli build \
  --input data-work/osm/us-dog-pois.ndjson \
  --states data-work/boundaries/us-states.geojson \
  --places data-work/boundaries/us-places.geojson \
  --counties data-work/boundaries/us-counties.geojson \
  --out "$BUILD"
python -m pupwiki_geo.cli qa --build "$BUILD"
python -m pupwiki_geo.cli compress --build "$BUILD"
