# Architecture decision

## Recommended Cloudflare architecture

### Phase 1: Cloudflare Pages static assets
Use this first.

Store generated files under:

```txt
public/data/places/v1/
  manifest.json
  search-index.min.json
  states/ca/index.json
  states/ca/cities/los-angeles/index.json
  states/ca/cities/los-angeles/dog-parks.json
  states/ca/cities/los-angeles/veterinary-clinics.json
```

Pros:
- No Worker required.
- Static asset requests are free.
- Simple deploy.
- Best for MVP.

Cons:
- Free Pages has file-count and per-file-size limits.
- Large generated datasets increase deploy size and build/upload time.

### Phase 2: Cloudflare R2 public bucket or custom domain

Move the heavy JSON shards to:

```txt
https://static.pupwiki.com/places/v1/...
```

Keep only:
- pages
- compact indexes
- page manifests

inside the Astro build.

Pros:
- Better for full US dataset.
- Avoids Pages file-count pressure.
- R2 has generous free tier and no egress fee.
- Can update datasets without rebuilding the whole website.

Cons:
- R2 reads count as operations.
- Need upload/sync script.
- Need cache headers and versioned paths.

## Final recommendation

Use a hybrid:

- Astro build:
  - `/places/`
  - state/city/category SEO pages
  - `public/data/places/v1/search-index.min.json`
  - `public/data/places/v1/page-manifest.json`
- R2:
  - full city/category POI shards
  - state/category aggregate shards
  - optional raw/diagnostic data
- Versioned paths:
  - `/places-data/v1/...`
  - later `/places-data/v2/...`

This gives you free/cheap hosting, fast pages, and no huge repo/build.
