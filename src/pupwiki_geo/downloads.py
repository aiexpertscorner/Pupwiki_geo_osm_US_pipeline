from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

from .jsonx import read_json


def iter_download_items(manifest_path: str | Path, priorities: set[str] | None = None, include_large: bool = False):
    manifest = read_json(manifest_path)
    for ds in manifest.get("datasets", []):
        if priorities and ds.get("Priority") not in priorities:
            continue
        for item in ds.get("download_items", []):
            if item.get("large") and not include_large:
                continue
            row = dict(item)
            row["dataset_id"] = ds.get("id")
            row["priority"] = ds.get("Priority")
            row["dataset"] = ds.get("Dataset")
            yield row


def verify_url(url: str, timeout: int = 20) -> tuple[bool, int | None, str | None]:
    try:
        res = requests.head(url, allow_redirects=True, timeout=timeout, headers={"User-Agent": "PupWikiGeoPipeline/0.1"})
        if res.status_code in (405, 403):
            res = requests.get(url, allow_redirects=True, timeout=timeout, stream=True, headers={"User-Agent": "PupWikiGeoPipeline/0.1"})
            res.close()
        size = int(res.headers.get("content-length", "0") or 0) or None
        return 200 <= res.status_code < 400, size, str(res.status_code)
    except Exception as exc:
        return False, None, str(exc)


def download_file(url: str, dest: str | Path, *, resume: bool = True, retries: int = 3, chunk_size: int = 1024 * 1024) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    existing = tmp.stat().st_size if resume and tmp.exists() else 0
    headers = {"User-Agent": "PupWikiGeoPipeline/0.1"}
    if existing:
        headers["Range"] = f"bytes={existing}-"
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, headers=headers, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", "0") or 0) + existing
                mode = "ab" if existing and r.status_code == 206 else "wb"
                if mode == "wb":
                    existing = 0
                with tmp.open(mode + "") as f, tqdm(total=total or None, initial=existing, unit="B", unit_scale=True, desc=dest.name) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
            tmp.replace(dest)
            return dest
        except Exception as exc:
            last_error = exc
            time.sleep(2 * attempt)
    raise RuntimeError(f"Failed to download {url}: {last_error}")


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
