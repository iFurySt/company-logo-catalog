# Full directory review — 2026-10-15

The source snapshot was collected on 2026-10-14 and covers 7,481 current non-test,
non-ETF securities. It replaces a 7,487-security cached comparison: BSRT, FLSC and
SKYD.W were added; BKKT.W, CCO, IAE, IHD, PRIF$L, QETA, QETAR, QETAU and SKYD.V were
absent from the new snapshot. This is a frozen scope, not a perpetual listing claim.

## Exhaustive availability outcomes

All 7,481 exact-symbol FMP paths were requested with bounded concurrency/rate.
After retries: 6,500 valid PNGs, 962 HTTP 404s and 19 invalid PNG headers.
The two initial network failures became one PNG (RYM) and one 404 (RAC.W).
All 6,500 positive PNGs were decoded locally with no failures; this still does not
verify the issuer/brand shown in every image.

Fourteen otherwise unresolved securities have byte-checked PNG alternatives at
pinned repository revisions. The 5,106 current-directory filename candidates
remain unreviewed; file presence alone does not make them usable. Original artwork
is not included in this repository or release artifacts.

## Reviewed changes

| Company | Result / primary brand reference |
| --- | --- |
| Ares Acquisition III | Ares orbital sponsor mark matches its issuer strategy page: https://www.ares.com/us/our-strategies/aac-iii |
| Averin Capital Acquisition | Sponsor wordmark matches official site header; press page identifies the acquisition company: https://www.averincapital.com/press |
| Wintrust | W and underline compared with official Q1 2026 presentation cover: https://s205.q4cdn.com/387403231/files/doc_financials/2026/q1/Wintrust-Financial-Corporation-Earnings-Release-Presentation-Q1-2026.pdf |
| Apogee Acquisition | Official shield/globe/arrow favicon replaces rejected generic blue A: https://apogeeacquisitioncorp.com/about-us/ |
| Accelevation / ACCV | Official operating-brand favicon: https://www.accelevation.com/; actual bytes are 32×32 despite the source filename saying 512. |
| ADVASA / ADBT | Orange A favicon linked by issuer site: https://adbt.io/; SEC listing evidence is in the company record. |
| ADI Global Distribution / ADIG | Official white ADI wordmark: https://investor.adiglobal.com/; distinguish it from unrelated Analog Devices ticker ADI. |
| ADARx / ADRX | Official RNA/DNA-style favicon: https://www.adarx.com/ |

Arbor and Alphabet retain unapproved source entries from the initial batch.
Related branding or a technically valid image is insufficient to silently call a
holding-company wordmark or historical variant fully reviewed.

## Remaining work

The explicitly enabled provider resolver offers a source for 7,091 securities:
29 reviewed, 6,486 exact-provider, 562 directory-name proposals and 14 repository
candidates. **390 have no usable source in this pass**; see `missing-logos.csv`.
That does not prove no logo exists elsewhere. Research their current issuer sites,
listing notices and original brand assets before promoting or adding mappings.

The 562 shared-image proposals normalize company-name display variants, not
symbol suffixes. They remain candidates; subsidiaries, sponsors, fund managers,
renamed/reused tickers and name collisions need independent issuer review.
Current-source name conflicts disable stale reviewed identity in the inventory.
Every stock is accounted for, but verified-logo coverage is not complete.
