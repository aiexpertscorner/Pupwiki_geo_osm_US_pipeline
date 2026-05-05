# PupWiki Dog Services Map — Technical Spec

## Purpose

The Dog Services Map is a location-data feature for US dog owners. It helps users discover dog-related services and dog-friendly places while creating reusable generated datasets for PupWiki SEO, city pages and future APIs.

## Data strategy

Static-first:

- Generated JSON/GeoJSON files are the primary frontend data source.
- Browser never calls Overpass directly.
- Real OSM data can be imported as local export files.
- Generator normalizes, dedupes and writes public output.

Future:

- D1 can become the master database.
- R2 can store larger GeoJSON outputs.
- Pages Functions can expose filtered API responses.

## Core categories

Tier A:

- Veterinary clinics
- Emergency vets
- Dog parks
- Pet stores
- Dog grooming
- Dog boarding
- Animal shelters
- Dog training

Tier B:

- Dog-friendly parks
- Dog-friendly beaches
- Pet-friendly hotels
- Dog-friendly restaurants

Tier C:

- Dog toilets
- Dog washing
- Dog water points

## Attribution

All pages/maps using OSM-derived data must show:

```txt
© OpenStreetMap contributors. Data available under ODbL.
```

## Disclaimers

General:

```txt
Listings may be incomplete. Always verify details before visiting.
```

Veterinary:

```txt
Always contact the clinic directly to confirm hours, emergency availability and services.
```

Dog-friendly:

```txt
Dog access rules can change. Always verify leash rules and pet policies before visiting.
```

## Quality rules

Do not claim:

- verified
- official
- top-rated
- best

unless supported by a real verification/rating source.

## SEO rules

Only generate indexable pages when data volume is sufficient:

- state page: 10+ records
- city page: 5+ records
- city/category page: 3+ records

Otherwise keep pages non-indexed or do not generate them.
