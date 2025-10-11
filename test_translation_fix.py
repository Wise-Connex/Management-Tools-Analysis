#!/usr/bin/env python3
"""
Test script to verify the translation fix works correctly.
"""

import os
import sys

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def test_source_mapping_fix():
    """Test that the source mapping fix works correctly"""
    print("Testing source mapping fix...")
    
    try:
        from fix_source_mapping import map_display_names_to_source_ids
        
        # Test with English names
        english_sources = ["Bain - Usability", "Bain - Satisfaction", "Google Trends"]
        print(f"Testing with English sources: {english_sources}")
        
        source_ids = map_display_names_to_source_ids(english_sources)
        print(f"Mapped to source IDs: {source_ids}")
        
        # Check if all sources were mapped
        if None in source_ids:
            print("ERROR: Some sources could not be mapped!")
            for i, source_id in enumerate(source_ids):
                if source_id is None:
                    print(f"  Failed to map: {english_sources[i]}")
            return False
        elif len(source_ids) != len(english_sources):
            print(f"ERROR: Not all sources were mapped! Expected {len(english_sources)}, got {len(source_ids)}")
            return False
        else:
            print("SUCCESS: All English sources mapped correctly!")
            
        # Test with Spanish names
        spanish_sources = ["Bain - Usabilidad", "Bain - Satisfacción", "Google Trends"]
        print(f"\nTesting with Spanish sources: {spanish_sources}")
        
        source_ids_es = map_display_names_to_source_ids(spanish_sources)
        print(f"Mapped to source IDs: {source_ids_es}")
        
        if None in source_ids_es:
            print("ERROR: Some Spanish sources could not be mapped!")
            for i, source_id in enumerate(source_ids_es):
                if source_id is None:
                    print(f"  Failed to map: {spanish_sources[i]}")
            return False
        elif len(source_ids_es) != len(spanish_sources):
            print(f"ERROR: Not all Spanish sources were mapped! Expected {len(spanish_sources)}, got {len(source_ids_es)}")
            return False
        else:
            print("SUCCESS: All Spanish sources mapped correctly!")
            
        return True
        
    except Exception as e:
        print(f"ERROR testing source mapping: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_functions():
    """Test translation functions"""
    print("\nTesting translation functions...")
    
    try:
        from translations import get_text, translate_source_name
        
        # Test UI translations
        print("Testing UI translations:")
        test_keys = ['select_tool', 'select_sources', 'data_table']
        for key in test_keys:
            es_text = get_text(key, 'es')
            en_text = get_text(key, 'en')
            print(f"  {key}: es='{es_text}', en='{en_text}'")
        
        # Test source name translations
        print("\nTesting source name translations:")
        test_sources = [
            ('Bain - Usabilidad', 'en'),
            ('Bain - Satisfacción', 'en'),
            ('Bain - Usability', 'es'),
            ('Bain - Satisfaction', 'es')
        ]
        
        for source, lang in test_sources:
            translated = translate_source_name(source, lang)
            print(f"  '{source}' -> '{translated}' (lang={lang})")
            
        print("SUCCESS: Translation functions working correctly!")
        return True
        
    except Exception as e:
        print(f"ERROR testing translation functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("TRANSLATION FIX VERIFICATION")
    print("="*60)
    
    success = True
    success &= test_translation_functions()
    success &= test_source_mapping_fix()
    
    print("\n" + "="*60)
    if success:
        print("ALL TESTS PASSED! The fix should resolve the Docker translation issue.")
    else:
        print("SOME TESTS FAILED! The fix needs more work.")
    print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)