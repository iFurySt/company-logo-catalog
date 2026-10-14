# Initial review — 2026-10-14

The first batch targets observed missing stock avatars and a few common companies.
Company/security identity is reviewed separately from image identity. It is not a
complete US listing set or a percentage-of-market coverage claim.

| Company | Securities | Logo outcome |
| --- | --- | --- |
| Abony Acquisition Corp. I | AACO, AACOU, AACOW | Verified ABONY source wordmark; AACOW source itself was 404 |
| PG&E Corporation | PCG, PCG$X | Verified PG&E mark; no inference of its subsidiary's preferred classes |
| QuasarEdge | QRED, QRED.U, QRED.R | Verified issuer wordmark; unrelated Qred lender excluded |
| Tactical Resources | TREO | Verified square favicon linked directly by official website |
| Apple | AAPL | Verified corporate mark |
| Microsoft | MSFT | Verified corporate mark |
| NVIDIA | NVDA | Verified corporate mark |
| AMD | AMD | Verified recognizable mark; provider's green color variant |
| Ares Acquisition Corporation III | AAC, AAC.U, AAC.W | Candidate: sponsor mark and reused ticker need issuer-specific image review |
| Apogee Acquisition Corp | AACP, AACPU, AACPR, AACPW | Candidate: generic blue A is not enough to establish company artwork |
| Averin Capital Acquisition Corp | ACAA, ACAAU, ACAAW | Candidate: sponsor/issuer branding distinction needs confirmation |
| Arbor Realty Trust | ABR, ABR$D, ABR$E, ABR$F | Candidate: compare current issuer artwork before promoting white mark |
| Wintrust Financial | WTFC, WTFCN | Candidate: compare white W with current issuer artwork |
| Alphabet | GOOG, GOOGL | Candidate: provider gives Google G, not Alphabet wordmark |

Candidate records provide useful reviewed security mappings but the offline
resolver returns no image for them. Exact SEC-style aliases are retained where
primary filings support them. Dollar/dot source notation is supported by the
Nasdaq Trader directory and matched security names; suffix guesses are not used.

Byte hashes/dimensions come from successful source requests or previously fetched
public image cache, followed by image inspection on the review date. No public
catalog includes the private cache or the image bytes themselves. Provider URL
availability can change; detect byte changes before reusing a reviewed image.

Primary evidence and logo reference URLs are stored in each company's JSON record.

## Follow-up

See [full-directory review](full-directory-review.md) for the 2026-10-15 changes:
Ares, Averin and Wintrust reviewed; Apogee generic provider artwork rejected and
replaced with an official source; four new issuer-site image records.
