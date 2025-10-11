#!/usr/bin/env python3
"""
Test script to verify the regression analysis callback fix v2
Tests that the function always returns a tuple (figure, equations_content)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the fixed function
from app import update_regression_analysis

def test_regression_callback_return_types():
    """Test that the callback always returns the correct tuple type"""
    
    print("Testing regression analysis callback return types...")
    
    # Test case 1: Missing keyword
    print("\n1. Testing with missing keyword...")
    result = update_regression_analysis(None, None, [], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Missing keyword test passed")
    
    # Test case 2: Missing sources
    print("\n2. Testing with missing sources...")
    result = update_regression_analysis(None, 'Calidad_Total', [], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Missing sources test passed")
    
    # Test case 3: Invalid click_data structure
    print("\n3. Testing with invalid click_data structure...")
    invalid_click_data = {"invalid": "structure"}
    result = update_regression_analysis(invalid_click_data, 'Calidad_Total', ['Google Trends', 'Crossref'], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Invalid click_data structure test passed")
    
    # Test case 4: Empty click_data
    print("\n4. Testing with empty click_data...")
    result = update_regression_analysis({}, 'Calidad_Total', ['Google Trends', 'Crossref'], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Empty click_data test passed")
    
    # Test case 5: Valid click_data but missing points
    print("\n5. Testing with click_data missing points...")
    click_data_no_points = {"points": []}
    result = update_regression_analysis(click_data_no_points, 'Calidad_Total', ['Google Trends', 'Crossref'], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Click data missing points test passed")
    
    # Test case 6: Valid click_data with incomplete point
    print("\n6. Testing with click_data with incomplete point...")
    click_data_incomplete = {"points": [{"x": "Google Trends"}]}  # Missing y
    result = update_regression_analysis(click_data_incomplete, 'Calidad_Total', ['Google Trends', 'Crossref'], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Incomplete point test passed")
    
    # Test case 7: Valid click_data with same variables (diagonal)
    print("\n7. Testing with same variables (diagonal click)...")
    click_data_same = {"points": [{"x": "Google Trends", "y": "Google Trends"}]}
    result = update_regression_analysis(click_data_same, 'Calidad_Total', ['Google Trends', 'Crossref'], 'es')
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got length {len(result)}"
    print("✓ Same variables test passed")
    
    print("\n✅ All tests passed! The callback always returns a tuple.")
    return True

if __name__ == "__main__":
    try:
        test_regression_callback_return_types()
        print("\n🎉 Regression analysis callback fix v2 verified successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)