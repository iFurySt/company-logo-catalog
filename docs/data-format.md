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
failure; consumers may supply their own fallback.

The resolver is offline and does not fetch images. Consumers should cache
appropriately, check source terms, detect byte changes against reviewed hashes,
and fall back when a source fails or changes. They should not blindly download
arbitrary URLs from an untrusted fork; use explicit source origins and size limits.
