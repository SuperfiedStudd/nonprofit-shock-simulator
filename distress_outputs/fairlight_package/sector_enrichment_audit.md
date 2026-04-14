# Sector Enrichment Audit

## What was searched

- Checked the local nonprofit cohort for any existing sector or NTEE-like field: none existed.
- Attempted an EIN join to the official IRS EO BMF extract using the four public regional CSV files.
- Source family used: IRS Tax Exempt Organization Search bulk data / EO BMF extract.

## Outcome

- Join status: **loaded_from_cache**
- Rows with NTEE coverage in the scored 2023 universe: **30,421**
- Coverage rate: **71.2%**

## Notes

- Used cached IRS EIN-to-NTEE lookup.
- IRS BMF provides broad NTEE classification, but the code can be missing or stale for some organizations.


## How it changed downstream outputs

- Sector enrichment was successfully added to benchmark cards, segment summaries, and shortlists.
- Sector should still be treated as a broad classification layer, not a perfect mission taxonomy.

## Top sector groups in the scored universe

| sector_group                              |   scored_orgs |
|:------------------------------------------|--------------:|
| Human Services                            |          5070 |
| Education                                 |          5053 |
| Health Care                               |          2330 |
| Arts, Culture & Humanities                |          2258 |
| Housing & Shelter                         |          1702 |
| Community Improvement & Capacity Building |          1697 |
| Philanthropy & Grantmaking                |          1360 |
| Recreation & Sports                       |          1216 |
| Religion-Related                          |          1065 |
| Environment                               |           940 |
