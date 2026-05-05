# 07 — Optional Cloudflare D1/R2 Preparation

Use this only after the static-first MVP works.

Prepare optional Cloudflare D1/R2 integration for Dog Services, without making the feature depend on it.

Goal:
Static datasets remain the default. D1/R2 support is future-ready.

## Tasks

### 1. Add schema file

```txt
database/dog-services/schema.sql
```

Tables:

- dog_services
- dog_service_sources
- dog_service_refresh_runs

dog_services fields:

- id TEXT PRIMARY KEY
- source TEXT
- source_id TEXT
- source_type TEXT
- source_license TEXT
- name TEXT
- category TEXT
- subcategory TEXT
- lat REAL
- lon REAL
- country TEXT
- state TEXT
- city TEXT
- postcode TEXT
- address TEXT
- phone TEXT
- website TEXT
- email TEXT
- opening_hours TEXT
- operator TEXT
- brand TEXT
- dog_policy TEXT
- emergency INTEGER
- osm_tags_json TEXT
- confidence_score REAL
- claim_strength TEXT
- verification_required INTEGER
- last_seen_at TEXT
- updated_at TEXT

Indexes:

- category/state/city
- source/source_id
- lat/lon if useful

### 2. Add optional Pages Function only if functions directory exists or framework supports it

```txt
functions/api/dog-services.ts
```

API behavior:

- Reads query params:
  - category
  - state
  - city
  - q
  - limit
- Uses D1 binding if available
- If D1 binding is not available, returns static dataset fallback or useful 501 JSON
- Never crashes production

### 3. Add documentation

```txt
docs/dog-services-cloudflare.md
```

Explain:

- static-first MVP
- D1 optional
- R2 optional for large GeoJSON
- Pages Functions binding names
- local dev notes

4. Do not require Cloudflare credentials.
5. Do not modify production deployment config unless safe and necessary.
6. Run build/typecheck.
