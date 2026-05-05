from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .categories import safe_frontend_tags
from .text import slugify, state_code_from_props


def _clean(v):
    if v in ("", None, "None", "null"):
        return None
    return str(v).strip()


def quality_score(tags: dict[str, Any], category: str, confidence: str, geo_source: str) -> tuple[int, list[str]]:
    warnings = []
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
    if tags.get("website") or tags.get("contact:website"):
        score += 8
    if tags.get("opening_hours"):
        score += 5
    if confidence == "high":
        score += 15
    elif confidence == "medium":
        score += 8
    if category.startswith("dog-friendly"):
        warnings.append("dog_access_rules_may_change")
        score -= 5
    if category == "emergency-vets" and str(tags.get("emergency", "")).lower() != "yes":
        warnings.append("emergency_status_inferred_verify_before_visiting")
        score -= 8
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
    osm_type = raw.get("osmType") or raw.get("type") or "node"
    osm_id = int(raw.get("osmId") or raw.get("id") or str(raw.get("id", "0")).split("_")[-1])
    state_name = state_row["name"] if state_row else tags.get("addr:state") or "Unknown"
    state_code = state_code_from_props(state_row.get("props") if state_row else {}, state_name)

    from .spatial import city_slug_from_row
    city_name, city_slug, geo_source = city_slug_from_row(city_row, tags, county_row)
    county = county_row["name"] if county_row else None
    name = _clean(tags.get("name")) or f"{category.replace('-', ' ').title()} {osm_id}"
    score, warnings = quality_score(tags, category, confidence, geo_source)
    addr_parts = [
        _clean(tags.get("addr:housenumber")),
        _clean(tags.get("addr:street")),
        _clean(tags.get("addr:city")) or (city_name if city_name != "Unknown" else None),
        state_code.upper() if state_code != "xx" else None,
        _clean(tags.get("addr:postcode")),
    ]
    display = ", ".join([p for p in addr_parts if p]) or None
    return {
        "id": f"{osm_type}_{osm_id}",
        "osmType": osm_type,
        "osmId": osm_id,
        "category": category,
        "name": name,
        "slug": f"{slugify(name)}-{osm_id}",
        "lat": round(lat, 7),
        "lon": round(lon, 7),
        "address": {
            "street": " ".join([x for x in [_clean(tags.get("addr:housenumber")), _clean(tags.get("addr:street"))] if x]) or None,
            "city": city_name if city_name != "Unknown" else None,
            "state": state_code.upper(),
            "postcode": _clean(tags.get("addr:postcode")),
            "display": display,
        },
        "contact": {
            "phone": _clean(tags.get("phone") or tags.get("contact:phone")),
            "website": _clean(tags.get("website") or tags.get("contact:website")),
            "email": _clean(tags.get("email") or tags.get("contact:email")),
        },
        "tags": safe_frontend_tags(tags, category_config),
        "confidence": confidence,
        "qualityScore": score,
        "warnings": warnings,
        "geo": {
            "stateCode": state_code,
            "stateName": state_name,
            "citySlug": city_slug,
            "cityName": city_name,
            "citySource": geo_source,
            "county": county,
        },
        "source": {
            "provider": "openstreetmap",
            "license": "ODbL",
            "fetchedAt": raw.get("source", {}).get("extractedAt") or datetime.now(timezone.utc).isoformat(),
        },
    }
