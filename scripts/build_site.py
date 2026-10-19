#!/usr/bin/env python3
"""Build public files without access to the private source repository."""
import json
import shutil
import yaml
from member_data import ROOT, load, profile_files

def build_payload(root=ROOT):
    payload = load(root)
    paths = {yaml.safe_load(p.read_text(encoding='utf-8'))['id']: p.relative_to(root).as_posix()
             for p in profile_files(root)}
    for member in payload['members']:
        member['profile_path'] = paths[member['id']]
    return payload

def main():
    payload = build_payload()
    output = ROOT / 'dist'
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT / 'site', output)
    (output / 'data').mkdir()
    (output / 'data/members.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Built {len(payload['members'])} profiles in dist/")

if __name__ == '__main__':
    main()
