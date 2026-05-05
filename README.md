# PupWiki Geo Pipeline

Clean starter repository for the PupWiki US dog-services/local-discovery pipeline.

The goal is not a tiny demo. The goal is a scalable local ETL pipeline that can process a full US OpenStreetMap PBF, enrich dog-related POIs with official Census boundaries, produce high-quality state/city/category shards, and feed PupWiki.com with MapLibre + pSEO-ready data.

## What this repo builds

```txt
Google Drive / local OSM PBF / Geofabrik
        ↓
OSM dog POI extraction
        ↓
normalized NDJSON
        ↓
Census / WOF / GNIS boundary enrichment
        ↓
quality scoring + dedupe
        ↓
Cloudflare-ready JSON shards + manifests
        ↓
PupWiki Astro pages + MapLibre components
```

## Your full US OSM source

Your Google Drive OSM file is configured here:

```txt
https://drive.google.com/file/d/1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY/view?usp=drivesdk
```

It is intentionally kept outside Git. Target local path:

```txt
data-raw/osm/google-drive/us-latest.osm.pbf
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m pupwiki_geo.cli init
```

Download core datasets from `configs/datasets.generated.json`:

```bash
python -m pupwiki_geo.cli download --priority P1 --verify-remote
```

Download the full US OSM file from Drive, if the Drive file is shared/public enough for `gdown`:

```bash
python -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY
```

If Drive blocks automated download, put the file manually at:

```txt
data-raw/osm/google-drive/us-latest.osm.pbf
```

Extract dog POIs:

```bash
python -m pupwiki_geo.cli extract-osm \
  --pbf data-raw/osm/google-drive/us-latest.osm.pbf \
  --out data-work/osm/us-dog-pois.ndjson
```

Build frontend/R2 shards:

```bash
python -m pupwiki_geo.cli build \
  --input data-work/osm/us-dog-pois.ndjson \
  --states data-work/boundaries/us-states.geojson \
  --places data-work/boundaries/us-places.geojson \
  --counties data-work/boundaries/us-counties.geojson \
  --out data-build/places/v1
```

Run QA:

```bash
python -m pupwiki_geo.cli qa --build data-build/places/v1
```

Copy compact frontend assets into a PupWiki Astro repo:

```bash
python -m pupwiki_geo.cli copy-public \
  --build data-build/places/v1 \
  --pupwiki ../Mr-Doggo-Style \
  --mode hybrid
```

## Recommended output model

For a full US run, use the hybrid Cloudflare approach:

- **PupWiki Astro repo**: pages, search index, compact manifests.
- **Cloudflare R2**: full POI shards and QA reports.
- **Versioned paths**: `places/v1/...` so browser caches can be long-lived.

## Repository layout

```txt
configs/              dataset manifest, OSM categories, thresholds
src/pupwiki_geo/      Python package / CLI
docs/                 architecture, data contract, runbook, integration notes
scripts/              shell wrappers and one-command pipelines
astro-integration/    Astro components/templates for PupWiki.com
cloudflare/           headers, R2 upload helpers, wrangler notes
legacy-packs/         original prompt/script packs kept for traceability
```

## License / attribution

OSM-derived frontend output must show:

```txt
© OpenStreetMap contributors. Data available under the Open Database License.
```

Do not claim places are “verified”, “best”, “top-rated”, “open now”, or “24/7” unless you add a source that supports those claims.
