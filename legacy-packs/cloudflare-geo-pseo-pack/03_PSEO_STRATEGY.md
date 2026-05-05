# Geo PSEO strategy

## Do not generate every possible URL

Generate pages only if the page has enough useful content.

Recommended thresholds:
- `/places/[state]/`: always, if state has data.
- `/places/[category]/`: always for core categories.
- `/places/[state]/[category]/`: min 20 POIs.
- `/places/[state]/[city]/`: min 10 total POIs.
- `/places/[state]/[city]/[category]/`: min 3 POIs and quality score average > 40.
- `/places/place/[slug]/`: only for high-quality places or later after traffic validation.

## Page types

### Indexable
- State hubs
- Category hubs
- City hubs with enough data
- City/category pages with enough data

### Noindex initially
- Low-data pages
- Experimental categories
- Unknown city pages
- POI detail pages with missing address/name/contact

## Example URL model

```txt
/places/
/places/dog-parks/
/places/veterinary-clinics/
/places/emergency-vets/
/places/ca/
/places/ca/los-angeles/
/places/ca/los-angeles/dog-parks/
```

Prefer state codes in URLs for clean scalable routing:
- `/places/ca/los-angeles/dog-parks/`

Display names in UI:
- Los Angeles, California

## SEO copy blocks

Each page should include:
- useful intro
- map/list
- data source notice
- category-specific trust/safety note
- related internal links
- "verify before visiting" notice

Do not use:
- "best"
- "top-rated"
- "verified"
- "open now"
- "24/7"

unless supported by real verified data.
