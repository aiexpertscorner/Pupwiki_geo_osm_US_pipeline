# Cloudflare Static-First Architecture

## Recommended MVP

For PupWiki, build the first version static-first:

```txt
local OSM/GeoJSON input
        ↓
generator script
        ↓
public/data/dog-services/us/all.geojson
public/data/dog-services/us/all.json
        ↓
Astro/React + MapLibre
```

## Why static-first?

- Fast to ship
- Works on Cloudflare Pages
- No database dependency
- No API keys
- No live OSM rate-limit risk
- Easier to debug
- Search-engine friendly

## Future D1/R2 architecture

```txt
Overpass export / local data
        ↓
Generator / Worker
        ↓
D1 master table
        ↓
R2 large GeoJSON objects
        ↓
Pages Function API
        ↓
MapLibre + SEO pages
```

## Suggested bindings later

```toml
[[d1_databases]]
binding = "DOG_SERVICES_DB"
database_name = "pupwiki-dog-services"
database_id = "..."

[[r2_buckets]]
binding = "DOG_SERVICES_BUCKET"
bucket_name = "pupwiki-dog-services"
```

Do not add required bindings until the static version is working.
