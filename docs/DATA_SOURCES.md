# Data sources

The canonical source manifest is `configs/datasets.generated.json`. It was generated from the PupWiki geo checklist workbook and then augmented with the Google Drive OSM source.

## Primary source layers

- Full US OpenStreetMap PBF from Google Drive or Geofabrik.
- US Census 2025 cartographic boundaries for states, places, counties, county subdivisions and metro context.
- Census Gazetteer files for centroids and display names.
- TIGER/Line as a precision fallback.
- GNIS / Who's On First for aliases and rural locality enrichment.
- AllThePlaces as future chain/business enrichment.

## Data storage policy

Raw files, shapefiles, PBFs, NDJSONs and full generated shards stay out of Git. Commit only:

- configs
- scripts
- docs
- compact examples
- integration templates
