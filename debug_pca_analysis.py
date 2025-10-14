#!/usr/bin/env python3
"""
Debug script to examine PCA data flow and identify why the AI analysis is basic
despite having complete PCA data.
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def debug_pca_data_flow():
    """Debug the PCA data flow to understand the issue."""
    
    print("🔍 DEBUGGING PCA DATA FLOW")
    print("=" * 50)
    
    try:
        # Import required modules
        from database import DatabaseManager
        from dashboard_app.key_findings.data_aggregator import DataAggregator
        from dashboard_app.key_findings.prompt_engineer import PromptEngineer
        from dashboard_app.key_findings.database_manager import KeyFindingsDBManager
        
        print("✅ Successfully imported required modules")
        
        # Initialize database
        db = DatabaseManager()
        print("✅ Database initialized")
        
        # Initialize Key Findings components
        kf_db_manager = KeyFindingsDBManager('/tmp/debug_key_findings.db')
        data_aggregator = DataAggregator(db, kf_db_manager)
        prompt_engineer = PromptEngineer(language='es')
        
        print("✅ Key Findings components initialized")
        
        # Test with a specific tool and sources
        tool_name = "Alianzas y Capital de Riesgo"
        selected_sources = [1, 2, 3, 4, 5]  # All sources
        
        print(f"\n📊 Testing PCA analysis for tool: {tool_name}")
        print(f"📋 Selected sources: {selected_sources}")
        
        # Step 1: Get raw data
        print("\n🔍 STEP 1: Getting raw data from database...")
        datasets_norm, sl_sc = db.get_data_for_keyword(tool_name, selected_sources)
        
        print(f"   - Retrieved {len(datasets_norm)} datasets")
        print(f"   - Source list: {sl_sc}")
        
        if not datasets_norm:
            print("❌ No data retrieved from database")
            return
        
        # Step 2: Create combined dataset
        print("\n🔍 STEP 2: Creating combined dataset...")
        combined_dataset = data_aggregator._create_combined_dataset(datasets_norm, sl_sc, tool_name)
        
        print(f"   - Combined dataset shape: {combined_dataset.shape}")
        print(f"   - Columns: {list(combined_dataset.columns)}")
        print(f"   - Date range: {combined_dataset.index.min()} to {combined_dataset.index.max()}")
        
        if combined_dataset.empty:
            print("❌ Combined dataset is empty")
            return
        
        # Step 3: Extract PCA insights
        print("\n🔍 STEP 3: Extracting PCA insights...")
        pca_insights = data_aggregator.extract_pca_insights(combined_dataset, sl_sc)
        
        print(f"   - PCA success: {pca_insights.get('pca_success', False)}")
        print(f"   - Components analyzed: {pca_insights.get('components_analyzed', 0)}")
        print(f"   - Total variance explained: {pca_insights.get('total_variance_explained', 0):.1f}%")
        print(f"   - Data points used: {pca_insights.get('data_points_used', 0)}")
        print(f"   - Dominant patterns: {len(pca_insights.get('dominant_patterns', []))}")
        
        if 'error' in pca_insights:
            print(f"❌ PCA error: {pca_insights['error']}")
            return
        
        # Step 4: Examine dominant patterns in detail
        print("\n🔍 STEP 4: Examining dominant patterns...")
        dominant_patterns = pca_insights.get('dominant_patterns', [])
        
        for i, pattern in enumerate(dominant_patterns):
            print(f"\n   📊 PATTERN {i+1}:")
            print(f"      - Component: {pattern.get('component', 'Unknown')}")
            print(f"      - Variance explained: {pattern.get('variance_explained', 0):.3f}")
            print(f"      - Pattern type: {pattern.get('pattern_type', 'Unknown')}")
            print(f"      - Interpretation: {pattern.get('interpretation', 'None')}")
            
            # Examine loadings
            loadings = pattern.get('loadings', {})
            print(f"      - Loadings ({len(loadings)} sources):")
            for source, loading in loadings.items():
                print(f"        * {source}: {loading:.4f}")
            
            # Examine source contributions
            source_contributions = pattern.get('source_contributions', [])
            print(f"      - Source contributions:")
            for contrib in source_contributions:
                print(f"        * {contrib['source']}: {contrib['contribution_level']} ({contrib['role']})")
        
        # Step 5: Create full analysis data
        print("\n🔍 STEP 5: Creating full analysis data...")
        
        # Get display names for sources
        from tools import tool_file_dic
        dbase_options = {}
        for tool_list in tool_file_dic.values():
            for i, source_key in enumerate([1, 2, 3, 4, 5]):
                if i < len(tool_list) and i < len(tool_list[1]):
                    dbase_options[source_key] = tool_list[i]
        
        source_display_names = [dbase_options.get(sid, f"Source_{sid}") for sid in selected_sources]
        
        analysis_data = {
            'tool_name': tool_name,
            'selected_sources': source_display_names,
            'selected_source_ids': selected_sources,
            'language': 'es',
            'data_points_analyzed': len(combined_dataset),
            'sources_count': len(selected_sources),
            'date_range_start': combined_dataset.index.min().strftime('%Y-%m-%d'),
            'date_range_end': combined_dataset.index.max().strftime('%Y-%m-%d'),
            'pca_insights': pca_insights,
            'statistical_summary': {},
            'trends_analysis': {},
            'data_quality': {}
        }
        
        print(f"   - Analysis data created with {len(analysis_data)} fields")
        
        # Step 6: Generate the actual prompt
        print("\n🔍 STEP 6: Generating AI prompt...")
        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {
            'analysis_type': 'comprehensive',
            'emphasis': 'pca'
        })
        
        print(f"   - Prompt length: {len(prompt)} characters")
        print(f"   - Prompt sections: {prompt.count('###')}")
        
        # Extract just the PCA section for detailed analysis
        pca_section_start = prompt.find("### ANÁLISIS DE COMPONENTES PRINCIPALES")
        if pca_section_start == -1:
            pca_section_start = prompt.find("### PRINCIPAL COMPONENT ANALYSIS")
        
        if pca_section_start != -1:
            # Find the next section after PCA
            next_section = prompt.find("\n### ", pca_section_start + 1)
            if next_section == -1:
                next_section = len(prompt)
            
            pca_section = prompt[pca_section_start:next_section]
            print(f"\n📋 PCA SECTION OF PROMPT:")
            print("=" * 50)
            print(pca_section)
            print("=" * 50)
        else:
            print("❌ PCA section not found in prompt")
        
        # Step 7: Save debug data
        print("\n🔍 STEP 7: Saving debug data...")
        debug_data = {
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'selected_sources': selected_sources,
            'source_display_names': source_display_names,
            'combined_dataset_info': {
                'shape': combined_dataset.shape,
                'columns': list(combined_dataset.columns),
                'date_range': {
                    'start': combined_dataset.index.min().strftime('%Y-%m-%d'),
                    'end': combined_dataset.index.max().strftime('%Y-%m-%d')
                },
                'sample_data': combined_dataset.head().to_dict()
            },
            'pca_insights': pca_insights,
            'prompt_pca_section': pca_section if 'pca_section' in locals() else None,
            'full_prompt_length': len(prompt)
        }
        
        with open('debug_pca_data.json', 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
        
        print("✅ Debug data saved to debug_pca_data.json")
        
        # Step 8: Analysis of the issue
        print("\n🔍 STEP 8: ANALYZING THE ISSUE")
        print("=" * 50)
        
        total_variance = pca_insights.get('total_variance_explained', 0)
        print(f"📊 Total variance explained: {total_variance:.1f}%")
        
        if total_variance < 5:
            print("⚠️  VERY LOW variance explained - this is likely the main issue!")
            print("   The AI is receiving data that shows almost no meaningful patterns.")
            print("   This explains why the analysis is basic and focuses on data quality issues.")
        elif total_variance < 20:
            print("⚠️  Low variance explained - this limits the AI's ability to provide deep insights.")
        else:
            print("✅ Variance explained seems reasonable.")
        
        # Check if there are dominant patterns
        dominant_count = len(dominant_patterns)
        print(f"📊 Number of dominant patterns: {dominant_count}")
        
        if dominant_count == 0:
            print("❌ No dominant patterns found - this is a major issue!")
        elif dominant_count == 1:
            print("⚠️  Only one dominant pattern - this limits analysis depth.")
        else:
            print("✅ Multiple patterns available for analysis.")
        
        # Check loadings distribution
        if dominant_patterns:
            first_pattern = dominant_patterns[0]
            loadings = first_pattern.get('loadings', {})
            
            if loadings:
                max_loading = max(abs(loading) for loading in loadings.values())
                min_loading = min(abs(loading) for loading in loadings.values())
                
                print(f"📊 Loading range: {min_loading:.4f} to {max_loading:.4f}")
                
                if max_loading > 0.9:
                    print("⚠️  Very high loading detected - potential single-source dominance")
                if min_loading < 0.01:
                    print("⚠️  Very low loading detected - some sources may be irrelevant")
        
        print("\n🎯 LIKELY ROOT CAUSES:")
        print("1. Low variance explained in PCA data")
        print("2. Single-source dominance (one source explains most variance)")
        print("3. AI model focusing on data quality rather than patterns")
        print("4. Prompt may not be emphasizing the rich PCA data enough")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Enhance prompt to emphasize loadings analysis and source relationships")
        print("2. Add specific instructions for interpreting low-variance scenarios")
        print("3. Include more context about the business meaning of each source")
        print("4. Add examples of how to interpret different loading patterns")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pca_data_flow()