# Astro route patterns

## Recommended routes

```txt
src/pages/places/index.astro
src/pages/places/[category].astro
src/pages/places/[state]/index.astro
src/pages/places/[state]/[city]/index.astro
src/pages/places/[state]/[city]/[category].astro
```

## Key principle

Use `page-manifest.json` to decide which pages exist.

Do not use `import.meta.glob('/src/data/us/**/*.json')` over the full dataset if the dataset is huge. That puts pressure on build memory and route count.

For Cloudflare/R2 model:
- `getStaticPaths()` reads only a compact manifest.
- Page HTML is static.
- The page fetches city/category POI JSON from `/data/places/v1/...` or `https://static.pupwiki.com/places/v1/...`.

## Example fetch path

```ts
const DATA_BASE = import.meta.env.PUBLIC_PLACES_DATA_BASE || '/data/places/v1';

const url = `${DATA_BASE}/states/${state}/cities/${city}/${category}.json`;
```
