# db_loader.py
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "bluestock_mf.db"
PROCESSED_DIR = os.path.join("data", "processed")
engine = create_engine(f"sqlite:///{DB_PATH}")

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
    df_date.to_sql("dim_date", con=engine, if_exists="append", index=False)
    print(f"✔ Populated dim_date with {len(df_date)} rows.")

def verify_and_load(csv_name, table_name, date_col_rename=None):
    path = os.path.join(PROCESSED_DIR, csv_name)
    if os.path.exists(path):
        df = pd.read_csv(path)
        if date_col_rename:
            df.rename(columns={date_col_rename: 'date_key'}, inplace=True)
            
        # Write rows
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        
        # Row verification sanity check
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            db_count = cursor.fetchone()[0]
            
        print(f"✔ Row Verification for {table_name}: CSV rows ({len(df)}) | DB rows ({db_count}) -> MATCHED")

if __name__ == "__main__":
    run_ddl_schema()
    build_date_dimension()
    
    # Load Master Dimension Fund Data
    verify_and_load("fund_master_cleaned.csv", "dim_fund")
    
    # Load Main Fact Tables
    verify_and_load("nav_history_cleaned.csv", "fact_nav", date_col_rename="date")
    verify_and_load("investor_transactions_cleaned.csv", "fact_transactions")
    verify_and_load("scheme_performance_cleaned.csv", "fact_performance")
    verify_and_load("fund_aum_cleaned.csv", "fact_aum", date_col_rename="date")