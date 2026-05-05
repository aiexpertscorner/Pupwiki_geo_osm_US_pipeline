# 00 — Master Prompt

You are Claude Code working inside the PupWiki repository.

Your task is to build a production-ready "Dog Services Map" feature for PupWiki.

Core goal:
Create an interactive MapLibre GL JS map for dog-related services in the US market, backed by generated JSON/GeoJSON datasets. The system must integrate with existing geo and content datasets already available in the repo, and must not rely on live OpenStreetMap/Overpass requests from end-user browsers.

Tech expectations:
- Use the current repo stack and conventions.
- Detect whether the repo is Astro-first, React SPA, or hybrid.
- Prefer Astro pages with a React island if Astro pages exist.
- If the project is a React SPA with App.tsx routing, integrate without breaking the existing navigation.
- Use MapLibre GL JS for the map.
- Use existing design tokens/components where possible.
- Use TypeScript.
- Use accessible, mobile-first UI.
- Avoid massive rewrites.

Primary route:
- /dog-services/

Secondary future-ready routes:
- /dog-services/[state]/
- /dog-services/[state]/[city]/
- /dog-services/[state]/[city]/[category]/

Data requirements:
- Search the repository for existing geo, state, city, location, breed, or service datasets.
- Reuse available datasets where possible.
- If existing datasets are incomplete, create adapter files rather than replacing existing data.
- Create a dog-services data contract.
- Create an OSM category config.
- Create generator scripts that can write:
  - public/data/dog-services/index.json
  - public/data/dog-services/us/index.json
  - public/data/dog-services/us/sample.geojson
  - optional state/city/category JSON and GeoJSON outputs

Do not:
- Do not make live Overpass/Nominatim calls from the browser.
- Do not add API keys.
- Do not invent real businesses.
- Do not remove existing PupWiki pages/features.
- Do not create medical/legal claims.
- Do not ignore OSM attribution.

Feature categories:
Tier A:
- Veterinary clinics: amenity=veterinary
- Emergency vets: amenity=veterinary + emergency=yes
- Dog parks: leisure=dog_park
- Pet stores: shop=pet
- Dog grooming: shop=pet_grooming
- Dog boarding: amenity=animal_boarding
- Animal shelters: amenity=animal_shelter
- Dog training: amenity=animal_training + animal_training=dog

Tier B:
- Dog-friendly parks: leisure=park + dog=yes/leashed/designated
- Dog-friendly beaches: natural=beach + dog=yes/leashed/designated
- Pet-friendly hotels: tourism=hotel/motel/guest_house + dog=yes or pets=yes
- Dog-friendly restaurants/cafes: amenity=restaurant/cafe/bar/pub + dog=yes/outside/leashed

Tier C:
- Dog toilets: amenity=dog_toilet
- Dog washing: dog_washing=yes
- Drinking water for dogs: amenity=drinking_water + dog=yes/designated

Implementation strategy:
Work in small phases. After each phase:
1. Summarize changed files.
2. Run typecheck/build if available.
3. Report issues and fix only scoped issues.
4. Avoid broad refactors.

Acceptance criteria:
- /dog-services/ renders without breaking existing pages.
- MapLibre loads only on the client.
- The page works if no generated production dataset exists by using safe sample data.
- Filters update visible service cards and map layers.
- Generated GeoJSON follows FeatureCollection format.
- OSM attribution is visible near the map.
- Dataset metadata includes source, license, generated_at, category counts.
- Build/typecheck passes or remaining issues are clearly listed.
