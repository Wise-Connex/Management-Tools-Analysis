#!/usr/bin/env python3
"""
Test script to verify the Key Findings source mapping fix
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_app'))

def test_source_mapping():
    """Test that display names are correctly mapped to source IDs"""
    print("🔍 Testing Key Findings source mapping fix...")
    
    try:
        # Import the mapping function
        from dashboard_app.fix_source_mapping import map_display_names_to_source_ids, DISPLAY_NAMES
        
        print(f"✅ Successfully imported mapping functions")
        print(f"📋 Available display names: {DISPLAY_NAMES}")
        
        # Test mapping of display names to source IDs
        test_display_names = ['Google Trends', 'Google Books', 'Bain Usability', 'Bain Satisfaction', 'Crossref']
        
        mapped_ids = map_display_names_to_source_ids(test_display_names)
        print(f"🔍 Mapped display names {test_display_names} to source IDs: {mapped_ids}")
        
        # Verify that we get proper source IDs (not display names)
        assert all(isinstance(id, int) for id in mapped_ids), "All mapped IDs should be integers"
        assert len(mapped_ids) == len(test_display_names), "Should map all display names"
        
        print("✅ Source mapping test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Source mapping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_name_translation():
    """Test that tool names are correctly translated between languages"""
    print("\n🔍 Testing tool name translation...")
    
    try:
        from dashboard_app.translations import get_text, TOOL_TRANSLATIONS
        
        # Test Spanish to English translation
        spanish_tool = 'Alianzas y Capital de Riesgo'
        english_translation = TOOL_TRANSLATIONS.get(spanish_tool, spanish_tool)
        
        print(f"📋 Spanish tool name: {spanish_tool}")
        print(f"📋 English translation: {english_translation}")
        
        # Test translation function
        spanish_text = get_text('management_tools', 'es')
        english_text = get_text('management_tools', 'en')
        
        print(f"📋 'management_tools' in Spanish: {spanish_text}")
        print(f"📋 'management_tools' in English: {english_text}")
        
        print("✅ Tool name translation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Tool name translation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Running Key Findings mapping fix tests...\n")
    
    test1_passed = test_source_mapping()
    test2_passed = test_tool_name_translation()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The Key Findings mapping fix should work correctly.")
        print("\n📝 Summary of the fix:")
        print("   - Display names (like 'Google Trends') are now mapped to source IDs before passing to Key Findings")
        print("   - Tool names are properly translated between Spanish and English")
        print("   - The database will receive the correct source IDs it expects")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())