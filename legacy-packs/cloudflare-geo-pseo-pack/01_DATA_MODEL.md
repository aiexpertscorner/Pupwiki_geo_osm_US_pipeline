# Data model

## Normalized POI

```ts
export type PupwikiPoi = {
  id: string; // osm node/way/relation id
  osmType: 'node' | 'way' | 'relation';
  osmId: number;
  category: string;
  name: string;
  slug: string;
  lat: number;
  lon: number;

  address?: {
    street?: string;
    city?: string;
    state?: string;
    postcode?: string;
    display?: string;
  };

  contact?: {
    phone?: string;
    website?: string;
    email?: string;
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
    county?: string;
  };

  source: {
    provider: 'openstreetmap';
    license: 'ODbL';
    fetchedAt: string;
  };
};
```

## Categories

Recommended first categories:
- dog-parks
- veterinary-clinics
- emergency-vets
- pet-stores
- dog-grooming
- animal-shelters
- dog-boarding-daycare
- dog-training

Do not index experimental categories until quality is acceptable:
- dog-friendly-cafes
- dog-friendly-hotels
- dog-waste-stations
- dog-beaches
