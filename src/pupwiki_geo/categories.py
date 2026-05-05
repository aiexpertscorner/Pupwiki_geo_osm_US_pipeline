from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .jsonx import read_json

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "osm_dog_categories.json"


def _tag(tags: dict[str, Any], key: str) -> str:
    return str(tags.get(key, "") or "").strip()


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


@lru_cache(maxsize=4)
def load_category_config(path: str | None = None) -> dict[str, Any]:
    return read_json(path or DEFAULT_CONFIG)


def match_category(tags: dict[str, Any], config: dict[str, Any] | None = None) -> tuple[str | None, str, dict[str, Any]]:
    """Return (category_id, confidence, match_meta)."""
    config = config or load_category_config()
    dog_values = set(config.get("dogAccessValues", []))
    name_blob = " ".join(str(tags.get(k, "")) for k in ("name", "alt_name", "description", "operator")).lower()

    # Emergency vets before generic vets.
    categories = config.get("categories", [])
    categories = sorted(categories, key=lambda c: 0 if c["id"] == "emergency-vets" else 1)

    for cat in categories:
        matched = False
        reasons = []
        for rule in cat.get("rules", []):
            ok = True
            if "all" in rule:
                ok = ok and _all_match(tags, rule["all"])
            if "anyBase" in rule:
                ok = ok and _any_base_match(tags, rule["anyBase"])
            if "amenityIn" in rule:
                ok = ok and _tag(tags, "amenity").lower() in {x.lower() for x in rule["amenityIn"]}
            if "amenityOrTourism" in rule:
                vals = {x.lower() for x in rule["amenityOrTourism"]}
                ok = ok and (_tag(tags, "amenity").lower() in vals or _tag(tags, "tourism").lower() in vals)
            if rule.get("dogAccess"):
                ok = ok and _has_dog_access(tags, dog_values)
            if "nameRegex" in rule:
                ok = ok and bool(re.search(rule["nameRegex"], name_blob, re.I))
            if ok:
                matched = True
                reasons.append(rule)
                break
        if not matched:
            continue
        if cat.get("excludeIfEmergency") and (_tag(tags, "emergency").lower() == "yes" or re.search(r"emergency|urgent|24 hour|24-hour", name_blob)):
            continue
        return cat["id"], cat.get("confidence", "low"), {"matchedRule": reasons[:1], "tier": cat.get("tier"), "label": cat.get("label")}
    return None, "low", {"matchedRule": None}


def safe_frontend_tags(tags: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, str]:
    config = config or load_category_config()
    allowed = set(config.get("safeFrontendTags", []))
    return {k: str(v) for k, v in tags.items() if k in allowed and v not in (None, "")}
