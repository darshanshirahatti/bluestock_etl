<<<<<<< HEAD
<<<<<<< HEAD
# Bluestock ETL (Mutual Fund Data + Live NAV Fetch)

A small ETL-style Python project to work with mutual-fund datasets stored as CSV files in `data/raw/`, including utilities to fetch live NAV history from **mfapi.in** and to quickly profile datasets.

> The repository focuses on data collection (CSV + live NAV), dataset profiling, and downstream ETL utilities. Analytics/visualizations may live in `dashboard/`, `notebooks/`, `reports/`, or `sql/`.

---

## Features

- **Live NAV fetching**: Download NAV history (JSON) for specific scheme codes and persist as CSV.
- **Batch fetching**: Fetch 5 “bluechip” large-cap schemes in one run.
- **Dataset profiling**: Load and print shapes, dtypes, samples, and basic data-quality checks for all CSVs in `data/raw/`.
- **ETL cleaning**: Clean/standardize nav, transactions, and performance inputs (see scripts in `Scripts/`).
- **Star schema + SQLite loading**: Build a simple star schema in `data/db/bluestock_mf.db` (see `Scripts/load_star_schema.py`).

---

## Repository Structure

```text
.
├── dashboard/                      # (Optional) BI/visual assets
├── data/
│   ├── raw/                        # Input CSVs (tracked or generated)
│   └── processed/                 # Placeholder for ETL outputs
│   └── db/                         # SQLite database outputs
├── notebooks/                     # (Optional) exploratory notebooks
├── reports/                       # (Optional) generated reports
├── sql/
│   ├── analytical_queries.sql
├── Scripts/
│   ├── live_nav_fetch.py
│   ├── data_ingestion.py
│   ├── clean_nav.py
│   ├── clean_transactions.py
│   ├── clean_performance.py
│   ├── etl_pipeline.py
│   ├── load_star_schema.py
│   └── sql/
│       └── schema.sql
├── requirements.txt
└── README.md
```

---

## Setup

### 1) Prerequisites

- Python 3.9+ recommended
- Internet access (only needed when running `Scripts/live_nav_fetch.py`)

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### A) Fetch live NAV history

`Scripts/live_nav_fetch.py` downloads data from:

- `https://api.mfapi.in/mf/{scheme_code}`

and writes CSVs into:

- `data/raw/{filename}.csv`

#### 1) Default (runs multiple tasks)

When executed directly, the script will:

1. Fetch HDFC Top 100 Direct NAV (`scheme_code=125497`) -> `data/raw/hdfc_top_100_direct.csv`
2. Fetch these 5 schemes and save into `data/raw/`:
   - `119551` -> `sbi_bluechip.csv`
   - `120503` -> `icici_bluechip.csv`
   - `118632` -> `nippon_large_cap.csv`
   - `119092` -> `axis_bluechip.csv`
   - `120841` -> `kotak_bluechip.csv`
3. Attempt to read the local “fund master” file from `data/raw/` and validate referential integrity against the fetched NAV.

Run:

```bash
python Scripts/live_nav_fetch.py
```

#### 2) Fetch a single scheme (function usage)

```python
from Scripts.live_nav_fetch import fetch_live_nav

fetch_live_nav("125497", "hdfc_top_100_direct")
```

---

### B) Profile datasets under `data/raw/`

`Scripts/data_ingestion.py` loads every `.csv` found in `data/raw/` and prints:

- dataset shape
- column dtypes
- first 3 rows
- missing-value count (total)
- duplicate-row count (exact duplicates)

Run:

```bash
python Scripts/data_ingestion.py
```

---

## Expected Data

This repo ships (in `data/raw/`) CSVs with numeric prefixes, for example:

- `01_fund_master.csv`
- `02_nav_history.csv`
- `03_aum_by_fund_house.csv`
- `04_monthly_sip_inflows.csv`
- `05_category_inflows.csv`
- `06_industry_folio_count.csv`
- `07_scheme_performance.csv`
- `08_investor_transactions.csv`
- `09_portfolio_holdings.csv`
- `10_benchmark_indices.csv`

Your `Scripts/live_nav_fetch.py` will additionally create files such as:

- `hdfc_top_100_direct.csv`
- `sbi_bluechip.csv`, `icici_bluechip.csv`, `axis_bluechip.csv`, `kotak_bluechip.csv`, `nippon_large_cap.csv`

---

## Notes / Troubleshooting

- **Empty `data/raw/`**: `Scripts/data_ingestion.py` will report that no CSV files were found.
- **API/network errors**: `Scripts/live_nav_fetch.py` catches request exceptions and prints an error per scheme.
- **Missing fund master**: validation inside `Scripts/live_nav_fetch.py` will skip if the expected master CSV is not found.

---

## .gitignore

This project ignores (via `.gitignore.txt` / Git configuration) generated and local files such as:

- `data/` (depending on your Git settings)
- `.env`
- `__pycache__/`

---

## License

Add your license here (e.g., MIT).

=======
# BLUESTOCK-ETL
>>>>>>> 277ef20 (Merge branch 'main' of https://github.com/darshanshirahatti/BLUESTOCK-ETL)
=======
# BLUESTOCK-ETL
>>>>>>> 277ef20e68bdf226f9f6e7097b4ae9089317716c
