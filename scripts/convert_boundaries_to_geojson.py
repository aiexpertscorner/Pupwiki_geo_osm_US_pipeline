#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Convert Census shapefiles/geopackages to GeoJSON for spatial joins.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--simplify", type=float, default=0.0, help="Optional simplify tolerance in source CRS units after reprojection.")
    args = ap.parse_args()
    try:
        import geopandas as gpd
    except Exception as exc:
        raise SystemExit("Install optional deps first: pip install geopandas pyogrio") from exc
    gdf = gpd.read_file(args.input)
    if gdf.crs is not None and str(gdf.crs).lower() not in ("epsg:4326", "wgs84"):
        gdf = gdf.to_crs("EPSG:4326")
    if args.simplify:
        gdf["geometry"] = gdf.geometry.simplify(args.simplify, preserve_topology=True)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out, driver="GeoJSON")
    print(f"Wrote {out} ({len(gdf)} features)")


if __name__ == "__main__":
    main()
