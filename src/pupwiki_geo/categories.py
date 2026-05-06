from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .jsonx import read_json

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "osm_dog_categories.json"

CONFIDENCE_RANK = {"low": 1, "medium": 2, "high": 3}


def _tag(tags: dict[str, Any], key: str) -> str:
    return str(tags.get(key, "") or "").strip()


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _has_dog_access(tags: dict[str, Any], values: set[str]) -> bool:
    for key in ("dog", "dogs", "pets", "pets_allowed"):
        val = _tag(tags, key).lower()
        if val in values or val.startswith("yes"):
            return True
    return False


def _all_match(tags: dict[str, Any], expected: dict[str, str]) -> bool:
    return all(_tag(tags, k).lower() == str(v).lower() for k, v in expected.items())


def _any_base_match(tags: dict[str, Any], bases: list[dict[str, str]]) -> bool:
    return any(_all_match(tags, b) for b in bases)


@lru_cache(maxsize=8)
def load_category_config(path: str | None = None) -> dict[str, Any]:
    return read_json(path or DEFAULT_CONFIG)


def category_meta(category_id: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or load_category_config()
    for cat in config.get("categories", []):
        if cat.get("id") == category_id or category_id in cat.get("legacyIds", []):
            return cat
    return {"id": category_id, "label": category_id.replace("-", " ").title(), "tier": "C", "indexable": False}


def category_id_map(config: dict[str, Any] | None = None) -> dict[str, str]:
    config = config or load_category_config()
    mapping: dict[str, str] = {}
    for cat in config.get("categories", []):
        cid = cat.get("id")
        if not cid:
            continue
        mapping[cid] = cid
        for legacy in cat.get("legacyIds", []):
            mapping[str(legacy)] = cid
    return mapping


def normalize_category_id(category_id: str | None, config: dict[str, Any] | None = None) -> str | None:
    if not category_id:
        return None
    return category_id_map(config).get(str(category_id), str(category_id))


def _rule_matches(rule: dict[str, Any], tags: dict[str, Any], dog_values: set[str], name_blob: str) -> bool:
    ok = True
    if "all" in rule:
        ok = ok and _all_match(tags, rule["all"])
    if "anyBase" in rule:
        ok = ok and _any_base_match(tags, rule["anyBase"])
    if "amenityIn" in rule:
        vals = {x.lower() for x in rule["amenityIn"]}
        ok = ok and _tag(tags, "amenity").lower() in vals
    if "amenityOrTourism" in rule:
        vals = {x.lower() for x in rule["amenityOrTourism"]}
        ok = ok and (_tag(tags, "amenity").lower() in vals or _tag(tags, "tourism").lower() in vals)
    if rule.get("dogAccess"):
        ok = ok and _has_dog_access(tags, dog_values)
    if "nameRegex" in rule:
        ok = ok and bool(re.search(rule["nameRegex"], name_blob, re.I))
    return bool(ok)


def match_category(tags: dict[str, Any], config: dict[str, Any] | None = None) -> tuple[str | None, str, dict[str, Any]]:
    """Return (category_id, confidence, match_meta).

    match_meta includes the exact matched rule id, rule body, tier, label, indexable and review flags.
    """
    config = config or load_category_config()
    dog_values = set(config.get("dogAccessValues", []))
    name_blob = " ".join(str(tags.get(k, "")) for k in ("name", "alt_name", "description", "operator", "brand")).lower()

    categories = list(config.get("categories", []))
    categories = sorted(categories, key=lambda c: 0 if c.get("id") == "emergency-vets" else 1)

    for cat in categories:
        matched_rule = None
        matched_confidence = cat.get("confidence", "low")
        for rule in cat.get("rules", []):
            if _rule_matches(rule, tags, dog_values, name_blob):
                matched_rule = rule
                matched_confidence = rule.get("confidence") or matched_confidence
                break
        if not matched_rule:
            continue

        if cat.get("excludeIfEmergency") and (
            _tag(tags, "emergency").lower() == "yes"
            or re.search(r"emergency|urgent|24 hour|24-hour|24/7|after hours", name_blob)
        ):
            continue

        meta = {
            "matchedRule": matched_rule,
            "matchedRuleId": matched_rule.get("id"),
            "tier": cat.get("tier"),
            "label": cat.get("label"),
            "indexable": bool(cat.get("indexable")),
            "needsReview": bool(matched_rule.get("needsReview")),
            "categoryDescription": cat.get("description"),
        }
        return cat["id"], matched_confidence, meta

    return None, "low", {"matchedRule": None, "matchedRuleId": None}


def safe_frontend_tags(tags: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, str]:
    config = config or load_category_config()
    allowed = set(config.get("safeFrontendTags", []))
    return {k: str(v) for k, v in tags.items() if k in allowed and v not in (None, "")}
