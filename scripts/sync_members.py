#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "WG2-Hadron-Spectroscopy" / "members"
SOURCE = Path(os.environ.get("WG2_SOURCE_MEMBERS", str(DEFAULT_SOURCE))).expanduser().resolve()
OUT_YAML = ROOT / "data" / "members.yaml"
OUT_JSON = ROOT / "data" / "members.json"

COUNTRY_NAMES = {
    "AM": "Armenia",
    "AT": "Austria",
    "DE": "Germany",
    "EE": "Estonia",
    "ES": "Spain",
    "IT": "Italy",
    "PT": "Portugal",
    "SE": "Sweden",
    "TR": "Turkey",
}

KEYWORDS = {
    "amplitude-analysis": ["amplitude", "partial-wave", "dispersion", "unitar", "line shape"],
    "lattice-qcd": ["lattice", "gribov"],
    "dyson-schwinger": ["dyson-schwinger", "green", "landau-gauge", "functional"],
    "effective-field-theory": ["effective field", "chpt", "hqet"],
    "heavy-hadrons": ["heavy", "tetra", "penta", "baryon", "charm", "bottom"],
    "light-hadrons": ["light meson", "pion", "kaon", "rho", "scalar"],
    "exotics": ["exotic", "hybrid", "multiquark", "4-", "5-", "6-quark"],
    "qcd-sum-rules": ["sum rules"],
    "experiment": ["compass", "belle", "lhcb", "alice", "experiment", "femtoscopy", "tau"],
    "machine-learning": ["machine learning", "monte carlo", "numerical"],
}

ICON_BY_TAG = {
    "amplitude-analysis": "A",
    "lattice-qcd": "L",
    "dyson-schwinger": "D",
    "effective-field-theory": "E",
    "heavy-hadrons": "H",
    "light-hadrons": "M",
    "exotics": "X",
    "qcd-sum-rules": "Q",
    "experiment": "R",
    "machine-learning": "N",
}


def parse_yaml_scalar(value: str) -> str:
    v = value.strip()
    if v in {"", "null", "~"}:
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1].replace('\\"', '"')
    return v


def parse_member_yaml(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    obj: dict[str, Any] = {}
    current_list: str | None = None
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        i += 1

        if not stripped or stripped.startswith("#"):
            continue

        if current_list and stripped.startswith("- "):
            obj[current_list].append(parse_yaml_scalar(stripped[2:].strip()))
            continue

        if current_list and not line.startswith("  - "):
            current_list = None

        m = re.match(r"^([a-zA-Z0-9_]+):\s*(.*)$", stripped)
        if not m:
            continue

        key, value = m.group(1), m.group(2)

        if value in {"[]", "[ ]"}:
            obj[key] = []
            current_list = None
            continue

        if value in {"|", ">", "|-", ">-"}:
            block: list[str] = []
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith("  "):
                    block.append(nxt[2:])
                    i += 1
                    continue
                if nxt.strip() == "":
                    block.append("")
                    i += 1
                    continue
                break
            obj[key] = "\n".join(block).strip()
            current_list = None
            continue

        if value == "":
            obj[key] = []
            current_list = key
            continue

        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            obj[key] = [] if not inner else [parse_yaml_scalar(x.strip()) for x in inner.split(",")]
            current_list = None
            continue

        obj[key] = parse_yaml_scalar(value)

    return obj


def infer_tags(text: str) -> list[str]:
    t = text.lower()
    return sorted({tag for tag, words in KEYWORDS.items() if any(w in t for w in words)})


def normalize_member(raw: dict[str, Any], source_path: Path) -> dict[str, Any]:
    name = str(raw.get("name", "")).strip() or source_path.stem
    institution = str(raw.get("institution", "")).strip()
    country_code = str(raw.get("country_code", "UN")).strip().upper() or "UN"
    email = str(raw.get("email", "")).strip().lower().replace("@@", "@")
    github = str(raw.get("github", "")).strip()
    past = str(raw.get("past_works", "")).strip()
    expertise = str(raw.get("expertise", "")).strip()
    current = str(raw.get("current_interests", "")).strip()

    tags = raw.get("expertise_tags", [])
    if isinstance(tags, str):
        tags = [tags] if tags else []
    tags = [str(t).strip() for t in tags if str(t).strip()]
    if not tags:
        tags = infer_tags(" ".join([past, expertise, current]))

    source_works = raw.get("source_works", tags)
    if isinstance(source_works, str):
        source_works = [source_works] if source_works else []
    source_works = [str(t).strip() for t in source_works if str(t).strip()]

    badge = str(raw.get("domain_badge", "")).strip() or (ICON_BY_TAG.get(tags[0], "A") if tags else "A")

    return {
        "id": str(raw.get("id", "")).strip() or source_path.stem,
        "name": name,
        "institution": institution,
        "country_code": country_code,
        "country": COUNTRY_NAMES.get(country_code, "Unknown"),
        "email": email,
        "github": "" if github.lower() in {"no", "??"} else github,
        "domain_badge": badge,
        "past_works": past,
        "expertise": expertise,
        "current_interests": current,
        "expertise_tags": sorted(set(tags)),
        "source_works": sorted(set(source_works)) if source_works else sorted(set(tags)),
        "source_file": f"members/{source_path.name}",
    }


def to_yaml(members: list[dict[str, Any]]) -> str:
    def y(v: Any) -> str:
        if isinstance(v, str):
            if v == "":
                return '""'
            return '"' + v.replace('"', '\\"').replace("\n", "\\n") + '"'
        if isinstance(v, list):
            return "[]" if not v else "[" + ", ".join(y(x) for x in v) + "]"
        return str(v)

    order = [
        "id", "name", "institution", "country_code", "country", "email", "github", "domain_badge",
        "past_works", "expertise", "current_interests", "expertise_tags", "source_works", "source_file",
    ]
    lines = ["members:"]
    for m in members:
        lines.append("  -")
        for key in order:
            lines.append(f"    {key}: {y(m.get(key, ''))}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source members directory not found: {SOURCE}")

    records: list[dict[str, Any]] = []
    for path in sorted(SOURCE.glob("*.yaml")):
        raw = parse_member_yaml(path)
        if raw:
            records.append(normalize_member(raw, path))

    records.sort(key=lambda m: m["name"].lower())

    OUT_YAML.parent.mkdir(parents=True, exist_ok=True)
    OUT_YAML.write_text(to_yaml(records), encoding="utf-8")
    OUT_JSON.write_text(json.dumps({"members": records}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Source: {SOURCE}")
    print(f"Wrote {OUT_YAML}")
    print(f"Wrote {OUT_JSON}")
    print(f"Members: {len(records)}")


if __name__ == "__main__":
    main()
