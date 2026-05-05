Implement PupWiki Places with the Cloudflare-optimized architecture.

Use:
- compact `page-manifest.json`
- compact `search-index.min.json`
- city/category JSON shards fetched client-side
- static HTML page shell for SEO
- SSR fallback summaries, not full huge data blobs

Create:
- src/pages/places/index.astro
- src/pages/places/[category].astro
- src/pages/places/[state]/index.astro
- src/pages/places/[state]/[city]/index.astro
- src/pages/places/[state]/[city]/[category].astro
- src/components/places/*
- src/lib/places/*
- public/_headers

Add sample data only. Do not commit full dataset until architecture is confirmed.
