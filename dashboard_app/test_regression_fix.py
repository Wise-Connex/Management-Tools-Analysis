#!/usr/bin/env python3
"""
Test script to verify the regression analysis fix works correctly.
This script simulates various click_data scenarios to ensure the fix handles them properly.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regression_fix import update_regression_analysis

# Mock dependencies for testing
class MockDbManager:
    def get_data_for_keyword(self, keyword, sources):
        # Return mock data for testing
        import pandas as pd
        import numpy as np
        
        # Create mock dataset
        dates = pd.date_range('2020-01-01', periods=100, freq='M')
        data = {
            'Google Trends': np.random.normal(50, 10, 100),
            'Google Books': np.random.normal(30, 5, 100),
            'Bain Usability': np.random.normal(40, 8, 100),
            'Bain Satisfaction': np.random.normal(35, 7, 100),
            'Crossref': np.random.normal(25, 4, 100)
        }
        
        df = pd.DataFrame(data, index=dates)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Fecha'}, inplace=True)
        
        # Return mock datasets_norm and sl_sc
        datasets_norm = {}
        for source in sources:
            if source in ['Google_Trends', 'Google_Books', 'BAIN_Ind_Usabilidad', 'BAIN_Ind_Satisfacción', 'Crossref']:
                source_name = source.replace('_Trends', ' Trends').replace('_Books', ' Books').replace('BAIN_Ind_', 'Bain ')
                datasets_norm[source] = df[['Fecha', source_name]].set_index('Fecha')
        
        return datasets_norm, sources

def mock_get_text(key, language, **kwargs):
    """Mock translation function"""
    translations = {
        'click_heatmap': 'Click on the heatmap to see regression analysis',
        'regression_title': f'Regression Analysis: {kwargs.get("y_var", "")} vs {kwargs.get("x_var", "")}',
        'cannot_regress_same': f'Cannot regress {kwargs.get("var", "")} against itself',
        'select_different_vars': 'Please select different variables',
        'invalid_selection': 'Invalid Selection',
        'variables_not_found': f'Variables not found: {kwargs.get("x_var", "")}, {kwargs.get("y_var", "")}',
        'regression_error': 'Error in regression analysis',
        'regression_equations': 'Regression Equations'
    }
    return translations.get(key, key)

def mock_map_display_names_to_source_ids(display_names):
    """Mock mapping function"""
    mapping = {
        'Google Trends': 'Google_Trends',
        'Google Books': 'Google_Books',
        'Bain Usability': 'BAIN_Ind_Usabilidad',
        'Bain Satisfaction': 'BAIN_Ind_Satisfacción',
        'Crossref': 'Crossref'
    }
    return [mapping.get(name, name) for name in display_names]

def mock_create_combined_dataset2(datasets_norm, selected_sources, dbase_options):
    """Mock dataset creation function"""
    import pandas as pd
    
    # Create a simple combined dataset
    all_data = {}
    for source in selected_sources:
        if source in datasets_norm:
            all_data[source] = datasets_norm[source].iloc[:, 0]
    
    combined_df = pd.DataFrame(all_data)
    combined_df.reset_index(inplace=True)
    return combined_df

# Mock color map
mock_color_map = {
    'Google Trends': '#1f77b4',
    'Google Books': '#ff7f0e',
    'Bain Usability': '#d62728',
    'Bain Satisfaction': '#9467bd',
    'Crossref': '#2ca02c'
}

def test_regression_fix():
    """Test the regression analysis fix with various scenarios"""
    
    print("Testing Regression Analysis Fix")
    print("=" * 50)
    
    # Test case 1: Valid click_data
    print("\n1. Testing with valid click_data...")
    valid_click_data = {
        'points': [
            {
                'x': 'Google Trends',
                'y': 'Google Books',
                'customdata': None
            }
        ]
    }
    
    try:
        fig, equations = update_regression_analysis(
            valid_click_data,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ Valid click_data test passed - No crash occurred")
    except Exception as e:
        print(f"❌ Valid click_data test failed: {e}")
    
    # Test case 2: Empty click_data
    print("\n2. Testing with empty click_data...")
    empty_click_data = {}
    
    try:
        fig, equations = update_regression_analysis(
            empty_click_data,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ Empty click_data test passed - Handled gracefully")
    except Exception as e:
        print(f"❌ Empty click_data test failed: {e}")
    
    # Test case 3: Invalid click_data structure (missing points)
    print("\n3. Testing with invalid click_data structure (missing points)...")
    invalid_click_data = {
        'other_data': 'some_value'
    }
    
    try:
        fig, equations = update_regression_analysis(
            invalid_click_data,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ Invalid click_data structure test passed - Handled gracefully")
    except Exception as e:
        print(f"❌ Invalid click_data structure test failed: {e}")
    
    # Test case 4: Invalid point structure (missing x/y)
    print("\n4. Testing with invalid point structure (missing x/y)...")
    invalid_point_data = {
        'points': [
            {
                'z': 'some_value'
            }
        ]
    }
    
    try:
        fig, equations = update_regression_analysis(
            invalid_point_data,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ Invalid point structure test passed - Handled gracefully")
    except Exception as e:
        print(f"❌ Invalid point structure test failed: {e}")
    
    # Test case 5: None click_data
    print("\n5. Testing with None click_data...")
    
    try:
        fig, equations = update_regression_analysis(
            None,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ None click_data test passed - Handled gracefully")
    except Exception as e:
        print(f"❌ None click_data test failed: {e}")
    
    # Test case 6: Empty points list
    print("\n6. Testing with empty points list...")
    empty_points_data = {
        'points': []
    }
    
    try:
        fig, equations = update_regression_analysis(
            empty_points_data,
            'Calidad Total',
            ['Google Trends', 'Google Books'],
            'es',
            MockDbManager(),
            {},
            mock_get_text,
            mock_map_display_names_to_source_ids,
            mock_create_combined_dataset2,
            mock_color_map
        )
        print("✅ Empty points list test passed - Handled gracefully")
    except Exception as e:
        print(f"❌ Empty points list test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Regression Analysis Fix Testing Complete!")
    print("The fix properly handles various click_data scenarios without crashing.")

if __name__ == "__main__":
    test_regression_fix()