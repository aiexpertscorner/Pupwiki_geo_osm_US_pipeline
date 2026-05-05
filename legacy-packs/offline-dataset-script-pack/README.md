# PupWiki Geo Offline Dataset Download Pack

Clean-start script pack for building the raw-data layer of the PupWiki geo / OpenStreetMap dog POI pipeline.

Generated from `geodatapupwiki.xlsm`.

## What is inside

- `config/datasets.generated.json` — workbook manifest + inferred direct download candidates.
- `config/datasets.generated.csv` — readable XLSM row inventory.
- `config/osm_dog_poi_tags.json` — dog-service OSM tag categories for the later extraction step.
- `scripts/create_folder_structure.py` — creates local folders and `.gitignore`.
- `scripts/download_geo_datasets.py` — resumable downloader with filters and dry-run.
- `scripts/verify_geo_datasets.py` — local existence/ZIP/GZIP checks.
- `scripts/unpack_archives.py` — extracts downloaded ZIP files.
- `scripts/extract_xlsm_manifest.py` — re-reads the XLSM without Excel/openpyxl.
- `docs/manual_downloads.todo.md` — optional/API-key/large/manual source queue.

## Clean start

Unzip into a new folder. Copy `geodatapupwiki.xlsm` into the root only if you want to re-extract the workbook rows.

```powershell
python --version
.\scriptsun_p1.ps1 -Xlsm .\geodatapupwiki.xlsm -VerifyRemote
```

```bash
python3 --version
bash scripts/run_p1.sh geodatapupwiki.xlsm --verify-remote
```

## Safe default behavior

The default P1 run downloads core non-huge direct candidates only: Census cartographic boundary candidates, Census Gazetteer candidates, small ACS MVP API files, OSM attribution page, and GNIS candidate.

It does **not** download the full `us-latest.osm.pbf` unless you explicitly run:

```powershell
python scripts/download_geo_datasets.py --priority P1 --dataset "United States OSM PBF" --include-large-osm
```

## Inspect before downloading

```powershell
python scripts/download_geo_datasets.py --priority P1 --dry-run
python scripts/download_geo_datasets.py --priority P2 --include-optional --dry-run
```

## Unpack and verify

```powershell
python scripts/unpack_archives.py
python scripts/verify_geo_datasets.py --priority P1
python scripts/build_inventory.py
```

## Notes

Some direct URLs are pattern-derived from public Census/Geofabrik/Natural Earth conventions and should be checked with `--verify-remote`. I could not live-verify URLs from this environment.

Keep raw and generated heavy data out of the PupWiki frontend repo. `data-raw/`, `data-work/`, and `data-build/` are intentionally gitignored.
