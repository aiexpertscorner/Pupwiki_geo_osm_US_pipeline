from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from .categories import category_meta, normalize_category_id, safe_frontend_tags
from .text import slugify, state_code_from_props


def _clean(v: Any) -> str | None:
    if v in ("", None, "None", "null"):
        return None
    s = re.sub(r"\s+", " ", str(v)).strip()
    return s or None


def clean_phone(v: Any) -> str | None:
    s = _clean(v)
    if not s:
        return None
    s = re.sub(r"^(tel:)", "", s, flags=re.I).strip()
    return s if re.search(r"\d", s) else None


def clean_email(v: Any) -> str | None:
    s = _clean(v)
    if not s:
        return None
    s = re.sub(r"^mailto:", "", s, flags=re.I).strip()
    return s if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s) else None


def clean_website(v: Any) -> str | None:
    s = _clean(v)
    if not s:
        return None
    if s.startswith("//"):
        s = "https:" + s
    if not re.match(r"^https?://", s, flags=re.I):
        s = "https://" + s
    parsed = urlparse(s)
    if not parsed.netloc or "." not in parsed.netloc:
        return None
    return s


def display_name(tags: dict[str, Any], category: str, osm_id: int) -> str:
    for key in ("name", "brand", "operator"):
        val = _clean(tags.get(key))
        if val:
            return val
    return f"{category.replace('-', ' ').title()} {osm_id}"


def address_from_tags(tags: dict[str, Any], *, city_name: str, state_code: str) -> dict[str, Any]:
    street = " ".join(
        x
        for x in [
            _clean(tags.get("addr:housenumber")),
            _clean(tags.get("addr:street")),
            _clean(tags.get("addr:unit")),
        ]
        if x
    ) or None
    city = _clean(tags.get("addr:city")) or (city_name if city_name != "Unknown" else None)
    state = (_clean(tags.get("addr:state")) or state_code or "").upper() or None
    postcode = _clean(tags.get("addr:postcode"))
    country = _clean(tags.get("addr:country")) or "US"
    display = ", ".join([x for x in [street, city, state, postcode] if x]) or None
    return {"street": street, "city": city, "state": state, "postcode": postcode, "country": country, "display": display}


def quality_score(tags: dict[str, Any], category: str, confidence: str, geo_source: str, match_meta: dict[str, Any] | None = None) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 15
    if tags.get("name"):
        score += 20
    else:
        warnings.append("missing_name")
    if tags.get("addr:street") or tags.get("addr:housenumber"):
        score += 12
    if tags.get("addr:city") or geo_source in ("place", "osm-address"):
        score += 10
    if tags.get("addr:postcode"):
        score += 5
    if tags.get("phone") or tags.get("contact:phone"):
        score += 8
    if tags.get("website") or tags.get("contact:website") or tags.get("url"):
        score += 8
    if tags.get("opening_hours"):
        score += 5
    if confidence == "high":
        score += 15
    elif confidence == "medium":
        score += 8
    if match_meta and match_meta.get("needsReview"):
        warnings.append("rule_needs_review")
        score -= 4
    if category.startswith("dog-friendly"):
        warnings.append("dog_access_rules_may_change")
        score -= 5
    if category == "emergency-vets" and str(tags.get("emergency", "")).lower() != "yes":
        warnings.append("emergency_status_inferred_verify_before_visiting")
        score -= 8
    if category == "animal-breeders":
        warnings.append("breeder_listing_requires_responsible_breeder_context")
        score -= 10
    return max(0, min(100, score)), warnings


def normalize_poi(raw: dict[str, Any], *, category: str, confidence: str, state_row, city_row, county_row, category_config: dict[str, Any]) -> dict[str, Any] | None:
    tags = raw.get("tags") or {}
    lat = raw.get("lat")
    lon = raw.get("lon")
    if lat is None or lon is None:
        return None
    lat = float(lat)
    lon = float(lon)
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None

    category = normalize_category_id(category, category_config) or category
    osm_type = raw.get("osmType") or raw.get("type") or "node"
    osm_id = int(raw.get("osmId") or str(raw.get("id", "0")).split("_")[-1])
    state_name = state_row["name"] if state_row else tags.get("addr:state") or "Unknown"
    state_code = state_code_from_props(state_row.get("props") if state_row else {}, state_name)

    from .spatial import city_slug_from_row
    city_name, city_slug, geo_source = city_slug_from_row(city_row, tags, county_row)
    county = county_row["name"] if county_row else None

    name = display_name(tags, category, osm_id)
    slug_seed = f"{slugify(name)}-{osm_type}-{osm_id}"
    match_meta = raw.get("matchMeta") or {}
    score, warnings = quality_score(tags, category, confidence, geo_source, match_meta)
    cat_meta = category_meta(category, category_config)

    contact = {
        "phone": clean_phone(tags.get("phone") or tags.get("contact:phone")),
        "website": clean_website(tags.get("website") or tags.get("contact:website") or tags.get("url")),
        "email": clean_email(tags.get("email") or tags.get("contact:email")),
    }

    return {
        "id": f"{osm_type}_{osm_id}",
        "osmType": osm_type,
        "osmId": osm_id,
        "category": category,
        "categoryLabel": cat_meta.get("label"),
        "categoryTier": cat_meta.get("tier"),
        "indexableCategory": bool(cat_meta.get("indexable")),
        "name": name,
        "displayName": name,
        "slugSeed": slug_seed,
        "slug": slug_seed,
        "lat": round(lat, 7),
        "lon": round(lon, 7),
        "address": address_from_tags(tags, city_name=city_name, state_code=state_code),
        "contact": contact,
        "tags": safe_frontend_tags(tags, category_config),
        "confidence": confidence,
        "qualityScore": score,
        "warnings": warnings,
        "matchMeta": match_meta,
        "geo": {"stateCode": state_code, "stateName": state_name, "citySlug": city_slug, "cityName": city_name, "citySource": geo_source, "county": county},
        "source": {"provider": "openstreetmap", "license": "ODbL", "fetchedAt": raw.get("source", {}).get("extractedAt") or datetime.now(timezone.utc).isoformat()},
    }
