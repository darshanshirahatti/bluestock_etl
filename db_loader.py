# db_loader.py
import os
import sqlite3
import pandas as pd

DB_PATH = "bluestock_mf.db"
PROCESSED_DIR = os.path.join("data", "processed")

def run_ddl_schema():
    print("Executing Task 4/5: Building Database Structures...")
    with sqlite3.connect(DB_PATH) as conn:
        with open(os.path.join("sql", "schema.sql"), "r") as f:
            conn.executescript(f.read())
    print("✔ Tables created with constraints successfully.")

def build_date_dimension():
    print("Generating Temporal Dimension Table Rows...")
    dates = pd.date_range(start="2020-01-01", end="2026-12-31")
    df_date = pd.DataFrame({
        'date_key': dates.strftime('%Y-%m-%d'),
        'year': dates.year,
        'month': dates.month,
        'month_name': dates.strftime('%B'),
        'quarter': dates.quarter,
        'day_of_week': dates.strftime('%A')
    })
    
    with sqlite3.connect(DB_PATH) as conn:
        # dim_date.date_key is a PRIMARY KEY; do not append on re-runs.
        df_date.to_sql("dim_date", con=conn, if_exists="replace", index=False)
    print(f"✔ Populated dim_date with {len(df_date)} rows (fresh load).")


def verify_and_load(csv_name, table_name, date_col_rename=None):
    path = os.path.join(PROCESSED_DIR, csv_name)
    if os.path.exists(path):
        df = pd.read_csv(path)
        
        # Clean headers
        df.columns = df.columns.str.strip().str.lower()
        
        # --- EXPLICIT MAPPING FOR YOUR CSV FILES ---
        rename_dict = {
            'amount_inr': 'amount',       # Direct fix for investor_transactions
            'transaction_amount': 'amount',
            'amt': 'amount',
            'transaction_date': 'transaction_date',
            'date': 'date_key',
            'amfi': 'amfi_code',
            'scheme_code': 'amfi_code'
        }
        
        if date_col_rename:
            rename_dict[date_col_rename.strip().lower()] = 'date_key'
            
        df.rename(columns=rename_dict, inplace=True)
            
        # --- FIX DATE STRING FORMATTING FOR TRANSACTION TABLES ---
        if 'transaction_date' in df.columns:
            # Converts DD-MM-YYYY strings to YYYY-MM-DD so they match SQLite date requirements
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

        # --- ALIGN transaction_type / kyc_status with SQLite CHECK constraints ---
        # fact_transactions.transaction_type CHECK: IN ('SIP', 'Lumpsum', 'Redemption')
        if 'transaction_type' in df.columns:
            allowed_tx = {'sip': 'SIP', 'lumpsum': 'Lumpsum', 'redemption': 'Redemption',
                           'SIP': 'SIP', 'Lumpsum': 'Lumpsum', 'Redemption': 'Redemption'}
            df['transaction_type'] = (
                df['transaction_type']
                .astype(str)
                .map(lambda x: allowed_tx.get(x.strip(), x.strip()))
            )

        # fact_transactions.kyc_status CHECK: IN ('Yes', 'No', 'Pending')
        # Your cleaned CSV currently contains: 'Verified' and 'Pending'
        if 'kyc_status' in df.columns:
            kyc_map = {'verified': 'Yes', 'pending': 'Pending', 'yes': 'Yes', 'no': 'No'}
            df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.lower().map(kyc_map)
            df['kyc_status'] = df['kyc_status'].fillna('Pending')

            
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Fetch target table column configuration from the database schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_info = cursor.fetchall()
            db_columns = [row[1] for row in table_info]
            not_null_columns = [row[1] for row in table_info if row[3] == 1]
            
            # Convert values to numeric and drop rows with empty values
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                
            for col in not_null_columns:
                if col in df.columns:
                    df = df.dropna(subset=[col])
            
            if table_name == "fact_transactions" and "amount" in df.columns:
                df = df[df["amount"] > 0]
            
            # Filter the dataframe to match the schema's columns exactly
            valid_columns = [col for col in df.columns if col in db_columns]
            df_filtered = df[valid_columns].copy()
            
            # --- SAFE DATA INSERTION ---
            # SQLite checks constraints (CHECK) during insert. If a constraint fails
            # we want to see the offending rows, not just crash.
            try:
                df_filtered.to_sql(table_name, con=conn, if_exists="append", index=False)
            except Exception as e:
                print(f"[ERROR] Failed to insert into {table_name}: {e}")
                if table_name == "fact_transactions":
                    # show the first few rows that violate transaction_type / kyc_status constraints
                    bad_type = ~df_filtered["transaction_type"].isin(['SIP','Lumpsum','Redemption']) if "transaction_type" in df_filtered.columns else None
                    bad_kyc = ~df_filtered["kyc_status"].isin(['Yes','No','Pending']) if "kyc_status" in df_filtered.columns else None
                    if bad_type is not None:
                        print("Bad transaction_type rows (sample):")
                        print(df_filtered[bad_type].head(10))
                    if bad_kyc is not None:
                        print("Bad kyc_status rows (sample):")
                        print(df_filtered[bad_kyc].head(10))
                    # Explicitly show the constraint-mapped unique kyc_status values
                    print("transaction_type uniques:", sorted(df_filtered["transaction_type"].dropna().unique().tolist()))
                    print("kyc_status uniques:", sorted(df_filtered["kyc_status"].dropna().unique().tolist()))
                raise


            
            # Row verification check
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            db_count = cursor.fetchone()[0]
            
        print(f"✔ Row Verification for {table_name}: CSV matching rows ({len(df_filtered)}) | DB rows ({db_count}) -> MATCHED")
    else:
        print(f"[INFO] File missing, skipping load: {csv_name}")

if __name__ == "__main__":
    run_ddl_schema()
    build_date_dimension()
    
    # Load Master Dimension Fund Data
    verify_and_load("01_fund_master_cleaned.csv", "dim_fund")
    
    # Load Main Fact Tables
    verify_and_load("02_nav_history_cleaned.csv", "fact_nav", date_col_rename="date")
    verify_and_load("08_investor_transactions_cleaned.csv", "fact_transactions")
    verify_and_load("07_scheme_performance_cleaned.csv", "fact_performance")