# 02 — Data Contract + OSM Category Config

Implement the data foundation for the PupWiki Dog Services Map.

Create or update files according to the repo structure. Prefer this structure if compatible:

```txt
src/features/dog-services/
  data/dogServiceCategories.ts
  data/dogServiceSeed.ts
  lib/dogServiceTypes.ts
  lib/dogServiceGeojson.ts
  lib/dogServiceFilters.ts
  lib/dogServiceMeta.ts

public/data/dog-services/
  index.json
  us/sample.geojson
```

## Requirements

### 1. dogServiceTypes.ts

Create TypeScript types for:

- DogServiceCategoryId
- DogServiceTier
- DogServiceSource
- DogServiceRecord
- DogServiceFeatureProperties
- DogServiceGeoJSONFeature
- DogServiceGeoJSONCollection
- DogServiceDatasetMeta
- DogServiceFilters

A DogServiceRecord must support:

- id
- source
- source_id
- source_type
- source_license
- name
- category
- subcategory
- lat
- lon
- country
- state
- city
- postcode
- address
- phone
- website
- email
- opening_hours
- operator
- brand
- dog_policy
- emergency
- osm_tags
- confidence_score
- claim_strength
- verification_required
- last_seen_at
- updated_at

### 2. dogServiceCategories.ts

Create category config for these categories:

- veterinary_clinics
- emergency_vets
- dog_parks
- pet_stores
- dog_grooming
- dog_boarding
- animal_shelters
- dog_training
- dog_friendly_parks
- dog_friendly_beaches
- pet_friendly_hotels
- dog_friendly_restaurants
- dog_toilets
- dog_washing
- dog_water_points

Each category must include:

- id
- slug
- label
- shortLabel
- tier
- iconName
- markerClass
- description
- osmTags
- optionalTags
- dataQuality
- seoPathTemplate
- disclaimerType

### 3. dogServiceGeojson.ts

Add helper functions:

- recordToFeature(record)
- recordsToFeatureCollection(records, meta)
- featureCollectionToRecords(collection)
- getFeatureCoordinates(feature)
- isValidDogServiceRecord(record)
- getCategoryCounts(records)

### 4. dogServiceFilters.ts

Add pure functions:

- filterDogServices(records, filters)
- searchDogServices(records, query)
- sortDogServices(records, mode)
- groupDogServicesByCategory(records)

### 5. dogServiceSeed.ts

Create a small safe sample dataset of fictional demo records only.

Important:
- Do not invent real businesses.
- Mark them as source: "sample".
- Put them in a clear sample city/state.
- Use only for development fallback.

### 6. public/data/dog-services/index.json

Create metadata index:

- version
- generated_at
- source_summary
- available_countries
- categories
- attribution
- disclaimer

### 7. public/data/dog-services/us/sample.geojson

Create valid FeatureCollection based on sample records.

Run typecheck/build if available.
Fix scoped issues only.
