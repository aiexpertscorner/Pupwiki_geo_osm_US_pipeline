param(
  [string]$Pbf = "data-raw/osm/google-drive/us-latest.osm.pbf",
  [string]$Version = "v1"
)
$ErrorActionPreference = "Stop"
$Build = "data-build/places/$Version"
python -m pupwiki_geo.cli init
if (!(Test-Path $Pbf)) {
  Write-Host "Missing OSM PBF at $Pbf"
  Write-Host "Download with: python -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY"
  exit 1
}
python -m pupwiki_geo.cli extract-osm --pbf $Pbf --out data-work/osm/us-dog-pois.ndjson
python -m pupwiki_geo.cli build --input data-work/osm/us-dog-pois.ndjson --states data-work/boundaries/us-states.geojson --places data-work/boundaries/us-places.geojson --counties data-work/boundaries/us-counties.geojson --out $Build
python -m pupwiki_geo.cli qa --build $Build
python -m pupwiki_geo.cli compress --build $Build
