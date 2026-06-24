
    CREATE TABLE IF NOT EXISTS dim_fund (
        amfi_code TEXT PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        risk_category TEXT
    );

    CREATE TABLE IF NOT EXISTS dim_date (
        date_id TEXT PRIMARY KEY,
        calendar_date TEXT,
        year INTEGER,
        month INTEGER,
        quarter TEXT,
        is_weekday INTEGER
    );

    CREATE TABLE IF NOT EXISTS fact_nav (
        amfi_code TEXT,
        date_id TEXT,
        nav REAL,
        PRIMARY KEY (amfi_code, date_id),
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
        FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
    );

    CREATE TABLE IF NOT EXISTS fact_transactions (
        investor_id TEXT,
        transaction_date TEXT,
        amfi_code TEXT,
        transaction_type TEXT,
        amount_inr REAL,
        state TEXT,
        kyc_status TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    