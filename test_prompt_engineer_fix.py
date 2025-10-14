#!/usr/bin/env python3
"""
Test script to verify the prompt engineer fix for Key Findings functionality.
"""

import sys
import os

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def test_prompt_engineer_with_string_sources():
    """Test that the prompt engineer works correctly with string sources."""
    print("🧪 Testing prompt engineer with string sources...")
    
    try:
        from key_findings.prompt_engineer import PromptEngineer
        
        # Create a prompt engineer instance
        prompt_engineer = PromptEngineer(language='es')
        
        # Create mock analysis data with string sources (the expected format)
        analysis_data = {
            'tool_name': 'Alianzas y Capital de Riesgo',
            'selected_sources': ['Google Trends', 'Google Books', 'Bain Usability', 'Bain Satisfaction', 'Crossref'],
            'language': 'es',
            'data_points_analyzed': 240,
            'pca_insights': {
                'total_variance_explained': 1.0,
                'dominant_patterns': []
            },
            'statistical_summary': {},
            'trends_analysis': {},
            'data_quality': {}
        }
        
        # This should work without errors
        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})
        
        print("✅ SUCCESS: Prompt engineer works with string sources")
        print(f"📝 Generated prompt length: {len(prompt)} characters")
        print(f"📋 First 200 characters: {prompt[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Prompt engineer failed with string sources: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_engineer_with_int_sources():
    """Test that the prompt engineer fails with integer sources (demonstrating the original issue)."""
    print("\n🧪 Testing prompt engineer with integer sources (should fail)...")
    
    try:
        from key_findings.prompt_engineer import PromptEngineer
        
        # Create a prompt engineer instance
        prompt_engineer = PromptEngineer(language='es')
        
        # Create mock analysis data with integer sources (the problematic format)
        analysis_data = {
            'tool_name': 'Alianzas y Capital de Riesgo',
            'selected_sources': [1, 2, 3, 5, 4],  # Integer source IDs
            'language': 'es',
            'data_points_analyzed': 240,
            'pca_insights': {
                'total_variance_explained': 1.0,
                'dominant_patterns': []
            },
            'statistical_summary': {},
            'trends_analysis': {},
            'data_quality': {}
        }
        
        # This should fail with the original error
        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})
        
        print("⚠️ UNEXPECTED: Prompt engineer worked with integer sources (this should have failed)")
        return False
        
    except TypeError as e:
        if "expected str instance, int found" in str(e):
            print("✅ EXPECTED: Prompt engineer failed with integer sources (original error reproduced)")
            return True
        else:
            print(f"❌ UNEXPECTED ERROR: {e}")
            return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_data_aggregator_with_display_names():
    """Test that the data aggregator preserves display names for prompts."""
    print("\n🧪 Testing data aggregator with display names...")
    
    try:
        from key_findings.data_aggregator import DataAggregator
        from database import get_database_manager
        
        # Create a mock database manager
        db_manager = None  # We'll use a mock for this test
        
        # Create a mock cache manager
        class MockCacheManager:
            def generate_scenario_hash(self, *args, **kwargs):
                return "test_hash"
            def get_cached_report(self, *args, **kwargs):
                return None
            def cache_report(self, *args, **kwargs):
                return "test_id"
            def get_cache_stats(self, *args, **kwargs):
                return {}
            def update_cache_statistics(self, *args, **kwargs):
                pass
            def log_model_performance(self, *args, **kwargs):
                pass
            def get_database_size(self, *args, **kwargs):
                return 1024
            def verify_persistence(self, *args, **kwargs):
                return True
        
        # Create data aggregator
        data_aggregator = DataAggregator(db_manager, MockCacheManager())
        
        # Test the method signature (we can't fully test without a real database)
        import inspect
        sig = inspect.signature(data_aggregator.collect_analysis_data)
        params = list(sig.parameters.keys())
        
        print(f"📋 Method parameters: {params}")
        
        if 'source_display_names' in params:
            print("✅ SUCCESS: Data aggregator accepts source_display_names parameter")
            return True
        else:
            print("❌ FAILED: Data aggregator missing source_display_names parameter")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: Data aggregator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Key Findings prompt engineer fix...\n")
    
    results = []
    
    # Test 1: Prompt engineer with string sources (should work)
    results.append(test_prompt_engineer_with_string_sources())
    
    # Test 2: Prompt engineer with integer sources (should fail with original error)
    results.append(test_prompt_engineer_with_int_sources())
    
    # Test 3: Data aggregator with display names
    results.append(test_data_aggregator_with_display_names())
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)} tests")
    
    if all(results):
        print("\n🎉 All tests passed! The fix should resolve the Key Findings issue.")
    else:
        print("\n⚠️ Some tests failed. The fix may need additional work.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)