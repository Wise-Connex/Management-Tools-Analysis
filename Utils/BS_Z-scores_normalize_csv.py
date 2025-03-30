#!/usr/bin/env python3
"""
CSV Value Normalization Utility for BS_ Files using Z-scores

This script normalizes the values in CSV files using Z-scores where:
- Each value is transformed to its Z-score using fixed population parameters:
  - Population mean = 3
  - Population standard deviation = 0.891609
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

# Fixed population parameters for Z-score calculation
POPULATION_MEAN = 3.0
POPULATION_STD = 0.891609

def normalize_bs_scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the values column using Z-scores with fixed population parameters
    and scale to a moderate range for better amplitude. Only uses 0 in the output 
    if it was present in the original data.
    
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
    
    # Check if zero exists in original data
    has_zero = 0 in values.values
    
    # Calculate Z-scores using fixed population parameters
    z_scores = (values - POPULATION_MEAN) / POPULATION_STD
    
    # Scale Z-scores with factor of 22 for better amplitude
    normalized_values = 50 + (z_scores * 22)  # Each std dev = 22 points
    
    # Clip values to ensure they stay within 0-100
    normalized_values = np.clip(normalized_values, 0, 100)
    
    # If no zeros in original data and min value would be 0, shift up slightly
    if not has_zero and normalized_values.min() < 1:
        shift = 1 - normalized_values.min()
        normalized_values = normalized_values + shift
    
    # Round to integers
    normalized_values = normalized_values.round().astype(int)
    
    # Create new dataframe with original column names
    result = pd.DataFrame({
        date_col: df.iloc[:, 0],
        value_col: normalized_values
    })
    
    # Log the transformation information
    logger.info(f"Using fixed population parameters - Mean: {POPULATION_MEAN}, Std: {POPULATION_STD}")
    logger.info(f"Using scaling factor: 22 (each std dev = 22 points)")
    logger.info(f"Original values - Min: {values.min():.2f}, Max: {values.max():.2f}")
    logger.info(f"Z-scores - Min: {z_scores.min():.2f}, Max: {z_scores.max():.2f}")
    logger.info(f"Normalized values - Min: {normalized_values.min():.0f}, Max: {normalized_values.max():.0f}")
    logger.info(f"Zero values in original data: {'Yes' if has_zero else 'No'}")
    
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