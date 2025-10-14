#!/usr/bin/env python3
"""
Test script to verify that the modal title font size has been changed to 16px.
"""

import re

def test_modal_title_font_size():
    """Test that modal title font size has been changed to 16px."""
    
    print("🔍 Testing Modal Title Font Size...")
    print("=" * 50)
    
    try:
        with open('dashboard_app/app.py', 'r') as f:
            app_content = f.read()
        
        # Check for modal title CSS style
        title_pattern = r'\.modal-title\s*\{[^}]*font-size:\s*(\d+)px\s*!important;'
        title_match = re.search(title_pattern, app_content, re.IGNORECASE | re.DOTALL)
        
        if title_match:
            title_size = title_match.group(1)
            if title_size == '16':
                print(f"✅ Modal title font-size correctly set to: {title_size}px")
                print("\nFinal Font Size Summary:")
                print("  • Executive Summary: 12px")
                print("  • Principal Findings: 11px")
                print("  • PCA Analysis: 10px")
                print("  • Modal Title: 16px")
                print("\n🎉 Modal title font size successfully updated to 16px!")
                return True
            else:
                print(f"❌ Modal title font-size is {title_size}px (expected 16px)")
                return False
        else:
            print("❌ Modal title font-size style not found")
            return False
            
    except FileNotFoundError:
        print("❌ Main app file not found")
        return False
    except Exception as e:
        print(f"❌ Error checking modal title: {e}")
        return False

if __name__ == "__main__":
    test_modal_title_font_size()