# Data contract

## Normalized POI

```ts
export type PupwikiPoi = {
  id: string;
  osmType: 'node' | 'way' | 'relation';
  osmId: number;
  category: string;
  name: string;
  slug: string;
  lat: number;
  lon: number;
  address: {
    street?: string | null;
    city?: string | null;
    state: string;
    postcode?: string | null;
    display?: string | null;
  };
  contact: {
    phone?: string | null;
    website?: string | null;
    email?: string | null;
  };
  tags: Record<string, string>;
  confidence: 'high' | 'medium' | 'low';
  qualityScore: number;
  warnings: string[];
  geo: {
    stateCode: string;
    stateName: string;
    citySlug: string;
    cityName: string;
    citySource: 'place' | 'osm-address' | 'county-fallback' | 'unknown';
    county?: string | null;
  };
  source: {
    provider: 'openstreetmap';
    license: 'ODbL';
    fetchedAt: string;
  };
};
```

## Frontend safety

Do not show raw backend notes, download paths or pipeline internals in PupWiki pages. User-facing output should be dog/location/service related only.

Avoid unsupported claims:

- best
- top-rated
- verified
- open now
- 24/7

unless a trustworthy source is added for those claims.
