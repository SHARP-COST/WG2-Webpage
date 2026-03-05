#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from sync_members import to_yaml

ROOT = Path(__file__).resolve().parents[1]

DATA_JSON = ROOT / "data" / "members.json"
DATA_YAML = ROOT / "data" / "members.yaml"
SITE_JSON = ROOT / "site" / "data" / "members.json"
SITE_YAML = ROOT / "site" / "data" / "members.yaml"

REQUIRED_KEYS = {
    "id",
    "name",
    "institution",
    "country_code",
    "country",
    "email",
    "github",
    "domain_badge",
    "past_works",
    "expertise",
    "current_interests",
    "expertise_tags",
    "source_works",
    "source_file",
}


def fail(msg: str) -> None:
    raise SystemExit(f"CHECK FAILED: {msg}")


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    data_json_raw = read_text(DATA_JSON)
    data_yaml_raw = read_text(DATA_YAML)
    site_json_raw = read_text(SITE_JSON)
    site_yaml_raw = read_text(SITE_YAML)

    try:
        payload = json.loads(data_json_raw)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {DATA_JSON}: {exc}")

    if not isinstance(payload, dict):
        fail("data/members.json must be an object")
    if "members" not in payload or not isinstance(payload["members"], list):
        fail("data/members.json must contain a 'members' list")

    members = payload["members"]
    if not members:
        fail("members list is empty")

    seen_ids: set[str] = set()
    for idx, member in enumerate(members):
        if not isinstance(member, dict):
            fail(f"members[{idx}] is not an object")

        missing = REQUIRED_KEYS - set(member.keys())
        if missing:
            fail(f"members[{idx}] is missing keys: {sorted(missing)}")

        member_id = str(member.get("id", "")).strip()
        if not member_id:
            fail(f"members[{idx}] has empty id")
        if member_id in seen_ids:
            fail(f"duplicate member id: {member_id}")
        seen_ids.add(member_id)

        if not isinstance(member["expertise_tags"], list):
            fail(f"members[{idx}] expertise_tags must be a list")
        if not isinstance(member["source_works"], list):
            fail(f"members[{idx}] source_works must be a list")

    sorted_names = sorted(members, key=lambda m: str(m["name"]).lower())
    if [m["id"] for m in sorted_names] != [m["id"] for m in members]:
        fail("members are not sorted by lowercased name")

    expected_yaml = to_yaml(members)
    if expected_yaml != data_yaml_raw:
        fail("data/members.yaml does not match data/members.json canonical serialization")

    if data_json_raw != site_json_raw:
        fail("site/data/members.json does not match data/members.json")
    if data_yaml_raw != site_yaml_raw:
        fail("site/data/members.yaml does not match data/members.yaml")

    print(f"Health checks passed for {len(members)} members.")


if __name__ == "__main__":
    main()
