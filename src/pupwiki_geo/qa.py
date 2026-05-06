from __future__ import annotations

from collections import Counter
from pathlib import Path

from .jsonx import iter_ndjson, read_json, write_json, write_ndjson


def _iter_build_pois(build: Path):
    for path in (build / "states").glob("*/cities/*/*.json"):
        if path.name == "index.json" or path.name.endswith(".gz"):
            continue
        try:
            rows = read_json(path)
            if isinstance(rows, list):
                for row in rows:
                    yield row
        except Exception:
            continue


def run_extract_qa(input_path: str | Path, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    category_counts = Counter()
    low_conf = []
    missing_name = []
    emergency_review = []
    total = 0
    for row in iter_ndjson(input_path):
        total += 1
        cat = row.get("categoryHint") or row.get("category") or "unknown"
        category_counts[cat] += 1
        tags = row.get("tags") or {}
        confidence = row.get("confidenceHint") or row.get("confidence") or "low"
        if confidence == "low" or (row.get("matchMeta") or {}).get("needsReview"):
            low_conf.append(row)
        if not tags.get("name"):
            missing_name.append(row)
        if cat == "emergency-vets":
            emergency_review.append(row)
    summary = {"total": total, "byCategory": dict(category_counts), "lowConfidence": len(low_conf), "missingName": len(missing_name), "emergencyReview": len(emergency_review)}
    write_json(out / "category-counts.json", summary, pretty=True)
    write_ndjson(out / "low-confidence-review.ndjson", low_conf[:50000])
    write_ndjson(out / "missing-name-review.ndjson", missing_name[:50000])
    write_ndjson(out / "emergency-vets-review.ndjson", emergency_review[:50000])
    return summary


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
    category_counts = Counter()
    low_conf = []
    missing_name = []
    emergency_review = []
    for poi in _iter_build_pois(build):
        cat = poi.get("category") or "unknown"
        category_counts[cat] += 1
        if poi.get("confidence") == "low" or "rule_needs_review" in poi.get("warnings", []):
            low_conf.append(poi)
        if "missing_name" in poi.get("warnings", []) or not poi.get("name"):
            missing_name.append(poi)
        if cat == "emergency-vets":
            emergency_review.append(poi)
    reports = build / "reports"
    write_json(reports / "category-counts.json", {"total": sum(category_counts.values()), "byCategory": dict(category_counts)}, pretty=True)
    write_ndjson(reports / "low-confidence-review.ndjson", low_conf[:50000])
    write_ndjson(reports / "missing-name-review.ndjson", missing_name[:50000])
    write_ndjson(reports / "emergency-vets-review.ndjson", emergency_review[:50000])
    report["reviewFiles"] = {"categoryCounts": "reports/category-counts.json", "lowConfidence": "reports/low-confidence-review.ndjson", "missingName": "reports/missing-name-review.ndjson", "emergencyVets": "reports/emergency-vets-review.ndjson"}
    write_json(reports / "qa-summary.json", report, pretty=True)
    return report
