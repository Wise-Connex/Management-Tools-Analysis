#!/usr/bin/env python3
"""
Test Key Findings Workflow
Tests the complete Key Findings functionality end-to-end
"""

import sys
import os
import asyncio

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_key_findings_workflow():
    """Test the complete Key Findings workflow"""
    print("🧪 Testing Key Findings Workflow")
    print("=" * 50)
    
    try:
        # Import required modules
        from key_findings import KeyFindingsService
        from key_findings.database_manager import KeyFindingsDBManager
        from database import get_database_manager
        from fix_source_mapping import map_display_names_to_source_ids
        
        print("✅ Modules imported successfully")
        
        # Initialize services
        db_manager = get_database_manager()
        config = {'key_findings_db_path': './test_key_findings.db'}
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        kf_service = KeyFindingsService(db_manager, config=config, api_key=api_key)
        print("✅ Key Findings service initialized")
        
        # Test data mapping
        test_sources = ['Google Trends', 'Crossref']
        source_ids = map_display_names_to_source_ids(test_sources)
        print(f"✅ Data mapping: {test_sources} -> {source_ids}")
        
        # Test data collection (without AI generation to save API calls)
        print("\n📊 Testing data collection...")
        analysis_data = kf_service.data_aggregator.collect_analysis_data(
            tool_name='Calidad Total',
            selected_sources=source_ids,
            language='es'
        )
        
        if 'error' in analysis_data:
            print(f"❌ Data collection failed: {analysis_data['error']}")
            return False
        else:
            print(f"✅ Data collection successful")
            print(f"   - Data points: {analysis_data.get('data_points_analyzed', 0)}")
            print(f"   - Sources: {analysis_data.get('sources_count', 0)}")
            print(f"   - Date range: {analysis_data.get('date_range_start', 'N/A')} to {analysis_data.get('date_range_end', 'N/A')}")
            
            # Check PCA insights
            pca_insights = analysis_data.get('pca_insights', {})
            if pca_insights.get('pca_success'):
                print(f"✅ PCA analysis successful")
                print(f"   - Components analyzed: {pca_insights.get('components_analyzed', 0)}")
                print(f"   - Variance explained: {pca_insights.get('total_variance_explained', 0):.2%}")
            else:
                print(f"⚠️  PCA analysis: {pca_insights.get('error', 'Unknown error')}")
        
        print("\n🎯 Key Findings workflow test completed successfully!")
        print("📝 To test AI generation:")
        print("   1. Start the dashboard: ./run_dashboard_local.sh")
        print("   2. Select 'Calidad Total' tool")
        print("   3. Select data sources")
        print("   4. Click '🧠 Generar Key Findings'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_key_findings_workflow())
    sys.exit(0 if success else 1)