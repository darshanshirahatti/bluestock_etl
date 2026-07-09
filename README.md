# BLUESTOCK-ETL

## Overview
BLUESTOCK-ETL is a Python-based ETL + analytics repository for mutual-fund datasets.

It supports:
- **Live NAV ingestion** from `https://api.mfapi.in/mf/{scheme_code}` (optional)
- **Data cleaning** and normalization into a consistent structure
- **SQLite star-schema loading** for analytics and BI reporting
- **Analytics outputs** including VaR/CVaR, rolling Sharpe charts, and EDA reporting

## Repository Structure
```text
.
├── dashboard/                 # BI assets (PowerBI PBIX/PDF) and theme
├── data/
│   ├── raw/                   # Input CSVs
│   └── processed/            # Cleaned CSV outputs
│   └── db/                   # SQLite database outputs
├── notebooks/                # Exploratory notebooks / supporting scripts
├── reports/                  # Generated documentation (data dictionary, etc.)
├── sql/                      # Schema + analytical SQL queries
├── scripts/                  # Operational scripts (ingestion, loading, analytics)
├── ANALYTICAL_REPORT.md      # Management-friendly generated report
├── PROJECT_DOCUMENTATION.md # Company-ready project document
└── requirement.txt           # Python dependencies
```

## Setup
### 1) Install dependencies
```bash
pip install -r requirement.txt
```

## Usage (Typical Workflow)
### 1) (Optional) Fetch live NAV data
```bash
python scripts/live_nav_fetch.py
```

### 2) Clean data
```bash
python notebooks/data_cleaning.py
```

### 3) Load into SQLite (star schema)
```bash
python scripts/db_loader.py
```

### 4) Run advanced analytics
```bash
python scripts/advanced_analytics.py
```

### 5) Generate EDA report
```bash
python notebooks/eda_analysis.py
```

## Key Outputs
- `data/processed/*_cleaned.csv` (cleaned datasets)
- `data/db/bluestock_mf.db` (SQLite star schema)
- `ANALYTICAL_REPORT.md` (EDA narrative)
- `var_cvar_report.csv`, `rolling_sharpe_chart.png` (advanced analytics)

## References
- Live NAV API: `https://api.mfapi.in/mf/`
- DB schema: `sql/schema.sql`
- Analytical SQL: `sql/analytical_queries.sql`

