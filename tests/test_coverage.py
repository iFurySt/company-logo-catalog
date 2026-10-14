import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import coverage as inventory
from test_catalog import company

NAS = 'Symbol|Security Name|Test Issue|ETF\nEX|Example Issuer - Common Stock|N|N\nEXW|Example Issuer - Warrant|N|N\nETF|Example Fund|N|Y\nTEST|Test security|Y|N\nFile Creation Time: 1014202610:00||||\n'
OTHER = 'ACT Symbol|Security Name|Exchange|CQS Symbol|NASDAQ Symbol|ETF|Test Issue\nPCG$X|PG&E Corporation Depositary Shares|N|PCGpX|PCG-PX|N|N\nFUND|Example Closed End Fund Common Shares|P|FUND|FUND|N|N\n'


def checks(symbol='EX', result='png-unverified'):
    return {symbol: {'result': result, 'sha256': 'a' * 64, 'width': 100, 'height': 100,
                     'checkedAt': '2026-10-14T00:00:00.000Z', 'format': 'png'}}


class CoverageTests(unittest.TestCase):
    def test_official_directory_scope_and_source_aliases(self):
        rows = inventory.parse_directory(NAS, 'nasdaqlisted.txt')
        self.assertEqual([r['symbol'] for r in rows], ['EX', 'EXW'])
        preferred, fund = inventory.parse_directory(OTHER, 'otherlisted.txt')
        self.assertEqual(preferred['sourceAliases'], ['PCG-PX', 'PCGpX'])
        self.assertEqual(fund['exchange'], 'NYSE_ARCA')
        txse = inventory.parse_directory(OTHER.replace('|P|', '|F|'), 'otherlisted.txt')[1]
        self.assertEqual(txse['exchange'], 'TXSE')

    def test_malformed_headers_flags_duplicates_and_unknown_exchanges_rejected(self):
        for text in [NAS.replace('ETF', 'Missing', 1), NAS.replace('|N|N', '|?|N', 1),
                     NAS.replace('EXW|', 'EX|', 1)]:
            with self.subTest(text=text), self.assertRaises(ValueError): inventory.parse_directory(text, 'nasdaqlisted.txt')
        with self.assertRaises(ValueError): inventory.parse_directory(OTHER.replace('|P|', '|?|'), 'otherlisted.txt')

    def test_cross_source_collision_is_not_silently_deduplicated(self):
        rows = inventory.parse_directory(NAS, 'nasdaqlisted.txt')
        with self.assertRaises(ValueError): inventory.build_inventory([rows[0], rows[0]], [company()], {}, '2026-10-14')

    def test_names_not_ticker_suffixes_propose_unverified_shared_sources(self):
        rows = inventory.parse_directory(NAS.replace('EXW|', 'OTHER|'), 'nasdaqlisted.txt')
        # The directory, not ticker similarity, connects this review candidate.
        rows[1]['symbol'] = 'OTHER'
        records = inventory.build_inventory(rows, [], checks(), '2026-10-14')
        sibling = records[1]
        self.assertEqual(sibling['sharedIssuerCandidate']['symbol'], 'EX')
        self.assertIsNone(sibling['issuerId'])
        self.assertEqual(sibling['mappingStatus'], 'needs-review')
        self.assertIsNone(inventory.resolve_inventory(records, 'US:OTHER')['logoUrl'])
        self.assertEqual(inventory.resolve_inventory(records, 'US:OTHER', True)['verification'], 'directory-name-candidate')

    def test_related_ticker_different_name_does_not_share_issuer_image(self):
        rows = inventory.parse_directory(NAS.replace('Example Issuer - Warrant', 'Different Issuer - Warrant'), 'nasdaqlisted.txt')
        records = inventory.build_inventory(rows, [], checks(), '2026-10-14')
        self.assertNotIn('sharedIssuerCandidate', records[1])

    def test_provider_success_is_not_a_verified_company_logo(self):
        records = inventory.build_inventory(inventory.parse_directory(NAS, 'nasdaqlisted.txt'), [], checks(), '2026-10-14')
        self.assertIsNone(inventory.resolve_inventory(records, 'US:EX')['logoUrl'])
        self.assertEqual(inventory.resolve_inventory(records, 'US:EX', True)['verification'], 'provider-unverified')
        summary = inventory.report(records)
        self.assertEqual(summary['unverifiedImageSecurities'], 1)
        self.assertFalse(summary['verifiedLogoComplete'])
        self.assertFalse(summary['sourceCheckComplete'])

    def test_reused_ticker_with_a_different_directory_name_cannot_keep_old_reviewed_logo(self):
        rows = inventory.parse_directory(NAS.replace('Example Issuer - Common Stock', 'Different Company - Common Stock'), 'nasdaqlisted.txt')
        records = inventory.build_inventory(rows, [company()], checks(), '2026-10-14')
        self.assertEqual(records[0]['mappingStatus'], 'directory-name-conflict')
        self.assertIsNone(records[0]['issuerId'])
        self.assertIsNone(inventory.resolve_inventory(records, 'US:EX')['logoUrl'])

    def test_exact_source_aliases_resolve_without_guessing_or_silent_collision(self):
        rows = inventory.parse_directory(OTHER, 'otherlisted.txt')
        records = inventory.build_inventory(rows, [], {}, '2026-10-14')
        self.assertEqual(inventory.resolve_inventory(records, 'US:PCGpX')['name'], rows[0]['name'])
        next(r for r in records if r['key'] == 'US:FUND')['sourceAliases'] = ['PCGpX']
        self.assertIsNone(inventory.resolve_inventory(records, 'US:PCGpX'))

    def test_filename_presence_is_not_a_usable_provider_image(self):
        records = inventory.build_inventory(inventory.parse_directory(NAS, 'nasdaqlisted.txt'), [], {}, '2026-10-14',
            {'EX': [{'url': 'https://example.org/EX.png', 'status': 'filename-present'}]})
        self.assertIsNone(inventory.resolve_inventory(records, 'US:EX', True)['logoUrl'])
        self.assertEqual(inventory.report(records)['otherSourceCandidateSecurities'], 1)

    def test_known_wrong_image_is_blocked_even_with_provider_opt_in(self):
        c = company()
        c['logos'][0]['status'] = 'rejected'
        records = inventory.build_inventory(inventory.parse_directory(NAS, 'nasdaqlisted.txt'), [c], checks(), '2026-10-14')
        self.assertEqual(records[0]['providerIdentityStatus'], 'rejected')
        self.assertIsNone(inventory.resolve_inventory(records, 'US:EX', True)['logoUrl'])
        self.assertNotIn('sharedIssuerCandidate', records[1])

    def test_verified_and_expired_catalog_mappings_keep_existing_semantics(self):
        c = company()
        rows = inventory.parse_directory(NAS, 'nasdaqlisted.txt')
        records = inventory.build_inventory(rows, [c], checks(), '2026-10-14')
        self.assertEqual(inventory.resolve_inventory(records, 'US:EX', True)['verification'], 'reviewed')
        c['securities'][0]['validTo'] = '2026-01-01'
        expired = inventory.build_inventory(rows, [c], checks(), '2026-10-14')
        self.assertIsNone(inventory.resolve_inventory(expired, 'US:EX')['logoUrl'])
        self.assertIsNone(inventory.resolve_inventory(expired, 'US:EX')['issuerId'])

    def test_checkpoint_checks_url_hash_dimensions_and_last_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'checks.jsonl'
            row = {**checks()['EX'], 'symbol': 'EX', 'url': 'https://financialmodelingprep.com/image-stock/EX.png'}
            p.write_text(json.dumps({**row, 'result': 'timeout'}) + '\n' + json.dumps(row) + '\n')
            self.assertEqual(inventory.read_checks(p)['EX']['result'], 'png-unverified')
            for change in [{'url': 'https://evil.example/EX.png'}, {'sha256': 'bad'}, {'width': 4096}, {'result': 'fake-success'}]:
                p.write_text(json.dumps({**row, **change}))
                with self.assertRaises(ValueError): inventory.read_checks(p)


if __name__ == '__main__': unittest.main()
