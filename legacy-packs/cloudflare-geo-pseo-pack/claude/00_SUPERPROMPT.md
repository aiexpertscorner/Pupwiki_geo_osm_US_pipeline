# Claude Code Superprompt: PupWiki Cloudflare Geo/PSEO

You are a senior Astro, Cloudflare, geospatial data, and technical SEO engineer.

Goal:
Implement PupWiki Places using a locally generated US OpenStreetMap dog-services dataset, optimized for Cloudflare Pages Free and optional R2.

Hard rules:
1. Do not import the full US POI dataset into the Astro bundle.
2. Do not generate all possible city/category pages.
3. Use compact manifests to decide static routes.
4. Use client-side fetch for city/category POI shards.
5. Heavy ETL runs locally, not during Cloudflare build.
6. Keep build under Cloudflare Pages Free constraints.
7. Add OSM attribution and ODbL notice.
8. No fake "verified", "best", "open now", or "24/7" claims.
9. Emergency vet pages must tell users to call first.
10. Implement in small phases and run `npm run build` after each phase.

Phase 1:
- Audit current repo.
- Create docs/geo/architecture.md.
- Add data model and category config.
- Add search/index loading pattern.

Phase 2:
- Add Places landing page and category/city route templates.
- Use page-manifest.json for getStaticPaths.
- Add search bar and data notice.

Phase 3:
- Add MapLibre client-only map.
- Add lazy loading and fallback list.
- Add mobile bottom sheet if practical.

Phase 4:
- Add local ETL scripts or wire existing scripts.
- Add quality report.
- Add Cloudflare _headers.
- Optional R2 upload script.

Acceptance:
- Build passes.
- `/places/` works.
- `/places/[state]/[city]/` works from manifest.
- `/places/[state]/[city]/[category]/` works from manifest.
- No huge JSON bundled.
- Data files are fetched from static/R2 path.
