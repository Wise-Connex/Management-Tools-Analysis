#!/usr/bin/env python3
"""
Test script to verify the Key Findings functionality works with the actual dashboard.
This script simulates the dashboard callback that was failing.
"""

import sys
import os

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def test_key_findings_callback():
    """Test the Key Findings callback that was failing."""
    print("🧪 Testing Key Findings callback with actual dashboard components...")
    
    try:
        # Import the required modules
        from key_findings.key_findings_service import KeyFindingsService
        from key_findings.data_aggregator import DataAggregator
        from key_findings.prompt_engineer import PromptEngineer
        from fix_source_mapping import map_display_names_to_source_ids
        
        print("✅ Successfully imported Key Findings components")
        
        # Create a mock database manager
        class MockDBManager:
            def get_data_for_keyword(self, tool_name, source_ids):
                # Return mock data for testing
                import pandas as pd
                import numpy as np
                from datetime import datetime, timedelta
                
                datasets_norm = {}
                sl_sc = []
                
                # Generate mock data for each source
                for source_id in source_ids:
                    # Create a date range
                    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
                    # Generate random data
                    data = np.random.randn(len(dates)) * 10 + 50
                    # Create a DataFrame
                    df = pd.DataFrame({f'source_{source_id}': data}, index=dates)
                    datasets_norm[source_id] = df
                    sl_sc.append(source_id)
                
                return datasets_norm, sl_sc
        
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
        
        # Create instances
        db_manager = MockDBManager()
        cache_manager = MockCacheManager()
        data_aggregator = DataAggregator(db_manager, cache_manager)
        prompt_engineer = PromptEngineer()
        
        print("✅ Successfully created mock components")
        
        # Test parameters (simulating the dashboard callback)
        selected_tool = 'Alianzas y Capital de Riesgo'
        selected_sources = ['Google Trends', 'Google Books', 'Bain Usability', 'Bain Satisfaction', 'Crossref']
        language = 'es'
        
        print(f"📋 Testing with tool: {selected_tool}")
        print(f"📋 Testing with sources: {selected_sources}")
        
        # Convert display names to source IDs (as done in the dashboard)
        selected_source_ids = map_display_names_to_source_ids(selected_sources)
        print(f"🔄 Mapped to source IDs: {selected_source_ids}")
        
        # Collect analysis data (this is where the original error occurred)
        print("📊 Collecting analysis data...")
        analysis_data = data_aggregator.collect_analysis_data(
            tool_name=selected_tool,
            selected_sources=selected_source_ids,
            language=language,
            source_display_names=selected_sources
        )
        
        print("✅ Successfully collected analysis data")
        print(f"📊 Analysis data keys: {list(analysis_data.keys())}")
        print(f"📊 Selected sources in analysis data: {analysis_data.get('selected_sources', 'NOT FOUND')}")
        
        # Generate prompt (this is where the original error occurred)
        print("📝 Generating analysis prompt...")
        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})
        
        print("✅ Successfully generated analysis prompt")
        print(f"📝 Prompt length: {len(prompt)} characters")
        print(f"📋 First 200 characters: {prompt[:200]}...")
        
        # Verify the prompt contains the source names (not IDs)
        if 'Google Trends' in prompt and 'Google Books' in prompt:
            print("✅ SUCCESS: Prompt contains source display names (not IDs)")
        else:
            print("❌ FAILED: Prompt does not contain expected source names")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Key Findings callback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🔧 Testing Key Findings functionality with dashboard components...\n")
    
    success = test_key_findings_callback()
    
    # Summary
    print("\n" + "="*50)
    if success:
        print("🎉 SUCCESS: Key Findings functionality is working correctly!")
        print("The fix has resolved the original error.")
    else:
        print("⚠️ FAILED: Key Findings functionality still has issues.")
        print("The fix may need additional work.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)