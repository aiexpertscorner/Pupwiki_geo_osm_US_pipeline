from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .categories import load_category_config, match_category
from .jsonx import dumps


def extract_osm_pbf(pbf: str | Path, out: str | Path, *, category_config: str | None = None, keep_other: bool = False) -> dict[str, Any]:
    try:
        import osmium
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install pyosmium/osmium first: pip install osmium") from exc

    pbf = Path(pbf)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    config = load_category_config(category_config)

    stats = {"nodes": 0, "ways": 0, "relations": 0, "written": 0, "byCategory": {}, "skippedNoCategory": 0, "skippedNoLocation": 0}

    class Handler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.f = out.open("wb")

        def close(self):
            self.f.close()

        def _write(self, obj, osm_type: str, lat: float | None, lon: float | None):
            if lat is None or lon is None:
                stats["skippedNoLocation"] += 1
                return
            tags = {str(k): str(v) for k, v in obj.tags}
            category, confidence, meta = match_category(tags, config)
            if not category:
                stats["skippedNoCategory"] += 1
                if not keep_other:
                    return
                category = "other"
            row = {
                "osmType": osm_type,
                "osmId": int(obj.id),
                "id": f"{osm_type}_{int(obj.id)}",
                "lat": float(lat),
                "lon": float(lon),
                "categoryHint": category,
                "confidenceHint": confidence,
                "matchMeta": meta,
                "tags": tags,
                "source": {"provider": "openstreetmap", "license": "ODbL", "extractedAt": datetime.now(timezone.utc).isoformat()}
            }
            self.f.write(dumps(row))
            self.f.write(b"\n")
            stats["written"] += 1
            stats["byCategory"][category] = stats["byCategory"].get(category, 0) + 1

        def node(self, n):
            stats["nodes"] += 1
            if not n.tags:
                return
            self._write(n, "node", n.location.lat, n.location.lon)

        def way(self, w):
            stats["ways"] += 1
            if not w.tags:
                return
            coords = []
            for node in w.nodes:
                try:
                    if node.location and node.location.valid():
                        coords.append((node.location.lat, node.location.lon))
                except Exception:
                    pass
            if coords:
                lat = sum(x for x, _ in coords) / len(coords)
                lon = sum(y for _, y in coords) / len(coords)
            else:
                lat = lon = None
            self._write(w, "way", lat, lon)

        def relation(self, r):
            # Relations often need multipolygon area assembly. Keep this for future enhancement.
            stats["relations"] += 1
            return

    handler = Handler()
    try:
        handler.apply_file(str(pbf), locations=True, idx="sparse_mem_array")
    finally:
        handler.close()
    return stats
