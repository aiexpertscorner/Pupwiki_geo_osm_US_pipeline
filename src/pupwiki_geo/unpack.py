from __future__ import annotations

import gzip
import shutil
import zipfile
from pathlib import Path


def unpack_archives(root: str | Path, *, overwrite: bool = False) -> dict:
    root = Path(root)
    stats = {"zip": 0, "gz": 0, "skipped": 0}
    for path in root.rglob("*"):
        if path.suffix.lower() == ".zip":
            out = path.with_suffix("")
            if out.exists() and not overwrite:
                stats["skipped"] += 1
                continue
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path) as zf:
                zf.extractall(out)
            stats["zip"] += 1
        elif path.suffix.lower() == ".gz" and not str(path).endswith(".json.gz"):
            out = path.with_suffix("")
            if out.exists() and not overwrite:
                stats["skipped"] += 1
                continue
            with gzip.open(path, "rb") as f_in, out.open("wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            stats["gz"] += 1
    return stats
