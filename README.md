# Bluestock ETL (Mutual Fund Data + Live NAV Fetch)

A small ETL-style Python project to work with mutual-fund datasets stored as CSV files in `data/raw/`, including utilities to fetch live NAV history from **mfapi.in** and to quickly profile datasets.

> The repository currently focuses on data collection (CSV + live NAV) and lightweight inspection/profiling. Downstream analytics/visualizations may live in `dashboard/`, `notebooks/`, `reports/`, or `sql/`.

---

## Features

- **Live NAV fetching**: Download NAV history (JSON) for specific scheme codes and persist as CSV.
- **Batch fetching**: Fetch 5 “bluechip” large-cap schemes in one run.
- **Dataset profiling**: Load and print shapes, dtypes, samples, and basic data-quality checks for all CSVs in `data/raw/`.
- **Schema/relational sanity checks**: Validate that `scheme_code` values in `fund_master.csv` exist in fetched NAV history.

---

## Repository Structure

```text
.
├── data/
│   ├── raw/               # Input CSVs (tracked or generated)
│   └── processed/        # Placeholder for ETL outputs
├── live_nav_fetch.py     # Fetch live NAV history into data/raw
├── data_ingestion.py     # Profile all CSVs under data/raw
├── requirements.txt
├── dashboard/            # (Optional) BI/visual assets
├── notebooks/           # (Optional) exploratory notebooks
├── reports/             # (Optional) generated reports
└── sql/                 # (Optional) SQL assets
```

---

## Setup

### 1) Prerequisites

- Python 3.9+ recommended
- Internet access (only needed when running `live_nav_fetch.py`)

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### A) Fetch live NAV history

`live_nav_fetch.py` downloads data from:

- `https://api.mfapi.in/mf/{scheme_code}`

and writes CSVs into:

- `data/raw/{filename}.csv`

#### 1) Default (runs multiple tasks)

When executed directly, the script will:

1. Fetch HDFC Top 100 Direct NAV (`scheme_code=125497`) -> `data/raw/hdfc_top_100_direct.csv`
2. Fetch the following 5 schemes and save into `data/raw/`:
   - `119551` -> `sbi_bluechip.csv`
   - `120503` -> `icici_bluechip.csv`
   - `118632` -> `nippon_large_cap.csv`
   - `119092` -> `axis_bluechip.csv`
   - `120841` -> `kotak_bluechip.csv`
3. Attempt to read `data/raw/fund_master.csv` and validate `scheme_code` overlap with fetched NAV.

Run:

```bash
python live_nav_fetch.py
```

#### 2) Fetch a single scheme (function usage)

If you want to reuse the function in another script/session:

```python
from live_nav_fetch import fetch_live_nav

fetch_live_nav("125497", "hdfc_top_100_direct")
```

---

### B) Profile all datasets under `data/raw/`

`data_ingestion.py` loads every `.csv` found in `data/raw/` and prints:

- dataset shape
- column dtypes
- first 3 rows
- missing-value count (total)
- duplicate-row count (exact duplicates)

Run:

```bash
python data_ingestion.py
```

---

## Expected Data

The repo ships (in `data/raw/`) multiple CSVs such as:

- `fund_master.csv`
- `nav_history.csv`
- `hdfc_top_100_direct.csv`
- `sbi_bluechip.csv`, `icici_bluechip.csv`, `axis_bluechip.csv`, `kotak_bluechip.csv`, `nippon_large_cap.csv`

Your own runs may also place additional CSVs into `data/raw/`; `data_ingestion.py` will automatically detect them.

---

## Notes / Troubleshooting

- **Empty `data/raw/`**: `data_ingestion.py` will report that no CSV files were found.
- **API/network errors**: `live_nav_fetch.py` catches request exceptions and prints an error per scheme.
- **Missing `fund_master.csv`**: The validation step will skip if the file is not present.

---

## .gitignore

This project ignores (via `.gitignore.txt` / Git configuration) generated and local files such as:

- `data/` (depending on your Git settings)
- `.env`
- `__pycache__/`

---

## License

Add your license here (e.g., MIT).
