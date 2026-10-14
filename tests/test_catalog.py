import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('catalog', Path(__file__).parents[1] / 'scripts/catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


def company():
    return {'id': 'example', 'name': 'Example Issuer', 'reviewedAt': '2026-10-14',
            'identityEvidenceUrls': ['https://example.org/issuer'],
            'securities': [{'market': 'US', 'symbol': 'EX', 'exchange': 'NASDAQ', 'kind': 'common',
                            'aliases': ['EX.A'], 'evidenceUrls': ['https://example.org/filing']}],
            'logos': [{'url': 'https://example.org/logo.png', 'source': 'issuer', 'status': 'verified',
                       'checkedAt': '2026-10-14', 'referenceUrl': 'https://example.org/issuer',
                       'redistribution': 'not-granted', 'sha256': 'a' * 64, 'width': 100,
                       'height': 100, 'format': 'png'}]}


class CatalogTests(unittest.TestCase):
    def test_shared_issuer_and_exact_alias(self):
        c = company()
        c['securities'].append({'market': 'US', 'symbol': 'EXW', 'exchange': 'NASDAQ', 'kind': 'warrant',
                                'evidenceUrls': ['https://example.org/filing']})
        self.assertEqual(catalog.resolve([c], 'US:EXW')['logoUrl'], catalog.resolve([c], 'US:EX.A')['logoUrl'])
        self.assertIsNone(catalog.resolve([c], 'US:EXU'))
        self.assertIsNone(catalog.resolve([c], 'US:ex'))

    def test_candidate_and_unavailable_do_not_leak(self):
        for status in ('candidate', 'unavailable', 'rejected'):
            c = company(); c['logos'][0]['status'] = status
            self.assertIsNone(catalog.resolve([c], 'US:EX')['logoUrl'])

    def test_no_logo_is_valid_mapping(self):
        c = company(); c['logos'] = []
        self.assertIsNone(catalog.resolve([c], 'US:EX')['logoUrl'])

    def test_duplicate_alias_across_issuers_rejected(self):
        a, b = company(), company(); b['id'] = 'other'
        b['securities'][0]['symbol'] = 'OTHER'
        with self.assertRaisesRegex(ValueError, 'Duplicate symbol'):
            catalog.validate([a, b])

    def test_private_credentials_and_signed_urls_rejected(self):
        for value in ('http://example.org/a', 'https://localhost/a', 'https://127.0.0.1/a',
                      'https://user:pass@example.org/a', 'https://example.org/a?token=abc',
                      'https://example.org/a?api_key=abc', 'https://example.org:8080/a'):
            with self.subTest(value=value), self.assertRaises(ValueError): catalog.url(value)

    def test_verified_requires_byte_evidence(self):
        c = company(); del c['logos'][0]['sha256']
        with self.assertRaisesRegex(ValueError, 'byte metadata'): catalog.validate([c])

    def test_expired_and_future_securities_not_usable(self):
        c = company(); c['securities'][0]['validTo'] = '2026-01-01'
        self.assertFalse(catalog.resolve([c], 'US:EX', as_of='2026-10-14')['active'])
        self.assertIsNone(catalog.resolve([c], 'US:EX', as_of='2026-10-14')['logoUrl'])
        c['securities'][0].pop('validTo'); c['securities'][0]['validFrom'] = '2026-10-14'
        self.assertFalse(catalog.resolve([c], 'US:EX', as_of='2026-10-13')['active'])

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
            json.loads('{"id":"a","id":"b"}', object_pairs_hook=catalog.no_duplicate_keys)

    def test_generated_output_deterministic(self):
        a, b = company(), company(); b['id'] = 'other'
        b['securities'][0]['symbol'] = 'OTHER'; b['securities'][0]['aliases'] = []
        self.assertEqual(catalog.bundle([a, b]), catalog.bundle([b, a]))

    def test_filename_identity_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path); (root / 'data/companies').mkdir(parents=True)
            (root / 'data/companies/wrong.json').write_text(json.dumps(company()))
            with self.assertRaisesRegex(ValueError, 'Filename'): catalog.load(root)


if __name__ == '__main__': unittest.main()
