# 03 — Generator Scripts for JSON/GeoJSON Output

Build the Dog Services dataset generator.

Goal:
Create scripts that can generate normalized JSON and GeoJSON outputs from available local input datasets and future OSM exports.

Preferred structure:

```txt
scripts/dog-services/
  generateDogServices.ts
  lib/loadLocalGeoDatasets.ts
  lib/loadOsmExports.ts
  lib/normalizeOsmElement.ts
  lib/classifyDogService.ts
  lib/writeDogServiceOutputs.ts
  lib/dedupeDogServices.ts
  README.md
```

## Input support

1. Existing local datasets discovered in repo.
2. Optional OSM export files if present:
   - data/osm/dog-services/*.json
   - data/osm/dog-services/*.geojson
   - public/data/osm/*.json
3. If no real data exists, use sample seed.

## Output

- public/data/dog-services/index.json
- public/data/dog-services/us/index.json
- public/data/dog-services/us/all.geojson
- public/data/dog-services/us/all.json
- public/data/dog-services/us/categories/{category}.geojson
- public/data/dog-services/us/states/{stateSlug}.json
- public/data/dog-services/us/states/{stateSlug}.geojson
- optional:
  - public/data/dog-services/us/cities/{stateSlug}/{citySlug}.json
  - public/data/dog-services/us/cities/{stateSlug}/{citySlug}/{category}.geojson

## Important

- Do not call Overpass yet unless explicitly configured by env var.
- Do not require API keys.
- Do not fail build if no real OSM data exists.
- Always generate sample fallback output.

## Implement

1. Category classifier based on OSM tags.
2. Normalizer for OSM node/way/relation-like objects:
   - node: lat/lon
   - way/relation: center.lat/center.lon if available
   - tags.name
   - contact fields: phone/contact:phone, website/contact:website, email/contact:email
   - address fields: addr:street, addr:housenumber, addr:city, addr:state, addr:postcode, addr:country
3. Deduping:
   - exact source_id
   - same category + same name + within 25 meters
   - same phone/website in same city
4. Metadata:
   - generated_at
   - record_count
   - category_counts
   - source_summary
   - attribution
   - license note
5. Add npm script if appropriate:
   - `"generate:dog-services": "tsx scripts/dog-services/generateDogServices.ts"`
   - or compatible alternative based on repo setup.

Add `scripts/dog-services/README.md` explaining:

- inputs
- outputs
- how to run
- how to add Overpass export files
- attribution requirements
- why live browser Overpass calls are avoided

Run the generator.
Run typecheck/build if available.
Fix scoped issues only.
