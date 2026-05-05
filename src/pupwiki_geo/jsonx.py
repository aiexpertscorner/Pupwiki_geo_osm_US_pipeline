from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import orjson
except Exception:  # pragma: no cover
    orjson = None


def dumps(obj: Any, *, pretty: bool = False) -> bytes:
    if orjson:
        option = 0
        if pretty:
            option |= orjson.OPT_INDENT_2
        return orjson.dumps(obj, option=option)
    return json.dumps(obj, ensure_ascii=False, indent=2 if pretty else None, separators=None if pretty else (",", ":")).encode("utf-8")


def loads_bytes(data: bytes) -> Any:
    if orjson:
        return orjson.loads(data)
    return json.loads(data.decode("utf-8"))


def read_json(path: str | Path) -> Any:
    return loads_bytes(Path(path).read_bytes())


def write_json(path: str | Path, obj: Any, *, pretty: bool = False) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(dumps(obj, pretty=pretty))


def iter_ndjson(path: str | Path):
    p = Path(path)
    opener = open
    if str(p).endswith(".gz"):
        import gzip
        opener = gzip.open
    with opener(p, "rb") as f:
        for line in f:
            line = line.strip()
            if line:
                yield loads_bytes(line)


def write_ndjson(path: str | Path, rows, *, gzip_output: bool = False) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if gzip_output or str(p).endswith(".gz"):
        import gzip
        with gzip.open(p, "wb", compresslevel=6) as f:
            for row in rows:
                f.write(dumps(row))
                f.write(b"\n")
                count += 1
    else:
        with p.open("wb") as f:
            for row in rows:
                f.write(dumps(row))
                f.write(b"\n")
                count += 1
    return count
