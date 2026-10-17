# Company Logo Catalog

Stock securities, reviewed issuer mappings and company image sources for the
current US listing directory. Shared issuer mappings let common shares, units,
warrants and preferred shares use the same company avatar.

[中文说明](README.zh-CN.md) · [Contribute](CONTRIBUTING.md) · [Data format](docs/data-format.md)

## Coverage

The 2026-10-14 Nasdaq Trader snapshot contains **7,481 non-test, non-ETF securities**.
Every one has a recorded source outcome in [catalog-provider.json](catalog-provider.json).

| Result | Securities |
| --- | ---: |
| Reviewed company image | 53 |
| Exact-symbol provider image, not identity-reviewed | 6,462 |
| Shared image proposed from directory company names, not issuer-reviewed | 562 |
| Probed repository image, not identity-reviewed | 14 |
| Publisher SVG, not identity-reviewed | 48 |
| No usable source found in this pass | 342 |

These are security counts, not distinct companies. Source availability is **not**
verified issuer/logo identity. The reviewed catalog contains 42 companies,
59 securities, 65 exact symbol/alias keys and 40 visually reviewed company images.
See [coverage.json](coverage.json), [missing-logos.csv](missing-logos.csv) and
[full review notes](docs/full-directory-review.md).

Latest batch: [24 issuer reviews, 2026-10-17](docs/review-2026-10-17.md), including
ECL, ED, EFX, EG, EIX, EL and the corrected Elevance Health image.

## Use

```sh
# Reviewed images only; unknown/unreviewed images remain null.
python3 scripts/catalog.py resolve 'US:AACOW'

# Explicitly allow unreviewed but byte-checked sources and name-group proposals.
python3 scripts/catalog.py resolve 'US:AA' --allow-provider
python3 scripts/catalog.py summary
```

Choose the appropriate dataset:

- [catalog.json](catalog.json): reviewed company records and exact issuer index;
  compatible with the existing AIFi catalog reader.
- [catalog-provider.json](catalog-provider.json): exhaustive security/source profile
  with availability, checksum, dimensions and explicit verification levels. It has
  a different schema shape; consumers must opt into this profile.

The default resolver only returns reviewed images. Provider opt-in never promotes
an image to `verified`, and known rejected images remain blocked. Repository
filename presence without a successful byte check is insufficient to return an
image. Source URLs have independent availability and artwork usage terms.

## Maintain

Requires Python 3.12+ and Node 24+; no third-party dependencies or API keys.

```sh
python3 scripts/catalog.py validate
python3 scripts/catalog.py build
python3 -m unittest discover -s tests
node --test tests/test_probe.mjs
```

See [maintenance commands](docs/full-directory-maintenance.md) for bounded,
resumable source probes and deterministic inventory rebuilding. CI is offline;
it validates both generated profiles and runs 30 regression tests.

## Scope and license

Initial focus is the current Nasdaq Trader candidate universe used by
[AIFi](https://github.com/ifuryst/aifi), including security classes and non-ETF
fund/debt listings. OTC and excluded ETFs are outside this snapshot.

Original code and curated metadata are MIT licensed. Linked logos retain their
owners' rights and source-provider terms. No third-party artwork pack is committed
or released. [Asset policy](assets/README.md) covers image contributions separately.

## Fund manager logos

[funds-catalog.json](funds-catalog.json) is a separate, reviewed profile for
institutional managers. Its initial 16 managers use exact SEC CIKs, official
website references and visually checked PNG URL metadata. Berkshire Hathaway and
Berkshire Asset are separate identities and have separate marks. This profile
contains corporate marks, not portraits copied from another application.

```sh
python3 scripts/funds.py validate
python3 scripts/funds.py build --check
python3 scripts/funds.py resolve 0001067983
```

Edit one file under `data/funds/`; review identity via SEC submissions and the
manager's official website, then review the actual image. Brand favicon services
and source owners retain their own rights. PNG files are not published in this
repository; consumers should cache privately, enforce source/byte limits and
verify recorded hashes. Wide official marks are allowed up to 4096 per dimension
with a 4-megapixel total cap. See [fund profile format](docs/fund-format.md).
