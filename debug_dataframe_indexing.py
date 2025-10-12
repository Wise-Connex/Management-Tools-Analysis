#!/usr/bin/env python3
"""
Debug script to investigate the DataFrame indexing error.
This error suggests that the translated source names don't match the actual DataFrame columns.
"""

import sys
import os

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def debug_dataframe_columns():
    """Debug the DataFrame column names vs translated source names"""
    print("="*60)
    print("DATAFRAME COLUMN INVESTIGATION")
    print("="*60)
    
    try:
        from fix_source_mapping import (
            DISPLAY_NAMES,
            DISPLAY_TO_DB_NAME,
            DBASE_OPTIONS,
            map_display_names_to_source_ids
        )
        
        print("DISPLAY_NAMES:", DISPLAY_NAMES)
        print("DISPLAY_TO_DB_NAME:", DISPLAY_TO_DB_NAME)
        print("DBASE_OPTIONS:", DBASE_OPTIONS)
        
        # Check what the mapping function returns
        english_names = ['Bain - Usability', 'Bain - Satisfaction']
        spanish_names = ['Bain - Usabilidad', 'Bain - Satisfacción']
        
        print("\nTesting English names:")
        english_ids = map_display_names_to_source_ids(english_names)
        print(f"  English: {english_names} -> IDs: {english_ids}")
        
        print("\nTesting Spanish names:")
        spanish_ids = map_display_names_to_source_ids(spanish_names)
        print(f"  Spanish: {spanish_names} -> IDs: {spanish_ids}")
        
        # Convert IDs back to database names
        print("\nConverting IDs back to database names:")
        for name, id_val in zip(english_names, english_ids):
            db_name = DBASE_OPTIONS.get(id_val, "NOT FOUND")
            print(f"  ID {id_val} -> '{db_name}'")
            
        # This is the critical part - check what names are used in the DataFrame
        print("\nExpected DataFrame column names from IDs:")
        expected_columns = []
        for id_val in english_ids:
            db_name = DBASE_OPTIONS.get(id_val, "NOT FOUND")
            expected_columns.append(db_name)
        print(f"  Expected columns: {expected_columns}")
        
        # Check if there are any inconsistencies
        print("\nPotential issues:")
        print("1. Are the English names being used directly as column names?")
        print("2. Are the Spanish names being used directly as column names?")
        print("3. Are the database names being used as column names?")
        
        # The issue is likely that the translated names are being used
        # to access DataFrame columns, but the columns use different names
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def check_translation_flow():
    """Check the complete translation flow from UI to DataFrame"""
    print("\n" + "="*60)
    print("TRANSLATION FLOW ANALYSIS")
    print("="*60)
    
    try:
        from translations import translate_source_name
        from fix_source_mapping import DBASE_OPTIONS, map_display_names_to_source_ids
        
        # Step 1: User selects English sources in UI
        english_selection = ['Bain - Usability', 'Bain - Satisfaction']
        print(f"1. User selects: {english_selection}")
        
        # Step 2: Map to source IDs
        source_ids = map_display_names_to_source_ids(english_selection)
        print(f"2. Mapped to IDs: {source_ids}")
        
        # Step 3: Get database names from IDs
        db_names = [DBASE_OPTIONS.get(id_val) for id_val in source_ids]
        print(f"3. Database names: {db_names}")
        
        # Step 4: Translate database names for display
        translated_names = [translate_source_name(name, 'en') for name in db_names]
        print(f"4. Translated for display: {translated_names}")
        
        # The problem is likely that step 4 is being used to access DataFrame columns
        # instead of step 3
        
        print("\nHYPOTHESIS:")
        print("The application is using translated names (step 4) to access")
        print("DataFrame columns, but the columns use database names (step 3).")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dataframe_columns()
    check_translation_flow()