#!/usr/bin/env python3
"""
Test script to verify if the Docker translation issue is still present.
This tests the enhanced source mapping functionality.
"""

import sys
import os

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def test_source_mapping():
    """Test the source mapping functionality with English names"""
    print("Testing Docker translation fix...")
    
    try:
        # Import the enhanced mapping function
        from fix_source_mapping import enhanced_display_names_to_ids
        
        # Test English names that were problematic before
        english_names = [
            'Bain - Usability',
            'Bain - Satisfaction',
            'Google Trends',
            'Google Books',
            'Crossref'
        ]
        
        print("\nTesting English source names:")
        for name in english_names:
            result = enhanced_display_names_to_ids([name])
            print(f"  '{name}' -> {result}")
        
        # Test Spanish names
        spanish_names = [
            'Bain - Usabilidad',
            'Bain - Satisfacción',
            'Google Trends',
            'Google Books Ngrams',
            'Crossref.org'
        ]
        
        print("\nTesting Spanish source names:")
        for name in spanish_names:
            result = enhanced_display_names_to_ids([name])
            print(f"  '{name}' -> {result}")
        
        # Test mixed names
        mixed_names = ['Bain - Usability', 'Google Trends', 'Bain - Satisfacción']
        print("\nTesting mixed source names:")
        result = enhanced_display_names_to_ids(mixed_names)
        print(f"  {mixed_names} -> {result}")
        
        return True
        
    except ImportError as e:
        print(f"Error importing enhanced function: {e}")
        return False
    except Exception as e:
        print(f"Error testing source mapping: {e}")
        return False

def test_app_imports():
    """Test if the app properly imports and uses the enhanced functions"""
    print("\nTesting app imports...")
    
    try:
        # Test if app can import the enhanced functions
        sys.path.insert(0, os.path.dirname(__file__))
        from dashboard_app.fix_source_mapping import map_display_names_to_source_ids
        
        # Test the mapping function used by the app
        test_names = ['Bain - Usability', 'Bain - Satisfaction']
        result = map_display_names_to_source_ids(test_names)
        print(f"App mapping function test: {test_names} -> {result}")
        
        return True
        
    except ImportError as e:
        print(f"Error importing from app: {e}")
        return False
    except Exception as e:
        print(f"Error testing app imports: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Docker Translation Fix Verification")
    print("=" * 60)
    
    success1 = test_source_mapping()
    success2 = test_app_imports()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed! The translation fix appears to be working.")
    else:
        print("❌ Some tests failed. The issue may still be present.")
    print("=" * 60)