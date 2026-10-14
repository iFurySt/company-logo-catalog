# Company Logo Catalog

Read README.md, CONTRIBUTING.md and docs/data-format.md before changing records.
Run `python3 scripts/catalog.py validate`, `python3 scripts/catalog.py build --check`
and `python3 -m unittest discover -s tests` before committing.

- Keep one company per data/companies/<id>.json.
- Verify issuer identity and every security alias with primary sources.
- A valid image or same-named ticker file is not proof of issuer identity.
- Use exact symbol keys; never derive issuer links by removing ticker suffixes.
- Candidate/unavailable logos must never be returned as verified images.
- Publish no credentials, signed URLs or personal workspace data.
- Image files require independent provenance and asset-use review; MIT covers
  this project's original metadata/code, not linked third-party artwork.
- Regenerate catalog.json after record changes. Record meaningful releases in CHANGELOG.md.
