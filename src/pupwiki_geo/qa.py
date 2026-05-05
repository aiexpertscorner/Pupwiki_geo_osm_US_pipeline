from __future__ import annotations

from pathlib import Path

from .jsonx import read_json, write_json


def run_qa(build_dir: str | Path) -> dict:
    build = Path(build_dir)
    manifest_path = build / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing build manifest: {manifest_path}")
    manifest = read_json(manifest_path)
    report = {"ok": True, "errors": [], "warnings": [], "counts": manifest.get("counts", {})}
    required = ["search-index.min.json", "page-manifest.json", "states/index.json", "reports/quality-report.json"]
    for rel in required:
        if not (build / rel).exists():
            report["ok"] = False
            report["errors"].append(f"Missing {rel}")
    if (build / "search-index.min.json").exists():
        idx = read_json(build / "search-index.min.json")
        if not idx:
            report["warnings"].append("Search index is empty.")
        for item in idx[:100]:
            for key in ("city", "state", "slug", "count", "lat", "lon"):
                if key not in item:
                    report["ok"] = False
                    report["errors"].append(f"Search index item missing {key}: {item}")
                    break
    q_path = build / "reports" / "quality-report.json"
    if q_path.exists():
        q = read_json(q_path)
        if q.get("warnings"):
            report["topWarnings"] = sorted(q["warnings"].items(), key=lambda kv: -kv[1])[:20]
        if q.get("totalOutput", 0) < 100:
            report["warnings"].append("Very low POI output count; probably a test run or missing PBF/categories.")
    write_json(build / "reports" / "qa-summary.json", report, pretty=True)
    return report
