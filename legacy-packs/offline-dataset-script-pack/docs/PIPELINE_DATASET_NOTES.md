# Dataset notes

Start with P1 only. Use P2 after the state/city spatial join works. P3/P4 are enrichment layers, not MVP blockers.

Recommended MVP set:

- Census cartographic state/county/place/county subdivision/CBSA.
- Census Gazetteer state/county/place/county subdivision.
- State-level Geofabrik OSM PBFs for test states before full-US.
- GNIS for aliases/rural names.
- Small ACS population queries for prioritization.

The later ETL target is: OSM PBF -> dog POI extraction -> spatial join with local boundaries -> normalized shards -> compact frontend manifests/R2 shards.
