#!/usr/bin/env python3
"""Validate, build and query a reviewed company logo catalog (standard library only)."""
import argparse
import datetime as dt
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'common', 'unit', 'warrant', 'right', 'preferred', 'depositary'}
STATUSES = {'verified', 'candidate', 'unavailable'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def url(value):
    require(isinstance(value, str), 'URL must be a string')
    p = urlsplit(value)
    require(p.scheme == 'https' and p.hostname and not p.username and not p.password
            and p.port in (None, 443) and not p.fragment, 'Use a credential-free HTTPS URL')
    require(p.hostname != 'localhost' and not p.hostname.endswith(('.local', '.internal')),
            'Private hosts are not catalog sources')
    try:
        address = ipaddress.ip_address(p.hostname)
    except ValueError:
        address = None
    require(address is None or address.is_global, 'Private addresses are not catalog sources')
    require(not re.search(r'(?:token|key|secret|signature|credential)=', p.query, re.I),
            'Do not publish provider keys or signed URLs')


def date(value, allow_future=False):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'Use YYYY-MM-DD dates')
    parsed = dt.date.fromisoformat(value)
    require(allow_future or parsed <= dt.date.today(), 'Review date cannot be in the future')


def evidence(values):
    require(isinstance(values, list) and values, 'Evidence URLs are required')
    for value in values:
        url(value)


def fields(obj, required, optional=()):
    require(isinstance(obj, dict), 'Expected an object')
    require(set(required) <= obj.keys(), 'Missing fields: ' + str(set(required) - obj.keys()))
    require(obj.keys() <= set(required) | set(optional), 'Unexpected fields: ' + str(obj.keys() - set(required) - set(optional)))


def validate(companies):
    require(isinstance(companies, list), 'Company records must be a list')
    ids, keys = set(), {}
    for c in companies:
        fields(c, ('id', 'name', 'reviewedAt', 'identityEvidenceUrls', 'securities', 'logos'),
               ('cik', 'websiteUrl', 'notes'))
        require(isinstance(c['id'], str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', c['id']), 'Invalid issuer id')
        require(c['id'] not in ids, 'Duplicate issuer id: ' + c['id'])
        ids.add(c['id'])
        require(isinstance(c['name'], str) and c['name'].strip(), 'Company name is required')
        date(c['reviewedAt']); evidence(c['identityEvidenceUrls'])
        if 'cik' in c:
            require(isinstance(c['cik'], str) and re.fullmatch(r'\d{10}', c['cik']), 'CIK must have ten digits')
        if 'websiteUrl' in c:
            url(c['websiteUrl'])
        if 'notes' in c:
            require(isinstance(c['notes'], str), 'Notes must be text')
        require(isinstance(c['securities'], list) and c['securities'], 'Securities are required')
        for s in c['securities']:
            fields(s, ('market', 'symbol', 'exchange', 'kind', 'evidenceUrls'), ('aliases', 'validFrom', 'validTo'))
            require(s['market'] == 'US', 'Schema v1 currently supports market US')
            require(s['exchange'] in ('NASDAQ', 'NYSE', 'NYSE_AMERICAN'), 'Invalid exchange')
            require(s['kind'] in KINDS, 'Invalid security kind')
            evidence(s['evidenceUrls'])
            if 'validFrom' in s: date(s['validFrom'])
            if 'validTo' in s:
                date(s['validTo'], allow_future=True)
                require(s.get('validFrom', '0000-00-00') <= s['validTo'], 'Invalid validity interval')
            aliases = s.get('aliases', [])
            require(isinstance(aliases, list), 'Aliases must be a list')
            for symbol in [s['symbol'], *aliases]:
                require(isinstance(symbol, str) and re.fullmatch(r'[A-Z0-9][A-Z0-9.$ -]{0,24}', symbol)
                        and symbol == symbol.strip(), 'Invalid exact symbol')
                key = s['market'] + ':' + symbol
                require(key not in keys, 'Duplicate symbol/alias: ' + key)
                keys[key] = c['id']
        require(isinstance(c['logos'], list), 'Logos must be a list')
        seen_urls = set()
        for logo in c['logos']:
            fields(logo, ('url', 'source', 'status', 'checkedAt', 'referenceUrl', 'redistribution'),
                   ('sha256', 'width', 'height', 'format', 'notes'))
            url(logo['url']); url(logo['referenceUrl']); date(logo['checkedAt'])
            require(logo['url'] not in seen_urls, 'Duplicate logo URL')
            seen_urls.add(logo['url'])
            require(logo['status'] in STATUSES, 'Invalid logo status')
            require(isinstance(logo['source'], str) and logo['source'].strip(), 'Logo source is required')
            require(logo['redistribution'] == 'not-granted', 'URL records do not grant asset redistribution')
            if logo['status'] == 'verified':
                require(all(k in logo for k in ('sha256', 'width', 'height', 'format')),
                        'Verified logos need byte metadata and visual review evidence')
            if 'sha256' in logo: require(bool(re.fullmatch(r'[0-9a-f]{64}', logo['sha256'])), 'Invalid SHA256')
            for dimension in ('width', 'height'):
                if dimension in logo:
                    require(type(logo[dimension]) is int and 4 <= logo[dimension] <= 2048, 'Invalid dimensions')
            if 'format' in logo: require(logo['format'] in ('png', 'jpg', 'webp', 'svg'), 'Invalid image format')
            if 'notes' in logo: require(isinstance(logo['notes'], str), 'Logo notes must be text')
    return keys


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load(root=ROOT):
    companies = []
    for path in sorted((root / 'data/companies').glob('*.json')):
        company = json.loads(path.read_text(), object_pairs_hook=no_duplicate_keys)
        require(path.stem == company.get('id'), 'Filename must match issuer id: ' + path.name)
        companies.append(company)
    require(companies, 'Catalog cannot be empty')
    validate(companies)
    return companies


def bundle(companies):
    keys = validate(companies)
    return {
        'schemaVersion': 1,
        'catalogVersion': '0.1.0',
        'updatedAt': max(c['reviewedAt'] for c in companies),
        'companies': sorted(companies, key=lambda c: c['id']),
        'symbols': dict(sorted(keys.items())),
    }


def resolve(companies, key, as_of=None):
    # Exact aliases only. Unknown or expired securities never inherit a guessed logo.
    validate(companies)
    as_of = as_of or dt.date.today().isoformat()
    for c in companies:
        for s in c['securities']:
            if key in [s['market'] + ':' + value for value in [s['symbol'], *s.get('aliases', [])]]:
                active = s.get('validFrom', '0000-00-00') <= as_of <= s.get('validTo', '9999-12-31')
                logos = [logo for logo in c['logos'] if logo['status'] == 'verified'] if active else []
                return {'issuerId': c['id'], 'name': c['name'], 'symbol': key,
                        'active': active, 'logoUrl': logos[0]['url'] if logos else None}
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'build', 'resolve', 'summary'))
    parser.add_argument('symbol', nargs='?', help='Exact key, e.g. US:AACOW')
    parser.add_argument('--check', action='store_true', help='Verify committed bundle is current')
    args = parser.parse_args()
    companies = load()
    data = bundle(companies)
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    if args.command == 'build':
        path = ROOT / 'catalog.json'
        if args.check: require(path.exists() and path.read_text() == rendered, 'Run python3 scripts/catalog.py build')
        else: path.write_text(rendered)
    elif args.command == 'resolve':
        require(args.symbol, 'Supply an exact market:symbol key')
        print(json.dumps(resolve(companies, args.symbol), indent=2))
    elif args.command == 'summary':
        print(json.dumps({'companies': len(companies), 'securities': sum(len(c['securities']) for c in companies),
                          'symbolKeys': len(data['symbols']), 'verifiedLogoCompanies': sum(any(l['status'] == 'verified' for l in c['logos']) for c in companies)}, indent=2))
    else: print('Catalog valid')


if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error)) from error
