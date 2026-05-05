param(
  [string]$Xlsm = "geodatapupwiki.xlsm",
  [switch]$IncludeLargeOsm,
  [switch]$IncludeOptional,
  [switch]$VerifyRemote
)
$ErrorActionPreference = "Stop"
python scripts/create_folder_structure.py --manifest config/datasets.generated.json --root .
if (Test-Path $Xlsm) { python scripts/extract_xlsm_manifest.py --xlsm $Xlsm --out config/datasets.from-xlsm.json --csv config/datasets.from-xlsm.csv }
$argsList = @("scripts/download_geo_datasets.py", "--manifest", "config/datasets.generated.json", "--root", ".", "--priority", "P1")
if ($IncludeLargeOsm) { $argsList += "--include-large-osm" }
if ($IncludeOptional) { $argsList += "--include-optional" }
if ($VerifyRemote) { $argsList += "--verify-remote" }
python @argsList
python scripts/verify_geo_datasets.py --manifest config/datasets.generated.json --root . --priority P1
