import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import funds


class FundCatalogTests(unittest.TestCase):
    def test_generated_profile_and_exact_identities(self):
        rows = funds.load()
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({r['cik'] for r in rows}), 16)
        self.assertEqual(json.loads((funds.ROOT / 'funds-catalog.json').read_text()), funds.bundle(rows))
        bh = next(r for r in rows if r['id'] == 'berkshire-hathaway')
        ba = next(r for r in rows if r['id'] == 'berkshire-asset')
        self.assertNotEqual(bh['cik'], ba['cik'])
        self.assertNotEqual(bh['logos'][0]['url'], ba['logos'][0]['url'])

    def test_rejects_duplicate_identity_private_url_and_unbounded_image(self):
        original = funds.load()[0]
        for mutate in (lambda r: r.update(cik='bad'), lambda r: r['logos'][0].update(url='https://127.0.0.1/logo.png'), lambda r: r['logos'][0].update(width=4096,height=4096)):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d); (root / 'data/funds').mkdir(parents=True)
                row = json.loads(json.dumps(original)); mutate(row)
                (root / 'data/funds' / (row['id'] + '.json')).write_text(json.dumps(row))
                with self.assertRaises(ValueError): funds.load(root)
