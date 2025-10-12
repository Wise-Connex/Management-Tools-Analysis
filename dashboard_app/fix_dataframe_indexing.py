"""
Fix for DataFrame indexing issue with translated source names.

The problem: When the language is switched to English, the application tries to access
DataFrame columns using translated names (e.g., 'Bain - Usability') but the actual
column names are in Spanish (e.g., 'Bain - Usabilidad').

This fix ensures that we always use the original database column names when
accessing DataFrame data, while still displaying translated names in the UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fix_source_mapping import DBASE_OPTIONS
from translations import translate_source_name

def create_translation_mapping(selected_source_ids, language):
    """
    Create a mapping between translated display names and original database column names.
    
    Args:
        selected_source_ids: List of source IDs
        language: Target language ('es' or 'en')
        
    Returns:
        Dictionary mapping translated names to original column names
    """
    translation_mapping = {}
    
    for src_id in selected_source_ids:
        # Get the original database column name
        original_name = DBASE_OPTIONS.get(src_id, "NOT FOUND")
        
        # Get the translated display name
        translated_name = translate_source_name(original_name, language)
        
        # Create the mapping
        translation_mapping[translated_name] = original_name
        
        # Also add mapping without special characters (for 'Bain Usability' vs 'Bain - Usability')
        translated_name_simple = translated_name.replace(' - ', ' ')
        translation_mapping[translated_name_simple] = original_name
        
    return translation_mapping

def get_original_column_name(display_name, translation_mapping):
    """
    Get the original column name for a translated display name.
    
    Args:
        display_name: The translated display name
        translation_mapping: Dictionary of translations to original names
        
    Returns:
        Original column name or the display name if not found in mapping
    """
    return translation_mapping.get(display_name, display_name)

def fix_dataframe_column_access(data, sources, language):
    """
    Fix DataFrame column access by ensuring we use original column names.
    
    Args:
        data: DataFrame with original column names
        sources: List of translated source names
        language: Current language
        
    Returns:
        Tuple of (fixed_data, translation_mapping)
    """
    # Get source IDs from display names (this handles the translation)
    from fix_source_mapping import map_display_names_to_source_ids
    selected_source_ids = map_display_names_to_source_ids(sources)
    
    # Create translation mapping
    translation_mapping = create_translation_mapping(selected_source_ids, language)
    
    # Create a new DataFrame with translated column names for display
    # but keep original names for data access
    display_data = data.copy()
    
    # Rename columns to translated names for display purposes
    for translated_name, original_name in translation_mapping.items():
        if original_name in display_data.columns and original_name != translated_name:
            display_data = display_data.rename(columns={original_name: translated_name})
    
    return display_data, translation_mapping

def safe_dataframe_column_access(data, translated_name, translation_mapping):
    """
    Safely access a DataFrame column using a translated name.
    
    Args:
        data: DataFrame with original column names
        translated_name: The translated column name
        translation_mapping: Dictionary of translations to original names
        
    Returns:
        pandas Series or None if column not found
    """
    original_name = get_original_column_name(translated_name, translation_mapping)
    
    if original_name in data.columns:
        return data[original_name]
    elif translated_name in data.columns:
        return data[translated_name]
    else:
        print(f"WARNING: Column '{translated_name}' (original: '{original_name}') not found in DataFrame")
        print(f"Available columns: {list(data.columns)}")
        return None

# Test function to verify the fix
def test_dataframe_indexing_fix():
    """Test the DataFrame indexing fix."""
    import pandas as pd
    
    # Create test data with Spanish column names
    test_data = pd.DataFrame({
        'Fecha': pd.date_range('2020-01-01', periods=5, freq='M'),
        'Bain - Usabilidad': [1, 2, 3, 4, 5],
        'Bain - Satisfacción': [10, 20, 30, 40, 50],
        'Google Trends': [100, 200, 300, 400, 500]
    })
    
    # Test with English language
    language = 'en'
    sources = ['Bain - Usability', 'Bain - Satisfaction', 'Google Trends']
    
    # Get source IDs
    from fix_source_mapping import map_display_names_to_source_ids
    selected_source_ids = map_display_names_to_source_ids(sources)
    
    # Create translation mapping
    translation_mapping = create_translation_mapping(selected_source_ids, language)
    
    print("Translation mapping:")
    for translated, original in translation_mapping.items():
        print(f"  '{translated}' -> '{original}'")
    
    # Test column access
    print("\nTesting column access:")
    for source in sources:
        column_data = safe_dataframe_column_access(test_data, source, translation_mapping)
        if column_data is not None:
            print(f"  '{source}': {column_data.tolist()}")
        else:
            print(f"  '{source}': NOT FOUND")
    
    # Test with fixed DataFrame
    print("\nTesting with fixed DataFrame:")
    fixed_data, _ = fix_dataframe_column_access(test_data, sources, language)
    print(f"Fixed DataFrame columns: {list(fixed_data.columns)}")
    
    for source in sources:
        if source in fixed_data.columns:
            print(f"  '{source}': {fixed_data[source].tolist()}")
        else:
            print(f"  '{source}': NOT FOUND in fixed DataFrame")

if __name__ == "__main__":
    test_dataframe_indexing_fix()