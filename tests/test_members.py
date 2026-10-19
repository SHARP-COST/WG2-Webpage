import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from member_data import public_email, validate, load, save
import sync_members
from build_site import build_payload

class PrivacyTests(unittest.TestCase):
    def test_profile_links_follow_actual_filenames(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(load(), root)
            path = next((root / 'data/members').glob('*.yaml'))
            member_id = yaml.safe_load(path.read_text())['id']
            path.rename(path.with_name('renamed-profile.yaml'))
            result = build_payload(root)
            member = next(m for m in result['members'] if m['id'] == member_id)
            self.assertEqual(member['profile_path'], 'data/members/renamed-profile.yaml')
            self.assertNotIn('profile_path', next(m for m in load(root)['members'] if m['id'] == member_id))

    def test_private_and_unreviewed_domains_are_omitted(self):
        for domain in ['gmail.com', 'outlook.com', 'unknown.example', 'rub.de.attacker.example']:
            self.assertEqual(public_email('test' + '@' + domain), '')

    def test_institutional_address_is_obfuscated(self):
        self.assertEqual(public_email('test' + '@' + 'physics.uu.se'), 'test (at) physics.uu.se')

    def test_rejects_leaks_in_profile_prose(self):
        for contact in ['test' + '@' + 'rub.de', 'test (at) ' + 'gmail.com']:
            payload = copy.deepcopy(load())
            payload['members'][0]['expertise'] = contact
            with self.assertRaises(ValueError):
                validate(payload)

    def test_roster_controls_membership_and_contacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            payload = copy.deepcopy(load())
            member = payload['members'][0]
            name, expertise = member['name'], member['expertise']
            save(payload, root)
            roster = root / 'WG2.list'
            roster.write_text('name,affiliation,email\n' + name + ',New institution,test' + '@' + 'gmail.com\n\n## Emails\n\nignored\n')
            with patch.object(sync_members, 'ROOT', root):
                sync_members.sync(roster)
            imported = load(root)['members']
            self.assertEqual(len(imported), 1)
            self.assertEqual(imported[0]['institution'], 'New institution')
            self.assertEqual(imported[0]['email'], '')
            self.assertEqual(imported[0]['expertise'], expertise)
            for field in ['research_topics', 'profile_prefill', 'profile_sources']:
                self.assertEqual(imported[0].get(field), member.get(field))
            self.assertEqual(len(list((root / 'data/members').glob('*.yaml'))), 1)

    def test_split_profiles_roundtrip_addition_and_stable_filenames(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = copy.deepcopy(load())
            save(payload, root)
            self.assertEqual(load(root), payload)
            original_path = next(p for p in (root / 'data/members').glob('*.yaml')
                                 if yaml.safe_load(p.read_text())['id'] == payload['members'][0]['id'])
            payload['members'][0]['name'] = 'Updated display name'
            new = copy.deepcopy(payload['members'][1])
            new.update(id='newmember', name='New Member', email='')
            payload['members'].append(new)
            save(payload, root)
            self.assertEqual(yaml.safe_load(original_path.read_text())['name'], 'Updated display name')
            self.assertTrue((root / 'data/members/new-member.yaml').exists())
            loaded = load(root)['members']
            self.assertEqual([m['name'] for m in loaded], sorted((m['name'] for m in loaded), key=str.casefold))

    def test_duplicate_profiles_and_invalid_import_do_not_overwrite_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = copy.deepcopy(load())
            save(payload, root)
            before = {p.name: p.read_bytes() for p in (root / 'data/members').glob('*.yaml')}
            payload['members'].append(copy.deepcopy(payload['members'][0]))
            with self.assertRaises(ValueError):
                save(payload, root)
            self.assertEqual(before, {p.name: p.read_bytes() for p in (root / 'data/members').glob('*.yaml')})
            (root / 'data/members/duplicate.yaml').write_text(yaml.safe_dump(payload['members'][0]))
            with self.assertRaises(ValueError):
                load(root)

    def test_prefills_require_sources_and_safe_links(self):
        payload = copy.deepcopy(load())
        member = next(m for m in payload['members'] if m.get('profile_prefill'))
        for url in ['javascript:alert(1)', 'https:///missing-host']:
            member['profile_sources'][0]['url'] = url
            with self.assertRaises(ValueError):
                validate(payload)
        member['profile_sources'] = []
        with self.assertRaises(ValueError):
            validate(payload)

if __name__ == '__main__':
    unittest.main()
