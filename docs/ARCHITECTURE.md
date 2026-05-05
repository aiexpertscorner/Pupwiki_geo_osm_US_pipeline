# Architecture

PupWiki Geo Pipeline is a local-first ETL system for US dog-service discovery.

## Stages

1. **Dataset ingest**: Census, GNIS, WOF, AllThePlaces, OSM and optional sources.
2. **OSM extraction**: full US PBF → dog-related POI NDJSON.
3. **Normalization**: compact, safe, user-facing POI schema.
4. **Spatial enrichment**: state/place/county/cbsa assignment with local boundaries.
5. **Quality scoring**: safe confidence labels and warnings.
6. **Shard build**: small JSON files by state/city/category.
7. **SEO manifest**: generate only useful indexable pages.
8. **Cloudflare publish**: compact assets in Astro, heavy assets in R2.

## Why not put everything in the PupWiki repo?

The full OSM file and full generated shards can be huge. Keep these out of Git. The PupWiki site should consume:

- `manifest.json`
- `search-index.min.json`
- `page-manifest.json`
- state/city/category shards from R2 or static data paths

## Output paths

```txt
data-build/places/v1/
  manifest.json
  search-index.min.json
  page-manifest.json
  states/index.json
  states/ca/index.json
  states/ca/cities/los-angeles/index.json
  states/ca/cities/los-angeles/dog-parks.json
  states/ca/categories/dog-parks.json
  categories/dog-parks.json
  reports/quality-report.json
```
