import os
import pandas as pd

# Define the data directory
RAW_DATA_DIR = os.path.join("data", "raw")

# List of your 10 CSV files (Update names to match your actual files)
csv_files = [
    "01_fund_master.csv", 
    "02_nav_history.csv", 
    # "dataset3.csv", "dataset4.csv", ... add all 10 here
]

def inspect_datasets():
    print("="*60)
    print("STARTING DATA INGESTION & QUALITY CHECK")
    print("="*60)
    
    for file_name in csv_files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        
        if not os.path.exists(file_path):
            print(f"\n[WARNING] File not found: {file_name}. Skipping...")
            continue
            
        print(f"\n--- Processing: {file_name} ---")
        
        # Load dataset
        df = pd.read_csv(file_path)
        
        # 1. Print Shape
        print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # 2. Print Data Types
        print("\nData Types:")
        print(df.dtypes)
        
        # 3. Print Head
        print("\nFirst 3 Rows:")
        print(df.head(3))
        
        # 4. Basic Quick Anomaly Detection
        print("\nAnomalies & Data Quality Notes:")
        missing_vals = df.isnull().sum()
        has_missing = missing_vals[missing_vals > 0]
        
        if not has_missing.empty:
            print("  - Missing values found:")
            for col, count in has_missing.items():
                print(f"    * Column '{col}': {count} missing values")
        else:
            print("  - No missing values detected.")
            
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            print(f"  - [ALERT] {duplicate_count} duplicate rows detected!")
            
        print("-" * 40)

if __name__ == "__main__":
    inspect_datasets()