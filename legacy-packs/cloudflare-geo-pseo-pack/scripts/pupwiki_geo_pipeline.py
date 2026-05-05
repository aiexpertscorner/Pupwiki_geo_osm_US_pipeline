"""
PupWiki Geo Pipeline skeleton.

Purpose:
- Read a normalized OSM POI NDJSON or JSON file.
- Spatially link every POI to US state and city/place polygons.
- Write optimized shards by state/city/category.
- Generate manifest, search-index, and quality report.

Install:
  pip install shapely orjson

Run:
  python scripts/pupwiki_geo_pipeline.py \
    --input data-raw/osm/extracted-us-dog-pois.ndjson \
    --states data-raw/geojson/us-states.geojson \
    --cities data-raw/geojson/us-places.geojson \
    --out data-build/places/v1
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    import orjson
except ImportError:
    orjson = None

from shapely.geometry import Point, shape
from shapely.strtree import STRtree


def dumps(obj: Any) -> bytes:
    if orjson:
        return orjson.dumps(obj, option=orjson.OPT_INDENT_2)
    import json
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")


def loads(data: bytes) -> Any:
    if orjson:
        return orjson.loads(data)
    import json
    return json.loads(data.decode("utf-8"))


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def state_code(props: Dict[str, Any]) -> str:
    return (
        props.get("STUSPS")
        or props.get("STATE")
        or props.get("state_code")
        or props.get("postal")
        or props.get("abbr")
        or props.get("NAME", "unknown")[:2]
    ).lower()


def load_polygons(path: Path, name_key: str = "NAME"):
    raw = loads(path.read_bytes())
    rows = []
    geoms = []
    for feat in raw.get("features", []):
        geom = shape(feat["geometry"])
        props = feat.get("properties", {})
        row = {
            "name": props.get(name_key) or props.get("name") or "Unknown",
            "props": props,
            "geom": geom,
        }
        rows.append(row)
        geoms.append(geom)
    tree = STRtree(geoms)
    # Shapely 2 returns indices; older versions return geometries.
    geom_to_idx = {id(g): i for i, g in enumerate(geoms)}
    return rows, geoms, tree, geom_to_idx


def tree_find(point: Point, rows, tree, geom_to_idx):
    candidates = tree.query(point)
    for c in candidates:
        if isinstance(c, (int,)):
            idx = int(c)
        else:
            idx = geom_to_idx.get(id(c))
            if idx is None:
                continue
        geom = rows[idx]["geom"]
        if geom.contains(point) or geom.intersects(point):
            return rows[idx]
    return None


def iter_pois(path: Path) -> Iterable[Dict[str, Any]]:
    if path.suffix == ".ndjson":
        with path.open("rb") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield loads(line)
    else:
        data = loads(path.read_bytes())
        if isinstance(data, list):
            yield from data
        elif isinstance(data, dict) and "items" in data:
            yield from data["items"]


def normalize_category(tags: Dict[str, Any]) -> Tuple[str, str]:
    # returns category, confidence
    if tags.get("leisure") == "dog_park":
        return "dog-parks", "high"
    if tags.get("amenity") == "veterinary" or tags.get("healthcare") == "veterinary":
        if tags.get("emergency") == "yes" or "emergency" in (tags.get("name", "") or "").lower():
            return "emergency-vets", "medium"
        return "veterinary-clinics", "high"
    if tags.get("shop") == "pet":
        return "pet-stores", "high"
    if tags.get("shop") == "pet_grooming" or "groom" in (tags.get("name", "") or "").lower():
        return "dog-grooming", "medium"
    if tags.get("amenity") == "animal_shelter":
        return "animal-shelters", "medium"
    if tags.get("amenity") in ("animal_boarding", "dog_daycare"):
        return "dog-boarding-daycare", "medium"
    if tags.get("amenity") == "animal_training" or "dog training" in (tags.get("name", "") or "").lower():
        return "dog-training", "low"
    return "other", "low"


def compact_poi(raw: Dict[str, Any], state_row, city_row) -> Dict[str, Any]:
    tags = raw.get("tags", {}) or {}
    category, confidence = normalize_category(tags)
    lat = float(raw.get("lat") or raw.get("center", {}).get("lat"))
    lon = float(raw.get("lon") or raw.get("center", {}).get("lon"))
    osm_type = raw.get("type") or raw.get("osmType") or "node"
    osm_id = int(raw.get("id") or raw.get("osmId"))

    state_name = state_row["name"] if state_row else tags.get("addr:state", "Unknown")
    code = state_code(state_row["props"]) if state_row else slugify(str(state_name))[:2]
    city_name = city_row["name"] if city_row else tags.get("addr:city", "Unknown")

    name = tags.get("name") or raw.get("name") or f"{category.replace('-', ' ').title()} {osm_id}"
    warnings = []
    if city_name == "Unknown":
        warnings.append("City could not be resolved.")
    if not tags.get("name"):
        warnings.append("Missing OSM name tag.")
    if category == "emergency-vets" and tags.get("emergency") != "yes":
        warnings.append("Emergency status inferred; call first to verify.")

    quality = 20
    quality += 25 if tags.get("name") else 0
    quality += 15 if tags.get("addr:street") or tags.get("addr:city") else 0
    quality += 10 if tags.get("phone") or tags.get("contact:phone") else 0
    quality += 10 if tags.get("website") or tags.get("contact:website") else 0
    quality += 15 if confidence == "high" else 5 if confidence == "medium" else 0
    quality = max(0, min(100, quality))

    display_address = ", ".join([v for v in [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:city") or city_name,
        tags.get("addr:state") or code.upper(),
        tags.get("addr:postcode")
    ] if v])

    return {
        "id": f"{osm_type}_{osm_id}",
        "osmType": osm_type,
        "osmId": osm_id,
        "category": category,
        "name": name,
        "slug": f"{slugify(name)}-{osm_id}",
        "lat": lat,
        "lon": lon,
        "address": {
            "city": city_name,
            "state": code.upper(),
            "postcode": tags.get("addr:postcode"),
            "display": display_address or None,
        },
        "contact": {
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "email": tags.get("email") or tags.get("contact:email"),
        },
        "tags": {k: str(v) for k, v in tags.items() if k in {
            "amenity", "shop", "leisure", "healthcare", "emergency", "dog", "pets_allowed",
            "opening_hours", "name", "website", "phone", "contact:website", "contact:phone"
        }},
        "confidence": confidence,
        "qualityScore": quality,
        "warnings": warnings,
        "geo": {
            "stateCode": code,
            "stateName": state_name,
            "citySlug": slugify(city_name),
            "cityName": city_name,
        },
        "source": {
            "provider": "openstreetmap",
            "license": "ODbL",
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
        },
    }


def write_json(path: Path, obj: Any, gzip_copy: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dumps(obj)
    path.write_bytes(data)
    if gzip_copy:
        with gzip.open(str(path) + ".gz", "wb", compresslevel=9) as f:
            f.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--states", required=True)
    ap.add_argument("--cities", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    input_path = Path(args.input)
    out = Path(args.out)

    states, _, state_tree, state_geom_map = load_polygons(Path(args.states))
    cities, _, city_tree, city_geom_map = load_polygons(Path(args.cities))

    buckets = defaultdict(list)
    seen = set()
    report = {
        "totalInput": 0,
        "totalOutput": 0,
        "duplicates": 0,
        "byCategory": defaultdict(int),
        "byState": defaultdict(int),
        "warnings": defaultdict(int),
    }

    for raw in iter_pois(input_path):
        report["totalInput"] += 1
        tags = raw.get("tags", {}) or {}
        category, _ = normalize_category(tags)
        if category == "other":
            continue

        osm_type = raw.get("type") or raw.get("osmType") or "node"
        osm_id = raw.get("id") or raw.get("osmId")
        key = f"{osm_type}_{osm_id}"
        if key in seen:
            report["duplicates"] += 1
            continue
        seen.add(key)

        lat = raw.get("lat") or raw.get("center", {}).get("lat")
        lon = raw.get("lon") or raw.get("center", {}).get("lon")
        if lat is None or lon is None:
            report["warnings"]["missingCoords"] += 1
            continue

        point = Point(float(lon), float(lat))
        state_row = tree_find(point, states, state_tree, state_geom_map)
        city_row = tree_find(point, cities, city_tree, city_geom_map)

        poi = compact_poi(raw, state_row, city_row)
        state_code_ = poi["geo"]["stateCode"]
        city_slug = poi["geo"]["citySlug"]
        cat = poi["category"]

        buckets[(state_code_, city_slug, cat)].append(poi)
        report["totalOutput"] += 1
        report["byCategory"][cat] += 1
        report["byState"][state_code_] += 1
        for warning in poi["warnings"]:
            report["warnings"][warning] += 1

    search_index = []
    page_manifest = []

    for (state, city, cat), items in buckets.items():
        items.sort(key=lambda x: (-x["qualityScore"], x["name"]))
        first = items[0]
        shard_path = out / "states" / state / "cities" / city / f"{cat}.json"
        write_json(shard_path, items)

    city_totals = defaultdict(lambda: {"count": 0, "categories": defaultdict(int), "latSum": 0.0, "lonSum": 0.0, "cityName": "", "stateName": ""})
    for (state, city, cat), items in buckets.items():
        meta = city_totals[(state, city)]
        meta["count"] += len(items)
        meta["categories"][cat] += len(items)
        meta["latSum"] += sum(i["lat"] for i in items)
        meta["lonSum"] += sum(i["lon"] for i in items)
        meta["cityName"] = items[0]["geo"]["cityName"]
        meta["stateName"] = items[0]["geo"]["stateName"]

        if len(items) >= 3:
            page_manifest.append({
                "type": "city-category",
                "state": state,
                "city": city,
                "category": cat,
                "url": f"/places/{state}/{city}/{cat}/",
                "count": len(items),
            })

    for (state, city), meta in city_totals.items():
        count = meta["count"]
        if count <= 0:
            continue
        lat = meta["latSum"] / count
        lon = meta["lonSum"] / count
        search_index.append({
            "city": meta["cityName"],
            "state": state.upper(),
            "stateName": meta["stateName"],
            "slug": f"/places/{state}/{city}/",
            "count": count,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "categories": dict(meta["categories"]),
            "searchKey": f"{meta['cityName']} {state} {meta['stateName']}".lower(),
        })
        if count >= 10:
            page_manifest.append({
                "type": "city",
                "state": state,
                "city": city,
                "url": f"/places/{state}/{city}/",
                "count": count,
            })

    search_index.sort(key=lambda x: -x["count"])
    page_manifest.sort(key=lambda x: (x["state"], x.get("city", ""), x.get("category", "")))

    # Convert defaultdicts before dumping
    report["byCategory"] = dict(report["byCategory"])
    report["byState"] = dict(report["byState"])
    report["warnings"] = dict(report["warnings"])

    write_json(out / "search-index.min.json", search_index)
    write_json(out / "page-manifest.json", page_manifest)
    write_json(out / "quality-report.json", report, gzip_copy=False)

    manifest = {
        "version": "v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "pois": report["totalOutput"],
            "cities": len(search_index),
            "indexablePages": len(page_manifest),
        },
        "files": {
            "searchIndex": "search-index.min.json",
            "pageManifest": "page-manifest.json",
            "qualityReport": "quality-report.json",
        },
        "license": "Contains OpenStreetMap data © OpenStreetMap contributors, licensed under ODbL."
    }
    write_json(out / "manifest.json", manifest, gzip_copy=False)
    print(f"Done. Output: {out}")


if __name__ == "__main__":
    main()
