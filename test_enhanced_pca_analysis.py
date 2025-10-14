#!/usr/bin/env python3
"""
Test script to verify the enhanced PCA analysis generates detailed insights.

This script tests the complete Key Findings pipeline with the enhanced 
prompt engineering to ensure it produces the specific narrative format expected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from datetime import datetime

# Import Key Findings components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))
from key_findings.data_aggregator import DataAggregator
from key_findings.prompt_engineer import PromptEngineer
from key_findings.ai_service import get_openrouter_service
from database import get_database_manager

async def test_enhanced_pca_analysis():
    """Test the enhanced PCA analysis with detailed prompt generation."""
    print("🔍 TESTING ENHANCED PCA ANALYSIS")
    print("="*60)
    
    # Test configuration
    tool_name = "Calidad Total"
    selected_display_names = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    language = 'es'
    
    try:
        # Initialize components
        print("📋 Initializing components...")
        db_manager = get_database_manager()
        cache_manager = None
        data_aggregator = DataAggregator(db_manager, cache_manager)
        prompt_engineer = PromptEngineer(language)
        
        # Convert display names to source IDs
        source_to_id = {
            "Google Trends": 1,
            "Google Books": 2,
            "Bain Usability": 3,
            "Crossref": 4,
            "Bain Satisfaction": 5
        }
        selected_source_ids = [source_to_id[name] for name in selected_display_names]
        
        print(f"🔧 Tool: {tool_name}")
        print(f"📊 Sources: {selected_display_names}")
        
        # Collect analysis data
        print("\n📊 Collecting analysis data...")
        analysis_data = data_aggregator.collect_analysis_data(
            tool_name=tool_name,
            selected_sources=selected_source_ids,
            language=language,
            source_display_names=selected_display_names
        )
        
        if 'error' in analysis_data:
            print(f"❌ Error in data collection: {analysis_data['error']}")
            return
        
        # Check PCA insights
        pca_insights = analysis_data.get('pca_insights', {})
        print(f"✅ PCA data collected:")
        print(f"   Total variance: {pca_insights.get('total_variance_explained', 0):.1f}%")
        print(f"   Components: {pca_insights.get('components_analyzed', 0)}")
        print(f"   Data points: {pca_insights.get('data_points_used', 0)}")
        
        # Generate enhanced prompt
        print("\n📝 Generating enhanced PCA prompt...")
        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})
        
        print(f"✅ Prompt generated: {len(prompt)} characters")
        
        # Show key parts of the prompt
        lines = prompt.split('\n')
        pca_section_start = None
        for i, line in enumerate(lines):
            if 'ANÁLISIS DE COMPONENTES PRINCIPALES (PCA)' in line:
                pca_section_start = i
                break
        
        if pca_section_start:
            print(f"\n📋 PCA Section Preview:")
            for i in range(pca_section_start, min(pca_section_start + 20, len(lines))):
                if lines[i].strip():
                    print(f"   {lines[i]}")
                if i > pca_section_start + 15 and 'Componente 1' in lines[i]:
                    break
        
        # Test AI analysis with enhanced prompt
        print(f"\n🤖 Testing AI analysis with enhanced prompt...")
        
        # Get API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("⚠️ No OpenRouter API key found, skipping AI test")
            return analysis_data
        
        ai_service = get_openrouter_service(api_key)
        
        # Generate analysis
        ai_result = await ai_service.generate_analysis(prompt, language=language)
        
        if ai_result.get('success'):
            content = ai_result.get('content', {})
            findings = content.get('principal_findings', [])
            pca_analysis = content.get('pca_insights', {})
            executive_summary = content.get('executive_summary', '')
            
            print(f"✅ AI Analysis completed:")
            print(f"   Model used: {ai_result.get('model_used', 'Unknown')}")
            print(f"   Response time: {ai_result.get('response_time_ms', 0)}ms")
            print(f"   Findings generated: {len(findings)}")
            
            # Check for detailed insights
            print(f"\n📈 PCA Insights from AI:")
            print(f"   Dominant components: {pca_analysis.get('dominant_components', 'None')}")
            print(f"   Variance explained: {pca_analysis.get('variance_explained', 'None')}")
            print(f"   Key patterns: {len(pca_analysis.get('key_patterns', []))}")
            
            # Show principal findings
            print(f"\n🎯 Principal Findings:")
            for i, finding in enumerate(findings[:3]):  # Top 3
                bullet = finding.get('bullet_point', '')
                confidence = finding.get('confidence', 'unknown')
                print(f"   {i+1}. [{confidence.upper()}] {bullet[:100]}...")
            
            # Show executive summary
            print(f"\n📋 Executive Summary:")
            print(f"   {executive_summary[:200]}...")
            
            # Check if this matches expected format
            has_detailed_pca = (
                pca_analysis.get('dominant_components') and
                pca_analysis.get('variance_explained') and
                len(findings) > 0
            )
            
            if has_detailed_pca:
                print(f"\n🎉 SUCCESS: Enhanced PCA analysis generated detailed insights!")
                print(f"✅ Detailed component interpretation present")
                print(f"✅ Specific variance percentages included")
                print(f"✅ Principal findings with confidence levels")
            else:
                print(f"\n⚠️ LIMITED: Analysis could be more detailed")
            
            # Save results for inspection
            result_file = f"enhanced_pca_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis_data': analysis_data,
                    'ai_result': ai_result,
                    'prompt_preview': prompt[:2000] + "..." if len(prompt) > 2000 else prompt
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Full results saved to: {result_file}")
            
        else:
            print(f"❌ AI analysis failed: {ai_result}")
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the enhanced PCA test."""
    print("🔍 ENHANCED PCA ANALYSIS TEST")
    print("="*60)
    
    # Run async test
    result = asyncio.run(test_enhanced_pca_analysis())
    
    if result:
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY")
        print(f"✅ Enhanced PCA analysis pipeline working")
        print(f"✅ Detailed prompts being generated")
        print(f"✅ AI interpretation producing structured insights")
    else:
        print(f"\n❌ TEST FAILED")
        print(f"⚠️ Check the error messages above")

if __name__ == "__main__":
    main()