from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .categories import load_category_config, match_category
from .jsonx import dumps

DEFAULT_PROGRESS_EVERY = 500_000
DEFAULT_PROGRESS_SECONDS = 20.0
DEFAULT_FLUSH_EVERY_WRITTEN = 1_000
DEFAULT_BATCH_SIZE = 50_000


class _StopExtraction(Exception):
    """Internal exception used for deliberate smoke-test/limit stops."""


def _as_set(value: Iterable[str] | str | None) -> set[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        raw = value.replace(";", ",").split(",")
    else:
        raw = []
        for part in value:
            raw.extend(str(part).replace(";", ",").split(","))
    result = {x.strip() for x in raw if str(x).strip()}
    return result or None


def _category_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    return list(config.get("categories", []))


def _category_ids(config: dict[str, Any]) -> set[str]:
    return {str(c.get("id")) for c in _category_rows(config) if c.get("id")}


def _preset_categories(config: dict[str, Any], preset: str) -> set[str]:
    preset = preset.strip().lower()
    cats = _category_rows(config)

    if preset in {"all", "*"}:
        return {c["id"] for c in cats if c.get("id")}

    if preset in {"core", "tier-a", "a", "mvp", "indexable"}:
        return {
            c["id"]
            for c in cats
            if c.get("id") and (c.get("tier") == "A" or c.get("indexable") is True)
        }

    if preset in {"tier-b", "b"}:
        return {c["id"] for c in cats if c.get("id") and c.get("tier") == "B"}

    if preset in {"tier-c", "c"}:
        return {c["id"] for c in cats if c.get("id") and c.get("tier") == "C"}

    return set()


def _parse_category_choice(raw: str, config: dict[str, Any]) -> set[str]:
    raw = (raw or "").strip()

    if not raw:
        return _preset_categories(config, "core")

    preset = _preset_categories(config, raw)
    if preset:
        return preset

    cats = _category_rows(config)
    by_id = {str(c.get("id")): c for c in cats if c.get("id")}
    by_number = {
        str(i): str(c.get("id"))
        for i, c in enumerate(cats, start=1)
        if c.get("id")
    }

    if raw.startswith("?") or raw.lower().startswith("q:"):
        query = raw[1:] if raw.startswith("?") else raw.split(":", 1)[1]
        query = query.strip().lower()
        return {
            str(c.get("id"))
            for c in cats
            if c.get("id")
            and query
            and query
            in " ".join(
                str(c.get(k, "")) for k in ("id", "label", "description", "tier")
            ).lower()
        }

    selected: set[str] = set()

    for token in raw.replace(";", ",").split(","):
        t = token.strip()
        if not t:
            continue

        t_lower = t.lower()

        if t in by_number:
            selected.add(by_number[t])
            continue

        if t in by_id:
            selected.add(t)
            continue

        if t_lower in by_id:
            selected.add(t_lower)
            continue

        hits = [cid for cid in by_id if t_lower in cid.lower()]
        selected.update(hits)

    return selected


def _print_category_menu(config: dict[str, Any]) -> None:
    print("\nPupWiki OSM dog POI category selection")
    print("Presets: core / tier-a / tier-b / tier-c / all")
    print("Search: ?vet, ?park, ?grooming")
    print("Select: 1,3,dog-parks or veterinary-clinics,dog-grooming")
    print("-" * 96)

    for i, cat in enumerate(_category_rows(config), start=1):
        cid = str(cat.get("id", ""))
        label = str(cat.get("label", cid))
        tier = str(cat.get("tier", "?"))
        indexable = "index" if cat.get("indexable") else "support"
        print(f"{i:>2}. {cid:<30} tier={tier:<1} {indexable:<7} {label}")

    print("-" * 96)


def _should_prompt(interactive: bool | None) -> bool:
    if interactive is True:
        return True
    if interactive is False:
        return False
    return bool(sys.stdin and sys.stdin.isatty() and sys.stdout and sys.stdout.isatty())


def _prompt_plan(
    config: dict[str, Any],
    *,
    include_categories: set[str] | None,
    exclude_categories: set[str] | None,
    object_types: set[str] | None,
    batch_size: int | None,
    max_written: int | None,
    max_objects: int | None,
) -> tuple[set[str] | None, set[str] | None, set[str], int | None, int | None, int | None]:
    valid_categories = _category_ids(config)

    if include_categories is None:
        _print_category_menu(config)
        raw = input("Welke categories extracten? [core] > ").strip()
        include_categories = _parse_category_choice(raw, config)

        if not include_categories:
            print("Geen geldige keuze gevonden. Fallback: core/tier-a.")
            include_categories = _preset_categories(config, "core")

    include_categories = include_categories & valid_categories if include_categories else include_categories

    if exclude_categories:
        exclude_categories = exclude_categories & valid_categories

    if object_types is None:
        print("\nObject types:")
        print("1. nodes only  = snelste smoke test, minder compleet")
        print("2. nodes+ways  = beste output, langzamer, gebruikt way centroid")
        print("3. ways only   = alleen polygon/way POIs")
        raw = input("Welke object types? [1 voor snelle test] > ").strip().lower()

        if raw in {"2", "node+way", "nodes+ways", "both", "all"}:
            object_types = {"node", "way"}
        elif raw in {"3", "way", "ways", "ways-only"}:
            object_types = {"way"}
        else:
            object_types = {"node"}

    if batch_size is None:
        raw = input(
            f"Batch output? regels per part, 0=single file [{DEFAULT_BATCH_SIZE}] > "
        ).strip()

        if raw == "":
            batch_size = DEFAULT_BATCH_SIZE
        else:
            try:
                batch_size = max(0, int(raw))
            except ValueError:
                batch_size = DEFAULT_BATCH_SIZE

    if max_written is None:
        raw = input("Max geschreven POIs voor test? Enter=geen limiet, bijv. 1000 > ").strip()

        if raw:
            try:
                max_written = max(1, int(raw))
            except ValueError:
                max_written = None

    if max_objects is None:
        raw = input("Max OSM objecten scannen voor smoke test? Enter=geen limiet > ").strip()

        if raw:
            try:
                max_objects = max(1, int(raw))
            except ValueError:
                max_objects = None

    return (
        include_categories,
        exclude_categories,
        object_types or {"node"},
        batch_size,
        max_written,
        max_objects,
    )


def _human_bytes(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{n}B"


def _elapsed(start: float) -> str:
    seconds = int(time.time() - start)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class _NdjsonWriter:
    def __init__(
        self,
        out: Path,
        *,
        batch_size: int | None,
        overwrite: bool,
        flush_every_written: int,
    ) -> None:
        self.out = out
        self.batch_size = batch_size if batch_size and batch_size > 0 else None
        self.overwrite = overwrite
        self.flush_every_written = max(1, int(flush_every_written or DEFAULT_FLUSH_EVERY_WRITTEN))

        self.files: list[str] = []
        self.current_file = None
        self.current_path: Path | None = None
        self.part_index = 0
        self.rows_in_part = 0
        self.total_written = 0

        out.parent.mkdir(parents=True, exist_ok=True)

        if self.batch_size:
            if overwrite:
                suffix = out.suffix or ".ndjson"
                pattern = f"{out.stem}.part-*{suffix}"
                for old in out.parent.glob(pattern):
                    old.unlink(missing_ok=True)
        else:
            if out.exists() and not overwrite:
                raise FileExistsError(f"Output exists: {out}")
            self.current_path = out
            self.current_file = out.open("wb")
            self.files.append(str(out))

    def _open_next_part(self) -> None:
        if self.current_file:
            self.current_file.flush()
            self.current_file.close()

        self.part_index += 1
        suffix = self.out.suffix or ".ndjson"
        self.current_path = self.out.parent / f"{self.out.stem}.part-{self.part_index:05d}{suffix}"
        self.current_file = self.current_path.open("wb")
        self.files.append(str(self.current_path))
        self.rows_in_part = 0

    def write(self, row: dict[str, Any]) -> None:
        if self.batch_size and (
            self.current_file is None or self.rows_in_part >= self.batch_size
        ):
            self._open_next_part()

        if self.current_file is None:
            raise RuntimeError("Writer is not open")

        self.current_file.write(dumps(row))
        self.current_file.write(b"\n")

        self.total_written += 1
        self.rows_in_part += 1

        if self.total_written % self.flush_every_written == 0:
            self.current_file.flush()

    def flush(self) -> None:
        if self.current_file:
            self.current_file.flush()

    def close(self) -> None:
        if self.current_file:
            self.current_file.flush()
            self.current_file.close()
            self.current_file = None

    def bytes_written(self) -> int:
        total = 0
        for file_name in self.files:
            path = Path(file_name)
            if path.exists():
                total += path.stat().st_size
        return total

    def manifest_path(self) -> Path | None:
        if not self.batch_size:
            return None
        return self.out.parent / f"{self.out.stem}.manifest.json"

    def write_manifest(self, stats: dict[str, Any]) -> None:
        manifest_path = self.manifest_path()
        if not manifest_path:
            return

        payload = {
            "type": "pupwiki-osm-extract-batches",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "baseOutput": str(self.out),
            "batchSize": self.batch_size,
            "parts": self.files,
            "stats": stats,
        }

        manifest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _write_stats(path: Path | None, stats: dict[str, Any]) -> None:
    if not path:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp") if path.suffix else path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _normalize_object_types(value: Iterable[str] | str | None) -> set[str] | None:
    raw = _as_set(value)

    if raw is None:
        return None

    aliases = {
        "nodes": "node",
        "node": "node",
        "n": "node",
        "ways": "way",
        "way": "way",
        "w": "way",
        "relations": "relation",
        "relation": "relation",
        "r": "relation",
    }

    result = {aliases[x.lower()] for x in raw if x.lower() in aliases}
    return result or None


def extract_osm_pbf(
    pbf: str | Path,
    out: str | Path,
    *,
    category_config: str | None = None,
    keep_other: bool = False,
    include_categories: Iterable[str] | str | None = None,
    exclude_categories: Iterable[str] | str | None = None,
    object_types: Iterable[str] | str | None = None,
    interactive: bool | None = None,
    batch_size: int | None = None,
    progress_every: int = DEFAULT_PROGRESS_EVERY,
    progress_seconds: float = DEFAULT_PROGRESS_SECONDS,
    flush_every_written: int = DEFAULT_FLUSH_EVERY_WRITTEN,
    max_objects: int | None = None,
    max_written: int | None = None,
    stats_path: str | Path | None = None,
    overwrite: bool = True,
    location_index: str = "sparse_mem_array",
) -> dict[str, Any]:
    try:
        import osmium
    except Exception as exc:
        raise RuntimeError("Install pyosmium/osmium first: pip install osmium") from exc

    pbf = Path(pbf)
    out = Path(out)

    if not pbf.exists():
        raise FileNotFoundError(f"PBF not found: {pbf}")

    if pbf.stat().st_size < 1_000_000:
        raise ValueError(
            f"PBF is suspiciously small ({pbf.stat().st_size} bytes): {pbf}. "
            "This is often a Google Drive HTML/warning response, not a real .osm.pbf."
        )

    config = load_category_config(category_config)

    include_set = _as_set(include_categories)
    exclude_set = _as_set(exclude_categories)
    object_type_set = _normalize_object_types(object_types)

    if _should_prompt(interactive):
        (
            include_set,
            exclude_set,
            object_type_set,
            batch_size,
            max_written,
            max_objects,
        ) = _prompt_plan(
            config,
            include_categories=include_set,
            exclude_categories=exclude_set,
            object_types=object_type_set,
            batch_size=batch_size,
            max_written=max_written,
            max_objects=max_objects,
        )
    else:
        if object_type_set is None:
            object_type_set = {"node", "way"}

    valid_categories = _category_ids(config)

    if include_set:
        unknown = sorted(include_set - valid_categories)
        if unknown:
            raise ValueError(f"Unknown include categories: {unknown}. Valid: {sorted(valid_categories)}")

    if exclude_set:
        unknown = sorted(exclude_set - valid_categories)
        if unknown:
            raise ValueError(f"Unknown exclude categories: {unknown}. Valid: {sorted(valid_categories)}")

    stats_path_obj = Path(stats_path) if stats_path else out.parent / f"{out.stem}.stats.json"

    writer = _NdjsonWriter(
        out,
        batch_size=batch_size,
        overwrite=overwrite,
        flush_every_written=flush_every_written,
    )

    start = time.time()

    stats: dict[str, Any] = {
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "finishedAt": None,
        "elapsedSeconds": None,
        "pbf": str(pbf),
        "pbfBytes": pbf.stat().st_size,
        "output": str(out),
        "outputMode": "batched" if batch_size and batch_size > 0 else "single",
        "batchSize": batch_size if batch_size and batch_size > 0 else None,
        "objectTypes": sorted(object_type_set or {"node", "way"}),
        "includeCategories": sorted(include_set) if include_set else None,
        "excludeCategories": sorted(exclude_set) if exclude_set else None,
        "keepOther": keep_other,
        "nodes": 0,
        "ways": 0,
        "relations": 0,
        "objectsScanned": 0,
        "written": 0,
        "byCategory": {},
        "skippedNoCategory": 0,
        "skippedExcludedCategory": 0,
        "skippedNoLocation": 0,
        "skippedObjectType": 0,
        "limitReached": None,
        "outputBytes": 0,
        "outputFiles": [],
    }

    next_progress = max(1, int(progress_every or DEFAULT_PROGRESS_EVERY))
    last_progress_time = time.time()

    def update_output_stats() -> None:
        stats["outputBytes"] = writer.bytes_written()
        stats["outputFiles"] = writer.files

    def maybe_progress(force: bool = False) -> None:
        nonlocal next_progress, last_progress_time

        now = time.time()
        scanned = int(stats["objectsScanned"])

        if not force and scanned < next_progress and (now - last_progress_time) < progress_seconds:
            return

        update_output_stats()

        cat_bits = ", ".join(
            f"{k}:{v}" for k, v in sorted(stats["byCategory"].items())
        ) or "none yet"

        print(
            "[extract-osm] "
            f"elapsed={_elapsed(start)} "
            f"scanned={scanned:,} "
            f"nodes={int(stats['nodes']):,} "
            f"ways={int(stats['ways']):,} "
            f"relations={int(stats['relations']):,} "
            f"written={int(stats['written']):,} "
            f"out={_human_bytes(int(stats['outputBytes']))} "
            f"categories={cat_bits}",
            flush=True,
        )

        _write_stats(stats_path_obj, stats)
        last_progress_time = now

        while next_progress <= scanned:
            next_progress += max(1, int(progress_every or DEFAULT_PROGRESS_EVERY))

    def check_limits() -> None:
        if max_objects and int(stats["objectsScanned"]) >= max_objects:
            stats["limitReached"] = f"max_objects={max_objects}"
            raise _StopExtraction()

        if max_written and int(stats["written"]) >= max_written:
            stats["limitReached"] = f"max_written={max_written}"
            raise _StopExtraction()

    def write_obj(obj, osm_type: str, lat: float | None, lon: float | None) -> None:
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

        if include_set and category not in include_set:
            stats["skippedExcludedCategory"] += 1
            return

        if exclude_set and category in exclude_set:
            stats["skippedExcludedCategory"] += 1
            return

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
            "source": {
                "provider": "openstreetmap",
                "license": "ODbL",
                "extractedAt": datetime.now(timezone.utc).isoformat(),
            },
        }

        writer.write(row)

        stats["written"] += 1
        stats["byCategory"][category] = stats["byCategory"].get(category, 0) + 1

        check_limits()

    class Handler(osmium.SimpleHandler):
        def node(self, n):
            stats["nodes"] += 1
            stats["objectsScanned"] += 1

            if "node" not in object_type_set:
                stats["skippedObjectType"] += 1
                maybe_progress()
                check_limits()
                return

            if not n.tags:
                maybe_progress()
                check_limits()
                return

            try:
                if n.location and n.location.valid():
                    write_obj(n, "node", n.location.lat, n.location.lon)
                else:
                    stats["skippedNoLocation"] += 1
            except Exception:
                stats["skippedNoLocation"] += 1

            maybe_progress()
            check_limits()

        def way(self, w):
            stats["ways"] += 1
            stats["objectsScanned"] += 1

            if "way" not in object_type_set:
                stats["skippedObjectType"] += 1
                maybe_progress()
                check_limits()
                return

            if not w.tags:
                maybe_progress()
                check_limits()
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
                write_obj(w, "way", lat, lon)
            else:
                stats["skippedNoLocation"] += 1

            maybe_progress()
            check_limits()

        def relation(self, r):
            stats["relations"] += 1
            stats["objectsScanned"] += 1

            if "relation" not in object_type_set:
                stats["skippedObjectType"] += 1

            maybe_progress()
            check_limits()

    print(
        "[extract-osm] starting "
        f"pbf={pbf} "
        f"size={_human_bytes(pbf.stat().st_size)} "
        f"out={out} "
        f"mode={stats['outputMode']} "
        f"objectTypes={','.join(sorted(object_type_set))} "
        f"include={stats['includeCategories'] or 'all'}",
        flush=True,
    )

    handler = Handler()

    try:
        uses_way_locations = "way" in object_type_set

        if uses_way_locations:
            handler.apply_file(str(pbf), locations=True, idx=location_index)
        else:
            handler.apply_file(str(pbf), locations=False)

    except _StopExtraction:
        print(f"[extract-osm] stopped by limit: {stats['limitReached']}", flush=True)

    finally:
        writer.flush()
        writer.close()
        update_output_stats()

        stats["finishedAt"] = datetime.now(timezone.utc).isoformat()
        stats["elapsedSeconds"] = round(time.time() - start, 2)

        _write_stats(stats_path_obj, stats)
        writer.write_manifest(stats)
        maybe_progress(force=True)

    return stats