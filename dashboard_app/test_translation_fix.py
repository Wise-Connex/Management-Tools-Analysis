#!/usr/bin/env python3
"""
Test script to verify the translation fix works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from translations import translate_source_name, enhanced_translate_source_name
from fix_source_mapping import map_display_names_to_source_ids, DBASE_OPTIONS

def test_translation_mapping():
    """Test that translation mapping works correctly"""
    print("=== Testing Translation Mapping ===")
    
    # Test Spanish names
    spanish_sources = ['Bain Usability', 'Bain Satisfaction', 'Google Trends', 'Google Books', 'Crossref']
    
    # Test mapping to IDs
    source_ids = map_display_names_to_source_ids(spanish_sources)
    print(f"Spanish sources: {spanish_sources}")
    print(f"Mapped to IDs: {source_ids}")
    
    # Test translation to English
    for source_id in source_ids:
        db_name = DBASE_OPTIONS.get(source_id, "NOT FOUND")
        english_name = enhanced_translate_source_name(db_name, 'en')
        print(f"ID {source_id}: {db_name} -> {english_name}")
    
    # Test reverse mapping
    english_sources = ['Bain - Usability', 'Bain - Satisfaction', 'Google Trends', 'Google Books', 'Crossref']
    english_ids = map_display_names_to_source_ids(english_sources)
    print(f"\nEnglish sources: {english_sources}")
    print(f"Mapped to IDs: {english_ids}")
    
    # Check if mapping is consistent
    if spanish_sources == english_sources:
        print("\n❌ ERROR: Spanish and English sources are the same - mapping issue!")
        return False
    elif set(source_ids) == set(english_ids):
        print("\n✓ SUCCESS: Both Spanish and English map to the same IDs")
        return True
    else:
        print(f"\n❌ ERROR: ID mismatch! Spanish: {source_ids}, English: {english_ids}")
        return False

def test_column_name_translation():
    """Test that column names are handled correctly"""
    print("\n=== Testing Column Name Translation ===")
    
    # Simulate what happens in the app
    selected_sources = ['Bain Usability', 'Bain Satisfaction']
    language = 'en'
    
    # Map to IDs
    source_ids = map_display_names_to_source_ids(selected_sources)
    
    # Get database names (these are the column names in the dataframe)
    db_names = [DBASE_OPTIONS.get(sid) for sid in source_ids]
    print(f"Database column names: {db_names}")
    
    # Get translated names (these are displayed in the UI)
    translated_names = [enhanced_translate_source_name(name, language) for name in db_names]
    print(f"Translated display names: {translated_names}")
    
    # Create translation mapping
    translation_mapping = {}
    for translated, original in zip(translated_names, db_names):
        translation_mapping[translated] = original
    
    print(f"Translation mapping: {translation_mapping}")
    
    # Test that we can map back correctly
    for translated in translated_names:
        original = translation_mapping.get(translated)
        if original:
            print(f"✓ '{translated}' maps back to '{original}'")
        else:
            print(f"❌ '{translated}' has no mapping")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing Docker translation fix...")
    
    test1_passed = test_translation_mapping()
    test2_passed = test_column_name_translation()
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed! The translation fix should work correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please check the translation implementation.")
        exit(1)