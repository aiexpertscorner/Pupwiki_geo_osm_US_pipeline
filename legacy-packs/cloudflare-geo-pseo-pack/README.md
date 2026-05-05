# PupWiki Cloudflare Geo/PSEO Pack

This pack is designed for PupWiki.com hosted on Cloudflare Pages Free, using a locally generated US OpenStreetMap dog-services dataset.

Core idea:
- Do heavy ETL locally.
- Do not bundle the full dataset into the Astro build.
- Store static shard JSON files in `public/data/places/` for the first phase, or R2 for larger scale.
- Generate only SEO pages that deserve indexing.
- Load map/list data client-side per city/category from small JSON shards.
- Keep all indexes tiny and cacheable.
