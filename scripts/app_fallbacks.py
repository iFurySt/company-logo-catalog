#!/usr/bin/env python3
"""Build a bounded app-consumable PNG availability supplement; never issuer verification."""
import argparse,json,re
from pathlib import Path
from urllib.parse import urlsplit
from catalog import ROOT, VERSION, require
from coverage import resolve_inventory


def build(inventory):
    items=[]
    by_symbol={r['symbol']:r for r in inventory['securities']}
    for row in inventory['securities']:
        if row['reviewedLogoUrl'] or row['providerOutcome']=='png-unverified': continue
        try: chosen=resolve_inventory([row],row['key'],True)
        except (KeyError, TypeError): raise ValueError('Malformed availability observation') from None
        if not chosen or chosen.get('format')=='svg' or not chosen.get('logoUrl'): continue
        if chosen['verification']=='directory-name-candidate':
            source=row['sharedIssuerCandidate'];url=source['url']
        elif chosen['verification']=='repository-unverified':
            source=next(s for s in row['otherCandidateSources'] if s.get('result')=='png-unverified');url=source['url']
        else: continue
        require(re.fullmatch(r'[a-f0-9]{64}',source.get('sha256','')) is not None,'Missing fallback checksum')
        require(all(type(source.get(k)) is int and 4<=source[k]<=2048 for k in ['width','height']),'Fallback dimensions required')
        items.append(dict(symbol=row['symbol'],name=row['securityName'],basis=chosen['verification'],url=url,
            sha256=source['sha256'],width=source['width'],height=source['height'],evidenceUrl=row['identityEvidenceUrl'],
            checkedAt=source.get('checkedAt') or by_symbol.get(source.get('symbol'),{}).get('checkedAt')))
    return dict(schemaVersion=1,profile='app-image-fallbacks',catalogVersion=VERSION,
                updatedAt=inventory['asOf'],items=items)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=ROOT/'catalog-provider.json');p.add_argument('--check',action='store_true');a=p.parse_args()
    data=build(json.loads(a.input.read_text()));out=ROOT/'app-fallbacks.json';text=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
    if a.check:require(out.exists() and out.read_text()==text,'Run python3 scripts/app_fallbacks.py')
    else:out.write_text(text)
    print('PNG availability fallbacks:',len(data['items']))
if __name__=='__main__':main()
