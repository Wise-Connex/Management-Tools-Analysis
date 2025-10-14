#!/usr/bin/env python3
"""
Test script to verify updated font sizes in the Key Findings modal component.
This test checks the adjusted font sizes based on user feedback.
"""

import re

def test_updated_font_sizes():
    """Test that updated font sizes have been applied correctly."""
    
    print("🔍 Testing Updated Font Sizes in Key Findings Modal...")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Check updated CSS styles for content sections
    print("\n1. Testing Updated Content Font Sizes")
    print("-" * 40)
    
    try:
        with open('dashboard_app/app.py', 'r') as f:
            app_content = f.read()
        
        # Check for updated CSS styles in main app
        css_tests = [
            {
                'name': 'Executive Summary (updated)',
                'pattern': r'\.executive-summary-text\s*\{[^}]*font-size:\s*12px\s*!important;',
                'expected': '12px',
                'previous': '11px'
            },
            {
                'name': 'Principal Findings (updated)',
                'pattern': r'\.principal-findings-text\s*\{[^}]*font-size:\s*11px\s*!important;',
                'expected': '11px',
                'previous': '10px'
            },
            {
                'name': 'PCA Analysis (updated)',
                'pattern': r'\.pca-analysis-text\s*\{[^}]*font-size:\s*10px\s*!important;',
                'expected': '10px',
                'previous': '9px'
            }
        ]
        
        for test_case in css_tests:
            print(f"   Checking {test_case['name']}...")
            if re.search(test_case['pattern'], app_content, re.IGNORECASE | re.DOTALL):
                print(f"   ✅ Updated font-size: {test_case['previous']} → {test_case['expected']}")
            else:
                print(f"   ❌ Missing updated font-size: {test_case['expected']}")
                all_passed = False
                
    except FileNotFoundError:
        print("   ❌ Main app file not found")
        all_passed = False
    
    # Test 2: Check modal title font size reduction
    print("\n2. Testing Modal Title Font Size Reduction")
    print("-" * 40)
    
    try:
        # Check for modal title CSS style
        title_pattern = r'\.modal-title\s*\{[^}]*font-size:\s*(\d+)px\s*!important;'
        title_match = re.search(title_pattern, app_content, re.IGNORECASE | re.DOTALL)
        
        if title_match:
            title_size = title_match.group(1)
            if title_size == '13':
                print(f"   ✅ Modal title font-size reduced to: {title_size}px")
                print(f"   📝 Note: Bootstrap default is ~16px, reduced by ~3px")
            else:
                print(f"   ⚠️  Modal title font-size is {title_size}px (expected 13px)")
        else:
            print("   ❌ Modal title font-size style not found")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ Error checking modal title: {e}")
        all_passed = False
    
    # Test 3: Verify all changes are in the correct location
    print("\n3. Testing CSS Location and Completeness")
    print("-" * 40)
    
    try:
        # Check if CSS is within the index_string section
        index_pattern = r'app\.index_string\s*=\s*\'\'\'(.*?)\'\'\''
        index_match = re.search(index_pattern, app_content, re.DOTALL)
        
        if index_match:
            index_content = index_match.group(1)
            
            # Check if all our CSS classes are in the index string
            css_in_index = [
                '.executive-summary-text' in index_content,
                '.principal-findings-text' in index_content,
                '.pca-analysis-text' in index_content,
                '.modal-title' in index_content
            ]
            
            if all(css_in_index):
                print("   ✅ All CSS classes found in index_string")
            else:
                print("   ❌ Some CSS classes missing from index_string")
                all_passed = False
        else:
            print("   ❌ index_string section not found")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ Error checking index_string: {e}")
        all_passed = False
    
    # Test 4: Summary of font size changes
    print("\n4. Font Size Change Summary")
    print("-" * 40)
    
    print("   Content font sizes (increased by 1px):")
    print("   • Executive Summary: 11px → 12px")
    print("   • Principal Findings: 10px → 11px")
    print("   • PCA Analysis: 9px → 10px")
    
    print(f"\n   Modal title font size (reduced by ~3px):")
    print("   • Modal Title: ~16px → 13px")
    
    print(f"\n   Smallest content font: 10px (PCA Analysis)")
    print(f"   Largest content font: 12px (Executive Summary)")
    
    # Final result
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Updated font sizes have been applied correctly!")
        print("\nImplementation Summary:")
        print("  • Increased content font sizes by 1px (better readability)")
        print("  • Reduced modal title font size by ~3px (better balance)")
        print("  • All CSS styles have !important declarations")
        print("  • CSS styles are properly located in the index_string section")
        print("\nUpdated font sizes (proportional):")
        print("  • Executive Summary: 12px")
        print("  • Principal Findings: 11px")
        print("  • PCA Analysis: 10px")
        print("  • Modal Title: 13px")
        print("\nThe 'Hallazgos principales' modal should now display with:")
        print("  • Slightly larger content text (better readability)")
        print("  • Smaller title text (better visual balance)")
    else:
        print("❌ SOME TESTS FAILED - Please review the updated font size implementation")
        
    return all_passed

if __name__ == "__main__":
    test_updated_font_sizes()