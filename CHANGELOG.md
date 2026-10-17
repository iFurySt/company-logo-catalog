# Changelog

## Fund manager profile 0.1.0 — 2026-10-17

- Add 16 SEC-CIK-verified institutional manager identities and reviewed logo URL metadata.
- Add separate funds-catalog.json, exact-CIK resolver, deterministic build and CI tests.
- Preserve artwork ownership; publish no third-party image files or portraits.


## 0.3.0 — 2026-10-17

- Add 24 visually reviewed US issuer records, prioritizing the E-symbol list.
- ECL, ED, EFX, EG, EIX and EL now have reviewed exact-symbol mappings.
- Prefer official small-icon artwork for Analog Devices and Elevance Health;
  reject the generic A returned for ELV and retain its checksum.
- Recheck 36 bounded FMP sources: all valid PNGs, unchanged from the frozen audit.
- Reviewed coverage: 42 companies / 59 securities / 65 keys / 40 company images.
- Preserve the frozen 7,481-security inventory and its unreviewed distinctions;
  no third-party artwork files published.

## 0.2.0 — 2026-10-15

- Full frozen-directory profile: 7,481 securities with exhaustive source outcomes.
- 7,139 have a selectable source with explicit provider opt-in; 342 remain unresolved.
- 6,500 exact FMP PNGs decoded; transient failures retried, invalid PNGs recorded.
- Reviewed catalog grows to 18 companies / 35 securities / 41 keys / 16 company images.
- Official Apogee shield replaces a rejected generic image; four missing listing
  images sourced from issuer sites; Ares, Averin and Wintrust marks reviewed.
- Scoped directory-name exceptions, reused-name conflict guard, explicit provider
  resolution, resumable bounded probes and deterministic full-directory checks.
- 30 offline regression tests; no third-party artwork files published.


## 0.1.0 — 2026-10-14

- Initial public catalog: 14 companies, 31 securities, 37 exact symbol/alias keys.
- Eight verified logo sources; six candidate sources withheld by the resolver.
- Missing stock classes mapped to reviewed issuers; TREO official-site favicon.
- JSON schema, deterministic bundle, exact offline resolver, ten regression tests,
  pinned CI actions, contribution templates and separate asset-use policy.
