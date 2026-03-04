#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"


def main() -> None:
    from sync_members import main as sync_main

    sync_main()

    SITE_DATA.mkdir(parents=True, exist_ok=True)
    for f in ["members.yaml", "members.json"]:
        src = ROOT / "data" / f
        dst = SITE_DATA / f
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")


if __name__ == "__main__":
    main()
