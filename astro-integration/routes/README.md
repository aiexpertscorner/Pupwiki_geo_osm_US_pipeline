# PupWiki route integration

Recommended pages in the Astro repo:

```txt
src/pages/places/index.astro
src/pages/places/[category].astro
src/pages/places/[state]/index.astro
src/pages/places/[state]/[city]/index.astro
src/pages/places/[state]/[city]/[category].astro
```

Use `page-manifest.json` to decide what is generated and what is noindexed.

Hybrid mode:

- Build pages from compact manifests inside `public/data/places/v1`.
- Load heavy city/category shards from `PUBLIC_PLACES_DATA_BASE_URL` / R2.

Do not embed all US POIs in the Astro build.
