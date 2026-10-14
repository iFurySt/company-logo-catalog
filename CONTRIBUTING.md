# Contributing

1. Open a missing/wrong-logo issue, or add one record under `data/companies/<id>.json`.
2. Verify the company and each security against an issuer site, SEC filing or
   exchange notice. Keep market/exchange context and cite every alias. Do not
   turn fuzzy search results or guessed W/U suffixes into company mappings.
3. Add a HTTPS logo source. Inspect the actual pixels and compare with a verified
   issuer/brand reference before using `verified`; otherwise use `candidate`. Mark confirmed wrong images `rejected`, not merely missing.
   Verified images need SHA256, format, dimensions and a check date. A successful
   HTTP response is insufficient (a prior AACOW lookup returned a Wix logo).
4. Do not paste API keys, signed URLs or third-party image-pack contents into a PR.
   Asset files have a separate process in assets/README.md.
5. Run validation, build catalog.json, and run the tests listed in README.md.
   Include the evidence and a concise explanation of the change in your PR.

For symbol changes or reused tickers, close the old record's validity interval
and add an explicit new record; do not silently overwrite historical identity.
The current index rejects symbol collisions, so retaining multiple historical
owners in one catalog will require a versioned schema change.

For broad coverage changes, regenerate both profiles and preserve source snapshots.
Follow [full-directory maintenance](docs/full-directory-maintenance.md).
