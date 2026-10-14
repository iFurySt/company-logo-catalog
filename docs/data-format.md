# Data format v1

`schemas/company.schema.json` describes each editable company record. The
standard-library validator adds cross-record alias uniqueness and URL/date checks.
The generated catalog has schemaVersion, catalogVersion, updatedAt, companies and
symbols. `symbols` maps exact `market:symbol` strings to a stable company id.

- **id**: stable slug independent of ticker; optional **cik** has ten digits.
- **identityEvidenceUrls**: primary sources linking the company and its securities.
- **securities**: market US, exchange, exact symbol, security kind, evidence URLs,
  optional exact aliases and validity interval. Aliases describe naming conventions
  for the same security, not inferred additional securities.
- **logos**: ordered source URLs, source name, status, checkedAt, issuer/brand
  referenceUrl and redistribution status. Verified records have SHA256, dimensions
  and format. `redistribution: not-granted` means the catalog license grants no
  rights to linked artwork; it is not a claim that every provider forbids reuse.

`verified` means the reviewer inspected pixels and found that they identify the
recorded issuer/brand at the review date. It does not mean an official endorsement,
perpetual identity, service SLA or asset redistribution permission. `candidate`
never gets returned by the CLI resolver. `unavailable` records a tested source
failure; `rejected` records a known wrong image and is blocked even when a caller
opts into provider images; consumers may supply their own fallback.

The resolver is offline and does not fetch images. Consumers should cache
appropriately, check source terms, detect byte changes against reviewed hashes,
and fall back when a source fails or changes. They should not blindly download
arbitrary URLs from an untrusted fork; use explicit source origins and size limits.

## Directory display aliases and full provider profile

Optional `directoryNameAliases` entries have name, explicit security symbol and
primary evidence URLs. They explain known directory display-name differences, not
new legal issuer identity or permission to map unrelated subsidiaries.

`catalog-provider.json` has profile `directory-provider-inventory`, source hashes,
a frozen directory date, summary and one security per line. It preserves primary
security names/exchanges/notation aliases, reviewed issuer identity where known,
image availability and explicit provisional name-group suggestions. It is not the
reviewed company-record schema. Exact alias ambiguity is unresolved, not a first
match. New stock names conflicting with reviewed identity disable stale images.

Provider resolver levels are `reviewed`, `provider-unverified`,
`directory-name-candidate`, `repository-unverified`, `publisher-unverified` and `unresolved`. Default
resolution returns only reviewed images. Byte checks and checksum metadata never
automatically promote identity. Curated timestamps use the reviewer's local date;
UTC CI permits the one-day calendar offset needed around midnight.
