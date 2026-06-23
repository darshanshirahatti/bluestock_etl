import os
import pandas as pd

def load_and_profile_data(data_directory="data/raw"):
    """Loads all CSV datasets from the target directory and prints structural profiles."""
    if not os.path.exists(data_directory):
        print(f"Error: Directory '{data_directory}' does not exist.")
        return

    # Dynamically find all CSV files in the raw data folder
    csv_files = [f for f in os.listdir(data_directory) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {data_directory}. Please drop your 10 datasets there.")
        return

    print(f"Found {len(csv_files)} datasets. Starting profiling...\n")
    print("=" * 60)

    for file in csv_files:
        file_path = os.path.join(data_directory, file)
        print(f"PROFILING DATASET: {file}")
        print("=" * 60)
        
        try:
            # Load dataset
            df = pd.read_csv(file_path)
            
            # 1. Shape
            print(f"Shape (Rows, Columns): {df.shape}")
            print("-" * 40)
            
            # 2. Data Types
            print("Data Types (.dtypes):")
            print(df.dtypes)
            print("-" * 40)
            
            # 3. Head (First 3 rows for brief preview)
            print("Sample Data (.head(3)):")
            print(df.head(3))
            print("-" * 40)
            
            # 4. Immediate Anomaly Check
            print("Anomalies / Data Quality Notes:")
            missing_values = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            
            if missing_values > 0:
                print(f" - [!] Warning: Found {missing_values} missing values.")
            else:
                print(" - No missing values detected.")
                
            if duplicate_rows > 0:
                print(f" - [!] Warning: Found {duplicate_rows} exact duplicate rows.")
            else:
                print(" - No duplicate rows detected.")
                
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
            
        print("=" * 60 + "\n")

if __name__ == "__main__":
    # Example execution: drops into your raw folder
    load_and_profile_data()