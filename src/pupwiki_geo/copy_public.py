from __future__ import annotations

import shutil
from pathlib import Path


def copy_for_pupwiki(build_dir: str | Path, pupwiki_root: str | Path, *, mode: str = "hybrid") -> dict:
    build = Path(build_dir)
    target = Path(pupwiki_root) / "public" / "data" / "places" / build.name
    target.mkdir(parents=True, exist_ok=True)
    copied = []
    always = ["manifest.json", "search-index.min.json", "page-manifest.json", "states/index.json", "reports/quality-report.json"]
    for rel in always:
        src = build / rel
        if src.exists():
            dst = target / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)
    if mode == "static":
        for src in build.rglob("*.json"):
            rel = src.relative_to(build)
            dst = target / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(str(rel))
    return {"target": str(target), "mode": mode, "copied": len(set(copied))}
