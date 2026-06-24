import os
import pandas as pd

def clean_transaction_data():
    raw_path = "data/raw/08_investor_transactions.csv"
    output_path = "data/processed/clean_transactions.csv"
    
    print("--- Task 2: Cleaning investor_transactions.csv ---")
    df = pd.read_csv(raw_path)
    
    # 1. Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df = df.dropna(subset=['transaction_date'])
    
    # 2. Standardize transaction_type values
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip().str.upper()
    # Map any variants cleanly
    tx_map = {'SIP': 'SIP', 'LUMPSUM': 'Lumpsum', 'REDEMPTION': 'Redemption'}
    df['transaction_type'] = df['transaction_type'].map(tx_map).fillna('Lumpsum')
    
    # 3. Validate amount > 0
    df['amount_inr'] = pd.to_numeric(df['amount_inr'], errors='coerce')
    df = df[df['amount_inr'] > 0]
    
    # 4. Check KYC status enum values (Verified / Pending)
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.capitalize()
    df.loc[~df['kyc_status'].isin(['Verified', 'Pending']), 'kyc_status'] = 'Pending'
    
    df.to_csv(output_path, index=False)
    print(f"[Success] Cleaned transactions saved to {output_path}. Total rows: {len(df)}\n")

if __name__ == "__main__":
    clean_transaction_data()