from __future__ import annotations

import gzip
from pathlib import Path


def compress_json_tree(build_dir: str | Path, *, brotli: bool = False) -> dict:
    build = Path(build_dir)
    stats = {"gzip": 0, "brotli": 0}
    for path in build.rglob("*.json"):
        data = path.read_bytes()
        gz = Path(str(path) + ".gz")
        with gzip.open(gz, "wb", compresslevel=9) as f:
            f.write(data)
        stats["gzip"] += 1
        if brotli:
            import brotli as br
            Path(str(path) + ".br").write_bytes(br.compress(data, quality=9))
            stats["brotli"] += 1
    return stats
