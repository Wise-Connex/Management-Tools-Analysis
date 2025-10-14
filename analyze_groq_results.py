#!/usr/bin/env python3
"""
Quick analysis of the Groq comparison results to debug the issue.
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def analyze_responses():
    """Analyze the raw responses from each model to debug the issue."""
    import aiohttp
    
    groq_api_key = os.getenv('GROQ_API_KEY')
    models = [
        'openai/gpt-oss-120b',
        'meta-llama/llama-4-scout-17b-16e-instruct',
        'llama-3.3-70b-versatile',
        'moonshotai/kimi-k2-instruct'
    ]
    
    # Simple test prompt
    test_prompt = """
    Responde en formato JSON con la siguiente estructura:
    {
      "executive_summary": "Resumen ejecutivo",
      "principal_findings": ["Hallazgo 1", "Hallazgo 2"],
      "pca_analysis": "Análisis PCA"
    }
    """
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    for model in models:
        print(f"\n=== Testing {model} ===")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un analista de investigación."
                },
                {
                    "role": "user",
                    "content": test_prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            print(f"Response type: {type(content)}")
                            print(f"Response length: {len(content) if hasattr(content, '__len__') else 'N/A'}")
                            print(f"Response preview: {content[:200]}...")
                            
                            # Try to parse JSON
                            try:
                                import re
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    json_str = json_match.group()
                                    parsed = json.loads(json_str)
                                    print(f"Parsed JSON keys: {list(parsed.keys())}")
                                    
                                    # Check principal_findings type
                                    pf = parsed.get('principal_findings')
                                    print(f"principal_findings type: {type(pf)}")
                                    print(f"principal_findings value: {pf}")
                                    if hasattr(pf, '__len__'):
                                        print(f"principal_findings length: {len(pf)}")
                                    
                            except Exception as e:
                                print(f"JSON parsing error: {e}")
                    else:
                        print(f"API error: {response.status}")
        except Exception as e:
            print(f"Request error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_responses())