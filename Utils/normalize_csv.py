#!/usr/bin/env python3
"""
CSV Value Normalization Utility

This script normalizes the values in CSV files using Google Trends style indexation
where the maximum value becomes 100 and other values are scaled proportionally.
It reads CSV files from 'dbase-non-indexed' folder and saves normalized values to
corresponding files in 'dbase' folder while keeping the exact original column names.

Usage:
    python Utils/normalize_csv.py
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

def normalize_to_100(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the values column using Google Trends style indexation where
    the maximum value becomes 100 and other values are scaled proportionally.
    
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
    
    # Calculate maximum value
    max_val = values.max()
    
    # Handle case where all values are zero
    if max_val == 0:
        logger.warning("All values are zero. Setting all normalized values to 50.")
        normalized_values = pd.Series(50, index=values.index)
    else:
        # Normalize to 0-100 scale using the formula: (x / max) * 100
        normalized_values = (values / max_val) * 100
    
    # Round to integers like in Google Trends
    normalized_values = normalized_values.round().astype(int)
    
    # Create new dataframe with original column names
    result = pd.DataFrame({
        date_col: df.iloc[:, 0],
        value_col: normalized_values
    })
    
    return result

def process_csv_files() -> None:
    """
    Process all CSV files from dbase-non-indexed and save normalized versions to dbase.
    
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
    
    # Get list of CSV files from source folder
    csv_files = [f for f in os.listdir(source_folder) if f.endswith('.csv')]
    
    if not csv_files:
        logger.warning(f"No CSV files found in {source_folder}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
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
            normalized_df = normalize_to_100(df)
            
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