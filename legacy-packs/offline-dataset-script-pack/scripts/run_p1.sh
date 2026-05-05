#!/usr/bin/env bash
set -euo pipefail
XLSM="${1:-geodatapupwiki.xlsm}"
python3 scripts/create_folder_structure.py --manifest config/datasets.generated.json --root .
if [ -f "$XLSM" ]; then
  python3 scripts/extract_xlsm_manifest.py --xlsm "$XLSM" --out config/datasets.from-xlsm.json --csv config/datasets.from-xlsm.csv
fi
python3 scripts/download_geo_datasets.py --manifest config/datasets.generated.json --root . --priority P1 "${@:2}"
python3 scripts/verify_geo_datasets.py --manifest config/datasets.generated.json --root . --priority P1
