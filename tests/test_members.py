import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from member_data import public_email, validate, load
import sync_members

class PrivacyTests(unittest.TestCase):
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
            (root / 'data/members.yaml').write_text(yaml.safe_dump(payload))
            roster = root / 'WG2.list'
            roster.write_text('name,affiliation,email\n' + name + ',New institution,test' + '@' + 'gmail.com\n\n## Emails\n\nignored\n')
            with patch.object(sync_members, 'ROOT', root):
                sync_members.sync(roster)
            imported = yaml.safe_load((root / 'data/members.yaml').read_text())['members']
            self.assertEqual(len(imported), 1)
            self.assertEqual(imported[0]['institution'], 'New institution')
            self.assertEqual(imported[0]['email'], '')
            self.assertEqual(imported[0]['expertise'], expertise)
            for field in ['research_topics', 'profile_prefill', 'profile_sources']:
                self.assertEqual(imported[0].get(field), member.get(field))

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
