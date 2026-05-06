# PupWiki Geo enrichment update

This patch upgrades the OSM extraction layer from a basic matcher to a production-oriented enrichment flow.

## Files in this patch

- `configs/osm_dog_categories.json` — expanded dog POI taxonomy based on the uploaded OSM tag pack.
- `src/pupwiki_geo/categories.py` — exact matched rule metadata, legacy ID mapping, tier/indexable metadata.
- `src/pupwiki_geo/extract_osm.py` — interactive extraction, progress logging, batches, max limits, rule metadata in each row.
- `src/pupwiki_geo/normalize.py` — contact cleaning, address object, displayName, slugSeed, category metadata, qualityScore.
- `src/pupwiki_geo/qa.py` — category counts and review NDJSON outputs.
- `src/pupwiki_geo/cli.py` — new CLI flags and `extract-qa` command.

## Install after copying

```powershell
python -m pip install -e .
```

## Fast smoke test

```powershell
python -m pupwiki_geo.cli extract-osm --pbf ".\data-raw\osm\google-drive\us-latest.osm.pbf" --out ".\data-work\osm\test-core-nodes.ndjson" --include-categories core --object-types node --batch-size 0 --max-written 1000 --yes
python -m pupwiki_geo.cli extract-qa --input ".\data-work\osm\test-core-nodes.ndjson" --out ".\data-work\qa\test-core-nodes"
```

## More realistic smoke test

```powershell
python -m pupwiki_geo.cli extract-osm --pbf ".\data-raw\osm\google-drive\us-latest.osm.pbf" --out ".\data-work\osm\test-core-nodes-ways.ndjson" --include-categories core --object-types node,way --batch-size 0 --max-written 1000 --yes
python -m pupwiki_geo.cli extract-qa --input ".\data-work\osm\test-core-nodes-ways.ndjson" --out ".\data-work\qa\test-core-nodes-ways"
```

## Production extraction

```powershell
python -m pupwiki_geo.cli extract-osm --pbf ".\data-raw\osm\google-drive\us-latest.osm.pbf" --out ".\data-work\osm\us-dog-pois.ndjson" --include-categories core --object-types node,way --batch-size 50000 --yes
python -m pupwiki_geo.cli extract-qa --input ".\data-work\osm\us-dog-pois.manifest.json" --out ".\data-work\qa\us-dog-pois"
```

Note: `extract-qa` currently reads NDJSON files, not batch manifests. For batched production output, run QA against merged NDJSON or individual part files until a manifest-aware QA command is added.
