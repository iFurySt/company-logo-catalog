# Full directory maintenance

Keep reviewed company records and the exhaustive provider inventory separate.
A successful image request is an availability observation, not issuer verification.

## Source snapshot

`data/directory/2026-10-18/` archives the two official Nasdaq Trader directory files,
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
  --sources data/directory/2026-10-18 \
  --checks data/directory/2026-10-18/source-checks.jsonl \
  --alternatives data/directory/2026-10-18/github-candidates.json \
  --publisher-checks data/directory/2026-10-18/publisher-checks.jsonl \
  --date 2026-10-18 \
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

`catalog.json` remains the reviewed company profile. `catalog-provider.json`
is about 7 MB and retains availability/provisional verification levels. AIFi
consumes the smaller generated `app-fallbacks.json` explicitly as best-effort PNG
artwork, separately from reviewed identity. Every selected source still needs
an allowed origin/path, checksum and dimensions. Metadata cannot broaden the
consumer's source policy or grant rights to the linked artwork.

The additional SVG publisher pass stopped on HTTP 429. Do not retry access limits
by bypassing them; record attempted and unattempted entries distinctly.

## App PNG availability supplement

`python3 scripts/app_fallbacks.py` builds `app-fallbacks.json` from the current
inventory; `--check` verifies deterministic output. This small profile contains
exact security-to-image URL observations for name-group candidates and byte-checked
repository alternatives. It does not turn those records into verified issuer
aliases or change the default reviewed-only CLI resolver. Known rejected images
remain excluded. The consumer must explicitly support this best-effort profile,
pinned source paths, recorded hashes/dimensions and private bounded caching.

The 2026-10-18 directory is archived from AIFi's committed local Nasdaq snapshot,
fetched on October 17. Existing HTTP observations retain their original dates;
rechecks and additional repository probes are recorded separately. Availability
can also be checked offline against downloaded bytes with AIFi's real PNG decoder
and host cache path. A local decode date is not a new HTTP check or issuer review.
