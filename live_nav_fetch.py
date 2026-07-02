import os
import json
import requests
import pandas as pd
from datetime import datetime

# API Base URL
BASE_URL = "https://api.mfapi.in/mf/"

# Scheme Mapping
SCHEMES = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

def fetch_and_save_nav(scheme_code, scheme_name):
    url = f"{BASE_URL}{scheme_code}"
    print(f"Fetching data for {scheme_name} ({scheme_code})...")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract meta information and historical NAV data
            meta = data.get("meta", {})
            nav_data = data.get("data", [])
            
            if not nav_data:
                print(f"No NAV data found for {scheme_name}")
                return
            
            # Convert NAV array into a DataFrame
            df = pd.DataFrame(nav_data)
            
            # Inject metadata into columns for flat CSV structure
            df["scheme_code"] = scheme_code
            df["scheme_name"] = meta.get("scheme_name", scheme_name)
            df["fund_house"] = meta.get("fund_house", "Unknown")
            df["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Reorder columns cleanly
            df = df[["scheme_code", "scheme_name", "fund_house", "date", "nav", "fetched_at"]]
            
            # Save raw file
            output_path = os.path.join("data", "raw", f"nav_{scheme_code}.csv")
            df.to_csv(output_path, index=False)
            print(f"Successfully saved raw CSV to: {output_path}")
            
        else:
            print(f"Failed API request for {scheme_code}. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred while fetching {scheme_code}: {str(e)}")

def main():
    print("="*60)
    print("MUTUAL FUND LIVE NAV INGESTION")
    print("="*60)
    
    # Ensure data/raw directory exists
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)
    
    # Loop through all schemes and download data
    for code, name in SCHEMES.items():
        fetch_and_save_nav(code, name)

if __name__ == "__main__":
    main()