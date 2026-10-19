"""Shared validation and privacy policy for public member data."""
import re
from urllib.parse import urlsplit
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
WORK_DOMAINS = set('yobu.edu.tr mpp.mpg.de ctn.tecnico.ulisboa.pt ectstar.eu vinca.rs selcuk.edu.tr uah.es rub.de cern.ch riken.jp uni-graz.at uned.es usal.es ut.ee ugr.es uni-bonn.de yerphi.am ucm.es umons.ac.be ub.edu uc.pt ulisboa.pt unime.it uni-lj.si unibe.ch uu.se upo.es ed.ac.uk lip.pt iu.edu cam.ac.uk ox.ac.uk'.split())
RAW_EMAIL = re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
PERSONAL = re.compile(r'(?:@|\(at\))\s*(?:gmail|googlemail|hotmail|outlook|yahoo|icloud|protonmail|proton|aol)\.', re.I)

def work_domain(domain):
    return any(domain == d or domain.endswith('.' + d) for d in WORK_DOMAINS)

def public_email(email):
    local, sep, domain = email.strip().partition('@')
    if not sep or not local or '@' in domain or re.search(r'\s', email):
        raise ValueError('Malformed roster email')
    return f'{local} (at) {domain.lower()}' if work_domain(domain.lower()) else ''

def validate(payload):
    members = payload.get('members')
    if not isinstance(members, list) or not members:
        raise ValueError('Expected nonempty members list')
    ids, names = set(), set()
    required = {'id','name','institution','email','expertise_tags','source_works'}
    for m in members:
        if required - m.keys():
            raise ValueError('Incomplete member profile')
        for field, seen in [('id', ids), ('name', names)]:
            key = m[field].strip().casefold()
            if not key or key in seen:
                raise ValueError(f'Missing or duplicate {field}')
            seen.add(key)
        for field in ['expertise_tags', 'source_works']:
            if not isinstance(m[field], list):
                raise ValueError(f'{field} must be a list')
        for source in m.get('profile_sources', []):
            url = urlsplit(source['url'])
            if url.scheme != 'https' or not url.hostname or url.username or not source.get('title'):
                raise ValueError('Profile sources require a titled HTTPS URL')
        if m.get('profile_prefill'):
            prefill = m['profile_prefill']
            if (prefill.get('status') != 'awaiting-member-review'
                    or not m.get('profile_sources')
                    or not prefill.get('fields')
                    or any(field not in {'expertise', 'research_topics', 'expertise_tags'}
                           or not m.get(field) for field in prefill['fields'])
                    or prefill.get('evidence_type') not in {'self-described', 'institutional', 'publication'}
                    or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', prefill.get('researched_on', ''))):
                raise ValueError('Prefills require provenance and populated research fields')
        if m['email']:
            match = re.fullmatch(r'[^\s@]+ \(at\) ([a-z0-9.-]+\.[a-z]{2,})', m['email'])
            if not match or not work_domain(match[1]):
                raise ValueError('Only approved work addresses with (at) may be published')
    text = yaml.safe_dump(payload)
    if RAW_EMAIL.search(text) or PERSONAL.search(text):
        raise ValueError('Unfiltered email address found in public data')
    return members

def load():
    payload = yaml.safe_load((ROOT / 'data/members.yaml').read_text())
    validate(payload)
    return payload
