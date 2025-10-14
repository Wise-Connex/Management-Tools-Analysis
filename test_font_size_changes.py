#!/usr/bin/env python3
"""
Test script to verify font size changes in the Key Findings modal component.
"""

import re

def test_font_size_changes():
    """Test that font sizes have been reduced proportionally with smallest at 9px."""
    
    # Read the modal component file
    with open('dashboard_app/key_findings/modal_component.py', 'r') as f:
        content = f.read()
    
    # Define expected font sizes
    expected_sizes = {
        'executive_summary': '11px',
        'principal_findings': '10px', 
        'pca_analysis': '9px'
    }
    
    # Test cases with line numbers and patterns
    test_cases = [
        {
            'name': 'Executive Summary',
            'pattern': r'html\.P\(summary,.*?style=\{"lineHeight": "1\.7", "fontSize": "([^"]+)"\}',
            'expected': expected_sizes['executive_summary'],
            'line_context': 'Resumen Ejecutivo section'
        },
        {
            'name': 'Principal Findings (Hallazgos Principales)',
            'pattern': r'html\.P\(findings_text,.*?style=\{"lineHeight": "1\.6", "fontSize": "([^"]+)"\}',
            'expected': expected_sizes['principal_findings'],
            'line_context': 'Hallazgos Principales section'
        },
        {
            'name': 'PCA Analysis',
            'pattern': r'html\.P\(pca_analysis_text,.*?style=\{"lineHeight": "1\.6", "fontSize": "([^"]+)"\}',
            'expected': expected_sizes['pca_analysis'],
            'line_context': 'Análisis PCA section'
        }
    ]
    
    print("🔍 Testing font size changes in Key Findings modal...")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print(f"   Context: {test_case['line_context']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Find all matches
        matches = re.findall(test_case['pattern'], content, re.DOTALL)
        
        if matches:
            # Get the first match (most relevant)
            actual_size = matches[0]
            print(f"   Actual: {actual_size}")
            
            if actual_size == test_case['expected']:
                print("   ✅ PASS")
            else:
                print("   ❌ FAIL")
                all_passed = False
                
            # Show all matches if there are multiple
            if len(matches) > 1:
                print(f"   📝 Note: Found {len(matches)} matches total")
        else:
            print("   ❌ FAIL - Pattern not found")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    # Additional verification: check that smallest font is 9px
    font_sizes = re.findall(r'"fontSize": "([^"]+)"', content)
    px_sizes = [size for size in font_sizes if size.endswith('px')]
    
    if px_sizes:
        min_size = min(px_sizes, key=lambda x: int(x.replace('px', '')))
        print(f"\n📊 Font size analysis:")
        print(f"   Total font sizes found: {len(font_sizes)}")
        print(f"   Pixel-based sizes: {px_sizes}")
        print(f"   Smallest size: {min_size}")
        
        if min_size == '9px':
            print("   ✅ Smallest font size is correctly set to 9px")
        else:
            print("   ❌ Smallest font size is not 9px")
            all_passed = False
    else:
        print("\n❌ No pixel-based font sizes found")
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Font sizes have been reduced proportionally!")
        print("\nSummary of changes:")
        print("  • Executive Summary: 1.2rem → 11px")
        print("  • Principal Findings: 1.1rem → 10px") 
        print("  • PCA Analysis: 1rem → 9px (smallest)")
        print("\nThe 'Hallazgos principales' modal font sizes are now optimized.")
    else:
        print("❌ SOME TESTS FAILED - Please review the font size changes")
    
    return all_passed

if __name__ == "__main__":
    test_font_size_changes()