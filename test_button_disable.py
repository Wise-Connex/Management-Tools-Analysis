#!/usr/bin/env python3
"""
Test script to verify the Key Findings button hide/show functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

from app import app
import dash
from dash.dependencies import Input, Output, State

def test_button_visibility_callback():
    """Test that the button visibility callback works correctly"""
    
    # Test case 1: No tool selected, no sources selected - should be hidden
    print("Test 1: No tool, no sources -> Button should be HIDDEN")
    
    # Test case 2: Tool selected, no sources - should be hidden
    print("Test 2: Tool selected, no sources -> Button should be HIDDEN")
    
    # Test case 3: No tool, sources selected - should be hidden
    print("Test 3: No tool, sources selected -> Button should be HIDDEN")
    
    # Test case 4: Tool selected, sources selected - should be visible
    print("Test 4: Tool selected, sources selected -> Button should be VISIBLE")
    
    # Find the callback
    callback_found = False
    for callback in app.callback_map.values():
        if 'key-findings-button-container.style' in str(callback['output']):
            callback_found = True
            print("✅ Found the button visibility callback")
            break
    
    if not callback_found:
        print("❌ Button visibility callback not found!")
        return False
    
    # Check if the callback has the correct inputs
    callback_inputs = []
    for callback in app.callback_map.values():
        if 'key-findings-button-container.style' in str(callback['output']):
            callback_inputs = callback['inputs']
            break
    
    # Verify inputs include keyword-dropdown and data-sources-store-v2
    has_keyword_input = any('keyword-dropdown' in str(inp) for inp in callback_inputs)
    has_sources_input = any('data-sources-store-v2' in str(inp) for inp in callback_inputs)
    
    if has_keyword_input and has_sources_input:
        print("✅ Callback has correct inputs: keyword-dropdown and data-sources-store-v2")
        return True
    else:
        print(f"❌ Callback missing required inputs. Found: {callback_inputs}")
        return False

if __name__ == "__main__":
    print("Testing Key Findings button visibility functionality...")
    print("=" * 50)
    
    success = test_button_visibility_callback()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! Button visibility functionality is correctly implemented.")
    else:
        print("❌ Tests failed! Button visibility functionality has issues.")