# Full stock image availability — 2026-10-18

Every one of the **7,484 securities** in the current AIFi non-test/non-ETF Nasdaq
Trader directory was included. The source files were fetched on October 17;
source provenance is archived separately. The audit on October 18 (Taipei time)
checks actual downloaded bytes and App eligibility, not just filename presence.

| Scope | Decodable PNG + offline App cache read | Total |
| --- | ---: | ---: |
| All current securities | 7,108 | 7,484 |
| S&P 500 | 503 | 503 |
| Nasdaq-100 | 101 | 101 |

[Every symbol and selected source](../data/audits/2026-10-18/availability.csv) ·
[376 unresolved App entries](../data/audits/2026-10-18/unresolved.csv) ·
[Machine-readable summary](../data/audits/2026-10-18/summary.json).

## What was checked

- Actual PNG byte checksum, dimensions, size cap and explicit source URL policy.
- Native decoder success and the same transparent/blank-white checks as the UI.
- 5,928 unique image contents; shared images count once for decoding, while every
  security has its own result. This is distinct from independent issuer review.
- Explicit private-cache import, followed by the real AIFi host's offline read
  for every positive row. No third-party artwork is distributed in this repo.
- Source check timestamps remain attached. Reusing a downloaded image does not
  invent a fresh HTTP request date. Unknown historical check times stay unknown.

FICO, FIS, FISV, FITB, FIX, FLEX, FOX and FOXA already had working PNG sources.
Their missing App images were delivery/cache misses, not absent branding. AIFi
now queues page reads and retries transient pressure instead of caching it as
absence. This is verified separately with a 50-avatar offline interaction test.

The latest primary-brand pass adds SKYD/SKYD.W, VMRK and VYLR after their recent
corporate changes. FSP and KNX's provider PNGs decoded to blank white images;
those checksums are rejected and usable pinned alternatives are preferred.
Google's favicon proxy returned a WordPress icon for KNX, so that candidate was
also excluded instead of treating HTTP success as proof of company identity.

## Availability is not verified issuer identity

The reviewed catalog has 45 companies with visually reviewed images. The much
larger provider inventory and **588-entry App PNG supplement** retain explicit
`provider-unverified`, `directory-name-candidate` and `repository-unverified`
levels. The default catalog CLI still resolves reviewed images only. AIFi opts
into best-effort decorative image candidates with exact symbols, hashes and
bounded source policy; this does not create verified legal issuer aliases.

Known rejected bytes never become eligible through provider opt-in. Name-group
candidates are current-directory observations, not historical identity or a rule
to strip W/U/preferred suffixes. Ticker reuse and corporate changes still require
catalog maintenance.

## Remaining 376

- **338** have no selected usable source after the recorded provider/repository
  passes. These include recent listings and security classes whose issuer assets
  still need evidence-backed mapping. This is not proof that no logo exists online.
- **38** have SVG publisher candidates but no accepted PNG source. AIFi's runtime
  intentionally does not treat remote SVG as a PNG or report those rows as usable.

A further pinned repository pass checked 18 exact PNG paths: 17 decoded; this
improved PNG availability without promoting the images to verified identity.
An eight-symbol EODHD legacy-image-path sample returned eight 404s; a publisher
`.png` variant sample also returned 404. These probes do not establish universal
provider failure. Paid/authenticated logo APIs and audited SVG conversion remain
possible follow-ups, not fabricated coverage in this report.

## Additional source follow-up

A bounded follow-up tested [LoadLogo](https://loadlogo.com/docs) using its documented PNG ticker endpoint and
`fallback=404`. BXBL still returned a ticker-letter monogram (not company artwork)
and its metadata endpoint returned 404. AMRO returned a 1,549×2,062 PNG despite
`size=128`, exceeding the current host height cap. Neither response was silently
counted as a usable App logo. This sample is not a universal judgment of the API;
other symbols and an audited resizing path may be investigated independently.
[Exact probe outcomes](../data/audits/2026-10-18/additional-source-probes.json)
preserve URLs, status and byte hashes. No third-party images are published.

An additional NYSE repository inventory request hit GitHub API HTTP 403 rate
limits and stopped. Its coverage is unknown; the existing 7,108/376 accounting
is unchanged.

## Reproduce

In AIFi, export the current local directory through its CLI, then run:

```sh
node scripts/audit-stock-logos.mjs \
  --catalog /path/to/company-logo-catalog \
  --directory /path/to/local-directory.json \
  --output /path/to/private-report
```

The local directory JSON has `snapshotId`, `total` and `items` from stable paged
CLI reads. Private audit-download PNGs are needed for byte-level reproduction;
they are deliberately not published as an artwork pack. `--import-cache` is an
explicit optional private cache import. It never runs on ordinary App reads or
startup. Without that flag, the report checks source bytes/decoder eligibility,
not successful cache import. Source URLs may later fail or change: checksums and
last-good private data make that visible rather than silently changing identity.
