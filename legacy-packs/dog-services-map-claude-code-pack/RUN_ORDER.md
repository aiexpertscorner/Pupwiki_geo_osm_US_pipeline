# Recommended Claude Code Run Order

## Phase 0 — Master context

Paste:

```txt
prompts/00_MASTER_PROMPT.md
```

This establishes the full task, constraints and acceptance criteria.

## Phase 1 — Audit only

Paste:

```txt
prompts/01_REPO_AUDIT.md
```

Do not implement in this phase. Let Claude inspect the repo and produce a precise plan.

## Phase 2 — Data foundation

Paste:

```txt
prompts/02_DATA_CONTRACT_AND_OSM_CONFIG.md
```

This creates types, category config, sample data and GeoJSON helpers.

## Phase 3 — Generator

Paste:

```txt
prompts/03_GENERATOR_SCRIPTS.md
```

This creates the static-first dataset generation layer.

## Phase 4 — MapLibre UI

Paste:

```txt
prompts/04_MAPLIBRE_COMPONENTS.md
```

This creates the interactive map, filters, list, cards and attribution.

## Phase 5 — Route integration

Paste:

```txt
prompts/05_ROUTE_INTEGRATION.md
```

This adds `/dog-services/` into the actual PupWiki app/router.

## Phase 6 — QA

Paste:

```txt
prompts/08_QA_PERFORMANCE_CLEANUP.md
```

This checks build, routing, map loading, accessibility, disclaimers and output validity.

## Later phase — SEO pages

Paste only after MVP works:

```txt
prompts/06_SEO_LOCATION_PAGES.md
```

## Later phase — Cloudflare D1/R2

Paste only after static-first version works:

```txt
prompts/07_CLOUDFLARE_D1_R2_OPTIONAL.md
```
