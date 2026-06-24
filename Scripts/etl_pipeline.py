import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def clean_and_transform_data():
    print("="*20 + " STARTING DATA CLEANING (DAY 2) " + "="*20)
    
    # -------------------------------------------------------------
    # TASK 1: Clean nav_history.csv
    # -------------------------------------------------------------
    nav_path = "data/raw/nav_history.csv"
    if os.path.exists(nav_path):
        print("\nCleaning nav_history.csv...")
        nav_df = pd.read_csv(nav_path)
        
        # Standardize column name just in case
        if 'scheme_code' in nav_df.columns:
            nav_df.rename(columns={'scheme_code': 'amfi_code'}, inplace=True)
            
        # Parse dates & drop explicit duplicates
        nav_df['date'] = pd.to_datetime(nav_df['date'], errors='coerce')
        nav_df.dropna(subset=['date', 'amfi_code'], inplace=True)
        nav_df.drop_duplicates(subset=['amfi_code', 'date'], inplace=True)
        
        # Validate NAV > 0
        nav_df['nav'] = pd.to_numeric(nav_df['nav'], errors='coerce')
        nav_df = nav_df[nav_df['nav'] > 0]
        
        # Sort and Forward-Fill missing NAV values for holidays/weekends per fund group
        nav_df = nav_df.sort_values(by=['amfi_code', 'date'])
        
        # To forward-fill missing dates cleanly, re-index each group to a daily calendar range
        filled_nav_list = []
        for amfi, group in nav_df.groupby('amfi_code'):
            group.set_index('date', inplace=True)
            full_idx = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
            group = group.reindex(full_idx)
            group['amfi_code'] = amfi
            group['nav'] = group['nav'].ffill() # Forward fill missing NAV values
            group = group.reset_index().rename(columns={'index': 'date'})
            filled_nav_list.append(group)
            
        nav_clean_df = pd.concat(filled_nav_list, ignore_index=True)
        print(f"-> nav_history clean. Row count changed from {len(nav_df)} to {len(nav_clean_df)} after daily ffill.")
    else:
        print("[!] Warning: nav_history.csv not found in data/raw/")
        nav_clean_df = pd.DataFrame()

    # -------------------------------------------------------------
    # TASK 2: Clean investor_transactions.csv
    # -------------------------------------------------------------
    tx_path = "data/raw/investor_transactions.csv"
    if os.path.exists(tx_path):
        print("\nCleaning investor_transactions.csv...")
        tx_df = pd.read_csv(tx_path)
        
        if 'scheme_code' in tx_df.columns:
            tx_df.rename(columns={'scheme_code': 'amfi_code'}, inplace=True)
            
        # Format dates
        tx_df['transaction_date'] = pd.to_datetime(tx_df['transaction_date'], errors='coerce')
        tx_df.dropna(subset=['transaction_date'], inplace=True)
        
        # Standardize transaction_type capitalization and white spaces
        tx_df['transaction_type'] = tx_df['transaction_type'].astype(str).str.strip().str.capitalize()
        # Map values neatly to match exact allowed enums
        tx_map = {'Sip': 'SIP', 'Lumpsum': 'Lumpsum', 'Redemption': 'Redemption'}
        tx_df['transaction_type'] = tx_df['transaction_type'].map(tx_map).fillna('Lumpsum')
        
        # Validate amount > 0
        amount_col = 'amount_inr' if 'amount_inr' in tx_df.columns else 'amount'
        tx_df[amount_col] = pd.to_numeric(tx_df[amount_col], errors='coerce')
        tx_df = tx_df[tx_df[amount_col] > 0]
        
        # Check KYC Status
        if 'kyc_status' in tx_df.columns:
            tx_df['kyc_status'] = tx_df['kyc_status'].astype(str).str.strip().str.capitalize()
            tx_df['kyc_status'] = tx_df['kyc_status'].replace({'Verified': 'Verified', 'Pending': 'Pending'})
            
        print(f"-> investor_transactions clean. Validated rows: {len(tx_df)}")
    else:
        print("[!] Warning: investor_transactions.csv not found.")
        tx_df = pd.DataFrame()

    # -------------------------------------------------------------
    # TASK 3: Clean scheme_performance.csv
    # -------------------------------------------------------------
    perf_path = "data/raw/scheme_performance.csv"
    if os.path.exists(perf_path):
        print("\nCleaning scheme_performance.csv...")
        perf_df = pd.read_csv(perf_path)
        
        # Ensure return metrics are numeric
        return_cols = [c for c in perf_df.columns if 'return' in c or 'sharpe' in c or 'sortino' in c or 'alpha' in c or 'beta' in c]
        for col in return_cols:
            perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce').fillna(0.0)
            
        # Check expense ratio column
        exp_col = [c for c in perf_df.columns if 'expense' in c]
        if exp_col:
            ec = exp_col[0]
            perf_df[ec] = pd.to_numeric(perf_df[ec], errors='coerce')
            # Flag anomalies outside range 0.1% to 2.5% (stored as decimal 0.001 to 0.025 or percentage number)
            # Standardizing to assume it is parsed as a normal percentage value if values are > 1
            is_percentage_scale = perf_df[ec].max() > 0.1
            lower_bound = 0.1 if is_percentage_scale else 0.001
            upper_bound = 2.5 if is_percentage_scale else 0.025
            
            perf_df['expense_ratio_anomaly'] = np.where((perf_df[ec] < lower_bound) | (perf_df[ec] > upper_bound), 1, 0)
            print(f"-> scheme_performance clean. Flagged {perf_df['expense_ratio_anomaly'].sum()} expense ratio anomalies.")
    else:
        print("[!] Warning: scheme_performance.csv not found.")
        perf_df = pd.DataFrame()

    # Create processed folder
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/db", exist_ok=True)
    
    # -------------------------------------------------------------
    # TASKS 4 & 5: Star Schema Design & DB Loading
    # -------------------------------------------------------------
    print("\nInitializing SQLite Star Schema Database via SQLAlchemy...")
    engine = create_engine('sqlite:///data/db/bluestock_mf.db')
    
    # Write structural schema directly using engine raw execution bounds
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dim_fund (
            amfi_code TEXT PRIMARY KEY,
            fund_house TEXT,
            scheme_name TEXT,
            category TEXT,
            sub_category TEXT,
            risk_grade TEXT
        );"""))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dim_date (
            date_id TEXT PRIMARY KEY,
            calendar_date TEXT,
            year INTEGER,
            month INTEGER,
            quarter TEXT,
            is_weekday INTEGER
        );"""))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fact_nav (
            amfi_code TEXT,
            date_id TEXT,
            nav REAL,
            PRIMARY KEY(amfi_code, date_id),
            FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code),
            FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
        );"""))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fact_transactions (
            tx_id TEXT PRIMARY KEY,
            investor_id TEXT,
            amfi_code TEXT,
            date_id TEXT,
            transaction_type TEXT,
            amount_inr REAL,
            state TEXT,
            kyc_status TEXT,
            FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code),
            FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
        );"""))

    # Load cleaned data tables into database
    if not nav_clean_df.empty:
        # Load Dim Date records dynamically from the master range
        unique_dates = pd.to_datetime(nav_clean_df['date'].unique())
        date_dim = pd.DataFrame({
            'date_id': unique_dates.strftime('%Y%m%d'),
            'calendar_date': unique_dates.strftime('%Y-%m-%d'),
            'year': unique_dates.year,
            'month': unique_dates.month,
            'quarter': 'Q' + unique_dates.quarter.astype(str),
            'is_weekday': np.where(unique_dates.dayofweek < 5, 1, 0)
        })
        date_dim.drop_duplicates(subset=['date_id']).to_sql('dim_date', con=engine, if_exists='append', index=False)
        
        # Link and save fact tables
        nav_clean_df['date_id'] = nav_clean_df['date'].dt.strftime('%Y%m%d')
        nav_clean_df[['amfi_code', 'date_id', 'nav']].to_sql('fact_nav', con=engine, if_exists='append', index=False)

    # Map Fund Master info directly to dimensional setup
    master_file = "data/raw/fund_master.csv"
    if os.path.exists(master_file):
        f_master = pd.read_csv(master_file)
        if 'Scheme Code' in f_master.columns: f_master.rename(columns={'Scheme Code': 'amfi_code'}, inplace=True)
        if 'amfi_code' in f_master.columns:
            f_master.to_sql('dim_fund', con=engine, if_exists='replace', index=False)
            
    print("[Success] Data engineering extraction and schema database load complete.")

from sqlalchemy import text
if __name__ == "__main__":
    clean_and_transform_data()