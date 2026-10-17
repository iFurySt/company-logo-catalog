import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import app_fallbacks

class AppFallbackTests(unittest.TestCase):
    def row(self):
        return dict(symbol='EXW',key='US:EXW',securityName='Example - Warrants',identityEvidenceUrl='https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt',reviewedLogoUrl=None,providerOutcome='not-found',mappingStatus='needs-review',issuerId=None,sourceAliases=[],sharedIssuerCandidate=dict(symbol='EX',url='https://financialmodelingprep.com/image-stock/EX.png',sha256='a'*64,width=64,height=64,status='candidate'))
    def test_candidate_is_exact_availability_mapping_not_verified_identity(self):
        result=app_fallbacks.build(dict(asOf='2026-10-18',securities=[self.row()]))
        self.assertEqual(result['items'][0]['symbol'],'EXW')
        self.assertEqual(result['items'][0]['basis'],'directory-name-candidate')
        self.assertNotIn('verified',result['items'][0])
    def test_own_provider_and_reviewed_sources_do_not_need_supplement(self):
        for change in [dict(providerOutcome='png-unverified'),dict(reviewedLogoUrl='https://example.org/logo.png')]:
            row={**self.row(),**change};self.assertEqual(app_fallbacks.build(dict(asOf='2026-10-18',securities=[row]))['items'],[])
    def test_missing_checksums_and_dimensions_cannot_create_fallback(self):
        for field in ['sha256','width','height']:
            row=self.row();del row['sharedIssuerCandidate'][field]
            with self.assertRaises(ValueError):app_fallbacks.build(dict(asOf='2026-10-18',securities=[row]))
