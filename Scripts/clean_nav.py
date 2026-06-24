import os
import pandas as pd

def clean_nav_data():
    raw_path = "data/raw/02_nav_history.csv"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    print("--- Task 1: Cleaning nav_history.csv ---")
    df = pd.read_csv(raw_path)
    
    # 1. Parse dates to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'amfi_code'])
    
    # 2. Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # 3. Validate NAV > 0
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    df = df[df['nav'] > 0]
    
    # 4. Sort by amfi_code + date
    df = df.sort_values(by=['amfi_code', 'date'])
    
    # 5. Forward-fill missing NAV for holidays/weekends per fund group
    filled_groups = []
    for amfi, group in df.groupby('amfi_code'):
        group = group.set_index('date')
        full_idx = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
        group = group.reindex(full_idx)
        group['amfi_code'] = amfi
        group['nav'] = group['nav'].ffill() # Forward-fill
        filled_groups.append(group.reset_index().rename(columns={'index': 'date'}))
        
    final_df = pd.concat(filled_groups, ignore_index=True)
    
    output_path = os.path.join(processed_dir, "clean_nav.csv")
    final_df.to_csv(output_path, index=False)
    print(f"[Success] Cleaned NAV history saved to {output_path}. Total rows: {len(final_df)}\n")

if __name__ == "__main__":
    clean_nav_data()