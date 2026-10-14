# Company Logo Catalog

A small, reviewed catalog connecting stock securities to companies and company
logo URLs. Shared issuer mappings let common shares, units, warrants and preferred
shares use the same company avatar.

[中文说明](README.zh-CN.md) · [Contribute](CONTRIBUTING.md) · [Data format](docs/data-format.md)

## Initial batch

14 companies, 31 securities and 37 exact symbol/alias keys. Eight company logos
are verified; six remain candidates. Missing security classes include AACOW,
AACPR/AACPW, ABR preferred shares, PCG$X, QRED.R and WTFCN. TREO uses its official
website favicon. See [review notes](docs/initial-review.md) for remaining gaps.

## Use

Download [catalog.json](catalog.json) from a pinned release or commit. It contains
company records and an exact `market:symbol` index. No API key is needed to read
the catalog; linked image sources have their own availability and usage rules.

```sh
python3 scripts/catalog.py resolve 'US:AACOW'
python3 scripts/catalog.py summary
```

The resolver returns a `logoUrl` only for visually reviewed images with status
`verified`. `candidate` means identity review is incomplete; `unavailable` records
a known source gap. Unknown/expired securities return no usable logo. Review dates
are snapshots, not a promise that a URL or ticker stays unchanged.

## Maintain

Edit one JSON file under `data/companies/`, then validate and rebuild:

```sh
python3 scripts/catalog.py validate
python3 scripts/catalog.py build
python3 -m unittest discover -s tests
```

Checks run on pushes and pull requests. They use Python's standard library and
make no network requests. CI checks structure, alias collisions and generated
output; issuer/image correctness still needs source and visual review.

## Scope and license

Initial focus: US stocks and the missing security-class avatars observed in
[AIFi](https://github.com/ifuryst/aifi). This is an incremental catalog, not a
complete exchange directory or a financial-data API.

Original code and curated metadata are MIT licensed. Linked logos retain their
owners' rights and provider terms. No third-party image pack is bundled in v0.1.0.
[Asset policy](assets/README.md) explains how images can be contributed separately.
