#!/usr/bin/env python3
"""
CSV Value Normalization Utility

This script normalizes the values in CSV files to a 0-100 scale while preserving
the relative relationships between values. It processes all CSV files in a specified
folder, overwriting the original files with normalized values while keeping the exact
original column names.

Usage:
    python normalize_csv.py [folder_path]

Arguments:
    folder_path (optional): Path to the folder containing CSV files.
                          Defaults to 'dbase' if not specified.
"""

import pandas as pd
import os
import sys
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_to_100(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the values column to a 0-100 scale using min-max normalization.
    
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
    
    # Calculate min and max
    min_val = values.min()
    max_val = values.max()
    
    # Handle case where all values are the same
    if max_val == min_val:
        logger.warning("All values are identical. Setting all normalized values to 50.")
        normalized_values = pd.Series(50, index=values.index)
    else:
        # Normalize to 0-100 scale using the formula: ((x - min) / (max - min)) * 100
        normalized_values = ((values - min_val) / (max_val - min_val)) * 100
    
    # Create new dataframe with original column names
    result = pd.DataFrame({
        date_col: df.iloc[:, 0],
        value_col: normalized_values
    })
    
    return result

def process_csv_files(folder_path: str) -> None:
    """
    Process all CSV files in the specified folder.
    
    Args:
        folder_path (str): Path to the folder containing CSV files
        
    Raises:
        ValueError: If the folder doesn't exist
        Exception: For any other processing errors
    """
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder {folder_path} does not exist")
    
    # Get list of CSV files
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        logger.warning(f"No CSV files found in {folder_path}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files to process")
    
    # Process each CSV file
    for filename in csv_files:
        try:
            # Full path to the file
            file_path = os.path.join(folder_path, filename)
            
            # Read the CSV file
            logger.info(f"Processing {filename}...")
            df = pd.read_csv(file_path)
            
            # Normalize the values
            normalized_df = normalize_to_100(df)
            
            # Save the normalized data back to the original file
            normalized_df.to_csv(file_path, index=False)
            logger.info(f"Successfully normalized and saved {filename}")
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            continue

def main(folder_path: Optional[str] = None) -> None:
    """
    Main function to run the normalization process.
    
    Args:
        folder_path (Optional[str]): Path to the folder containing CSV files
    """
    # Use default folder if none specified
    if folder_path is None:
        folder_path = 'dbase'
    
    try:
        process_csv_files(folder_path)
        logger.info("Normalization process completed successfully")
    except Exception as e:
        logger.error(f"Error during normalization process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Get folder path from command line argument if provided
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(folder_path) 