from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import requests
from tqdm import tqdm


def extract_drive_id(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{20,}", value):
        return value
    m = re.search(r"/d/([A-Za-z0-9_-]+)", value)
    if m:
        return m.group(1)
    m = re.search(r"id=([A-Za-z0-9_-]+)", value)
    if m:
        return m.group(1)
    raise ValueError(f"Could not extract Google Drive file id from {value!r}")


def download_with_gdown(file_id: str, out: str | Path) -> bool:
    try:
        subprocess.run(["gdown", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return False
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["gdown", "--fuzzy", f"https://drive.google.com/file/d/{file_id}/view", "-O", str(out)], check=True)
    return out.exists() and out.stat().st_size > 0


def download_public_drive_file(file_id: str, out: str | Path, chunk_size: int = 1024 * 1024) -> Path:
    """Best-effort public Drive download. For private/huge files, gdown/rclone/Drive Desktop is more reliable."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    base = "https://docs.google.com/uc?export=download"
    response = session.get(base, params={"id": file_id}, stream=True, timeout=60)
    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break
    if token:
        response.close()
        response = session.get(base, params={"id": file_id, "confirm": token}, stream=True, timeout=60)
    response.raise_for_status()
    tmp = out.with_suffix(out.suffix + ".part")
    total = int(response.headers.get("content-length", "0") or 0) or None
    with tmp.open("wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=out.name) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    tmp.replace(out)
    return out


def download_drive_osm(file_id_or_url: str, out: str | Path) -> Path:
    file_id = extract_drive_id(file_id_or_url)
    out = Path(out)
    if download_with_gdown(file_id, out):
        return out
    return download_public_drive_file(file_id, out)
