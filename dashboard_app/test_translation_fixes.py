#!/usr/bin/env python3
"""
Test script to verify the translation fixes for:
1. Bain source names in English display
2. Regression equation types in the regression analysis graph
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the translation functions
from translations import translate_source_name, get_text

def test_bain_source_translation():
    """Test that Bain source names are properly translated to English"""
    print("Testing Bain source name translations...")
    
    # Test Spanish names (should remain unchanged)
    assert translate_source_name('Bain - Usabilidad', 'es') == 'Bain - Usabilidad'
    assert translate_source_name('Bain - Satisfacción', 'es') == 'Bain - Satisfacción'
    assert translate_source_name('Bain Usabilidad', 'es') == 'Bain Usabilidad'
    assert translate_source_name('Bain Satisfacción', 'es') == 'Bain Satisfacción'
    print("✓ Spanish names unchanged")
    
    # Test English translations
    assert translate_source_name('Bain - Usabilidad', 'en') == 'Bain - Usability'
    assert translate_source_name('Bain - Satisfacción', 'en') == 'Bain - Satisfaction'
    assert translate_source_name('Bain Usabilidad', 'en') == 'Bain Usability'
    assert translate_source_name('Bain Satisfacción', 'en') == 'Bain Satisfaction'
    assert translate_source_name('BAIN_Ind_Usabilidad', 'en') == 'Bain - Usability'
    assert translate_source_name('BAIN_Ind_Satisfacción', 'en') == 'Bain - Satisfaction'
    print("✓ English names properly translated")
    
    # Test other sources (should remain unchanged)
    assert translate_source_name('Google Trends', 'en') == 'Google Trends'
    assert translate_source_name('Crossref', 'en') == 'Crossref'
    print("✓ Other sources unchanged")
    
    print("✅ Bain source name translations verified successfully!")

def test_regression_equation_translation():
    """Test that regression equation types are properly translated"""
    print("\nTesting regression equation type translations...")
    
    # Test Spanish translations
    assert get_text('linear', 'es') == 'Lineal'
    assert get_text('quadratic', 'es') == 'Cuadrática'
    assert get_text('cubic', 'es') == 'Cúbica'
    assert get_text('quartic', 'es') == 'Cuártica'
    assert get_text('data_points', 'es') == 'Puntos de Datos'
    print("✓ Spanish equation types correct")
    
    # Test English translations
    assert get_text('linear', 'en') == 'Linear'
    assert get_text('quadratic', 'en') == 'Quadratic'
    assert get_text('cubic', 'en') == 'Cubic'
    assert get_text('quartic', 'en') == 'Quartic'
    assert get_text('data_points', 'en') == 'Data Points'
    print("✓ English equation types correct")
    
    print("✅ Regression equation type translations verified successfully!")

if __name__ == "__main__":
    try:
        test_bain_source_translation()
        test_regression_equation_translation()
        print("\n🎉 All translation fixes verified successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)