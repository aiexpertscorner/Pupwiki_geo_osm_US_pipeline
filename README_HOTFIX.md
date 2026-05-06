# PupWiki extractor hotfix

This patch fixes `src/pupwiki_geo/extract_osm.py` after the broken indentation on `main`.

## Apply from repo root

PowerShell:

```powershell
Copy-Item ".\src\pupwiki_geo\extract_osm.py" ".\src\pupwiki_geo\extract_osm.py.bak" -Force
# Extract this zip over the repo root, then:
python -m py_compile ".\src\pupwiki_geo\extract_osm.py"
python -m pip install -e .
python -m pupwiki_geo.cli extract-osm --pbf ".\data-raw\osm\google-drive\us-latest.osm.pbf" --out ".\data-work\osm\test-core-v2.ndjson" --include-categories core --object-types node --batch-size 0 --max-written 1000 --yes
```
