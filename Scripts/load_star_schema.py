import os
import pandas as pd
import glob
from sqlalchemy import create_engine, text

def build_and_load_db():
    print("--- Tasks 4 & 5: Creating Schema & Loading Database ---")
    db_dir = "data/db"
    os.makedirs(db_dir, exist_ok=True)
    
    # Connect/Create SQLite Database
    engine = create_engine(f'sqlite:///{db_dir}/bluestock_mf.db')
    
    schema_sql = """
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
    """
    
    os.makedirs("sql", exist_ok=True)
    with open("sql/schema.sql", "w") as f:
        f.write(schema_sql)
        
    # Execute explicit table builds
    with engine.connect() as conn:
        for statement in schema_sql.split(";"):
            if statement.strip():
                conn.execute(text(statement))
                
    # --- SAFE LOAD METHODS BYPASSING PANDAS TO_SQL ---
    with engine.connect() as conn:
        
        # 1. Load Fund Master
        master_files = glob.glob("data/raw/*01_fund_master*.csv")
        if master_files:
            fund_master = pd.read_csv(master_files[0])
            fund_master.columns = fund_master.columns.str.strip()
            
            # Standardize column naming mappings to fit SQL tables
            if 'Scheme Code' in fund_master.columns:
                fund_master.rename(columns={'Scheme Code': 'amfi_code'}, inplace=True)
            elif 'Scheme_Code' in fund_master.columns:
                fund_master.rename(columns={'Scheme_Code': 'amfi_code'}, inplace=True)
                
            # --- FIX: Slice only the exact columns our SQL schema table contains ---
            allowed_columns = ['amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 'risk_category']
            
            # Fallback check in case risk column uses a slightly different name
            if 'risk_category' not in fund_master.columns and 'risk_grade' in fund_master.columns:
                fund_master.rename(columns={'risk_grade': 'risk_category'}, inplace=True)
                
            # Filter the dataframe to keep only the expected schema keys
            fund_master_filtered = fund_master[[col for col in allowed_columns if col in fund_master.columns]]
            
            # Clear table before insertion to prevent duplicate constraints
            conn.execute(text("DELETE FROM dim_fund;"))
            records = fund_master_filtered.to_dict(orient='records')
            if records:
                # Dynamically construct INSERT keys for the filtered columns
                columns = ", ".join(records[0].keys())
                placeholders = ", ".join([f":{k}" for k in records[0].keys()])
                conn.execute(text(f"INSERT INTO dim_fund ({columns}) VALUES ({placeholders})"), records)
            print("-> dim_fund populated successfully with filtered schema columns.")
        # 2. Load Clean NAV History & Dim Date
        if os.path.exists("data/processed/clean_nav.csv"):
            clean_nav = pd.read_csv("data/processed/clean_nav.csv")
            clean_nav['date'] = pd.to_datetime(clean_nav['date'])
            
            # Build and load Date Dimension rows
            unique_dates = pd.to_datetime(clean_nav['date'].unique())
            dim_date_df = pd.DataFrame({
                'date_id': unique_dates.strftime('%Y%m%d'),
                'calendar_date': unique_dates.strftime('%Y-%m-%d'),
                'year': unique_dates.year,
                'month': unique_dates.month,
                'quarter': 'Q' + unique_dates.quarter.astype(str),
                'is_weekday': (unique_dates.dayofweek < 5).astype(int)
            }).drop_duplicates()
            
            conn.execute(text("DELETE FROM dim_date;"))
            date_records = dim_date_df.to_dict(orient='records')
            if date_records:
                conn.execute(text("INSERT INTO dim_date (date_id, calendar_date, year, month, quarter, is_weekday) VALUES (:date_id, :calendar_date, :year, :month, :quarter, :is_weekday)"), date_records)
            print("-> dim_date populated successfully.")

            # Map and load Fact NAV
            clean_nav['date_id'] = clean_nav['date'].dt.strftime('%Y%m%d')
            fact_nav_df = clean_nav[['amfi_code', 'date_id', 'nav']]
            
            conn.execute(text("DELETE FROM fact_nav;"))
            nav_records = fact_nav_df.to_dict(orient='records')
            if nav_records:
                conn.execute(text("INSERT INTO fact_nav (amfi_code, date_id, nav) VALUES (:amfi_code, :date_id, :nav)"), nav_records)
            print("-> fact_nav populated successfully.")

        # 3. Load Clean Transactions
        # 3. Load Clean Transactions
        if os.path.exists("data/processed/clean_transactions.csv"):
            clean_tx = pd.read_csv("data/processed/clean_transactions.csv")
            clean_tx.columns = clean_tx.columns.str.strip()
            
            # --- FIX: Slice only the exact columns our SQL fact_transactions table contains ---
            allowed_tx_columns = [
                'investor_id', 'transaction_date', 'amfi_code', 
                'transaction_type', 'amount_inr', 'state', 'kyc_status'
            ]
            
            # Filter the dataframe to drop extra demographic columns (city, age_group, etc.)
            clean_tx_filtered = clean_tx[[col for col in allowed_tx_columns if col in clean_tx.columns]]
            
            # Clear table before insertion to prevent duplication
            conn.execute(text("DELETE FROM fact_transactions;"))
            tx_records = clean_tx_filtered.to_dict(orient='records')
            if tx_records:
                columns = ", ".join(tx_records[0].keys())
                placeholders = ", ".join([f":{k}" for k in tx_records[0].keys()])
                conn.execute(text(f"INSERT INTO fact_transactions ({columns}) VALUES ({placeholders})"), tx_records)
            print("-> fact_transactions populated successfully with filtered schema columns.")

if __name__ == "__main__":
    build_and_load_db()