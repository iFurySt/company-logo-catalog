# Full current US security coverage

Scope: the current Nasdaq Trader US candidate directory (all non-test, non-ETF
listings), including preferred/depositary shares, units, warrants and rights.
Only this catalog repository is changed; AIFi runtime and personal state stay intact.

## Requirements

- Pin source snapshots and exact securities; primary source identity evidence.
- Keep source availability separate from issuer/image verification. HTTP 200,
  valid PNG bytes and a filename match do not establish current issuer identity.
- Complete a per-security inventory, with explicit missing/rejected/network-error
  outcomes. Never call a timeout an unavailable source or invent missing artwork.
- Reuse reviewed issuer logos for confirmed sibling securities.
- Retain compatibility of the reviewed catalog with existing AIFi readers.
  Full unreviewed inventories must not silently become verified catalog entries.
- Keep source images in ignored local audit storage, not an unlicensed image pack.

## Steps

- [x] Current directory snapshot and exhaustive source/mapping inventory.
- [x] Resumable bounded availability checks with per-entry outcomes.
- [ ] Review existing candidates and expand primary-evidence-backed mappings/logos.
- [x] Deterministic coverage report, validation/tests and documentation.
- [ ] Commit/push catalog updates with remaining source gaps explicitly counted.

## Completion criterion

Every in-scope security has a recorded outcome. Verified-image coverage is reported
separately; unavailable or unverified images remain unresolved, not false successes.
The requested end goal is correct images wherever reliably obtainable, not merely
an inventory or invented 100% logo coverage.

## Current results

- All 7,481 entries scanned; 6,500 decoded PNGs, 962 404s, 19 bad PNG headers.
- Provider profile has 7,091 selectable sources with explicit opt-in and retains
  identity-review levels; 390 entries still have no usable source.
- Reviewed catalog has 18 companies, 16 approved images; raw Apogee image rejected.
- Source coverage is complete as an inventory; the requested complete correct-logo
  coverage is still open. Remaining gaps and bulk identity review are not complete.

## Open follow-up

Full correct-logo coverage remains unfinished: 390 entries lack a selectable
source and the bulk supplier/name-group/repository images are not all identity
reviewed. Source outcomes, frozen snapshots, source-profile data and the gap list
are published so subsequent review can proceed without repeating this scan.
