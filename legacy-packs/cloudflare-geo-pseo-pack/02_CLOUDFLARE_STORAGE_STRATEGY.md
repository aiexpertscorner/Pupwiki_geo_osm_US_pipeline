# Cloudflare storage strategy

## Pages static asset strategy

Good for:
- small/medium generated data
- search index
- manifests
- top city datasets
- state/category summary data

Rules:
- Keep each JSON file under 200 KB compressed where possible.
- Never load all US POIs on one route.
- Use content-hashed or versioned filenames.
- Add long cache headers for versioned data.
- Keep mutable manifest/search index with shorter cache.

## R2 strategy

Good for:
- full US city/category shards
- large raw exports
- QA reports
- historical versions

Recommended R2 key layout:

```txt
places/v1/manifest.json
places/v1/search/search-index.min.json
places/v1/states/ca/index.json
places/v1/states/ca/categories/dog-parks.json
places/v1/states/ca/cities/los-angeles/index.json
places/v1/states/ca/cities/los-angeles/dog-parks.json
places/v1/reports/quality-report.json
```

Use a custom domain:
```txt
https://static.pupwiki.com/places/v1/...
```

## Cache headers

For versioned data:
```txt
Cache-Control: public, max-age=31536000, immutable
Content-Type: application/json; charset=utf-8
Content-Encoding: br or gzip if precompressed
```

For manifests:
```txt
Cache-Control: public, max-age=3600, stale-while-revalidate=86400
```

## Important

Do not use KV for the full dataset. KV is better for tiny manifests, feature flags, redirect maps, or small hot lookups. For thousands of JSON shards, static Pages assets or R2 are better.
