#!/usr/bin/env python3
"""
Fixed debug script to properly test PCA analysis with correct source mapping.

This script will test the PCA analysis with the correct tool data sources
to generate the detailed insights expected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Import database manager
from database import get_database_manager

# Import Key Findings data aggregator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))
from key_findings.data_aggregator import DataAggregator
from key_findings.database_manager import KeyFindingsDBManager

def test_key_findings_pca_with_correct_tool():
    """
    Test Key Findings PCA with correct tool and source mapping.
    """
    print("🔍 FIXED PCA ANALYSIS DEBUG SCRIPT")
    print("="*60)
    
    # Test with a tool that should have good data
    tool_name = "Calidad Total"  # This tool should have better data coverage
    selected_display_names = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    
    try:
        # Initialize Key Findings components
        db_manager = get_database_manager()
        cache_manager = None  # Not needed for this test
        data_aggregator = DataAggregator(db_manager, cache_manager)
        
        # Convert display names to source IDs using Key Findings mapping
        source_to_id = {
            "Google Trends": 1,
            "Google Books": 2,
            "Bain Usability": 3,
            "Crossref": 4,
            "Bain Satisfaction": 5
        }
        selected_source_ids = [source_to_id[name] for name in selected_display_names]
        
        print(f"Testing tool: '{tool_name}'")
        print(f"Source IDs: {selected_source_ids}")
        print(f"Display names: {selected_display_names}")
        
        # Collect analysis data using Key Findings method
        print("\n📊 Collecting analysis data...")
        analysis_data = data_aggregator.collect_analysis_data(
            tool_name=tool_name,
            selected_sources=selected_source_ids,
            language='es',
            source_display_names=selected_display_names
        )
        
        if 'error' in analysis_data:
            print(f"❌ Error in analysis: {analysis_data['error']}")
            return
        
        # Check PCA insights
        pca_insights = analysis_data.get('pca_insights', {})
        print(f"\n📈 PCA Results:")
        print(f"Total variance explained: {pca_insights.get('total_variance_explained', 0):.1f}%")
        print(f"Components analyzed: {pca_insights.get('components_analyzed', 0)}")
        print(f"Data points used: {pca_insights.get('data_points_used', 0)}")
        
        # Show dominant patterns
        dominant_patterns = pca_insights.get('dominant_patterns', [])
        print(f"\n🔍 Dominant Patterns ({len(dominant_patterns)} components):")
        
        for i, pattern in enumerate(dominant_patterns[:3]):
            component = pattern.get('component', f'PC{i+1}')
            variance = pattern.get('variance_explained', 0)
            interpretation = pattern.get('interpretation', 'No interpretation')
            pattern_type = pattern.get('pattern_type', 'unknown')
            
            print(f"\n{component} ({variance:.1f}% variance) - {pattern_type}:")
            print(f"  Interpretation: {interpretation}")
            
            # Show loadings
            loadings = pattern.get('loadings', {})
            if loadings:
                print(f"  Loadings:")
                for source, loading in sorted(loadings.items(), key=lambda x: abs(x[1]), reverse=True):
                    print(f"    {source}: {loading:.3f}")
            
            # Show source contributions
            contributions = pattern.get('source_contributions', [])
            if contributions:
                print(f"  Source contributions:")
                for contrib in contributions[:3]:  # Top 3
                    source = contrib.get('source', 'Unknown')
                    level = contrib.get('contribution_level', 'unknown')
                    direction = contrib.get('direction', 'neutral')
                    print(f"    {source}: {level} ({direction})")
        
        # Test if this matches expected detailed analysis
        print(f"\n✅ Analysis completed successfully!")
        print(f"Data points analyzed: {analysis_data.get('data_points_analyzed', 0)}")
        print(f"Sources count: {analysis_data.get('sources_count', 0)}")
        print(f"Date range: {analysis_data.get('date_range_start', 'N/A')} to {analysis_data.get('date_range_end', 'N/A')}")
        
        # Check if we have the expected detailed insights
        has_detailed_insights = (
            len(dominant_patterns) >= 2 and
            dominant_patterns[0].get('variance_explained', 0) > 20 and
            len(dominant_patterns[0].get('loadings', {})) >= 3
        )
        
        if has_detailed_insights:
            print(f"\n🎉 SUCCESS: Detailed PCA insights generated!")
            print(f"✅ Multiple components with meaningful variance")
            print(f"✅ Detailed loadings analysis available")
            print(f"✅ Pattern interpretation generated")
        else:
            print(f"\n⚠️ LIMITED: PCA insights could be more detailed")
            print(f"Consider using a tool with better data coverage")
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_tools():
    """Test multiple tools to find one with good data coverage."""
    print("\n" + "="*60)
    print("TESTING MULTIPLE TOOLS FOR DATA COVERAGE")
    print("="*60)
    
    # Tools to test
    test_tools = [
        "Calidad Total",
        "Gestión del Conocimiento", 
        "Reingeniería de Procesos",
        "Benchmarking",
        "Competencias Centrales"
    ]
    
    selected_display_names = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    source_to_id = {
        "Google Trends": 1,
        "Google Books": 2,
        "Bain Usability": 3,
        "Crossref": 4,
        "Bain Satisfaction": 5
    }
    selected_source_ids = [source_to_id[name] for name in selected_display_names]
    
    best_tool = None
    best_variance = 0
    best_results = None
    
    try:
        db_manager = get_database_manager()
        cache_manager = None
        data_aggregator = DataAggregator(db_manager, cache_manager)
        
        for tool_name in test_tools:
            print(f"\n🔍 Testing tool: '{tool_name}'")
            
            try:
                analysis_data = data_aggregator.collect_analysis_data(
                    tool_name=tool_name,
                    selected_sources=selected_source_ids,
                    language='es',
                    source_display_names=selected_display_names
                )
                
                if 'error' in analysis_data:
                    print(f"  ❌ Error: {analysis_data['error']}")
                    continue
                
                pca_insights = analysis_data.get('pca_insights', {})
                variance = pca_insights.get('total_variance_explained', 0)
                components = pca_insights.get('components_analyzed', 0)
                data_points = analysis_data.get('data_points_analyzed', 0)
                
                print(f"  ✅ Variance: {variance:.1f}%, Components: {components}, Data points: {data_points}")
                
                # Check if this is better than previous best
                if components >= 2 and variance > best_variance and data_points > 50:
                    best_tool = tool_name
                    best_variance = variance
                    best_results = analysis_data
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                continue
        
        if best_tool:
            print(f"\n🎉 BEST TOOL FOUND: '{best_tool}' with {best_variance:.1f}% variance explained")
            return best_results
        else:
            print(f"\n⚠️ No tool with sufficient multi-source data found")
            return None
            
    except Exception as e:
        print(f"❌ Error in multi-tool testing: {e}")
        return None

def main():
    """Main function to run the fixed PCA analysis"""
    print("🔍 FIXED PCA ANALYSIS DEBUG SCRIPT")
    print("="*60)
    
    # First test with a specific tool
    results = test_key_findings_pca_with_correct_tool()
    
    if not results or results.get('pca_insights', {}).get('components_analyzed', 0) < 2:
        print(f"\n⚠️ First test limited, trying multiple tools...")
        results = test_multiple_tools()
    
    if results:
        print(f"\n🎉 FINAL RESULTS:")
        pca_insights = results.get('pca_insights', {})
        print(f"Tool: {results.get('tool_name', 'Unknown')}")
        print(f"Total variance explained: {pca_insights.get('total_variance_explained', 0):.1f}%")
        print(f"Components analyzed: {pca_insights.get('components_analyzed', 0)}")
        print(f"Data points: {results.get('data_points_analyzed', 0)}")
        
        # Show if this meets the expected criteria
        dominant_patterns = pca_insights.get('dominant_patterns', [])
        if len(dominant_patterns) >= 2:
            pc1_variance = dominant_patterns[0].get('variance_explained', 0)
            pc2_variance = dominant_patterns[1].get('variance_explained', 0)
            combined_variance = pc1_variance + pc2_variance
            
            print(f"\n📊 First two components combined: {combined_variance:.1f}% variance")
            
            if combined_variance >= 60:
                print(f"✅ EXCELLENT: Strong explanatory power for detailed analysis")
            elif combined_variance >= 40:
                print(f"✅ GOOD: Sufficient for meaningful insights")
            else:
                print(f"⚠️ LIMITED: May need more data sources for robust analysis")
    else:
        print(f"\n❌ No successful PCA analysis generated")

if __name__ == "__main__":
    main()