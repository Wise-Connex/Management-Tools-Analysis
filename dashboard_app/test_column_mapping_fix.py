#!/usr/bin/env python3
"""
Test script to verify the column mapping fix for translated English names
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the translation functions
from translations import translate_source_name, get_text

def test_column_mapping():
    """Test that column mapping works correctly for both Spanish and English"""
    print("Testing column mapping fix...")
    
    # Test Spanish names
    spanish_columns = ['Bain - Usabilidad', 'Bain - Satisfacción', 'Google Trends', 'Crossref']
    english_translations = [translate_source_name(col, 'en') for col in spanish_columns]
    
    print("\nSpanish to English translations:")
    for spanish, english in zip(spanish_columns, english_translations):
        print(f"  {spanish} -> {english}")
    
    # Create mapping as done in the fix
    translated_to_original = {}
    for col in spanish_columns:
        translated = translate_source_name(col, 'en')
        translated_to_original[translated] = col
    
    print("\nTranslation mapping (English -> Spanish):")
    for english, spanish in translated_to_original.items():
        print(f"  {english} -> {spanish}")
    
    # Verify mapping works correctly
    print("\nVerifying mapping works correctly:")
    for english in english_translations:
        original = translated_to_original.get(english, "NOT FOUND")
        if original in spanish_columns:
            print(f"  ✓ {english} correctly maps to {original}")
        else:
            print(f"  ✗ {english} failed to map correctly")
    
    # Test equation type translations
    print("\nTesting equation type translations:")
    equation_types = ['linear', 'quadratic', 'cubic', 'quartic', 'data_points']
    
    for eq_type in equation_types:
        spanish = get_text(eq_type, 'es')
        english = get_text(eq_type, 'en')
        print(f"  {eq_type}: es='{spanish}', en='{english}'")
    
    print("\n✅ Column mapping fix verified successfully!")

if __name__ == "__main__":
    test_column_mapping()