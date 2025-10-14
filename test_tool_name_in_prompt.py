#!/usr/bin/env python3
"""
Test script to verify that the AI mentions the tool name in key findings analysis.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from dashboard_app.key_findings.unified_ai_service import UnifiedAIService
from dashboard_app.key_findings.prompt_engineer import PromptEngineer

async def test_tool_name_in_prompt():
    """Test that the AI includes the tool name in its response."""
    
    # Initialize services
    ai_service = UnifiedAIService()
    prompt_engineer = PromptEngineer(language='es')
    
    # Create test data with a specific tool name
    test_data = {
        'tool_name': 'Alianzas y Capital de Riesgo',
        'selected_sources': ['Google Trends', 'Google Books', 'Bain Usability', 'Bain Satisfaction', 'Crossref'],
        'pca_insights': {
            'dominant_patterns': [
                {
                    'interpretation': 'Component 1 represents adoption dynamics',
                    'variance_explained': 45.2,
                    'loadings': {
                        'Google Trends': 0.45,
                        'Bain Usability': 0.38,
                        'Bain Satisfaction': -0.42,
                        'Crossref': -0.15,
                        'Google Books': 0.12
                    }
                },
                {
                    'interpretation': 'Component 2 represents academic influence',
                    'variance_explained': 32.1,
                    'loadings': {
                        'Crossref': 0.67,
                        'Google Books': 0.23,
                        'Google Trends': -0.18,
                        'Bain Usability': -0.11,
                        'Bain Satisfaction': -0.09
                    }
                }
            ],
            'total_variance_explained': 77.3,
            'tool_name': 'Alianzas y Capital de Riesgo'
        },
        'statistical_summary': {
            'source_statistics': {
                'Google Trends': {'mean': 25.3, 'std': 12.1, 'trend': {'trend_direction': 'moderate_upward', 'significance': 'significant'}},
                'Bain Satisfaction': {'mean': 18.7, 'std': 8.9, 'trend': {'trend_direction': 'moderate_downward', 'significance': 'significant'}}
            }
        },
        'trends_analysis': {
            'trends': {
                'Google Trends': {'trend_direction': 'moderate_upward', 'momentum': 0.234, 'volatility': 0.156},
                'Bain Satisfaction': {'trend_direction': 'moderate_downward', 'momentum': -0.189, 'volatility': 0.134}
            },
            'anomalies': {
                'Google Trends': {'count': 3, 'percentage': 1.2, 'max_z_score': 2.34}
            }
        },
        'data_quality': {
            'overall_score': 85.2,
            'completeness': {
                'Google Trends': {'completeness_percentage': 95.3, 'missing_percentage': 4.7},
                'Bain Satisfaction': {'completeness_percentage': 89.1, 'missing_percentage': 10.9}
            },
            'timeliness': {
                'latest_date': '2023-12-01',
                'days_since_latest': 45,
                'timeliness_score': 92.3
            }
        },
        'date_range_start': '1950-01-01',
        'date_range_end': '2023-12-01',
        'data_points_analyzed': 888
    }
    
    # Generate prompt
    prompt = prompt_engineer.create_analysis_prompt(test_data, {'analysis_type': 'comprehensive'})
    
    print("=" * 80)
    print("TEST: Verifying AI includes tool name in response")
    print("=" * 80)
    print(f"Tool name to test: 'Alianzas y Capital de Riesgo'")
    print(f"Prompt length: {len(prompt)} characters")
    print("\n" + "=" * 80)
    print("PROMPT PREVIEW (first 500 characters):")
    print("=" * 80)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("\n" + "=" * 80)
    
    # Generate AI analysis
    print("Generating AI analysis...")
    result = await ai_service.generate_analysis(prompt, language='es')
    
    if result['success']:
        content = result['content']
        executive_summary = content.get('executive_summary', '')
        principal_findings = content.get('principal_findings', '')
        pca_analysis = content.get('pca_analysis', '')
        
        print("\n" + "=" * 80)
        print("AI RESPONSE ANALYSIS:")
        print("=" * 80)
        
        # Check if tool name is mentioned
        tool_name = 'Alianzas y Capital de Riesgo'
        
        print(f"\n1. Checking Executive Summary for tool name...")
        if tool_name.lower() in executive_summary.lower():
            print("✅ Tool name FOUND in Executive Summary")
        else:
            print("❌ Tool name NOT FOUND in Executive Summary")
        
        print(f"\n2. Checking Principal Findings for tool name...")
        if isinstance(principal_findings, list):
            # If it's a list of bullet points
            found_in_bullets = any(tool_name.lower() in str(bullet).lower() for bullet in principal_findings)
            if found_in_bullets:
                print("✅ Tool name FOUND in Principal Findings")
            else:
                print("❌ Tool name NOT FOUND in Principal Findings")
        else:
            # If it's a text string
            if tool_name.lower() in principal_findings.lower():
                print("✅ Tool name FOUND in Principal Findings")
            else:
                print("❌ Tool name NOT FOUND in Principal Findings")
        
        print(f"\n3. Checking PCA Analysis for tool name...")
        if tool_name.lower() in pca_analysis.lower():
            print("✅ Tool name FOUND in PCA Analysis")
        else:
            print("❌ Tool name NOT FOUND in PCA Analysis")
        
        # Overall check
        overall_found = (
            tool_name.lower() in executive_summary.lower() or
            (tool_name.lower() in principal_findings.lower() if isinstance(principal_findings, str) else any(tool_name.lower() in str(bullet).lower() for bullet in principal_findings)) or
            tool_name.lower() in pca_analysis.lower()
        )
        
        print("\n" + "=" * 80)
        print("OVERALL RESULT:")
        print("=" * 80)
        if overall_found:
            print("✅ SUCCESS: Tool name is mentioned in the AI response!")
        else:
            print("❌ FAILURE: Tool name is NOT mentioned in the AI response!")
            print("\nDebug info:")
            print(f"- Model used: {result.get('model_used', 'Unknown')}")
            print(f"- Response time: {result.get('response_time_ms', 0)}ms")
            print(f"- Token count: {result.get('token_count', 0)}")
        
        # Show response preview
        print("\n" + "=" * 80)
        print("RESPONSE PREVIEW:")
        print("=" * 80)
        print(f"Executive Summary ({len(executive_summary)} chars): {executive_summary[:200]}...")
        if isinstance(principal_findings, list):
            print(f"Principal Findings ({len(principal_findings)} bullets):")
            for i, bullet in enumerate(principal_findings[:2]):
                print(f"  {i+1}. {str(bullet)[:100]}...")
        else:
            print(f"Principal Findings ({len(principal_findings)} chars): {principal_findings[:200]}...")
        print(f"PCA Analysis ({len(pca_analysis)} chars): {pca_analysis[:200]}...")
        
    else:
        print(f"❌ AI analysis failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_tool_name_in_prompt())