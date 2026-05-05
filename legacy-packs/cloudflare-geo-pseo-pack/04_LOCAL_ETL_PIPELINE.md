# Local ETL pipeline

## Pipeline

```txt
1. Read local full US OSM locations dataset or PBF.
2. Filter dog-related POIs.
3. Normalize OSM tags into PupWiki categories.
4. Spatial join with US states and places/cities GeoJSON.
5. Deduplicate node/way/relation records.
6. Score quality.
7. Write shards by state/city/category.
8. Write manifests and search indexes.
9. Compress JSON.
10. Upload heavy shards to R2 or copy small data into public/.
```

## Suggested local folders

```txt
data-raw/
  osm/
    us-latest.osm.pbf
    extracted-us-dog-pois.ndjson
  geojson/
    us-states.geojson
    us-places.geojson

data-build/
  places/v1/
    states/...
    manifest.json
    search-index.min.json
    quality-report.json

public/data/places/v1/
  manifest.json
  search-index.min.json
  states/... only if keeping static in Pages
```

## Performance improvements

- Use NDJSON as intermediate format.
- Use Python `orjson` if available.
- Use Shapely STRtree, not nested loops over every city polygon.
- First detect state using state polygons, then city/place candidates.
- Write batch files once, not append-read-write per POI.
- Precompute city centroids and category counts.
- Remove unused OSM tags before writing frontend shards.
