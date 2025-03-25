import pandas as pd
import glob
import os
import sys
from pathlib import Path

def convert_to_scientific():
    # Get the project root directory (parent of Utils)
    project_root = Path(__file__).parent.parent
    
    # Get all CSV files in the directory
    csv_path = project_root / 'output' / 'csv_reports' / 'CR_mod'
    csv_files = glob.glob(str(csv_path / '*.csv'))
    
    if not csv_files:
        print("No CSV files found in output/csv_reports/CR_mod/")
        return
    
    for file in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Get the name of the second column
            second_col = df.columns[1]
            
            # Create a copy of the DataFrame
            df_modified = df.copy()
            
            # Convert to scientific notation with 2 decimal places
            df_modified[second_col] = df_modified[second_col].apply(lambda x: '{:.2E}'.format(x))
            
            # Preview the changes for the first few rows
            print(f"\nProcessing: {os.path.basename(file)}")
            print("First few rows before:")
            print(df.head()[second_col])
            print("\nFirst few rows after:")
            print(df_modified.head()[second_col])
            
            # Save with the same filename (overwrites the original)
            df_modified.to_csv(file, index=False)
            print(f"\nSaved changes to: {os.path.basename(file)}")
            
        except Exception as e:
            print(f"Error processing {os.path.basename(file)}: {str(e)}")

if __name__ == "__main__":
    convert_to_scientific() 