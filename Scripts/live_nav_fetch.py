import os
import requests
import glob
import pandas as pd

def fetch_live_nav(scheme_code, filename):
    """Fetches real-time JSON NAV data from mfapi.in and saves it as a raw CSV."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching NAV data from: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Trigger error for bad status codes
        
        data = response.json()
        
        # Metadata parsing
        meta = data.get('meta', {})
        nav_history = data.get('data', [])
        
        if not nav_history:
            print(f"Warning: No historical data returned for scheme {scheme_code}")
            return None
            
        # Flatten data to save as a structured CSV
        df = pd.DataFrame(nav_history)
        
        # Attach meta information as standard columns for analytical utility
        df['scheme_code'] = str(meta.get('scheme_code', scheme_code))
        df['scheme_name'] = meta.get('scheme_name', '')
        df['fund_house'] = meta.get('fund_house', '')
        
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
    Explores the structural setup of the mutual fund master file.
    Dynamically searches for any file containing 'fund_master' in the data/raw folder.
    """
    target_path = None
    
    # 1. Check the default path
    if os.path.exists(fund_master_path):
        target_path = fund_master_path
    else:
        # 2. Dynamic Search: Look for any CSV with 'fund_master' in its name inside data/raw/
        search_pattern = os.path.join("data", "raw", "*fund_master*.csv")
        found_files = glob.glob(search_pattern)
        
        if found_files:
            target_path = found_files[0] # Grab the first match found
        else:
            # 3. Last Resort: Search the entire root folder just in case it was placed outside data/raw/
            backup_pattern = os.path.join("**", "*fund_master*.csv")
            found_files_backup = glob.glob(backup_pattern, recursive=True)
            if found_files_backup:
                target_path = found_files_backup[0]

    if not target_path:
        print(f"\n[!] ALERT: Could not find any fund master CSV file on your computer.")
        print(f"Please ensure you have copied the provided '01_fund_master.csv' file into your 'data/raw/' folder.")
        return None

    print(f"\n[Success] Found fund master file at: {target_path}")
    df = pd.read_csv(target_path)
    print("\n" + "="*20 + " FUND MASTER EXPLORATION " + "="*20)
    
    # Clean column names by stripping trailing whitespaces/newlines
    df.columns = df.columns.str.strip()
    
    # Unique values checks
    for col in ['fund_house', 'category', 'sub_category', 'risk_grade', 'risk_category']:
        if col in df.columns:
            print(f"\nUnique {col.replace('_', ' ').title()}s (Top 10):")
            print(df[col].dropna().unique()[:10])
            
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
        
    # Standardize column searching to accommodate variations in naming (amfi_code, AMFI Code, etc.)
    master_col = None
    for col in ['amfi_code', 'AMFI Code', 'scheme_code', 'Scheme Code']:
        if col in fund_master_df.columns:
            master_col = col
            break
            
    if master_col is None:
        print(f"Error: Could not find AMFI identifier column in Fund Master. Found columns: {list(fund_master_df.columns)}")
        return

    # Extract unique codes and turn them to strings for safe matching
    master_codes = set(fund_master_df[master_col].astype(str).str.strip().unique())
    history_codes = set(nav_history_df['scheme_code'].astype(str).str.strip().unique())
    
    missing_in_history = master_codes - history_codes
    
    print(f"Total Unique Schemes in Master File: {len(master_codes)}")
    print(f"Total Unique Schemes in API Download: {len(history_codes)}")
    
    if len(missing_in_history) == 0:
        print("PASS: Referential Integrity Validated. All codes match cleanly.")
    else:
        print(f"Data Profiling Note: Found {len(missing_in_history)} codes in master file that are not in this single API sample download.")
        print(f"Sample of Master Codes: {list(master_codes)[:5]}")

if __name__ == "__main__":
    # Task 4: Fetch HDFC Top 100 Direct live NAV
    hdfc_df = fetch_live_nav("125497", "hdfc_top_100_direct")
    
    # Task 5: Fetch 5 Key Schemes
    fetch_key_schemes()
    
    # Task 6 & 7: Profile and validate (Checks fund master)
    master_df = explore_fund_master()
    validate_amfi_codes(master_df, hdfc_df)