#!/usr/bin/env python3
"""Build an exhaustive current-security inventory without promoting unreviewed images."""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit, unquote

from catalog import load, resolve, require, url

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URLS = {
    'nasdaqlisted.txt': 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt',
    'otherlisted.txt': 'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt',
}
EXCHANGES = {'NASDAQ': 'NASDAQ', 'N': 'NYSE', 'A': 'NYSE_AMERICAN',
             'P': 'NYSE_ARCA', 'Z': 'CBOE_BZX', 'F': 'TXSE', 'V': 'IEX'}
RESULTS = {'png-unverified', 'not-found', 'http-error', 'network-error', 'timeout',
           'rejected-image', 'rate-limited', 'not-tested'}


def parse_directory(text, filename):
    key = 'Symbol' if filename == 'nasdaqlisted.txt' else 'ACT Symbol'
    require(filename in SOURCE_URLS, 'Unknown directory source')
    rows = csv.DictReader(io.StringIO(text), delimiter='|')
    require(rows.fieldnames and {key, 'Security Name', 'Test Issue', 'ETF'} <= set(rows.fieldnames),
            'Incomplete directory header')
    found, result = set(), []
    for row in rows:
        symbol = row[key]
        if symbol.startswith('File Creation Time:'):
            continue
        require(row.get('Security Name') is not None and row.get('Test Issue') in {'N', 'Y'}
                and row.get('ETF') in {'N', 'Y'}, 'Malformed directory row')
        if row['Test Issue'] == 'Y' or row['ETF'] == 'Y':
            continue
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.$/ -]{0,39}', symbol or '') is not None,
                'Invalid directory symbol')
        require(symbol not in found, 'Duplicate directory symbol')
        found.add(symbol)
        exchange = 'NASDAQ' if filename == 'nasdaqlisted.txt' else row.get('Exchange')
        require(exchange in EXCHANGES, 'Unknown exchange code')
        aliases = sorted({v for k in ('CQS Symbol', 'NASDAQ Symbol')
                          if (v := row.get(k)) and v != symbol})
        result.append({'symbol': symbol, 'name': row['Security Name'].strip(),
                       'exchange': EXCHANGES[exchange], 'sourceFile': filename,
                       'sourceAliases': aliases})
    require(result, 'Empty directory')
    return result


def issuer_hint(name):
    """Name grouping is a review hint, never automatic legal-issuer confirmation."""
    if ' - ' in name:
        return name.split(' - ', 1)[0].strip()
    marker = re.search(r'\s+(?:Class\s+[A-Z0-9]|Common\s+(?:Stock|Shares|Units)|'
                       r'Ordinary\s+Shares|American\s+Depositary|(?:Depositary|Depository)\s+Sh(?:ares?)?\b|'
                       r'Non[- ]Cumulative\s+.*(?:Pfd|Preferred|Preference)|'
                       r'Redeemable\s+Warrants?|Warrants?\b|Units?\b|Rights?\b|'
                       r'\d+(?:\.\d+)?%|Series\s+[A-Z0-9])', name, re.I)
    return name[:marker.start()].strip() if marker else name.strip()


def normalized_hint(name):
    name = re.sub(r'\(the\)', '', name.casefold())
    name = re.sub(r'[.,]', ' ', name)
    for full, short in [('incorporated', 'inc'), ('corporation', 'corp'), ('limited', 'ltd')]:
        name = re.sub(r'\b' + full + r'\b', short, name)
    return re.sub(r'\s+', ' ', name).strip()


def identity_name(name):
    value = normalized_hint(name)
    return re.sub(r'\s+', ' ', re.sub(r'\b(?:inc|corp|ltd|plc|co)\b', '', value)).strip()


def security_kind(name):
    value = name.lower()
    if 'warrant' in value: return 'warrant'
    if re.search(r'\bright\b|\brights\b', value): return 'right'
    if 'depositary' in value or 'depository' in value: return 'depositary'
    if 'preferred' in value or 'preference' in value or re.search(r'\bpfd\b', value): return 'preferred'
    if re.search(r'\bunits?\b', value): return 'unit'
    if re.search(r'\bnotes?\b|\bbonds?\b|\bdebentures?\b', value): return 'debt'
    if 'common' in value or 'ordinary' in value or 'class ' in value: return 'common'
    if re.search(r'\bfund\b|\btrust\b', value): return 'fund-or-trust'
    return 'unknown'


def read_checks(path):
    result = {}
    if not path or not path.exists(): return result
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        row = json.loads(line)
        require(row.get('result') in RESULTS, 'Invalid source result')
        symbol = row.get('symbol')
        require(isinstance(symbol, str), 'Missing probe symbol')
        require(row.get('url') == 'https://financialmodelingprep.com/image-stock/' + quote(symbol, safe='') + '.png',
                'Probe URL must be the exact public symbol image')
        require(isinstance(row.get('checkedAt'), str) and
                re.fullmatch(r'\d{4}-\d{2}-\d{2}T.*Z', row['checkedAt']), 'Probe date missing')
        if row['result'] == 'png-unverified':
            require(re.fullmatch(r'[a-f0-9]{64}', row.get('sha256', '')) is not None,
                    'Image hash missing')
            require(type(row.get('width')) is int and type(row.get('height')) is int
                    and 4 <= row['width'] <= 2048 and 4 <= row['height'] <= 2048,
                    'Invalid probe dimensions')
        result[symbol] = row  # A resumed retry supersedes the previous result.
    return result


def validate_alternatives(index):
    require(isinstance(index, dict), 'Alternative source index must be an object')
    for symbol, sources in index.items():
        require(isinstance(sources, list) and len(sources) <= 2, 'Bounded alternative sources required')
        for source in sources:
            url(source['url'])
            path = unquote(urlsplit(source['url']).path)
            require(urlsplit(source['url']).hostname == 'raw.githubusercontent.com' and
                    re.fullmatch(r'/(?:nvstly/icons|ShaadyEmad/ticker-logos)/[a-f0-9]{40}/(?:ticker_icons|US Market/PNG)/[^/]+\.png', path),
                    'Use a pinned known repository PNG source')
            require(Path(path).stem.upper() == symbol.upper(), 'Alternative filename must match the exact symbol')
            require(source['status'] == 'filename-present-unverified', 'Never promote filename matches automatically')
            if source.get('result') == 'png-unverified':
                require(re.fullmatch(r'[a-f0-9]{64}', source.get('sha256', '')) is not None,
                        'Probed alternative needs a checksum')
                require(type(source.get('width')) is int and type(source.get('height')) is int and
                        4 <= source['width'] <= 2048 and 4 <= source['height'] <= 2048,
                        'Probed alternative dimensions out of bounds')
    return index


def read_publisher_checks(path):
    result = {}
    if path is None: return result
    for line in path.read_text().splitlines():
        row = json.loads(line)
        expected = 'https://logos.stockanalysis.com/' + quote(row['symbol'].lower(), safe='') + '.svg'
        require(row['url'] == expected, 'Publisher source must be the exact fixed-origin symbol SVG')
        if row['result'] == 'svg-unverified':
            require(re.fullmatch(r'[a-f0-9]{64}', row.get('sha256', '')) is not None,
                    'Publisher image checksum required')
            require(row.get('format') == 'svg' and type(row.get('width')) is int and type(row.get('height')) is int
                    and 4 <= row['width'] <= 2048 and 4 <= row['height'] <= 2048, 'Publisher dimensions required')
        result[row['symbol']] = row
    return result


def build_inventory(directory, companies, checks, as_of, alternatives=None, publishers=None):
    require(len({r['symbol'] for r in directory}) == len(directory), 'Cross-source symbol collision')
    company_by_symbol = {s['market'] + ':' + a: c for c in companies for s in c['securities']
                         for a in [s['symbol'], *s.get('aliases', [])]}
    records = []
    for row in sorted(directory, key=lambda r: r['symbol']):
        key = 'US:' + row['symbol']
        known = company_by_symbol.get(key)
        logo = resolve(companies, key, as_of=as_of) if known else None
        accepted_names = [known['name'], *[a['name'] for a in known.get('directoryNameAliases', [])
                                          if a['symbol'] == row['symbol']]] if known else []
        conflict = known and identity_name(issuer_hint(row['name'])) not in {identity_name(n) for n in accepted_names}
        if logo and not logo['active']:
            known = None
        if conflict:
            known = None
            logo = None
        record = {
            'key': key, 'symbol': row['symbol'], 'securityName': row['name'],
            'exchange': row['exchange'], 'securityKindHint': security_kind(row['name']),
            'identityEvidenceUrl': SOURCE_URLS[row['sourceFile']],
            'sourceAliases': row['sourceAliases'], 'issuerNameHint': issuer_hint(row['name']),
            'issuerId': known['id'] if known else None,
            'mappingStatus': 'directory-name-conflict' if conflict else 'reviewed' if known else 'needs-review',
            'reviewedLogoUrl': logo['logoUrl'] if logo and logo['active'] else None,
            'providerSourceUrl': 'https://financialmodelingprep.com/image-stock/' + quote(row['symbol'], safe='') + '.png',
            'providerOutcome': checks.get(row['symbol'], {}).get('result', 'not-tested'),
        }
        check = checks.get(row['symbol'])
        if check:
            for field in ('checkedAt', 'httpStatus', 'sha256', 'width', 'height', 'format', 'bytes'):
                if field in check: record[field] = check[field]
        if known and check and any(l['status'] == 'rejected' and l.get('sha256') == check.get('sha256')
                                   for l in known['logos']):
            record['providerIdentityStatus'] = 'rejected'
        if alternatives and row['symbol'] in alternatives:
            record['otherCandidateSources'] = alternatives[row['symbol']]
        if publishers and row['symbol'] in publishers:
            record['publisherCandidate'] = publishers[row['symbol']]
        records.append(record)
    groups = collections.defaultdict(list)
    for row in records:
        groups[normalized_hint(row['issuerNameHint'])].append(row)
    for siblings in groups.values():
        # Grouping is explicit and provisional. Never silently promote a name hint
        # into a reviewed issuer relation, nor use arbitrary ticker suffix stripping.
        candidates = [r for r in siblings if r['providerOutcome'] == 'png-unverified'
                      and r.get('providerIdentityStatus') != 'rejected']
        candidates.sort(key=lambda r: (r['securityKindHint'] != 'common', len(r['symbol']), r['symbol']))
        if not candidates: continue
        source = candidates[0]
        for row in siblings:
            if row['providerOutcome'] != 'png-unverified' and row['reviewedLogoUrl'] is None:
                row['sharedIssuerCandidate'] = {'symbol': source['symbol'], 'url': source['providerSourceUrl'],
                    'evidenceUrl': source['identityEvidenceUrl'], 'matchBasis': 'directory-name-hint',
                    'status': 'candidate', 'sha256': source['sha256'],
                    'width': source['width'], 'height': source['height'], 'format': 'png'}
    return records


def report(records):
    outcomes = dict(sorted(collections.Counter(r['providerOutcome'] for r in records).items()))
    return {'securities': len(records), 'reviewedIssuerSecurities': sum(r['issuerId'] is not None for r in records),
            'reviewedLogoSecurities': sum(r['reviewedLogoUrl'] is not None for r in records),
            'sourceOutcomes': outcomes,
            'unverifiedImageSecurities': outcomes.get('png-unverified', 0),
            'sharedIssuerCandidateSecurities': sum('sharedIssuerCandidate' in r for r in records),
            'otherSourceCandidateSecurities': sum(bool(r.get('otherCandidateSources')) for r in records),
            'publisherCandidateSecurities': sum(r.get('publisherCandidate', {}).get('result') == 'svg-unverified' for r in records),
            'anyKnownSourceSecurities': sum(r['reviewedLogoUrl'] is not None or r['providerOutcome'] == 'png-unverified'
                                          or 'sharedIssuerCandidate' in r or bool(r.get('otherCandidateSources'))
                                          or r.get('publisherCandidate', {}).get('result') == 'svg-unverified' for r in records),
            'sourceCheckComplete': outcomes.get('not-tested', 0) == 0,
            'verifiedLogoComplete': all(r['reviewedLogoUrl'] is not None for r in records)}


def resolve_inventory(records, key, allow_unverified=False):
    row = next((r for r in records if r['key'] == key), None)
    if row is None:
        aliases = [r for r in records if key in ['US:' + a for a in r['sourceAliases']]]
        if len(aliases) == 1: row = aliases[0]
    if row is None: return None
    result = {'symbol': key, 'name': row['securityName'], 'issuerId': row['issuerId'],
              'mappingStatus': row['mappingStatus'], 'logoUrl': row['reviewedLogoUrl'],
              'verification': 'reviewed' if row['reviewedLogoUrl'] else 'unresolved',
              'providerOutcome': row['providerOutcome']}
    if result['logoUrl'] or not allow_unverified: return result
    if row['providerOutcome'] == 'png-unverified' and row.get('providerIdentityStatus') != 'rejected':
        result.update(logoUrl=row['providerSourceUrl'], verification='provider-unverified',
                      sha256=row['sha256'], width=row['width'], height=row['height'])
    elif 'sharedIssuerCandidate' in row:
        shared = row['sharedIssuerCandidate']
        result.update(logoUrl=shared['url'], verification='directory-name-candidate',
                      sourceSymbol=shared['symbol'], sha256=shared['sha256'],
                      width=shared['width'], height=shared['height'])
    else:
        checked = next((s for s in row.get('otherCandidateSources', []) if s.get('result') == 'png-unverified'), None)
        if checked:
            result.update(logoUrl=checked['url'], verification='repository-unverified',
                          sha256=checked['sha256'], width=checked['width'], height=checked['height'])
        else:
            publisher = row.get('publisherCandidate')
            if publisher and publisher['result'] == 'svg-unverified':
                result.update(logoUrl=publisher['url'], verification='publisher-unverified',
                              sha256=publisher['sha256'], width=publisher['width'],
                              height=publisher['height'], format='svg')
    # A GitHub filename alone cannot establish that actual image bytes are available.
    return result


def render_inventory(output):
    # One security per line makes the generated full directory reviewable in Git.
    meta = {k: v for k, v in output.items() if k != 'securities'}
    header = json.dumps(meta, indent=2, ensure_ascii=False).rstrip()[:-1].rstrip()
    rows = ',\n'.join('    ' + json.dumps(row, ensure_ascii=False, separators=(',', ':'))
                     for row in output['securities'])
    return header + ',\n  "securities": [\n' + rows + '\n  ]\n}\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--checks', type=Path)
    parser.add_argument('--date', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--alternatives', type=Path, help='Pinned exact filename candidates (JSON symbol index)')
    parser.add_argument('--publisher-checks', type=Path)
    parser.add_argument('--summary', type=Path)
    parser.add_argument('--gaps', type=Path)
    parser.add_argument('--check', action='store_true', help='Check generated outputs without writing')
    args = parser.parse_args()
    dt.date.fromisoformat(args.date)
    companies = load()
    directory, sources = [], []
    for filename, url in SOURCE_URLS.items():
        raw = (args.sources / filename).read_bytes()
        directory.extend(parse_directory(raw.decode('utf-8-sig'), filename))
        sources.append({'file': filename, 'url': url, 'sha256': hashlib.sha256(raw).hexdigest()})
    alternatives = validate_alternatives(json.loads(args.alternatives.read_text())) if args.alternatives else None
    publishers = read_publisher_checks(args.publisher_checks)
    records = build_inventory(directory, companies, read_checks(args.checks), args.date, alternatives, publishers)
    output = {'schemaVersion': 1, 'profile': 'directory-provider-inventory',
              'asOf': args.date, 'scope': 'non-test-non-etf-us-securities',
              'sources': sources, 'summary': report(records), 'securities': records}
    results = [resolve_inventory([row], row['key'], True) for row in records]
    gaps = [row for row, result in zip(records, results) if result['logoUrl'] is None]
    output['summary'].update(usableSourceSecurities=len(records) - len(gaps),
                            noUsableSourceSecurities=len(gaps),
                            resolverOutcomes=dict(sorted(collections.Counter(r['verification'] for r in results).items())))
    outputs = [(args.output, render_inventory(output))]
    if args.summary:
        outputs.append((args.summary, json.dumps({'asOf': args.date, 'scope': output['scope'],
                                                  'summary': output['summary']}, indent=2) + '\n'))
    if args.gaps:
        text = io.StringIO(newline='')
        writer = csv.DictWriter(text, fieldnames=['symbol', 'securityName', 'exchange', 'issuerNameHint',
                                                'providerOutcome', 'identityEvidenceUrl'], lineterminator='\n')
        writer.writeheader(); writer.writerows({k: row[k] for k in writer.fieldnames} for row in gaps)
        outputs.append((args.gaps, text.getvalue()))
    for path, text in outputs:
        if args.check:
            require(path.exists() and path.read_bytes() == text.encode('utf-8'), 'Regenerate directory output: ' + path.name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode('utf-8'))
    print(json.dumps(output['summary'], indent=2))


if __name__ == '__main__':
    main()
