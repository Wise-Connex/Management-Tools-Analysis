#!/usr/bin/env python3
"""
Key Findings Streaming Console Test

Tests the Key Findings generation process with detailed console streaming
to show exactly what's happening at each step.
"""

import asyncio
import time
import logging
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure detailed logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('key_findings_streaming.log')
    ]
)

async def test_key_findings_streaming():
    """Test Key Findings generation with full streaming output"""
    print("🎬 STARTING KEY FINDINGS STREAMING TEST")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    try:
        # Import required modules
        print("📦 Importing modules...")
        from database import get_database_manager
        from dashboard_app.key_findings.data_aggregator import DataAggregator
        from dashboard_app.key_findings.prompt_engineer import PromptEngineer
        from dashboard_app.key_findings.ai_service import get_openrouter_service
        print("✅ Modules imported successfully")

        # Check API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY not found!")
            print("   Please set your OpenRouter API key to test AI generation")
            return

        print(f"🔑 API key found: {api_key[:10]}...")

        # Initialize components
        print("🔧 Initializing components...")
        db_manager = get_database_manager()
        ai_service = get_openrouter_service(api_key)
        data_aggregator = DataAggregator(db_manager, None)
        prompt_engineer = PromptEngineer('es')
        print("✅ Components initialized")

        # Test with sample data
        test_tool = "Benchmarking"
        test_sources = ["Google Trends", "Google Books", "Crossref"]

        print(f"\n🧪 Testing Key Findings generation for '{test_tool}'")
        print(f"📋 Sources: {test_sources}")

        # Step 1: Data Collection
        print(f"\n📊 STEP 1: Data Collection")
        print("-" * 40)
        collection_start = time.time()

        analysis_data = data_aggregator.collect_analysis_data(
            tool_name=test_tool,
            selected_sources=test_sources,
            language='es'
        )

        collection_time = time.time() - collection_start

        if 'error' in analysis_data:
            print(f"❌ Data collection failed: {analysis_data['error']}")
            return

        print(f"✅ Data collection completed in {collection_time:.2f}s")
        print(f"   ├── Data points: {analysis_data.get('data_points_analyzed', 0):,}")
        print(f"   ├── PCA variance: {analysis_data.get('pca_insights', {}).get('total_variance_explained', 0):.1f}%")
        print(f"   └── Performance metrics: {analysis_data.get('performance_metrics', {})}")

        # Step 2: Prompt Generation
        print(f"\n📝 STEP 2: Prompt Generation")
        print("-" * 40)
        prompt_start = time.time()

        prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})

        prompt_time = time.time() - prompt_start
        print(f"✅ Prompt generated in {prompt_time:.2f}s")
        print(f"   ├── Prompt length: {len(prompt)} characters")
        print(f"   ├── Estimated tokens: ~{len(prompt)//4}")
        print(f"   └── Language: {prompt_engineer.language}")

        # Show prompt preview
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        print(f"\n📋 PROMPT PREVIEW:")
        print(f"{prompt_preview}")

        # Step 3: AI Analysis
        print(f"\n🤖 STEP 3: AI Analysis")
        print("-" * 40)
        ai_start = time.time()

        print(f"🚀 Calling AI service...")
        ai_response = ai_service.generate_analysis(
            prompt=prompt,
            language='es'
        )

        ai_time = time.time() - ai_start

        if not ai_response.get('success', False):
            print(f"❌ AI analysis failed: {ai_response}")
            return

        print(f"✅ AI analysis completed in {ai_time:.2f}s")
        print(f"   ├── Model used: {ai_response.get('model_used', 'unknown')}")
        print(f"   ├── Response time: {ai_response.get('response_time_ms', 0)}ms")
        print(f"   ├── Tokens processed: {ai_response.get('token_count', 0)}")
        print(f"   └── Language: {ai_response.get('language', 'unknown')}")

        # Step 4: Response Processing
        print(f"\n📄 STEP 4: Response Processing")
        print("-" * 40)
        ai_content = ai_response.get('content', {})

        print(f"📊 Response parsed:")
        print(f"   ├── Principal findings: {len(ai_content.get('principal_findings', []))}")
        print(f"   ├── PCA insights: {len(ai_content.get('pca_insights', {}))}")
        print(f"   └── Executive summary: {len(ai_content.get('executive_summary', ''))} characters")

        # Show response preview
        if ai_content.get('principal_findings'):
            print(f"\n🔍 FIRST FINDING PREVIEW:")
            first_finding = ai_content['principal_findings'][0]
            print(f"   Bullet point: {first_finding.get('bullet_point', '')[:200]}...")
            print(f"   Confidence: {first_finding.get('confidence', 'unknown')}")
            print(f"   Data sources: {first_finding.get('data_source', [])}")

        if ai_content.get('executive_summary'):
            print(f"\n📋 EXECUTIVE SUMMARY PREVIEW:")
            summary_preview = ai_content['executive_summary'][:300] + "..." if len(ai_content['executive_summary']) > 300 else ai_content['executive_summary']
            print(f"   {summary_preview}")

        # Final Summary
        total_time = collection_time + prompt_time + ai_time
        print(f"\n🏁 FINAL SUMMARY")
        print("-" * 40)
        print(f"⏱️ Total processing time: {total_time:.2f}s")
        print(f"   ├── Data collection: {collection_time:.2f}s ({collection_time/total_time*100:.1f}%)")
        print(f"   ├── Prompt generation: {prompt_time:.2f}s ({prompt_time/total_time*100:.1f}%)")
        print(f"   └── AI analysis: {ai_time:.2f}s ({ai_time/total_time*100:.1f}%)")

        print(f"\n✅ STREAMING TEST COMPLETED SUCCESSFULLY!")
        print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 Detailed logs in: key_findings_streaming.log")

    except Exception as e:
        print(f"\n❌ STREAMING TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_key_findings_streaming())