import os
import pandas as pd
import numpy as np

def clean_performance_data():
    raw_path = "data/raw/07_scheme_performance.csv"
    output_path = "data/processed/clean_performance.csv"
    
    print("--- Task 3: Cleaning scheme_performance.csv ---")
    df = pd.read_csv(raw_path)
    
    # 1. Validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
    for col in return_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    # 2. Check and flag expense_ratio range (0.1% to 2.5%)
    if 'expense_ratio_pct' in df.columns:
        df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
        # Flag anomalies outside standard limits
        df['expense_ratio_anomaly'] = np.where(
            (df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5), 1, 0
        )
    
    df.to_csv(output_path, index=False)
    print(f"[Success] Cleaned performance saved to {output_path}.\n")

if __name__ == "__main__":
    clean_performance_data()