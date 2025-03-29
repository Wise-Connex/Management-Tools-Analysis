#!/usr/bin/env python3
"""
CSV Value Normalization Utility for BS_ Files using Z-scores

This script normalizes the values in CSV files using Z-scores where:
- Each value is transformed to its Z-score: (x - mean) / standard_deviation
- The Z-scores are then scaled to a 0-100 range for consistency
- Only processes files starting with 'BS_' in the dbase-non-indexed folder
- Saves normalized values to corresponding files in dbase folder.

Usage:
    python Utils/BS_Z-scores_normalize_csv.py
"""

import pandas as pd
import os
import sys
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_bs_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the values column using Z-scores and scale to 0-100 range.
    
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
    
    # Calculate Z-scores
    z_scores = (values - values.mean()) / values.std()
    
    # Scale Z-scores to 0-100 range
    # Formula: (z_score - min_z) / (max_z - min_z) * 100
    min_z = z_scores.min()
    max_z = z_scores.max()
    
    # Handle case where all values are identical (std = 0)
    if max_z == min_z:
        logger.warning("All values are identical. Setting all normalized values to 50.")
        normalized_values = pd.Series(50, index=values.index)
    else:
        normalized_values = ((z_scores - min_z) / (max_z - min_z)) * 100
    
    # Round to integers like in Google Trends
    normalized_values = normalized_values.round().astype(int)
    
    # Create new dataframe with original column names
    result = pd.DataFrame({
        date_col: df.iloc[:, 0],
        value_col: normalized_values
    })
    
    # Log the transformation information
    logger.info(f"Original values - Mean: {values.mean():.2f}, Std: {values.std():.2f}")
    logger.info(f"Z-scores - Min: {min_z:.2f}, Max: {max_z:.2f}")
    logger.info(f"Normalized values - Min: {normalized_values.min():.0f}, Max: {normalized_values.max():.0f}")
    
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