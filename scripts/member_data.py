"""Shared validation and privacy policy for public member data."""
import re
import unicodedata
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

def profile_files(root):
    return sorted((root / 'data/members').glob('*.yaml'))

def load(root=None):
    root = ROOT if root is None else root
    members = []
    for path in profile_files(root):
        member = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not isinstance(member, dict):
            raise ValueError(f'Expected one member mapping in {path.name}')
        members.append(member)
    payload = {'members': sorted(members, key=lambda m: m.get('name', '').casefold())}
    validate(payload)
    return payload

def save(payload, root=None):
    """Validate the whole roster before updating individual public profiles."""
    root = ROOT if root is None else root
    validate(payload)
    directory = root / 'data/members'
    old_paths = profile_files(root)
    if old_paths:
        load(root)  # Refuse to overwrite an invalid existing directory.
    by_id = {yaml.safe_load(p.read_text(encoding='utf-8'))['id']: p for p in old_paths}
    planned = {}
    for member in payload['members']:
        ascii_name = unicodedata.normalize('NFKD', member['name']).encode('ascii', 'ignore').decode()
        slug = re.sub(r'[^a-z0-9]+', '-', ascii_name.lower()).strip('-')
        if not slug:
            raise ValueError('Member name needs a filename slug')
        path = by_id.get(member['id'], directory / f'{slug}.yaml')
        if path in planned:
            raise ValueError(f'Duplicate profile filename: {path.name}')
        planned[path] = yaml.safe_dump(member, allow_unicode=True, sort_keys=False)
    directory.mkdir(parents=True, exist_ok=True)
    for path, text in planned.items():
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8')
    for path in set(old_paths) - planned.keys():
        path.unlink()
