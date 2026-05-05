# PupWiki Dog Services Map — Claude Code Pack

Generated: 2026-04-26

This pack helps Claude Code build a production-ready **Dog Services Map** feature for PupWiki using:

- MapLibre GL JS
- Static-first JSON/GeoJSON generated datasets
- Existing geo/location datasets in the repo where available
- OSM-derived category config
- Future-ready D1/R2/API architecture
- Mobile-first PupWiki UI
- OSM attribution and service disclaimers

## Recommended run order

Use these prompts in separate Claude Code sessions/runs to reduce timeout risk:

1. `prompts/00_MASTER_PROMPT.md`
2. `prompts/01_REPO_AUDIT.md`
3. `prompts/02_DATA_CONTRACT_AND_OSM_CONFIG.md`
4. `prompts/03_GENERATOR_SCRIPTS.md`
5. `prompts/04_MAPLIBRE_COMPONENTS.md`
6. `prompts/05_ROUTE_INTEGRATION.md`
7. `prompts/08_QA_PERFORMANCE_CLEANUP.md`

Later, after the MVP works:

8. `prompts/06_SEO_LOCATION_PAGES.md`
9. `prompts/07_CLOUDFLARE_D1_R2_OPTIONAL.md`

## Core principle

Do **not** call Overpass, Nominatim, or OpenStreetMap endpoints from the browser for every visitor.

Use OSM/GeoJSON as input to a generator, then serve your own generated datasets:

```txt
OSM / GeoJSON / local datasets
        ↓
PupWiki generator
        ↓
public/data/dog-services/us/all.geojson
public/data/dog-services/us/all.json
        ↓
MapLibre map + SEO/location pages
```

## MVP target

The first production-safe version should include:

- `/dog-services/`
- MapLibre map
- Filters
- Service cards
- Fallback sample data
- Generated `public/data/dog-services/us/all.geojson`
- Visible OSM attribution
- General verification disclaimer

## Do not let Claude do everything in one run

Each phase should end with:

- changed files summary
- build/typecheck run if available
- scoped fixes only
- no broad refactors
