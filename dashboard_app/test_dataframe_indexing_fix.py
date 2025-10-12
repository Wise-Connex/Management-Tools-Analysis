#!/usr/bin/env python3
"""
Test script to verify that the DataFrame indexing fix resolves the translation issue.
This script simulates the operations that were causing the "not in index" error.
"""

import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(__file__))

from fix_source_mapping import (
    enhanced_display_names_to_ids,
    DBASE_OPTIONS as dbase_options
)
from fix_dataframe_indexing import (
    create_translation_mapping,
    get_original_column_name,
    safe_dataframe_column_access
)

def test_dataframe_indexing_fix():
    """Test that the DataFrame indexing fix resolves the translation issue."""
    print("Testing DataFrame indexing fix...")
    
    # Test with both Spanish and English display names
    test_cases = [
        {
            'language': 'es',
            'display_names': ['Bain Usabilidad', 'Bain Satisfacción'],
            'expected_original': ['Bain - Usabilidad', 'Bain - Satisfacción']
        },
        {
            'language': 'en',
            'display_names': ['Bain Usability', 'Bain Satisfaction'],
            'expected_original': ['Bain - Usabilidad', 'Bain - Satisfacción']
        }
    ]
    
    for test_case in test_cases:
        language = test_case['language']
        display_names = test_case['display_names']
        expected_original = test_case['expected_original']
        
        print(f"\nTesting with language: {language}")
        print(f"Display names: {display_names}")
        print(f"Expected original: {expected_original}")
        
        # Map display names to source IDs
        source_ids = enhanced_display_names_to_ids(display_names)
        print(f"Mapped source IDs: {source_ids}")
        
        # Create translation mapping
        translation_mapping = create_translation_mapping(source_ids, language)
        print(f"Translation mapping: {translation_mapping}")
        
        # Create a test DataFrame with Spanish column names (as they would be in the database)
        test_data = {
            'Fecha': pd.date_range('2020-01-01', periods=10, freq='M'),
            'Bain - Usabilidad': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Bain - Satisfacción': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            'Google Trends': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        }
        df = pd.DataFrame(test_data)
        print(f"Test DataFrame columns: {list(df.columns)}")
        
        # Test safe column access for each display name
        for i, display_name in enumerate(display_names):
            original_name = expected_original[i]
            
            # Get the column using safe access
            column_data = safe_dataframe_column_access(df, display_name, translation_mapping)
            
            if column_data is not None:
                print(f"✓ Successfully accessed column for '{display_name}'")
                print(f"  Original name: '{original_name}'")
                print(f"  Data: {column_data.tolist()}")
                
                # Verify the data is correct
                expected_data = df[original_name].tolist()
                if column_data.tolist() == expected_data:
                    print(f"  ✓ Data matches expected values")
                else:
                    print(f"  ✗ Data mismatch. Expected: {expected_data}, Got: {column_data.tolist()}")
            else:
                print(f"✗ Failed to access column for '{display_name}'")
    
    print("\nDataFrame indexing fix test completed!")

if __name__ == "__main__":
    test_dataframe_indexing_fix()