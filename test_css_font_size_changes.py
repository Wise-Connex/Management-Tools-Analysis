#!/usr/bin/env python3
"""
Test script to verify CSS font size changes in the Key Findings modal component.
This test checks both the modal component classes and the CSS styles in the main app.
"""

import re

def test_css_font_size_changes():
    """Test that CSS font size classes have been applied correctly."""
    
    print("🔍 Testing CSS font size changes in Key Findings modal...")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Check modal component has correct CSS classes
    print("\n1. Testing Modal Component CSS Classes")
    print("-" * 40)
    
    try:
        with open('dashboard_app/key_findings/modal_component.py', 'r') as f:
            modal_content = f.read()
        
        # Check for CSS classes in modal component
        class_tests = [
            {
                'name': 'Executive Summary CSS Class',
                'pattern': r'html\.P\(summary, className="lead text-justify mb-0 executive-summary-text"',
                'expected': 'executive-summary-text'
            },
            {
                'name': 'Principal Findings CSS Class',
                'pattern': r'html\.P\(findings_text, className="lead text-justify principal-findings-text"',
                'expected': 'principal-findings-text'
            },
            {
                'name': 'PCA Analysis CSS Class',
                'pattern': r'html\.P\(pca_analysis_text, className="text-justify pca-analysis-text"',
                'expected': 'pca-analysis-text'
            }
        ]
        
        for test_case in class_tests:
            print(f"   Checking {test_case['name']}...")
            if re.search(test_case['pattern'], modal_content):
                print(f"   ✅ Found CSS class: {test_case['expected']}")
            else:
                print(f"   ❌ Missing CSS class: {test_case['expected']}")
                all_passed = False
                
    except FileNotFoundError:
        print("   ❌ Modal component file not found")
        all_passed = False
    
    # Test 2: Check main app has CSS styles
    print("\n2. Testing Main App CSS Styles")
    print("-" * 40)
    
    try:
        with open('dashboard_app/app.py', 'r') as f:
            app_content = f.read()
        
        # Check for CSS styles in main app
        css_tests = [
            {
                'name': 'Executive Summary CSS Style',
                'pattern': r'\.executive-summary-text\s*\{[^}]*font-size:\s*11px\s*!important;',
                'expected': '11px'
            },
            {
                'name': 'Principal Findings CSS Style',
                'pattern': r'\.principal-findings-text\s*\{[^}]*font-size:\s*10px\s*!important;',
                'expected': '10px'
            },
            {
                'name': 'PCA Analysis CSS Style',
                'pattern': r'\.pca-analysis-text\s*\{[^}]*font-size:\s*9px\s*!important;',
                'expected': '9px'
            }
        ]
        
        for test_case in css_tests:
            print(f"   Checking {test_case['name']}...")
            if re.search(test_case['pattern'], app_content, re.IGNORECASE | re.DOTALL):
                print(f"   ✅ Found CSS style with font-size: {test_case['expected']}")
            else:
                print(f"   ❌ Missing CSS style with font-size: {test_case['expected']}")
                all_passed = False
                
    except FileNotFoundError:
        print("   ❌ Main app file not found")
        all_passed = False
    
    # Test 3: Verify CSS is in the correct location (index_string)
    print("\n3. Testing CSS Location in index_string")
    print("-" * 40)
    
    try:
        # Check if CSS is within the index_string section
        index_pattern = r'app\.index_string\s*=\s*\'\'\'(.*?)\'\'\''
        index_match = re.search(index_pattern, app_content, re.DOTALL)
        
        if index_match:
            index_content = index_match.group(1)
            
            # Check if our CSS classes are in the index string
            css_in_index = [
                '.executive-summary-text' in index_content,
                '.principal-findings-text' in index_content,
                '.pca-analysis-text' in index_content
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
    
    # Test 4: Check for !important declarations
    print("\n4. Testing CSS Specificity (!important)")
    print("-" * 40)
    
    important_checks = [
        'font-size: 11px !important' in app_content,
        'font-size: 10px !important' in app_content,
        'font-size: 9px !important' in app_content
    ]
    
    if all(important_checks):
        print("   ✅ All font sizes have !important declarations")
    else:
        print("   ❌ Some font sizes missing !important declarations")
        all_passed = False
    
    # Test 5: Summary of font sizes
    print("\n5. Font Size Summary")
    print("-" * 40)
    
    expected_sizes = {
        'Executive Summary': '11px',
        'Principal Findings': '10px',
        'PCA Analysis': '9px'
    }
    
    print("   Target font sizes (proportional reduction):")
    for section, size in expected_sizes.items():
        print(f"   • {section}: {size}")
    
    print(f"\n   Smallest font size: 9px (PCA Analysis)")
    print(f"   Largest font size: 11px (Executive Summary)")
    print(f"   Middle font size: 10px (Principal Findings)")
    
    # Final result
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - CSS font sizes have been applied correctly!")
        print("\nImplementation Summary:")
        print("  • Added CSS classes to modal component HTML elements")
        print("  • Added CSS styles with !important declarations to app.py")
        print("  • CSS styles are properly located in the index_string section")
        print("  • Proportional font sizes: 11px → 10px → 9px")
        print("\nThe 'Hallazgos principales' modal should now display with smaller font sizes.")
        print("\nTo test in browser:")
        print("  1. Open the dashboard at http://localhost:8051")
        print("  2. Select a tool and data sources")
        print("  3. Click the 'Hallazgos Principales' button")
        print("  4. Verify the text appears smaller than before")
    else:
        print("❌ SOME TESTS FAILED - Please review the CSS implementation")
        
    return all_passed

if __name__ == "__main__":
    test_css_font_size_changes()