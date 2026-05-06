from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from .build import build_places
from .compress import compress_json_tree
from .copy_public import copy_for_pupwiki
from .downloads import download_file, iter_download_items, verify_url
from .drive import download_drive_osm
from .extract_osm import extract_osm_pbf
from .qa import run_extract_qa, run_qa
from .unpack import unpack_archives

ROOTS = ["data-raw", "data-work", "data-build", "tmp", "logs", "data-raw/osm/google-drive", "data-work/osm", "data-work/boundaries", "data-work/qa"]


def cmd_init(args):
    for d in ROOTS:
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / ".gitkeep").touch(exist_ok=True)
    print("Initialized PupWiki Geo Pipeline folders.")


def cmd_download(args):
    priorities = set(args.priority or []) or None
    rows = list(iter_download_items(args.manifest, priorities=priorities, include_large=args.include_large))
    print(f"Matched {len(rows)} download items.")
    for item in rows:
        url = item["url"]
        dest = item["destination"]
        if args.verify_remote:
            ok, size, detail = verify_url(url)
            print(f"[{item.get('priority')}] {url} -> {detail} {size or ''}")
            if not ok and not args.allow_failed_verify:
                continue
        if args.dry_run:
            print(f"DRY RUN: {url} -> {dest}")
            continue
        if Path(dest).exists() and not args.force:
            print(f"SKIP exists: {dest}")
            continue
        download_file(url, dest)


def cmd_drive_osm(args):
    out = args.out or os.getenv("PUPWIKI_OSM_PBF") or "data-raw/osm/google-drive/us-latest.osm.pbf"
    file_id = args.file_id or os.getenv("PUPWIKI_OSM_GOOGLE_DRIVE_FILE_ID")
    if not file_id:
        raise SystemExit("Missing --file-id or PUPWIKI_OSM_GOOGLE_DRIVE_FILE_ID")
    p = download_drive_osm(file_id, out)
    print(f"Downloaded Drive OSM file to {p}")


def cmd_extract_osm(args):
    interactive = None
    if args.yes:
        interactive = False
    if args.interactive:
        interactive = True
    stats = extract_osm_pbf(
        args.pbf,
        args.out,
        category_config=args.categories,
        keep_other=args.keep_other,
        include_categories=args.include_categories,
        exclude_categories=args.exclude_categories,
        object_types=args.object_types,
        interactive=interactive,
        batch_size=args.batch_size,
        max_objects=args.max_objects,
        max_written=args.max_written,
        progress_every=args.progress_every,
        progress_seconds=args.progress_seconds,
        stats_path=args.stats_path,
        overwrite=not args.no_overwrite,
    )
    print(json.dumps(stats, indent=2))


def cmd_extract_qa(args):
    print(json.dumps(run_extract_qa(args.input, args.out), indent=2))


def cmd_build(args):
    manifest = build_places(args.input, args.states, args.places, args.out, counties_geojson=args.counties, category_config=args.categories, pretty=args.pretty)
    print(json.dumps(manifest, indent=2))


def cmd_qa(args):
    print(json.dumps(run_qa(args.build), indent=2))


def cmd_compress(args):
    print(json.dumps(compress_json_tree(args.build, brotli=args.brotli), indent=2))


def cmd_unpack(args):
    print(json.dumps(unpack_archives(args.root, overwrite=args.overwrite), indent=2))


def cmd_copy_public(args):
    print(json.dumps(copy_for_pupwiki(args.build, args.pupwiki, mode=args.mode), indent=2))


def main(argv=None):
    load_dotenv()
    ap = argparse.ArgumentParser(prog="pupgeo", description="PupWiki Geo/OpenStreetMap dog POI pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("download")
    s.add_argument("--manifest", default="configs/datasets.generated.json")
    s.add_argument("--priority", action="append", help="P1/P2/P3/P4; can repeat")
    s.add_argument("--include-large", action="store_true")
    s.add_argument("--verify-remote", action="store_true")
    s.add_argument("--allow-failed-verify", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_download)

    s = sub.add_parser("drive-osm")
    s.add_argument("--file-id")
    s.add_argument("--out")
    s.set_defaults(func=cmd_drive_osm)

    s = sub.add_parser("unpack")
    s.add_argument("--root", default="data-raw")
    s.add_argument("--overwrite", action="store_true")
    s.set_defaults(func=cmd_unpack)

    s = sub.add_parser("extract-osm")
    s.add_argument("--pbf", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--categories", default="configs/osm_dog_categories.json")
    s.add_argument("--keep-other", action="store_true")
    s.add_argument("--include-categories", help="Comma-separated category ids/preset selection, e.g. core or dog-parks,pet-stores")
    s.add_argument("--exclude-categories", help="Comma-separated category ids to skip")
    s.add_argument("--object-types", help="node, way, relation, or comma-separated values")
    s.add_argument("--batch-size", type=int, help="Rows per part file. 0 disables batching.")
    s.add_argument("--max-objects", type=int)
    s.add_argument("--max-written", type=int)
    s.add_argument("--progress-every", type=int, default=500000)
    s.add_argument("--progress-seconds", type=float, default=20.0)
    s.add_argument("--stats-path")
    s.add_argument("--no-overwrite", action="store_true")
    s.add_argument("--yes", action="store_true", help="Non-interactive defaults")
    s.add_argument("--interactive", action="store_true", help="Force interactive prompts")
    s.set_defaults(func=cmd_extract_osm)

    s = sub.add_parser("extract-qa")
    s.add_argument("--input", required=True)
    s.add_argument("--out", default="data-work/qa/extract")
    s.set_defaults(func=cmd_extract_qa)

    s = sub.add_parser("build")
    s.add_argument("--input", required=True)
    s.add_argument("--states", required=True)
    s.add_argument("--places", required=True)
    s.add_argument("--counties")
    s.add_argument("--out", required=True)
    s.add_argument("--categories", default="configs/osm_dog_categories.json")
    s.add_argument("--pretty", action="store_true")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("qa")
    s.add_argument("--build", required=True)
    s.set_defaults(func=cmd_qa)

    s = sub.add_parser("compress")
    s.add_argument("--build", required=True)
    s.add_argument("--brotli", action="store_true")
    s.set_defaults(func=cmd_compress)

    s = sub.add_parser("copy-public")
    s.add_argument("--build", required=True)
    s.add_argument("--pupwiki", required=True)
    s.add_argument("--mode", choices=["hybrid", "static"], default="hybrid")
    s.set_defaults(func=cmd_copy_public)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
