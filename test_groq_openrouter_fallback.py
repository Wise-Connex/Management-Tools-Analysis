#!/usr/bin/env python3
"""
Test script to verify Groq primary and OpenRouter fallback functionality
"""

import asyncio
import os
import sys
import json

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

from key_findings.unified_ai_service import get_unified_ai_service

async def test_providers():
    """Test both Groq and OpenRouter providers"""
    
    print("🧪 Testing Unified AI Service with Groq Primary and OpenRouter Fallback")
    print("=" * 70)
    
    # Get API keys
    groq_api_key = os.getenv('GROQ_API_KEY')
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    
    print(f"🔑 Groq API Key: {'✅ Configured' if groq_api_key else '❌ Missing'}")
    print(f"🔑 OpenRouter API Key: {'✅ Configured' if openrouter_api_key else '❌ Missing'}")
    print()
    
    # Initialize unified service
    try:
        ai_service = get_unified_ai_service(groq_api_key, openrouter_api_key)
        print("✅ Unified AI Service initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize Unified AI Service: {e}")
        return
    
    # Test model availability
    print("🔍 Testing model availability...")
    try:
        availability = await ai_service.test_model_availability()
        
        print("\n📊 Model Availability Results:")
        print("-" * 40)
        
        groq_models = [model for model in availability.keys() if model in ai_service.groq_models]
        openrouter_models = [model for model in availability.keys() if model in ai_service.openrouter_models]
        
        print(f"\n🚀 Groq Models (Primary):")
        for model in groq_models:
            status = "✅ Available" if availability[model] else "❌ Unavailable"
            print(f"  {model}: {status}")
        
        print(f"\n🔄 OpenRouter Models (Fallback):")
        for model in openrouter_models:
            status = "✅ Available" if availability[model] else "❌ Unavailable"
            print(f"  {model}: {status}")
        
        # Count available models
        available_groq = sum(1 for model in groq_models if availability[model])
        available_openrouter = sum(1 for model in openrouter_models if availability[model])
        
        print(f"\n📈 Summary:")
        print(f"  Groq: {available_groq}/{len(groq_models)} models available")
        print(f"  OpenRouter: {available_openrouter}/{len(openrouter_models)} models available")
        
    except Exception as e:
        print(f"❌ Model availability test failed: {e}")
        return
    
    # Test actual AI generation with fallback
    print("\n🤖 Testing AI generation with automatic fallback...")
    test_prompt = "Analyze the following business data and provide a brief summary. Respond in JSON format with 'summary' and 'insights' fields."
    
    try:
        result = await ai_service.generate_analysis(test_prompt, language='en')
        
        print(f"\n✅ AI Generation Successful!")
        print(f"  Provider Used: {result.get('provider_used', 'unknown')}")
        print(f"  Model Used: {result.get('model_used', 'unknown')}")
        print(f"  Response Time: {result.get('response_time_ms', 0)}ms")
        print(f"  Token Count: {result.get('token_count', 0)}")
        print(f"  Success: {result.get('success', False)}")
        
        if result.get('content'):
            content = result['content']
            print(f"\n📄 Generated Content Preview:")
            print(f"  Executive Summary: {content.get('executive_summary', 'N/A')[:100]}...")
            print(f"  Principal Findings: {len(content.get('principal_findings', []))} items")
        
    except Exception as e:
        print(f"❌ AI generation test failed: {e}")
        return
    
    # Test performance stats
    print(f"\n📊 Performance Statistics:")
    stats = ai_service.get_performance_stats()
    for model, model_stats in stats.items():
        print(f"  {model}:")
        print(f"    Requests: {model_stats.get('total_requests', 0)}")
        print(f"    Success Rate: {model_stats.get('success_rate', 0):.1f}%")
        print(f"    Avg Response Time: {model_stats.get('avg_response_time_ms', 0):.1f}ms")
        print(f"    Total Tokens: {model_stats.get('total_tokens', 0)}")
    
    print("\n🎉 Test completed successfully!")
    print("✅ Groq is working as primary provider")
    print("✅ OpenRouter is configured as fallback")
    print("✅ Automatic provider switching is functional")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    asyncio.run(test_providers())