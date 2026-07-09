import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def generate_peer_group_recommendations(target_amfi, recommendations_count=3):
    """
    Identifies similar peer funds within matching investment fields,
    ranking alternatives by cost efficiency.
    """
    master_path = PROCESSED_DIR / "01_fund_master_cleaned.csv"
    metrics_path = BASE_DIR / "fund_scorecard.csv"
    
    if not (master_path.exists() and metrics_path.exists()):
        return "❌ Mandatory analytics source data matrices missing from execution path."

    # Load processing tables
    df_master = pd.read_csv(master_path)
    df_score = pd.read_csv(metrics_path)
    
    # FIX: Drop 'scheme_name' from df_score before merging so it doesn't create _x and _y suffixes
    if 'scheme_name' in df_score.columns:
        df_score = df_score.drop(columns=['scheme_name'])
    
    # Merge properties cleanly
    df_pool = df_master.merge(df_score, on='amfi_code')
    
    # Isolate target fund context parameters
    target_fund = df_pool[df_pool['amfi_code'] == int(target_amfi)]
    if target_fund.empty:
        return f"❌ Target reference code '{target_amfi}' not present in repository database."
        
    target_category = target_fund['category'].values[0]
    
    # Filter peer group down to matching asset allocation classes (excluding itself)
    peer_universe = df_pool[
        (df_pool['category'] == target_category) & 
        (df_pool['amfi_code'] != int(target_amfi))
    ].copy()
    
    # Sort peer assets based on maximum returns and lowest underlying expense burdens
    recommendations = peer_universe.sort_values(
        by=['Composite_Score', 'expense_ratio_pct'], 
        ascending=[False, True]
    ).head(recommendations_count)
    
    return recommendations[['amfi_code', 'scheme_name', 'Composite_Score', 'expense_ratio_pct']]

if __name__ == "__main__":
    # Sample Test Target Execution
    print("🔍 Testing content recommendation calculations...")
    test_run = generate_peer_group_recommendations(target_amfi=125497)
    print(test_run)