# 08 — QA, Performance and Cleanup

Audit and harden the Dog Services Map feature.

## Checklist

1. Build/typecheck passes.
2. `/dog-services/` renders.
3. Existing homepage still renders.
4. Existing breed/content pages still render.
5. MapLibre only loads client-side.
6. No direct Overpass/Nominatim browser requests.
7. GeoJSON output is valid FeatureCollection.
8. Filters work.
9. Empty state works.
10. Sample fallback works.
11. OSM attribution visible near map.
12. Dog-friendly disclaimer visible.
13. Emergency vet disclaimer visible if category is active.
14. No invented real businesses.
15. No false claims like "verified", "best", "official", "top-rated".
16. Mobile layout is usable.
17. Desktop layout is usable.
18. Console has no fatal errors.
19. Bundle impact is reasonable.
20. Large data path is documented.

Then:
- Summarize final changed files.
- Summarize how to run generator.
- Summarize how to add real OSM export data.
- List remaining optional improvements.
