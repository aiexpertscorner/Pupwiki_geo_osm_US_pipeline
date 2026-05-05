# 06 — SEO-Ready Generated Pages Without Spam

Add SEO-ready architecture for Dog Services without generating low-quality/thin pages.

Goal:
Prepare data-driven location pages, but only generate pages when data exists and count thresholds are met.

Preferred future routes:

```txt
/dog-services/{state}/
/dog-services/{state}/{city}/
/dog-services/{state}/{city}/{category}/
```

## Implementation

1. Add helper functions:
   - getAvailableDogServiceLocations()
   - getDogServiceStatePages()
   - getDogServiceCityPages()
   - getDogServiceCategoryPages()
   - shouldGenerateDogServicePage({ recordCount, category, location })

2. Page generation rules:
   - state page: minimum 10 records
   - city page: minimum 5 records
   - category city page: minimum 3 records
   - otherwise do not generate indexable page

3. Add noindex fallback:
If a page is manually accessible but has too little data:
   - display useful content
   - add noindex metadata if framework supports it

4. Add copy templates:
   - veterinary clinics
   - emergency vets
   - dog parks
   - pet stores
   - grooming
   - boarding
   - shelters
   - training
   - dog-friendly parks
   - pet-friendly hotels

5. Add disclaimers:

For vets/emergency:

```txt
Always contact the clinic directly to confirm emergency availability, hours and services.
```

For dog-friendly places:

```txt
Dog access rules can change. Always verify leash rules and pet policies before visiting.
```

6. Add internal linking:
   - from dog service city page to related category pages
   - from breed/care pages only if relevant and safe
   - footer link to main dog services map

7. Avoid claims like:
   - best
   - top-rated
   - verified

unless supported by actual data.

8. Run build/typecheck.
