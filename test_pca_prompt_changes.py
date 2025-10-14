#!/usr/bin/env python3
"""
Test script to verify PCA Analysis prompt changes for 3-paragraph structure
"""

import sys
import os
sys.path.append('dashboard_app')

from dashboard_app.key_findings.prompt_engineer import PromptEngineer

def test_pca_prompt_structure():
    """Test that the PCA Analysis section now requires exactly 3 paragraphs"""
    
    print("🧪 Testing PCA Analysis prompt structure changes...")
    
    # Test Spanish version
    print("\n📝 Testing Spanish prompt...")
    engineer_es = PromptEngineer(language='es')
    
    # Create mock data
    mock_data = {
        'tool_name': 'Cuadro de Mando Integral',
        'selected_sources': ['Google Trends', 'Google Books', 'Bain Usability', 'Bain Satisfaction', 'Crossref'],
        'pca_insights': {
            'dominant_patterns': [
                {
                    'interpretation': 'Test component 1',
                    'variance_explained': 45.2,
                    'loadings': {
                        'Google Trends': 0.387,
                        'Bain Satisfaction': -0.380,
                        'Crossref': 0.245
                    }
                },
                {
                    'interpretation': 'Test component 2', 
                    'variance_explained': 32.1,
                    'loadings': {
                        'Google Books': 0.412,
                        'Bain Usability': 0.298,
                        'Crossref': 0.186
                    }
                }
            ],
            'total_variance_explained': 77.3,
            'tool_name': 'Cuadro de Mando Integral'
        },
        'statistical_summary': {},
        'trends_analysis': {},
        'data_quality': {}
    }
    
    mock_context = {}
    
    # Generate prompt
    prompt_es = engineer_es.create_analysis_prompt(mock_data, mock_context)
    
    # Check for 3-paragraph requirement
    checks_passed = 0
    total_checks = 6
    
    print("🔍 Checking Spanish prompt requirements...")
    
    # Check 1: EXACTAMENTE 3 párrafos
    if "EXACTAMENTE 3 párrafos" in prompt_es:
        print("✅ Contains 'EXACTAMENTE 3 párrafos' requirement")
        checks_passed += 1
    else:
        print("❌ Missing 'EXACTAMENTE 3 párrafos' requirement")
    
    # Check 2: Párrafo 1: interpretación técnica
    if "Párrafo 1" in prompt_es and "interpretación técnica" in prompt_es:
        print("✅ Contains Párrafo 1 technical interpretation requirement")
        checks_passed += 1
    else:
        print("❌ Missing Párrafo 1 technical interpretation requirement")
    
    # Check 3: Párrafo 2: relaciones
    if "Párrafo 2" in prompt_es and "RELACIONES" in prompt_es:
        print("✅ Contains Párrafo 2 relationships requirement")
        checks_passed += 1
    else:
        print("❌ Missing Párrafo 2 relationships requirement")
    
    # Check 4: Párrafo 3: implicaciones
    if "Párrafo 3" in prompt_es and "IMPLICACIONES" in prompt_es:
        print("✅ Contains Párrafo 3 implications requirement")
        checks_passed += 1
    else:
        print("❌ Missing Párrafo 3 implications requirement")
    
    # Check 5: Output format section updated
    if "EXACTAMENTE 3 párrafos sobre componentes principales" in prompt_es:
        print("✅ Output format section updated with 3-paragraph requirement")
        checks_passed += 1
    else:
        print("❌ Output format section not updated")
    
    # Check 6: Specific instructions updated
    if "PCA Analysis DEBE tener EXACTAMENTE 3 párrafos" in prompt_es:
        print("✅ Specific instructions updated with 3-paragraph requirement")
        checks_passed += 1
    else:
        print("❌ Specific instructions not updated")
    
    print(f"\n📊 Spanish prompt: {checks_passed}/{total_checks} checks passed")
    
    # Test English version
    print("\n📝 Testing English prompt...")
    engineer_en = PromptEngineer(language='en')
    
    prompt_en = engineer_en.create_analysis_prompt(mock_data, mock_context)
    
    checks_en = 0
    total_en = 6
    
    print("🔍 Checking English prompt requirements...")
    
    # Check 1: EXACTLY 3 paragraphs
    if "EXACTLY 3 paragraphs" in prompt_en:
        print("✅ Contains 'EXACTLY 3 paragraphs' requirement")
        checks_en += 1
    else:
        print("❌ Missing 'EXACTLY 3 paragraphs' requirement")
    
    # Check 2: Paragraph 1: technical interpretation
    if "Paragraph 1" in prompt_en and "technical interpretation" in prompt_en:
        print("✅ Contains Paragraph 1 technical interpretation requirement")
        checks_en += 1
    else:
        print("❌ Missing Paragraph 1 technical interpretation requirement")
    
    # Check 3: Paragraph 2: relationships
    if "Paragraph 2" in prompt_en and "RELATIONSHIPS" in prompt_en:
        print("✅ Contains Paragraph 2 relationships requirement")
        checks_en += 1
    else:
        print("❌ Missing Paragraph 2 relationships requirement")
    
    # Check 4: Paragraph 3: implications
    if "Paragraph 3" in prompt_en and "IMPLICATIONS" in prompt_en:
        print("✅ Contains Paragraph 3 implications requirement")
        checks_en += 1
    else:
        print("❌ Missing Paragraph 3 implications requirement")
    
    # Check 5: Output format section updated
    if "EXACTLY 3 paragraphs about principal components" in prompt_en:
        print("✅ Output format section updated with 3-paragraph requirement")
        checks_en += 1
    else:
        print("❌ Output format section not updated")
    
    # Check 6: Specific instructions updated
    if "PCA Analysis MUST have EXACTLY 3 paragraphs" in prompt_en:
        print("✅ Specific instructions updated with 3-paragraph requirement")
        checks_en += 1
    else:
        print("❌ Specific instructions not updated")
    
    print(f"\n📊 English prompt: {checks_en}/{total_en} checks passed")
    
    # Overall result
    total_passed = checks_passed + checks_en
    total_possible = total_checks + total_en
    
    print(f"\n🎯 Overall result: {total_passed}/{total_possible} checks passed")
    
    if total_passed == total_possible:
        print("🎉 All checks passed! PCA Analysis prompt structure successfully updated.")
        return True
    else:
        print("⚠️  Some checks failed. Please review the prompt structure.")
        return False

if __name__ == "__main__":
    success = test_pca_prompt_structure()
    sys.exit(0 if success else 1)