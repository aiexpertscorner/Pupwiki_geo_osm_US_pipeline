from __future__ import annotations

import gzip
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .categories import load_category_config, match_category
from .jsonx import dumps, iter_ndjson, write_json
from .normalize import normalize_poi
from .spatial import FeatureIndex


def _write(path: Path, obj: Any, *, gzip_copy: bool = True, pretty: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dumps(obj, pretty=pretty)
    path.write_bytes(data)
    if gzip_copy:
        with gzip.open(str(path) + ".gz", "wb", compresslevel=9) as f:
            f.write(data)


def build_places(input_path: str | Path, states_geojson: str | Path, places_geojson: str | Path, out: str | Path, *, counties_geojson: str | None = None, category_config: str | None = None, pretty: bool = False) -> dict[str, Any]:
    out = Path(out)
    config = load_category_config(category_config)
    states = FeatureIndex.from_geojson(states_geojson)
    places = FeatureIndex.from_geojson(places_geojson)
    counties = FeatureIndex.from_geojson(counties_geojson) if counties_geojson and Path(counties_geojson).exists() else None

    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    state_buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    category_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    report = {"generatedAt": datetime.now(timezone.utc).isoformat(), "totalInput": 0, "totalOutput": 0, "duplicates": 0, "skipped": defaultdict(int), "byCategory": defaultdict(int), "byState": defaultdict(int), "warnings": defaultdict(int)}

    for raw in iter_ndjson(input_path):
        report["totalInput"] += 1
        tags = raw.get("tags") or {}
        category = raw.get("categoryHint")
        confidence = raw.get("confidenceHint") or "low"
        if not category:
            category, confidence, _ = match_category(tags, config)
        if not category or category == "other":
            report["skipped"]["no_category"] += 1
            continue
        key = raw.get("id") or f"{raw.get('osmType')}_{raw.get('osmId')}"
        if key in seen:
            report["duplicates"] += 1
            continue
        seen.add(key)
        try:
            lat, lon = float(raw.get("lat")), float(raw.get("lon"))
        except Exception:
            report["skipped"]["bad_coords"] += 1
            continue
        state_row = states.find(lon, lat)
        city_row = places.find(lon, lat)
        county_row = counties.find(lon, lat) if counties else None
        poi = normalize_poi(raw, category=category, confidence=confidence, state_row=state_row, city_row=city_row, county_row=county_row, category_config=config)
        if not poi:
            report["skipped"]["normalization_failed"] += 1
            continue
        sc = poi["geo"]["stateCode"]
        cs = poi["geo"]["citySlug"]
        cat = poi["category"]
        buckets[(sc, cs, cat)].append(poi)
        state_buckets[(sc, cat)].append(poi)
        category_buckets[cat].append(poi)
        report["totalOutput"] += 1
        report["byCategory"][cat] += 1
        report["byState"][sc] += 1
        for warning in poi.get("warnings", []):
            report["warnings"][warning] += 1

    # Sort and write city/category shards.
    city_totals = defaultdict(lambda: {"count": 0, "categories": defaultdict(int), "latSum": 0.0, "lonSum": 0.0, "qualitySum": 0.0, "cityName": "", "stateName": ""})
    state_totals = defaultdict(lambda: {"count": 0, "categories": defaultdict(int), "cities": set(), "stateName": ""})
    page_manifest = []

    for (state, city, cat), items in buckets.items():
        items.sort(key=lambda x: (-x["qualityScore"], x["name"]))
        _write(out / "states" / state / "cities" / city / f"{cat}.json", items, pretty=pretty)
        meta = city_totals[(state, city)]
        meta["count"] += len(items)
        meta["categories"][cat] += len(items)
        meta["latSum"] += sum(i["lat"] for i in items)
        meta["lonSum"] += sum(i["lon"] for i in items)
        meta["qualitySum"] += sum(i["qualityScore"] for i in items)
        meta["cityName"] = items[0]["geo"]["cityName"]
        meta["stateName"] = items[0]["geo"]["stateName"]
        sm = state_totals[state]
        sm["count"] += len(items)
        sm["categories"][cat] += len(items)
        sm["cities"].add(city)
        sm["stateName"] = items[0]["geo"]["stateName"]
        avg_q = sum(i["qualityScore"] for i in items) / max(1, len(items))
        if len(items) >= 3 and avg_q >= 40:
            page_manifest.append({"type": "city-category", "state": state, "city": city, "category": cat, "url": f"/places/{state}/{city}/{cat}/", "count": len(items), "avgQuality": round(avg_q, 1), "indexable": True})

    # State/category aggregate shards.
    for (state, cat), items in state_buckets.items():
        items.sort(key=lambda x: (-x["qualityScore"], x["name"]))
        _write(out / "states" / state / "categories" / f"{cat}.json", items[:10000], pretty=pretty)
        if len(items) >= 20:
            page_manifest.append({"type": "state-category", "state": state, "category": cat, "url": f"/places/{state}/{cat}/", "count": len(items), "indexable": True})

    # Category national summary shards (trimmed, not full for very large categories).
    for cat, items in category_buckets.items():
        items.sort(key=lambda x: (-x["qualityScore"], x["name"]))
        _write(out / "categories" / f"{cat}.json", items[:20000], pretty=pretty)
        page_manifest.append({"type": "category", "category": cat, "url": f"/places/{cat}/", "count": len(items), "indexable": True})

    search_index = []
    city_index = []
    for (state, city), meta in city_totals.items():
        count = meta["count"]
        if count <= 0:
            continue
        lat = round(meta["latSum"] / count, 6)
        lon = round(meta["lonSum"] / count, 6)
        avg_q = round(meta["qualitySum"] / count, 1)
        row = {"city": meta["cityName"], "state": state.upper(), "stateName": meta["stateName"], "slug": f"/places/{state}/{city}/", "count": count, "lat": lat, "lon": lon, "avgQuality": avg_q, "categories": dict(meta["categories"]), "searchKey": f"{meta['cityName']} {state} {meta['stateName']}".lower()}
        search_index.append(row)
        city_index.append(row)
        _write(out / "states" / state / "cities" / city / "index.json", row, gzip_copy=False, pretty=True)
        if count >= 10:
            page_manifest.append({"type": "city", "state": state, "city": city, "url": f"/places/{state}/{city}/", "count": count, "avgQuality": avg_q, "indexable": True})

    state_index = []
    for state, meta in state_totals.items():
        row = {"state": state.upper(), "stateName": meta["stateName"], "slug": f"/places/{state}/", "count": meta["count"], "cityCount": len(meta["cities"]), "categories": dict(meta["categories"])}
        state_index.append(row)
        _write(out / "states" / state / "index.json", row, gzip_copy=False, pretty=True)
        page_manifest.append({"type": "state", "state": state, "url": f"/places/{state}/", "count": meta["count"], "indexable": True})

    search_index.sort(key=lambda x: (-x["count"], x["state"], x["city"]))
    page_manifest.sort(key=lambda x: (x.get("state", ""), x.get("city", ""), x.get("category", ""), x["type"]))
    state_index.sort(key=lambda x: x["state"])

    report["byCategory"] = dict(report["byCategory"])
    report["byState"] = dict(report["byState"])
    report["warnings"] = dict(report["warnings"])
    report["skipped"] = dict(report["skipped"])

    _write(out / "search" / "search-index.min.json", search_index, gzip_copy=True, pretty=False)
    _write(out / "search-index.min.json", search_index, gzip_copy=True, pretty=False)  # compatibility
    _write(out / "page-manifest.json", page_manifest, gzip_copy=True, pretty=False)
    _write(out / "states" / "index.json", state_index, gzip_copy=True, pretty=False)
    _write(out / "reports" / "quality-report.json", report, gzip_copy=False, pretty=True)

    manifest = {"version": out.name if out.name.startswith("v") else "v1", "generatedAt": datetime.now(timezone.utc).isoformat(), "counts": {"pois": report["totalOutput"], "cities": len(city_index), "states": len(state_index), "indexablePages": len([p for p in page_manifest if p.get("indexable")])}, "files": {"searchIndex": "search/search-index.min.json", "pageManifest": "page-manifest.json", "stateIndex": "states/index.json", "qualityReport": "reports/quality-report.json"}, "license": "Contains OpenStreetMap data © OpenStreetMap contributors, licensed under ODbL. Verify hours, access rules and emergency availability before visiting."}
    _write(out / "manifest.json", manifest, gzip_copy=False, pretty=True)
    return manifest
