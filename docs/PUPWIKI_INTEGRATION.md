# PupWiki.com integration

## Recommended pattern

1. Run this repo locally or on a dedicated machine.
2. Upload heavy `data-build/places/v1` shards to Cloudflare R2.
3. Copy compact manifests to the PupWiki Astro repo:

```bash
python -m pupwiki_geo.cli copy-public --build data-build/places/v1 --pupwiki ../Mr-Doggo-Style --mode hybrid
```

4. Add Astro components from `astro-integration/components`.
5. Generate only URLs from `page-manifest.json`.

## SEO content rules

Each page should include useful dog-owner context:

- category-specific intro
- map/list
- state/city context
- related categories and nearby cities
- data source notice
- verify-before-visiting note

Do not output backend terms such as “pipeline”, “R2 shard”, “OSM tag match”, or “generated file” in normal user-facing copy.
