# Bluestock Mutual Fund System Data Dictionary

## Core Schemas

### 1. dim_fund (Dimension Table)
* **amfi_code** (`INTEGER`, Primary Key): Association of Mutual Funds in India tracking id identifier.
* **fund_house** (`TEXT`): Corporate entity managing asset allocation pool.
* **scheme_name** (`TEXT`): Commercial product marketing name.
* **category** (`TEXT`): Broad class mapping (Equity, Debt, Hybrid).
* **sub_category** (`TEXT`): Granular asset classification.
* **risk_grade** (`TEXT`): Risk ranking metrics (Low, Moderate, High, etc.).

### 2. fact_nav (Fact Table)
* **nav_id** (`INTEGER`, Primary Key AutoIncrement): Sequential identifier.
* **amfi_code** (`INTEGER`, Foreign Key): Mapping reference key to `dim_fund`.
* **date_key** (`TEXT`, Foreign Key): Temporal tracking key mapping to `dim_date`.
* **nav** (`REAL`): Value rate of a single transaction index unit.