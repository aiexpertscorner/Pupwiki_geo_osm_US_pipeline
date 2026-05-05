-- Optional future Cloudflare D1 schema for PupWiki Dog Services

CREATE TABLE IF NOT EXISTS dog_services (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_type TEXT,
  source_license TEXT,
  name TEXT,
  category TEXT NOT NULL,
  subcategory TEXT,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  country TEXT,
  state TEXT,
  city TEXT,
  postcode TEXT,
  address TEXT,
  phone TEXT,
  website TEXT,
  email TEXT,
  opening_hours TEXT,
  operator TEXT,
  brand TEXT,
  dog_policy TEXT,
  emergency INTEGER DEFAULT 0,
  osm_tags_json TEXT,
  confidence_score REAL DEFAULT 0.5,
  claim_strength TEXT,
  verification_required INTEGER DEFAULT 1,
  last_seen_at TEXT,
  updated_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_dog_services_source
  ON dog_services(source, source_id);

CREATE INDEX IF NOT EXISTS idx_dog_services_category_location
  ON dog_services(category, country, state, city);

CREATE INDEX IF NOT EXISTS idx_dog_services_location
  ON dog_services(country, state, city);

CREATE TABLE IF NOT EXISTS dog_service_sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  license TEXT,
  attribution TEXT,
  url TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS dog_service_refresh_runs (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  records_read INTEGER DEFAULT 0,
  records_written INTEGER DEFAULT 0,
  errors_json TEXT
);
