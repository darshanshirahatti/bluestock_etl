# Day 2 Schema Data Dictionary

## 1. dim_fund
* [cite_start]`amfi_code` (TEXT, PK): Unique identification key issued by AMFI India[cite: 424].
* [cite_start]`fund_house` (TEXT): Core parent asset management firm title banner[cite: 424].
* [cite_start]`scheme_name` (TEXT): Full corporate public marketing scheme index title[cite: 424].
* [cite_start]`expense_ratio_pct` (REAL): Annual fund operational expense percentage metrics[cite: 424].

## 2. fact_nav
* [cite_start]`amfi_code` (TEXT, FK): Relational framework mapping index reference pointer[cite: 425].
* `date_id` (TEXT): Standalone custom chronological index row key format.
* [cite_start]`nav` (REAL): Daily computed valuation point closing asset quote mark[cite: 425].