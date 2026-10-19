#!/usr/bin/env python3
"""Check the public roster, generated bundle and repository for email leaks."""
import json
import subprocess
from member_data import ROOT, RAW_EMAIL, PERSONAL, load

def main():
    payload = load()
    paths = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    paths += [str(p.relative_to(ROOT)) for p in (ROOT / 'dist').rglob('*') if p.is_file()]
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        if RAW_EMAIL.search(text) or PERSONAL.search(text):
            raise ValueError(f'Unfiltered email address in {relative}')
    bundle = ROOT / 'dist/data/members.json'
    if not bundle.exists() or json.loads(bundle.read_text()) != payload:
        raise ValueError('Build the site: deployed data must match data/members/*.yaml')
    print(f"Checks passed for {len(payload['members'])} members.")

if __name__ == '__main__':
    main()
