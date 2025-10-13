#!/usr/bin/env python3
"""
Key Findings Performance Test Script

Tests the entire Key Findings generation process to identify performance bottlenecks
and measure response times for each component.
"""

import asyncio
import time
import logging
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging to see our debug messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('key_findings_performance.log')
    ]
)

def analyze_potential_bottlenecks():
    """Analyze and document potential performance bottlenecks"""
    print("\n" + "="*80)
    print("🔍 ANALYZING POTENTIAL PERFORMANCE BOTTLENECKS")
    print("="*80)

    bottlenecks = [
        {
            "issue": "AI Service Model Selection & Response Time",
            "description": "The AI service tries multiple models sequentially with timeouts up to 12 seconds",
            "impact": "High - Could add 30+ seconds if multiple models fail",
            "likelihood": "High - Free models often have rate limits and timeouts",
            "location": "ai_service.py - generate_analysis() method"
        },
        {
            "issue": "Database Query Performance",
            "description": "Multiple database queries to collect data from different sources",
            "impact": "Medium - Depends on database size and query optimization",
            "likelihood": "Medium - Could be slow with large datasets",
            "location": "data_aggregator.py - collect_analysis_data() method"
        },
        {
            "issue": "Complex PCA Analysis",
            "description": "PCA involves data preprocessing, scaling, and component analysis",
            "impact": "Medium - Computational intensive for large datasets",
            "likelihood": "Medium - Depends on data size and complexity",
            "location": "data_aggregator.py - extract_pca_insights() method"
        },
        {
            "issue": "Large Prompt Generation",
            "description": "Creating detailed prompts with extensive statistical data",
            "impact": "Low-Medium - Prompt creation is usually fast",
            "likelihood": "Low - String operations are typically quick",
            "location": "prompt_engineer.py - create_analysis_prompt() method"
        },
        {
            "issue": "Statistical Calculations",
            "description": "Multiple statistical summaries, correlations, and trend analyses",
            "impact": "Medium - Multiple calculations on large datasets",
            "likelihood": "Medium - Depends on data volume",
            "location": "data_aggregator.py - calculate_statistical_summaries() method"
        },
        {
            "issue": "Data Processing Pipeline",
            "description": "Converting and aligning data from multiple sources",
            "impact": "Medium - Data transformation and alignment operations",
            "likelihood": "Medium - Depends on source compatibility",
            "location": "data_aggregator.py - _create_combined_dataset() method"
        },
        {
            "issue": "Memory Usage with Large Datasets",
            "description": "Large datasets being processed in memory",
            "impact": "High - Could cause memory issues and slow performance",
            "likelihood": "Medium - Depends on dataset size",
            "location": "Throughout the pipeline"
        }
    ]

    for i, bottleneck in enumerate(bottlenecks, 1):
        print(f"\n{i}. {bottleneck['issue']}")
        print(f"   Description: {bottleneck['description']}")
        print(f"   Impact: {bottleneck['impact']}")
        print(f"   Likelihood: {bottleneck['likelihood']}")
        print(f"   Location: {bottleneck['location']}")

    print(f"\n📊 SUMMARY: {len(bottlenecks)} potential bottlenecks identified")
    print("="*80)

    return bottlenecks

async def test_ai_service_performance():
    """Test AI service response times"""
    print("\n" + "="*80)
    print("🤖 TESTING AI SERVICE PERFORMANCE")
    print("="*80)

    try:
        from dashboard_app.key_findings.ai_service import get_openrouter_service

        # Check if API key is available
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY not found in environment variables")
            print("   Please set your OpenRouter API key to test AI service performance")
            return None

        print(f"🔑 API key found: {api_key[:10]}...")
        print("🚀 Initializing AI service...")

        # Initialize service
        ai_service = get_openrouter_service(api_key)

        # Test model availability
        print("🔍 Testing model availability...")
        availability_start = time.time()
        availability = await ai_service.test_model_availability()
        availability_time = time.time() - availability_start

        available_models = [model for model, available in availability.items() if available]
        unavailable_models = [model for model, available in availability.items() if not available]

        print(f"✅ Model availability test completed in {availability_time:.2f}s")
        print(f"   Available models: {len(available_models)}")
        print(f"   Unavailable models: {len(unavailable_models)}")

        if available_models:
            print(f"   ✅ {', '.join(available_models[:3])}" + ("..." if len(available_models) > 3 else ""))
        if unavailable_models:
            print(f"   ❌ {', '.join(unavailable_models[:3])}" + ("..." if len(unavailable_models) > 3 else ""))

        # Test individual model performance
        if available_models:
            test_prompt = "Test prompt for performance measurement. Please respond with 'OK'."
            print("\n🚀 Testing individual model performance...")
            for model in available_models[:2]:  # Test first 2 available models
                print(f"\n🔄 Testing {model}...")
                model_start = time.time()

                try:
                    result = await ai_service._call_model(test_prompt, model, 'en')
                    model_time = time.time() - model_start

                    if result and 'choices' in result:
                        tokens = result.get('usage', {}).get('total_tokens', 0)
                        print(f"   ✅ {model} responded in {model_time:.2f}s with {tokens} tokens")
                    else:
                        print(f"   ⚠️ {model} returned invalid response after {model_time:.2f}s")

                except Exception as e:
                    model_time = time.time() - model_start
                    print(f"   ❌ {model} failed after {model_time:.2f}s: {e}")

        return {
            'availability_test_time': availability_time,
            'available_models': available_models,
            'unavailable_models': unavailable_models
        }

    except Exception as e:
        print(f"❌ Error testing AI service: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_data_collection_performance():
    """Test data collection performance without AI calls"""
    print("\n" + "="*80)
    print("📊 TESTING DATA COLLECTION PERFORMANCE")
    print("="*80)

    try:
        from database import get_database_manager
        from dashboard_app.key_findings.data_aggregator import DataAggregator
        from dashboard_app.key_findings.prompt_engineer import PromptEngineer

        print("🔌 Connecting to database...")
        db_manager = get_database_manager()

        # Test database connectivity
        db_start = time.time()
        try:
            # Try to get table stats as a connectivity test
            table_stats = db_manager.get_table_stats()
            db_connect_time = time.time() - db_start
            print(f"✅ Database connected in {db_connect_time:.2f}s")
            print(f"   Tables found: {len(table_stats)}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

        # Initialize components
        print("🔧 Initializing data aggregator...")
        aggregator = DataAggregator(db_manager, None)  # No cache manager for this test

        print("📝 Initializing prompt engineer...")
        prompt_engineer = PromptEngineer('es')

        # Test data collection for a sample tool
        sample_tools = ['Benchmarking', 'Business Intelligence', 'Customer Relationship Management']
        test_sources = ['Google Trends', 'Google Books', 'Crossref']

        for tool in sample_tools:
            print(f"\n🧪 Testing data collection for '{tool}'...")
            collection_start = time.time()

            try:
                # Collect analysis data (this will test the full pipeline except AI)
                analysis_data = aggregator.collect_analysis_data(
                    tool_name=tool,
                    selected_sources=test_sources,
                    language='es'
                )

                collection_time = time.time() - collection_start

                if 'error' in analysis_data:
                    print(f"   ❌ Collection failed in {collection_time:.2f}s: {analysis_data['error']}")
                else:
                    data_points = analysis_data.get('data_points_analyzed', 0)
                    pca_variance = analysis_data.get('pca_insights', {}).get('total_variance_explained', 0)

                    print(f"   ✅ Collection completed in {collection_time:.2f}s")
                    print(f"      ├── Data points: {data_points:,}")
                    print(f"      ├── PCA variance: {pca_variance:.1f}%")
                    print(f"      └── Performance: {analysis_data.get('performance_metrics', {})}")

                    # Test prompt generation
                    prompt_start = time.time()
                    prompt = prompt_engineer.create_analysis_prompt(analysis_data, {})
                    prompt_time = time.time() - prompt_start

                    print(f"   📝 Prompt generated in {prompt_time:.2f}s")
                    print(f"      ├── Prompt length: {len(prompt)} characters")
                    print(f"      └── Estimated tokens: ~{len(prompt)//4}")

            except Exception as e:
                collection_time = time.time() - collection_start
                print(f"   ❌ Collection error after {collection_time:.2f}s: {e}")
                import traceback
                traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ Error in data collection test: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_comprehensive_performance_test():
    """Run comprehensive performance test"""
    print("🚀 STARTING COMPREHENSIVE KEY FINDINGS PERFORMANCE TEST")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Analyze potential bottlenecks
    bottlenecks = analyze_potential_bottlenecks()

    # Test AI service performance
    ai_results = await test_ai_service_performance()

    # Test data collection performance
    data_results = test_data_collection_performance()

    # Generate summary
    print("\n" + "="*80)
    print("📋 PERFORMANCE TEST SUMMARY")
    print("="*80)

    print("🔍 Potential Bottlenecks Identified:")
    for i, bottleneck in enumerate(bottlenecks, 1):
        print(f"   {i}. {bottleneck['issue']} ({bottleneck['impact']})")

    if ai_results:
        print("\n🤖 AI Service Results:")
        print(f"   ├── Availability test: {ai_results['availability_test_time']:.2f}s")
        print(f"   ├── Available models: {len(ai_results['available_models'])}")
        print(f"   └── Unavailable models: {len(ai_results['unavailable_models'])}")

    if data_results:
        print("\n📊 Data Collection: ✅ Completed successfully")
    print("\n🎯 RECOMMENDATIONS:")
    print("   1. Monitor AI service model timeouts and fallback behavior")
    print("   2. Optimize database queries for large datasets")
    print("   3. Consider caching frequently accessed data")
    print("   4. Implement parallel processing where possible")
    print("   5. Add early validation to fail fast on invalid inputs")
    print(f"\n✅ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📄 Detailed logs available in: key_findings_performance.log")

if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(run_comprehensive_performance_test())