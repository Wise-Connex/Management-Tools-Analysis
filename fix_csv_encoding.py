#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV Encoding and Delimiter Fix

This script fixes encoding and delimiter issues in CSV files. 
It handles files that use semicolons as delimiters instead of commas
and converts files from Latin-1/Windows-1252 encoding to UTF-8.
"""

import os
import csv
import pandas as pd
import chardet
from pathlib import Path

# Directory containing the CSV files
CSV_DIR = "pub-assets"

# List of CSV files to process
CSV_FILES = [
    "BS-Portada.csv",
    "BU-Portada.csv",
    "GT-Portada.csv",
    "CR-Portada.csv",
    "GB-Portada.csv"
]

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet."""
    with open(file_path, 'rb') as f:
        # Read a sample of the file to detect encoding
        raw_data = f.read(10000)  # Read a chunk to detect encoding
        result = chardet.detect(raw_data)
        return result['encoding']

def process_csv_file(file_path, output_path=None):
    """
    Process a CSV file to fix encoding and delimiter issues.
    
    Args:
        file_path: Path to the input CSV file
        output_path: Path to save the fixed CSV (if None, overwrites the original)
    
    Returns:
        DataFrame with the processed data
    """
    if output_path is None:
        output_path = file_path
        
    # Step 1: Detect the file encoding
    detected_encoding = detect_encoding(file_path)
    print(f"Detected encoding for {file_path}: {detected_encoding}")
    
    try:
        # Step 2: Read the file using pandas with the detected encoding and semicolon delimiter
        df = pd.read_csv(file_path, sep=';', encoding=detected_encoding, header=0)
        
        # Step 3: Save the file with UTF-8 encoding and semicolon delimiter
        # Preserve semicolon as delimiter since it appears to be the standard format for these files
        df.to_csv(output_path, sep=';', encoding='utf-8', index=False)
        
        print(f"Successfully processed {file_path} and saved to {output_path}")
        return df
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
        # Fallback method using csv module
        try:
            # Try alternate encodings if detection failed
            encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1'] 
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.reader(f, delimiter=';')
                        rows = list(reader)
                    
                    with open(output_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f, delimiter=';')
                        writer.writerows(rows)
                    
                    print(f"Successfully processed {file_path} using fallback method with {encoding} encoding")
                    return pd.DataFrame(rows[1:], columns=rows[0])
                except Exception:
                    continue
                    
            print(f"All fallback attempts failed for {file_path}")
            return None
            
        except Exception as e2:
            print(f"Fallback method also failed for {file_path}: {e2}")
            return None

def main():
    """Main function to process all CSV files."""
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(CSV_DIR, "backup")
    os.makedirs(backup_dir, exist_ok=True)
    
    for csv_file in CSV_FILES:
        file_path = os.path.join(CSV_DIR, csv_file)
        
        # Create backup of original file
        backup_path = os.path.join(backup_dir, csv_file)
        if not os.path.exists(backup_path):
            try:
                with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                print(f"Created backup of {csv_file} at {backup_path}")
            except Exception as e:
                print(f"Failed to create backup of {csv_file}: {e}")
                continue
        
        # Process the file
        df = process_csv_file(file_path)
        
        if df is not None:
            # Display a sample of the processed data
            print(f"\nSample of processed data from {csv_file}:")
            print(df.head(2))
            print()

if __name__ == "__main__":
    main() 