# Runbook

## 1. Initialize

```bash
python -m pupwiki_geo.cli init
```

## 2. Download boundaries and support datasets

```bash
python -m pupwiki_geo.cli download --priority P1 --verify-remote
python -m pupwiki_geo.cli unpack --root data-raw
```

## 3. Add the full OSM PBF

Preferred target:

```txt
data-raw/osm/google-drive/us-latest.osm.pbf
```

Automated attempt:

```bash
python -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY
```

If Google blocks automated large-file download, use Google Drive Desktop or rclone, then place the file at the path above.

## 4. Convert Census boundaries

Example:

```bash
python scripts/convert_boundaries_to_geojson.py \
  --input data-raw/census/2025/cartographic/states_500k/cb_2025_us_state_500k/cb_2025_us_state_500k.shp \
  --out data-work/boundaries/us-states.geojson
```

Repeat for places/counties/county subdivisions.

## 5. Extract OSM dog POIs

```bash
python -m pupwiki_geo.cli extract-osm \
  --pbf data-raw/osm/google-drive/us-latest.osm.pbf \
  --out data-work/osm/us-dog-pois.ndjson
```

## 6. Build shards

```bash
python -m pupwiki_geo.cli build \
  --input data-work/osm/us-dog-pois.ndjson \
  --states data-work/boundaries/us-states.geojson \
  --places data-work/boundaries/us-places.geojson \
  --counties data-work/boundaries/us-counties.geojson \
  --out data-build/places/v1
```

## 7. QA and publish

```bash
python -m pupwiki_geo.cli qa --build data-build/places/v1
python -m pupwiki_geo.cli compress --build data-build/places/v1
scripts/upload_r2.sh data-build/places/v1
```
