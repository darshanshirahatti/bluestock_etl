import os
import json
import requests
import pandas as pd

def fetch_live_nav(scheme_code, filename):
    """Fetches real-time JSON NAV data from mfapi.in and saves it as a raw CSV."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching NAV data from: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Trigger error for bad status codes
        
        data = response.json()
        
        # Metadata parsing
        meta = data.get('meta', {})
        nav_history = data.get('data', [])
        
        # Flatten data to save as a structured CSV
        df = pd.DataFrame(nav_history)
        
        # Attach meta information as standard columns for analytical utility
        df['scheme_code'] = meta.get('scheme_code')
        df['scheme_name'] = meta.get('scheme_name')
        df['fund_house'] = meta.get('fund_house')
        
        # Ensure target directory exists
        os.makedirs("data/raw", exist_ok=True)
        output_path = f"data/raw/{filename}.csv"
        
        df.to_csv(output_path, index=False)
        print(f"Successfully saved {len(df)} records to {output_path}")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Network / API Error for scheme {scheme_code}: {e}")
        return None

def fetch_key_schemes():
    """Fetches operational NAV tracking for the 5 mandated large-cap schemes."""
    schemes = {
        "119551": "sbi_bluechip",
        "120503": "icici_bluechip",
        "118632": "nippon_large_cap",
        "119092": "axis_bluechip",
        "120841": "kotak_bluechip"
    }
    
    print("\n--- Starting Batch Fetch for Bluechip Schemes ---")
    for code, name in schemes.items():
        fetch_live_nav(code, name)

def explore_fund_master(fund_master_path="data/raw/fund_master.csv"):
    """
    Simulates exploring the structural setup of the mutual fund master file.
    Note: Replace logic with your actual fund_master filename once dropped in data/raw.
    """
    if not os.path.exists(fund_master_path):
        print(f"\n[Note] fund_master.csv not found at {fund_master_path}. Skipping internal exploration.")
        return None

    df = pd.read_csv(fund_master_path)
    print("\n" + "="*20 + " FUND MASTER EXPLORATION " + "="*20)
    
    # Unique values checks
    for col in ['fund_house', 'category', 'sub_category', 'risk_grade']:
        if col in df.columns:
            print(f"\nUnique {col.replace('_', ' ').title()}s (Top 10):")
            print(df[col].unique()[:10])
            
    # AMFI Architecture validation notes
    print("\nAMFI Code Architecture Analysis:")
    print(" - Scheme codes serve as unique digital primary keys issued by AMFI.")
    print(" - Format typically presents as a 6-digit identifier (e.g., 125497).")
    return df

def validate_amfi_codes(fund_master_df, nav_history_df):
    """Validates structural relational boundaries between Master files and NAV Data."""
    print("\n" + "="*25 + " DATA QUALITY SUMMARY " + "="*25)
    if fund_master_df is None or nav_history_df is None:
        print("Validation Skipped: Missing active dataframes for comparison metrics.")
        return
        
    master_codes = set(fund_master_df['scheme_code'].unique())
    history_codes = set(nav_history_df['scheme_code'].unique())
    
    missing_in_history = master_codes - history_codes
    
    print(f"Total Unique Schemes in Master: {len(master_codes)}")
    print(f"Total Unique Schemes in Historical Log: {len(history_codes)}")
    
    if len(missing_in_history) == 0:
        print("PASS: Referential Integrity Validated. All codes match cleanly.")
    else:
        print(f"FAIL: Found {len(missing_in_history)} codes in master missing tracking history.")
        print(f"Missing Codes Sample: {list(missing_in_history)[:5]}")

if __name__ == "__main__":
    # Task 4: Fetch HDFC Top 100 Direct live NAV
    hdfc_df = fetch_live_nav("125497", "hdfc_top_100_direct")
    
    # Task 5: Fetch 5 Key Schemes
    fetch_key_schemes()
    
    # Task 6 & 7: Profile and validate (Will check if fund_master.csv exists)
    master_df = explore_fund_master()
    validate_amfi_codes(master_df, hdfc_df)