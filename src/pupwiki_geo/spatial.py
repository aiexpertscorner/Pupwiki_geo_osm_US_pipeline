from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from .jsonx import read_json
from .text import slugify, state_code_from_props


@dataclass
class FeatureIndex:
    rows: list[dict[str, Any]]
    geoms: list[Any]
    tree: STRtree
    geom_to_idx: dict[int, int]

    @classmethod
    def from_geojson(cls, path: str | Path, *, name_keys: tuple[str, ...] = ("NAME", "name"), state_filter: str | None = None):
        data = read_json(path)
        rows = []
        geoms = []
        for feat in data.get("features", []):
            props = feat.get("properties", {}) or {}
            geom = shape(feat.get("geometry"))
            if geom.is_empty:
                continue
            name = next((props.get(k) for k in name_keys if props.get(k)), None) or "Unknown"
            row = {"name": name, "props": props, "geom": geom}
            if state_filter:
                code = state_code_from_props(props)
                if code != state_filter.lower():
                    continue
            rows.append(row)
            geoms.append(geom)
        return cls(rows=rows, geoms=geoms, tree=STRtree(geoms), geom_to_idx={id(g): i for i, g in enumerate(geoms)})

    def find(self, lon: float, lat: float) -> dict[str, Any] | None:
        if not self.rows:
            return None
        point = Point(lon, lat)
        candidates = self.tree.query(point)
        for c in candidates:
            if isinstance(c, (int,)):
                idx = int(c)
            else:
                idx = self.geom_to_idx.get(id(c))
                if idx is None:
                    continue
            geom = self.rows[idx]["geom"]
            if geom.contains(point) or geom.intersects(point):
                return self.rows[idx]
        return None


def geo_name(row: dict[str, Any] | None, fallback: str = "Unknown") -> str:
    return row["name"] if row else fallback


def county_name(row: dict[str, Any] | None) -> str | None:
    return row["name"] if row else None


def city_slug_from_row(row: dict[str, Any] | None, tags: dict[str, Any] | None, county: dict[str, Any] | None = None) -> tuple[str, str, str]:
    tags = tags or {}
    if row:
        name = row["name"]
        return name, slugify(name), "place"
    city_tag = tags.get("addr:city") or tags.get("is_in:city")
    if city_tag:
        return str(city_tag), slugify(str(city_tag)), "osm-address"
    if county:
        name = f"{county['name']} County"
        return name, slugify(name), "county-fallback"
    return "Unknown", "unknown", "unknown"
