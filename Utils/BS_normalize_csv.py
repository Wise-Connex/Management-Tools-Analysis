#!/usr/bin/env python3
"""
CSV Value Normalization Utility for BS_ Files

This script normalizes the values in CSV files using a custom scale where:
- 5 maps to 1000
- 3 maps to 600
- The minimum value in the series maps proportionally
- The maximum value in the series maps proportionally
- Values > 5 are capped at 1000
It only processes files starting with 'BS_' in the dbase-non-indexed folder
and saves normalized values to corresponding files in dbase folder.

Usage:
    python Utils/BS_normalize_csv.py
"""

import pandas as pd
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_bs_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the values column using custom scale where:
    - 5 maps to 1000
    - 3 maps to 600
    - The minimum value in the series maps proportionally
    - The maximum value in the series maps proportionally
    - Values > 5 are capped at 1000
    - Values stay within the actual range of the series
    
    Args:
        df (pd.DataFrame): Input dataframe with dates in first column and values in second column
        
    Returns:
        pd.DataFrame: DataFrame with original dates and normalized values
        
    Raises:
        ValueError: If the input dataframe doesn't have exactly 2 columns
    """
    if len(df.columns) != 2:
        raise ValueError("Input DataFrame must have exactly 2 columns (date and value)")
    
    # Store original column names
    date_col = df.columns[0]
    value_col = df.columns[1]
    
    # Get the values column (second column)
    values = df.iloc[:, 1]
    
    # Find the actual minimum and maximum values in the series
    min_val = values.min()
    max_val = values.max()
    
    # Calculate what the minimum value should map to in the 0-1000 scale
    # Using the same proportion as the 3->600 mapping
    min_scaled = ((min_val - 3) * 400 / 2) + 600
    
    # Calculate what the maximum value should map to
    # If max_val > 5, it should map to 1000
    # If max_val < 5, it should map proportionally
    max_scaled = 1000 if max_val >= 5 else ((max_val - 3) * 400 / 2) + 600
    
    # Initialize normalized values
    normalized_values = pd.Series(index=values.index)
    
    # Handle different ranges
    # 1. Values > 5 become 1000
    # 2. Values between min_val and max_val use linear interpolation
    normalized_values = values.apply(lambda x: 
        1000 if x >= 5 else (
            ((x - min_val) * (max_scaled - min_scaled) / (max_val - min_val) + min_scaled)
        )
    )
    
    # Ensure values stay within the actual range of the series
    normalized_values = normalized_values.clip(min_scaled, max_scaled)
    
    # Round to integers
    normalized_values = normalized_values.round().astype(int)
    
    # Create new dataframe with original column names
    result = pd.DataFrame({
        date_col: df.iloc[:, 0],
        value_col: normalized_values
    })
    
    # Log the scaling information
    logger.info(f"Series min value: {min_val:.2f} -> scaled to: {min_scaled:.0f}")
    logger.info(f"Series max value: {max_val:.2f} -> scaled to: {max_scaled:.0f}")
    logger.info(f"Reference point: 3.00 -> 600")
    logger.info(f"Series max cap: 5.00 -> 1000")
    
    return result

def process_csv_files() -> None:
    """
    Process BS_ CSV files from dbase-non-indexed and save normalized versions to dbase.
    
    Raises:
        ValueError: If either folder doesn't exist
        Exception: For any other processing errors
    """
    # Define source and destination folders (relative to project root)
    source_folder = 'dbase-non-indexed'
    dest_folder = 'dbase'
    
    # Log the paths being used
    logger.info(f"Source folder: {source_folder}")
    logger.info(f"Destination folder: {dest_folder}")
    
    # Ensure both folders exist
    if not os.path.exists(source_folder):
        raise ValueError(f"Source folder {source_folder} does not exist")
    if not os.path.exists(dest_folder):
        raise ValueError(f"Destination folder {dest_folder} does not exist")
    
    # Get list of BS_ CSV files from source folder
    csv_files = [f for f in os.listdir(source_folder) if f.startswith('BS_') and f.endswith('.csv')]
    
    if not csv_files:
        logger.warning(f"No BS_ CSV files found in {source_folder}")
        return
    
    logger.info(f"Found {len(csv_files)} BS_ CSV files to process")
    
    # Process each CSV file
    for filename in csv_files:
        try:
            # Full paths to source and destination files
            source_path = os.path.join(source_folder, filename)
            dest_path = os.path.join(dest_folder, filename)
            
            # Read the CSV file from source
            logger.info(f"Processing {filename}...")
            df = pd.read_csv(source_path)
            
            # Normalize the values
            normalized_df = normalize_bs_scale(df)
            
            # Save the normalized data to destination
            normalized_df.to_csv(dest_path, index=False)
            logger.info(f"Successfully normalized and saved {filename} to {dest_folder}")
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            continue

def main() -> None:
    """
    Main function to run the normalization process.
    """
    try:
        process_csv_files()
        logger.info("Normalization process completed successfully")
    except Exception as e:
        logger.error(f"Error during normalization process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 