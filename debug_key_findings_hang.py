#!/usr/bin/env python3
"""
Debug Key Findings Hanging Issue

Tests database connectivity and checks available tools to diagnose
why the Key Findings process is hanging during data collection.
"""

import sys
import os
import time
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_database_connectivity():
    """Test basic database connectivity and available tools"""
    print("🔌 Testing database connectivity...")

    try:
        from database import get_database_manager

        db_start = time.time()
        db_manager = get_database_manager()
        db_connect_time = time.time() - db_start

        print(f"✅ Database connected in {db_connect_time:.2f}s")

        # Test available tools
        print("🔍 Checking available tools in database...")
        problematic_tool = "Alianzas y Capital de Riesgo"

        try:
            # Try to get table stats which should include available tools
            table_stats = db_manager.get_table_stats()
            print(f"✅ Retrieved table stats: {len(table_stats)} tables")

            # Extract unique keywords from table stats
            available_tools = []
            for stat in table_stats:
                if 'keyword_count' in stat and stat.get('keyword_count', 0) > 0:
                    # This is a simplified approach - in reality you'd need to query the actual keywords
                    pass

            print(f"📋 Available tables: {list(table_stats.keys())}")

            # For now, let's try a simpler approach - just test the problematic tool directly
            print(f"🔍 Testing tool: '{problematic_tool}'")

        except Exception as e:
            print(f"❌ Error querying available tools: {e}")
            import traceback
            traceback.print_exc()

        # Test data retrieval for the problematic tool
        print(f"\n🧪 Testing data retrieval for '{problematic_tool}'...")
        test_sources = ['Google Trends', 'Google Books', 'Crossref']

        try:
            data_start = time.time()
            datasets_norm, sl_sc = db_manager.get_data_for_keyword(problematic_tool, test_sources[:1])  # Test with just one source first
            data_time = time.time() - data_start

            print(f"✅ Data retrieval test completed in {data_time:.2f}s")
            print(f"   ├── Datasets retrieved: {len(datasets_norm)}")
            print(f"   ├── Source list: {sl_sc}")
            print(f"   └── Dataset keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")

            if not datasets_norm:
                print("❌ No data found for this tool")
            else:
                for key, data in datasets_norm.items():
                    print(f"   📊 Dataset '{key}': {data.shape if hasattr(data, 'shape') else 'No shape'}")

        except Exception as e:
            data_time = time.time() - data_start
            print(f"❌ Data retrieval failed after {data_time:.2f}s: {e}")
            import traceback
            traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_key_findings_components():
    """Test Key Findings components individually"""
    print("\n🔧 Testing Key Findings components...")

    try:
        from database import get_database_manager
        from dashboard_app.key_findings.data_aggregator import DataAggregator
        from dashboard_app.key_findings.prompt_engineer import PromptEngineer

        print("📦 Importing components...")
        db_manager = get_database_manager()
        data_aggregator = DataAggregator(db_manager, None)
        prompt_engineer = PromptEngineer('es')
        print("✅ Components imported successfully")

        # Test with a known working tool first
        test_tool = "Benchmarking"  # Use a simpler tool name
        test_sources = ['Google Trends']

        print(f"\n🧪 Testing with known tool '{test_tool}'...")
        try:
            collection_start = time.time()
            analysis_data = data_aggregator.collect_analysis_data(
                tool_name=test_tool,
                selected_sources=test_sources,
                language='es'
            )
            collection_time = time.time() - collection_start

            if 'error' in analysis_data:
                print(f"❌ Collection failed in {collection_time:.2f}s: {analysis_data['error']}")
            else:
                print(f"✅ Collection succeeded in {collection_time:.2f}s")
                print(f"   ├── Data points: {analysis_data.get('data_points_analyzed', 0)}")
                print(f"   └── Performance: {analysis_data.get('performance_metrics', {})}")

        except Exception as e:
            collection_time = time.time() - collection_start
            print(f"❌ Collection error after {collection_time:.2f}s: {e}")
            import traceback
            traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 STARTING KEY FINDINGS HANG DEBUGGING")
    print(f"🕒 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test database connectivity first
    db_ok = test_database_connectivity()

    if db_ok:
        # Test components
        components_ok = test_key_findings_components()

        print("\n📋 DEBUGGING SUMMARY:")
        print(f"   ├── Database connectivity: {'✅ OK' if db_ok else '❌ FAILED'}")
        print(f"   └── Components test: {'✅ OK' if components_ok else '❌ FAILED'}")

        if db_ok and components_ok:
            print("🎯 Diagnosis: Database and components are working")
            print("💡 Possible causes of hanging:")
            print("   1. The specific tool 'Alianzas y Capital de Riesgo' may not exist")
            print("   2. The tool name may need different encoding")
            print("   3. Database query may be hanging on specific data")
            print("   4. Network timeout or connection issue")
        else:
            print("❌ Basic functionality is broken")
    else:
        print("❌ Database connectivity is the main issue")

    print(f"\n✅ Debugging completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")