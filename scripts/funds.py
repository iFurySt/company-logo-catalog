#!/usr/bin/env python3
"""Validate and bundle independently reviewed fund manager logo URL metadata."""
import argparse
import json
import re
from pathlib import Path
from catalog import ROOT, date, evidence, fields, no_duplicate_keys, require, url


def load(root=ROOT):
    rows = []
    ids, ciks = set(), set()
    for path in sorted((root / 'data/funds').glob('*.json')):
        r = json.loads(path.read_text(), object_pairs_hook=no_duplicate_keys)
        fields(r, ('id', 'name', 'displayName', 'cik', 'reviewedAt', 'websiteUrl', 'identityEvidenceUrls', 'logos'))
        require(path.stem == r['id'] and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', r['id']), 'Invalid manager id')
        require(r['id'] not in ids and re.fullmatch(r'\d{10}', r['cik']) and r['cik'] not in ciks, 'Duplicate/invalid CIK')
        ids.add(r['id']); ciks.add(r['cik'])
        require(all(isinstance(r[k], str) and r[k].strip() for k in ('name', 'displayName')), 'Manager names required')
        date(r['reviewedAt']); url(r['websiteUrl']); evidence(r['identityEvidenceUrls'])
        require('https://data.sec.gov/submissions/CIK' + r['cik'] + '.json' in r['identityEvidenceUrls'], 'SEC identity evidence required')
        require(isinstance(r['logos'], list) and len(r['logos']) <= 4, 'Bound manager logo sources')
        for logo in r['logos']:
            fields(logo, ('url', 'source', 'status', 'checkedAt', 'referenceUrl', 'redistribution', 'sha256', 'width', 'height', 'format', 'notes'))
            url(logo['url']); url(logo['referenceUrl']); date(logo['checkedAt'])
            require(logo['status'] in ('verified', 'candidate', 'unavailable', 'rejected'), 'Invalid review state')
            require(logo['format'] == 'png' and re.fullmatch(r'[0-9a-f]{64}', logo['sha256']), 'PNG/hash required')
            require(all(type(logo[k]) is int and 4 <= logo[k] <= 4096 for k in ('width', 'height')) and logo['width'] * logo['height'] <= 2048**2, 'Bound image pixels')
            require(logo['redistribution'] == 'not-granted', 'Metadata does not grant artwork rights')
        rows.append(r)
    require(rows, 'Fund manager catalog is empty')
    return rows


def bundle(rows):
    return {'schemaVersion': 1, 'profile': 'fund-manager-logos', 'catalogVersion': '0.1.0',
            'updatedAt': max(r['reviewedAt'] for r in rows), 'funds': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('validate', 'build', 'resolve'))
    p.add_argument('cik', nargs='?'); p.add_argument('--check', action='store_true')
    args = p.parse_args(); rows = load()
    if args.command == 'build':
        path = ROOT / 'funds-catalog.json'; rendered = json.dumps(bundle(rows), ensure_ascii=False, indent=2) + '\n'
        if args.check: require(path.read_text() == rendered, 'Regenerate funds-catalog.json')
        else: path.write_text(rendered)
    elif args.command == 'resolve':
        require(args.cik and re.fullmatch(r'\d{10}', args.cik), 'Supply an exact ten-digit manager CIK')
        row = next((r for r in rows if r['cik'] == args.cik), None)
        logo = next((l for l in row['logos'] if l['status'] == 'verified'), None) if row else None
        print(json.dumps({'managerId': row['id'], 'logoUrl': logo['url'] if logo else None} if row else None))
    else: print(f'{len(rows)} manager identities and logo metadata valid')


if __name__ == '__main__': main()
