# Fund manager logo profile v1

The separate `funds-catalog.json` profile has schemaVersion 1, profile
`fund-manager-logos`, its own catalogVersion 0.1.0, updatedAt and funds records.
It does not change the company/symbol schema or imply security ticker aliases.

Each `data/funds/<id>.json` file has an immutable slug, exact ten-digit SEC CIK,
legal/display names, reviewed date, website, primary identity evidence and ordered
logo metadata. SEC submissions were queried to confirm every initial CIK/legal
name; identifying request contact information is neither stored nor published.
Official sites were compared with each actual mark. No portrait or name-only
match from another research application is used. The initial Chilton domain was
found to be parked; the source was corrected to the official chiltonfunds.com.

Image URLs are public, credential-free, bounded PNGs with SHA256, dimensions,
review dates and explicit `redistribution: not-granted`. Some URLs use a public
brand-favicon service; this is not an endorsement or artwork rights grant.
The Whale Rock mark is a wide official PNG, bounded by a 4 MP pixel cap even when
one dimension exceeds 2048. Candidate/rejected/unavailable entries never resolve
as approved logos. Unknown CIKs resolve to null; never guess by fund name.

Run `python3 scripts/funds.py build` after record edits. Validation, deterministic
bundle checks and independent identity/URL/geometry tests run offline in CI.
