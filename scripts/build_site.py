#!/usr/bin/env python3
"""Build public files without access to the private source repository."""
import json
import shutil
from member_data import ROOT, load

def main():
    payload = load()
    output = ROOT / 'dist'
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT / 'site', output)
    (output / 'data').mkdir()
    (output / 'data/members.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Built {len(payload['members'])} profiles in dist/")

if __name__ == '__main__':
    main()
