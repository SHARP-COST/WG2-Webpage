#!/usr/bin/env python3
"""Import WG2.list; retain profile enrichment but never private contact data."""
import argparse
import csv
import io
import unicodedata
from pathlib import Path
from member_data import ROOT, public_email, save, load

def name_key(name):
    return ''.join(c for c in unicodedata.normalize('NFKD', name).casefold() if c.isalnum())

ALIASES = {name_key('Felipe José Llanes-Estrada'): name_key('Felipe Llanes-Estrada')}

def sync(source):
    existing = load(ROOT)['members']
    by_name = {name_key(m['name']): m for m in existing}
    text = source.read_text(encoding='utf-8-sig').split('\n## Emails', 1)[0].strip()
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ['name', 'affiliation', 'email']:
        raise ValueError('Expected name,affiliation,email roster columns')
    members = []
    for row in reader:
        if None in row or not all(row.get(k, '').strip() for k in reader.fieldnames):
            raise ValueError('Incomplete roster record')
        key = name_key(row['name'])
        m = dict(by_name.get(key, by_name.get(ALIASES.get(key), {})))
        m.update(name=row['name'], institution=row['affiliation'], email=public_email(row['email']))
        m.setdefault('id', key)
        for field in ['country_code','country','github','domain_badge','past_works','expertise','current_interests']:
            m.setdefault(field, '')
        for field in ['expertise_tags','source_works']:
            m.setdefault(field, [])
        m.pop('source_file', None)
        members.append(m)
    members.sort(key=lambda m: m['name'].casefold())
    payload = {'members': members}
    save(payload, ROOT)
    print(f"Imported {len(members)} members; {sum(bool(m['email']) for m in members)} work contacts.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', default=ROOT.parent / 'WG2-Hadron-Spectroscopy/WG2.list')
    sync(parser.parse_args().source)
