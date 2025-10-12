#!/usr/bin/env python3
"""
Test script to reproduce the regression analysis issue specifically for Bain sources
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from database import get_database_manager
from fix_source_mapping import map_display_names_to_source_ids, enhanced_display_names_to_ids
from fix_dataframe_indexing import create_translation_mapping, get_original_column_name, safe_dataframe_column_access
from translations import translate_source_name

def test_bain_regression_mapping():
    """Test the mapping logic specifically for Bain sources in regression analysis"""
    
    print("Testing Bain Sources Regression Mapping")
    print("=" * 50)
    
    # Test in both languages
    for language in ['es', 'en']:
        print(f"\n=== Testing in {language.upper()} ===")
        
        # Test sources containing Bain
        test_sources = ['Bain Usabilidad', 'Bain Satisfaction', 'Google Trends']
        
        # Map display names to source IDs
        selected_source_ids = enhanced_display_names_to_ids(test_sources)
        print(f"Source IDs: {selected_source_ids}")
        
        # Database options (from app.py)
        dbase_options = {
            1: "Google Trends",
            2: "Google Books Ngrams", 
            3: "Bain - Usabilidad",
            4: "Bain - Satisfacción",
            5: "Crossref.org"
        }
        
        # Create translation mapping
        translation_mapping = create_translation_mapping(selected_source_ids, language)
        print(f"Translation mapping: {translation_mapping}")
        
        # Test specific pairs that would be clicked in the heatmap
        test_pairs = [
            ('Bain Usabilidad', 'Google Trends'),
            ('Bain Satisfaction', 'Google Trends'),
            ('Bain Usabilidad', 'Bain Satisfaction')
        ]
        
        for x_var, y_var in test_pairs:
            print(f"\n--- Testing pair: {x_var} vs {y_var} ---")
            
            # Method 1: Current callback logic (problematic)
            selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]
            translated_to_original = {}
            for src_id in selected_source_ids:
                original_name = dbase_options.get(src_id, "NOT FOUND")
                translated_name = translate_source_name(original_name, language)
                translated_to_original[translated_name] = original_name
            
            x_var_original_callback = translated_to_original.get(x_var, x_var)
            y_var_original_callback = translated_to_original.get(y_var, y_var)
            
            print(f"  Current callback logic:")
            print(f"    x_var: {x_var} -> {x_var_original_callback}")
            print(f"    y_var: {y_var} -> {y_var_original_callback}")
            
            # Method 2: Using fix_dataframe_indexing functions (correct)
            x_var_original_fix = get_original_column_name(x_var, translation_mapping)
            y_var_original_fix = get_original_column_name(y_var, translation_mapping)
            
            print(f"  Using fix_dataframe_indexing:")
            print(f"    x_var: {x_var} -> {x_var_original_fix}")
            print(f"    y_var: {y_var} -> {y_var_original_fix}")
            
            # Check which method works
            expected_x = dbase_options.get('BAIN_Ind_Usabilidad', 'Bain - Usabilidad') if 'Usabilidad' in x_var else dbase_options.get('BAIN_Ind_Satisfacción', 'Bain - Satisfacción')
            expected_y = dbase_options.get('BAIN_Ind_Usabilidad', 'Bain - Usabilidad') if 'Usabilidad' in y_var else dbase_options.get('BAIN_Ind_Satisfacción', 'Bain - Satisfacción')
            if 'Google Trends' in [x_var, y_var]:
                gt_var = dbase_options.get('Google_Trends', 'Google Trends')
                if 'Google Trends' in x_var:
                    expected_x = gt_var
                else:
                    expected_y = gt_var
            
            print(f"  Expected mapping:")
            print(f"    x_var should map to: {expected_x}")
            print(f"    y_var should map to: {expected_y}")
            
            # Check if callback logic is correct
            callback_correct = (x_var_original_callback == expected_x and y_var_original_callback == expected_y)
            fix_correct = (x_var_original_fix == expected_x and y_var_original_fix == expected_y)
            
            print(f"  Results:")
            print(f"    Current callback logic: {'✓' if callback_correct else '✗'}")
            print(f"    fix_dataframe_indexing: {'✓' if fix_correct else '✗'}")

def test_with_mock_data():
    """Test with mock data to simulate the regression analysis"""
    
    print("\n\nTesting with Mock Data")
    print("=" * 50)
    
    # Create mock dataset
    dates = pd.date_range('2020-01-01', periods=100, freq='ME')
    np.random.seed(42)
    
    # Create mock dataset with actual column names as they would appear
    mock_data = pd.DataFrame({
        'Fecha': dates,
        'Google Trends': np.random.normal(50, 10, 100),
        'Google Books Ngrams': np.random.normal(30, 5, 100),
        'Bain - Usabilidad': np.random.normal(70, 15, 100),
        'Bain - Satisfacción': np.random.normal(60, 12, 100),
        'Crossref.org': np.random.normal(40, 8, 100)
    })
    
    print(f"Mock dataset columns: {list(mock_data.columns)}")
    
    # Test in English
    language = 'en'
    test_sources = ['Bain Usabilidad', 'Bain Satisfaction', 'Google Trends']
    selected_source_ids = enhanced_display_names_to_ids(test_sources)
    translation_mapping = create_translation_mapping(selected_source_ids, language)
    
    # Test pairs
    test_pairs = [
        ('Bain Usabilidad', 'Google Trends'),
        ('Bain Satisfaction', 'Google Trends'),
        ('Bain Usabilidad', 'Bain Satisfaction')
    ]
    
    for x_var, y_var in test_pairs:
        print(f"\n--- Testing pair with mock data: {x_var} vs {y_var} ---")
        
        # Using safe_dataframe_column_access
        x_data = safe_dataframe_column_access(mock_data, x_var, translation_mapping)
        y_data = safe_dataframe_column_access(mock_data, y_var, translation_mapping)
        
        if x_data is not None and y_data is not None:
            print(f"  ✓ Successfully accessed data for both variables")
            print(f"    x_data shape: {x_data.shape}")
            print(f"    y_data shape: {y_data.shape}")
            
            # Check if we have valid data
            valid_data = pd.concat([x_data, y_data], axis=1).dropna()
            print(f"    Valid data points: {len(valid_data)}")
            
            if len(valid_data) >= 2:
                print(f"    ✓ Sufficient data for regression")
            else:
                print(f"    ✗ Insufficient data for regression")
        else:
            print(f"  ✗ Failed to access data")
            print(f"    x_data: {'Found' if x_data is not None else 'Not found'}")
            print(f"    y_data: {'Found' if y_data is not None else 'Not found'}")

if __name__ == "__main__":
    test_bain_regression_mapping()
    test_with_mock_data()
    
    print("\n=== Test completed ===")