#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV Consolidation Script

This script consolidates multiple CSV files into one, changes the separator from semicolon to comma,
and adds a 'File' column with paths to corresponding image files.
"""

import pandas as pd
import os

def process_csv_files():
    """
    Process and consolidate CSV files from pub-assets directory.
    
    Returns:
        DataFrame: The consolidated data
    """
    # Define the paths to your CSV files - adjusted for script being in pub-assets folder
    file_paths = [
        'BS-Portada.csv',
        'BU-Portada.csv',
        'CR-Portada.csv',
        'GB-Portada.csv',
        'GT-Portada.csv'
    ]
    
    # Create an empty list to store all dataframes
    all_dfs = []
    
    # Process each file
    for file_path in file_paths:
        print(f"Processing {file_path}...")
        
        # Read the CSV file with semicolon separator and UTF-8 encoding
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback to Latin-1 encoding if UTF-8 fails
            df = pd.read_csv(file_path, sep=';', encoding='latin1')
            print(f"Used Latin-1 encoding for {file_path}")
        
        # Add a column indicating the source file (without extension and path)
        source_file = os.path.basename(file_path).split('.')[0]
        df['Source'] = source_file
        
        # Add the dataframe to our list
        all_dfs.append(df)
    
    # Concatenate all dataframes into one
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Now, create the File column based on the Cód column WITH pub-assets prefix
    # Since we're now in the pub-assets folder, we don't need to include it in the path
    combined_df['File'] = combined_df['Cód'].apply(
        lambda x: f"{x.split('-')[1]}-Portada/{int(x.split('-')[0])}.png" if '-' in x else ""
    )
    
    # Sort by Nro. if needed
    combined_df = combined_df.sort_values(by='Nro.')
    
    # Save the combined DataFrame to a new CSV file with comma separator
    # Changed filename to portada-combined.csv
    output_path = 'portada-combined.csv'
    combined_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Combined data saved to {output_path}")
    
    # Display sample of the data
    print("\nSample of combined data:")
    print(combined_df.head(3))
    
    return combined_df

if __name__ == "__main__":
    process_csv_files() 