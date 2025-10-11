#!/usr/bin/env python3
"""
Debug script to identify the root cause of the column name mismatch error
when using translated English names for Bain sources.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import necessary modules
from translations import translate_source_name, get_text
from fix_source_mapping import map_display_names_to_source_ids, DBASE_OPTIONS as dbase_options, DISPLAY_NAMES

# Add parent directory to path for database imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_database_manager
from translations import get_tool_name

def debug_column_names():
    """Debug function to trace column name transformations"""
    
    print("=" * 80)
    print("DEBUGGING COLUMN NAME TRANSFORMATIONS")
    print("=" * 80)
    
    # Test with a specific keyword and sources
    selected_keyword = 'Calidad_Total'
    selected_sources = ['Bain Usability', 'Bain Satisfaction']
    language = 'en'
    
    print(f"\nSelected Keyword: {selected_keyword}")
    print(f"Selected Sources: {selected_sources}")
    print(f"Language: {language}")
    
    # Step 1: Map display names to source IDs
    print("\n" + "-" * 40)
    print("STEP 1: Mapping Display Names to Source IDs")
    print("-" * 40)
    
    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"Display Names: {selected_sources}")
    print(f"Source IDs: {selected_source_ids}")
    
    # Step 2: Get database options
    print("\n" + "-" * 40)
    print("STEP 2: Database Options Mapping")
    print("-" * 40)
    
    print("Source ID -> Database Name Mapping:")
    for src_id in selected_source_ids:
        db_name = dbase_options.get(src_id, "NOT FOUND")
        print(f"  {src_id} -> {db_name}")
    
    # Step 3: Translate source names
    print("\n" + "-" * 40)
    print("STEP 3: Translating Source Names")
    print("-" * 40)
    
    print("Original -> Translated (English):")
    for src_id in selected_source_ids:
        original_name = dbase_options.get(src_id, "NOT FOUND")
        translated_name = translate_source_name(original_name, language)
        print(f"  {original_name} -> {translated_name}")
    
    # Step 4: Get actual data and check column names
    print("\n" + "-" * 40)
    print("STEP 4: Checking Actual DataFrame Column Names")
    print("-" * 40)
    
    try:
        db_manager = get_database_manager()
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        
        print("Retrieved datasets_norm keys:")
        for key in datasets_norm.keys():
            print(f"  {key}")
        
        # Create combined dataset
        from app import create_combined_dataset2
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        print("\nActual DataFrame columns:")
        for col in combined_dataset.columns:
            print(f"  '{col}'")
        
        # Check for mismatch
        print("\n" + "-" * 40)
        print("STEP 5: Checking for Column Name Mismatch")
        print("-" * 40)
        
        translated_names = []
        for src_id in selected_source_ids:
            original_name = dbase_options.get(src_id, "NOT FOUND")
            translated_name = translate_source_name(original_name, language)
            translated_names.append(translated_name)
            print(f"Translated name: '{translated_name}'")
            print(f"  In DataFrame: {'Yes' if translated_name in combined_dataset.columns else 'No'}")
        
        # Identify the issue
        print("\n" + "-" * 40)
        print("ROOT CAUSE ANALYSIS")
        print("-" * 40)
        
        if any(name not in combined_dataset.columns for name in translated_names):
            print("ISSUE IDENTIFIED: Translated column names don't match DataFrame columns!")
            print("\nThe problem is that:")
            print("1. We translate column names for display purposes")
            print("2. But the DataFrame still has the original Spanish column names")
            print("3. When we try to access columns with translated names, they don't exist")
            
            print("\nSOLUTION NEEDED:")
            print("Keep Spanish column names in the DataFrame but translate only for display")
            print("OR ensure all DataFrame operations use the original (untranslated) column names")
        else:
            print("No column name mismatch detected. Issue might be elsewhere.")
    
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_column_names()