#!/usr/bin/env python3
"""
Test script to reproduce and fix the regression analysis issue for Bain sources
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from database import get_database_manager
from fix_source_mapping import map_display_names_to_source_ids, enhanced_display_names_to_ids
from fix_dataframe_indexing import create_translation_mapping, get_original_column_name
from translations import translate_source_name

def test_regression_mapping():
    """Test the mapping logic used in regression analysis"""
    
    # Test in both languages
    for language in ['es', 'en']:
        print(f"\n=== Testing in {language.upper()} ===")
        
        # Test sources containing Bain
        test_sources = ['Bain Usabilidad', 'Bain Satisfaction', 'Google Trends', 'Crossref']
        
        # Map display names to source IDs
        selected_source_ids = enhanced_display_names_to_ids(test_sources)
        print(f"Source IDs: {selected_source_ids}")
        
        # Database options (from app.py)
        dbase_options = {
            1: "Google Trends",
            2: "Google Books Ngrams", 
            3: "Bain - Usabilidad",
            4: "Bain - Satisfacción",
            5: "Crossref.org"
        }
        
        # Create translation mapping
        translation_mapping = create_translation_mapping(selected_source_ids, language)
        print(f"Translation mapping: {translation_mapping}")
        
        # Test mapping for regression analysis (mimicking the callback logic)
        selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]
        print(f"Selected source names: {selected_source_names}")
        
        # Create mapping between translated names and original column names (from callback)
        translated_to_original = {}
        for src_id in selected_source_ids:
            original_name = dbase_options.get(src_id, "NOT FOUND")
            translated_name = translate_source_name(original_name, language)
            translated_to_original[translated_name] = original_name
        
        print(f"Translated to original mapping: {translated_to_original}")
        
        # Test specific pairs that would be clicked in the heatmap
        test_pairs = [
            ('Bain Usabilidad', 'Google Trends'),
            ('Bain Satisfaction', 'Crossref'),
            ('Bain Usabilidad', 'Bain Satisfaction')
        ]
        
        for x_var, y_var in test_pairs:
            print(f"\n--- Testing pair: {x_var} vs {y_var} ---")
            
            # Convert translated names back to original column names (from callback)
            x_var_original = translated_to_original.get(x_var, x_var)
            y_var_original = translated_to_original.get(y_var, y_var)
            
            print(f"  x_var: {x_var} -> {x_var_original}")
            print(f"  y_var: {y_var} -> {y_var_original}")
            
            # Check if the mapping is correct
            if x_var_original in dbase_options.values() and y_var_original in dbase_options.values():
                print(f"  ✓ Both variables found in database options")
            else:
                print(f"  ✗ Variables not found in database options")
                
            # Test using the dataframe indexing fix functions
            x_var_original_fix = get_original_column_name(x_var, translation_mapping)
            y_var_original_fix = get_original_column_name(y_var, translation_mapping)
            
            print(f"  Using fix_dataframe_indexing:")
            print(f"    x_var: {x_var} -> {x_var_original_fix}")
            print(f"    y_var: {y_var} -> {y_var_original_fix}")

def test_with_actual_data():
    """Test with actual data from the database"""
    
    print("\n=== Testing with actual data ===")
    
    # Get database manager
    db_manager = get_database_manager()
    
    # Test keyword
    selected_keyword = "BSC"  # Using a keyword that should have data
    selected_sources = ['Bain Usabilidad', 'Bain Satisfaction', 'Google Trends']
    
    # Map display names to source IDs
    selected_source_ids = enhanced_display_names_to_ids(selected_sources)
    
    # Get data
    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        
        if not datasets_norm:
            print("No data retrieved for keyword BSC")
            return
            
        # Create combined dataset (mimicking app.py logic)
        dbase_options = {
            1: "Google Trends",
            2: "Google Books Ngrams", 
            3: "Bain - Usabilidad",
            4: "Bain - Satisfacción",
            5: "Crossref.org"
        }
        
        combined_dataset = create_combined_dataset2(datasets_norm, sl_sc, dbase_options)
        
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})
        
        print(f"Combined dataset columns: {list(combined_dataset.columns)}")
        
        # Test regression analysis mapping
        language = 'en'
        translation_mapping = create_translation_mapping(selected_source_ids, language)
        
        # Test pairs
        test_pairs = [
            ('Bain Usabilidad', 'Google Trends'),
            ('Bain Satisfaction', 'Google Trends'),
            ('Bain Usabilidad', 'Bain Satisfaction')
        ]
        
        for x_var, y_var in test_pairs:
            print(f"\n--- Testing pair with actual data: {x_var} vs {y_var} ---")
            
            # Using the fix_dataframe_indexing functions
            x_var_original = get_original_column_name(x_var, translation_mapping)
            y_var_original = get_original_column_name(y_var, translation_mapping)
            
            print(f"  Mapped to: {x_var_original} vs {y_var_original}")
            
            # Check if columns exist
            if x_var_original in combined_dataset.columns and y_var_original in combined_dataset.columns:
                print(f"  ✓ Both columns exist in dataset")
                
                # Check if we have valid data
                valid_data = combined_dataset[[x_var_original, y_var_original]].dropna()
                print(f"  Valid data points: {len(valid_data)}")
                
                if len(valid_data) >= 2:
                    print(f"  ✓ Sufficient data for regression")
                else:
                    print(f"  ✗ Insufficient data for regression")
            else:
                print(f"  ✗ Columns not found in dataset")
                print(f"    Available columns: {[col for col in combined_dataset.columns if col != 'Fecha']}")
                
    except Exception as e:
        print(f"Error testing with actual data: {e}")
        import traceback
        traceback.print_exc()

def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):
    """Create combined dataset with all dates from all sources (from app.py)"""
    combined_dataset2 = pd.DataFrame()

    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)

    # Sort dates
    all_dates = sorted(list(all_dates))

    # Create DataFrame with all dates
    combined_dataset2 = pd.DataFrame(index=all_dates)

    # Add data from each source - use source name directly as column name
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            source_data = datasets_norm[source].reindex(all_dates)
            # Use just the source name as the column name (not source_name_col)
            combined_dataset2[source_name] = source_data.iloc[:, 0]

    return combined_dataset2

if __name__ == "__main__":
    print("Testing regression analysis mapping for Bain sources...")
    
    test_regression_mapping()
    test_with_actual_data()
    
    print("\n=== Test completed ===")