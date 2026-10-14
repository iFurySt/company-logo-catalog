# Full directory maintenance

Keep reviewed company records and the exhaustive provider inventory separate.
A successful image request is an availability observation, not issuer verification.

## Source snapshot

`data/directory/2026-10-14/` archives the two official Nasdaq Trader directory files,
per-symbol source outcomes and pinned GitHub filename candidates. Only non-test,
non-ETF listings enter the generated profile. Raw exchange codes are translated
from Nasdaq references; `F` is **TXSE**, not NYSE Texas. Primary notice:
https://www.nasdaqtrader.com/TraderNews.aspx?id=DTN2026-10

Do not infer legal issuer identity from a ticker suffix. Company-name groups are
explicit review candidates. Directory naming exceptions are security-scoped,
evidence-backed records; PCG's operating-company display name is not authority to
map other subsidiary securities to the holding company.

## Availability probes

Node's standard-library HTTPS client limits concurrency/rate/bytes/dimensions,
uses TLS verification, does not follow redirects, and stops a batch on 403/429.
Default four workers, two requests/second; maximum eight workers/four requests/second.
Each request has a 20-second default deadline and at most one transient retry.
No cookies, keys or personal workspace data are transmitted.

```sh
node scripts/probe-logos.mjs \
  --input catalog-provider.json \
  --output .artifacts/current/source-results.jsonl \
  --images .artifacts/current/images \
  --workers 4 --rate 2

# Checkpointed exact symbols are skipped. Retry only transient outcomes:
node scripts/probe-logos.mjs \
  --input catalog-provider.json \
  --output .artifacts/current/source-results.jsonl \
  --retry-errors
```

Image downloads are optional, private audit material and never part of published
catalog artifacts. Header validation is not a full decoder or visual brand check;
review images separately. The initial exhaustive pass additionally decoded all
6,500 returned PNGs locally; none failed. Source failures and valid-but-wrong images
must remain distinct. Provider profile opt-in cannot return known rejected artwork.

## Deterministic rebuild

```sh
python3 scripts/catalog.py build
python3 scripts/coverage.py \
  --sources data/directory/2026-10-14 \
  --checks data/directory/2026-10-14/source-checks.jsonl \
  --alternatives data/directory/2026-10-14/github-candidates.json \
  --publisher-checks data/directory/2026-10-14/publisher-checks.jsonl \
  --date 2026-10-14 \
  --output catalog-provider.json \
  --summary coverage.json \
  --gaps missing-logos.csv
```

Add `--check` to compare committed generated files without writing. CI performs
this check offline. Keep a frozen source snapshot/provenance when updating the
universe so delistings, newly added securities and reused tickers remain auditable.
Actual stock/company names, source dates, byte hashes and naming conflicts must
not be overwritten with guesses.

## Consumer compatibility

`catalog.json` remains the small reviewed company profile. `catalog-provider.json`
is about 7 MB and uses security records, not the company-record schema. Existing
AIFi readers only consume the reviewed profile and have smaller manifest limits;
provider-profile integration needs a separate bounded reader and user choice.
New official company PNG hosts also need explicit host allowlisting in AIFi.
No application-runtime change is included in this catalog repository task.

The additional SVG publisher pass stopped on HTTP 429. Do not retry access limits
by bypassing them; record attempted and unattempted entries distinctly.
