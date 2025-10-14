#!/usr/bin/env python3
"""
Test script to verify the tool mapping fix for Key Findings
"""

import sys
import os

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def test_tool_mapping():
    """Test the tool name mapping fix"""
    print("🔍 Testing tool name mapping fix for Key Findings...")
    
    try:
        # Import the necessary modules
        from translations import TOOL_TRANSLATIONS, get_text
        from tools import get_tool_name
        from key_findings.data_aggregator import DataAggregator
        from database import get_database_manager
        from key_findings.database_manager import KeyFindingsDBManager
        
        print("✅ Successfully imported all required modules")
        
        # Test 1: Check if the translation mapping works
        print("\n📋 Test 1: Checking translation mapping...")
        test_tool = "Alianzas y Capital de Riesgo"
        if test_tool in TOOL_TRANSLATIONS:
            english_translation = TOOL_TRANSLATIONS[test_tool]
            print(f"  Spanish: '{test_tool}' -> English: '{english_translation}'")
        else:
            print(f"  ⚠️ Tool '{test_tool}' not found in TOOL_TRANSLATIONS")
        
        # Test 2: Check if the tool exists in the database
        print("\n📋 Test 2: Checking if tool exists in database...")
        db_manager = get_database_manager()
        
        try:
            # Try to get a small sample of data for the tool
            test_sources = [1]  # Use just one source for testing
            datasets, sl_sc = db_manager.get_data_for_keyword(test_tool, test_sources)
            
            if datasets:
                print(f"  ✅ Tool '{test_tool}' exists in database with {len(datasets)} datasets")
                print(f"  📊 Dataset keys: {list(datasets.keys())}")
            else:
                print(f"  ❌ Tool '{test_tool}' not found in database")
        except Exception as e:
            print(f"  ❌ Error checking database: {e}")
        
        # Test 3: Test the DataAggregator with both Spanish and English tool names
        print("\n📋 Test 3: Testing DataAggregator with bilingual tool names...")
        
        # Create a mock cache manager for testing
        class MockCacheManager:
            def get(self, key):
                return None
            def set(self, key, value, ttl=None):
                pass
        
        try:
            data_aggregator = DataAggregator(db_manager, MockCacheManager())
            print("  ✅ DataAggregator created successfully")
            
            # Test with Spanish tool name
            print(f"  🔍 Testing with Spanish tool name: '{test_tool}'")
            try:
                # This should work now with the fix
                spanish_result = data_aggregator.collect_analysis_data(
                    tool_name=test_tool,
                    selected_sources=[1],
                    language='es'
                )
                if 'error' in spanish_result:
                    print(f"  ❌ Spanish tool name failed: {spanish_result['error']}")
                else:
                    print(f"  ✅ Spanish tool name worked: {spanish_result['data_points_analyzed']} data points")
            except Exception as e:
                print(f"  ❌ Spanish tool name failed with exception: {e}")
            
            # Test with English tool name if translation exists
            if 'en' in TOOL_TRANSLATIONS and test_tool in TOOL_TRANSLATIONS['en']:
                english_tool_name = TOOL_TRANSLATIONS['en'][test_tool]
                print(f"  🔍 Testing with English tool name: '{english_tool_name}'")
                try:
                    # This should also work now with the fix
                    english_result = data_aggregator.collect_analysis_data(
                        tool_name=english_tool_name,
                        selected_sources=[1],
                        language='en'
                    )
                    if 'error' in english_result:
                        print(f"  ❌ English tool name failed: {english_result['error']}")
                    else:
                        print(f"  ✅ English tool name worked: {english_result['data_points_analyzed']} data points")
                except Exception as e:
                    print(f"  ❌ English tool name failed with exception: {e}")
            
        except Exception as e:
            print(f"  ❌ Error creating or testing DataAggregator: {e}")
        
        print("\n🎉 Tool mapping fix test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the project root directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_mapping()