#!/usr/bin/env python3
"""
Simple test for the improved Key Findings prompt structure.
"""

import sys
from pathlib import Path

# Add the dashboard_app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "dashboard_app"))

def test_prompt_structure():
    """Test the improved prompt structure"""
    print("🧪 Testing Improved Prompt Structure...")
    
    from dashboard_app.key_findings.prompt_engineer import PromptEngineer
    
    # Test Spanish
    prompt_engineer_es = PromptEngineer(language='es')
    
    # Create sample data
    sample_data = {
        'tool_name': 'Gestión de la Cadena de Suministro',
        'selected_sources': ['Google Trends', 'Bain Usability', 'Crossref'],
        'pca_insights': {
            'dominant_patterns': [
                {
                    'component': 'PC1',
                    'variance_explained': 58.6,
                    'loadings': {
                        'Google Trends': 0.387,
                        'Bain Satisfaction': -0.380,
                        'Google Books': 0.347
                    }
                },
                {
                    'component': 'PC2', 
                    'variance_explained': 21.5,
                    'loadings': {
                        'Crossref': 0.321,
                        'Bain Usability': 0.255,
                        'Google Trends': 0.159
                    }
                }
            ],
            'total_variance_explained': 80.1
        },
        'trends_analysis': {
            'trends': {
                'Google Trends': {
                    'trend_direction': 'strong_upward',
                    'momentum': 0.15,
                    'volatility': 0.08
                },
                'Bain Satisfaction': {
                    'trend_direction': 'strong_downward', 
                    'momentum': -0.12,
                    'volatility': 0.12
                }
            },
            'anomalies': {
                'Crossref': {
                    'count': 3,
                    'percentage': 8.3,
                    'max_z_score': 2.8
                }
            }
        }
    }
    
    # Generate prompt
    prompt = prompt_engineer_es.create_analysis_prompt(sample_data, {})
    
    # Check if prompt contains new structure requirements
    checks = [
        ("Resumen Ejecutivo section", "Resumen Ejecutivo" in prompt),
        ("Hallazgos Principales section", "Hallazgos Principales" in prompt),
        ("Análisis PCA section", "Análisis PCA" in prompt),
        ("Doctoral essay requirement", "ensayo doctoral" in prompt),
        ("No bullet points instruction", "NO USE viñetas" in prompt),
        ("Temporal analysis integration", "integre análisis temporal" in prompt.lower()),
        ("Narrative format", "narrativa fluida" in prompt),
        ("New JSON structure", '"executive_summary"' in prompt),
        ("Principal findings as text", '"principal_findings"' in prompt),
        ("PCA analysis section", '"pca_analysis"' in prompt),
        ("Temporal integration guidance", "conecte los patrones temporales" in prompt.lower()),
        ("Quantitative data requirement", "datos cuantitativos específicos" in prompt),
        ("Academic language bonus", "lenguaje académico" in prompt)
    ]
    
    print("\n📋 Prompt Structure Verification:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All prompt structure checks passed!")
        
        # Show key improvements
        print("\n🔧 Key Improvements Implemented:")
        print("✅ Three-section structure (Executive, Findings, PCA)")
        print("✅ Narrative essay format instead of bullet points")
        print("✅ Temporal analysis integration instructions")
        print("✅ Quantitative data requirements")
        print("✅ Academic language emphasis")
        print("✅ New JSON structure for narrative content")
        
        # Extract sample requirements
        if "REQUISITOS DEL ANÁLISIS" in prompt:
            start = prompt.find("REQUISITOS DEL ANÁLISIS")
            end = prompt.find("FORMATO DE SALIDA", start)
            if end != -1:
                requirements = prompt[start:end]
                print(f"\n📝 Sample Requirements Section ({len(requirements)} chars):")
                print("=" * 50)
                print(requirements[:300] + "..." if len(requirements) > 300 else requirements)
                print("=" * 50)
        
        return True
    else:
        print("\n❌ Some checks failed!")
        return False

def test_english_prompt():
    """Test English prompt structure"""
    print("\n🧪 Testing English Prompt Structure...")
    
    from dashboard_app.key_findings.prompt_engineer import PromptEngineer
    
    prompt_engineer_en = PromptEngineer(language='en')
    
    sample_data = {
        'tool_name': 'Supply Chain Management',
        'selected_sources': ['Google Trends', 'Bain Usability', 'Crossref'],
        'pca_insights': {
            'dominant_patterns': [
                {
                    'component': 'PC1',
                    'variance_explained': 58.6,
                    'loadings': {
                        'Google Trends': 0.387,
                        'Bain Satisfaction': -0.380,
                        'Google Books': 0.347
                    }
                }
            ],
            'total_variance_explained': 80.1
        },
        'trends_analysis': {
            'trends': {
                'Google Trends': {
                    'trend_direction': 'strong_upward',
                    'momentum': 0.15,
                    'volatility': 0.08
                }
            }
        }
    }
    
    prompt = prompt_engineer_en.create_analysis_prompt(sample_data, {})
    
    # Check English structure
    checks = [
        ("Executive Summary section", "Executive Summary" in prompt),
        ("Principal Findings section", "Principal Findings" in prompt),
        ("PCA Analysis section", "PCA Analysis" in prompt),
        ("Doctoral essay requirement", "doctoral essay" in prompt),
        ("No bullet points instruction", "DO NOT USE bullet points" in prompt),
        ("Temporal analysis integration", "integrate temporal analysis" in prompt.lower()),
        ("Narrative format", "fluid narrative" in prompt),
        ("New JSON structure", '"executive_summary"' in prompt),
        ("Principal findings as text", '"principal_findings"' in prompt),
        ("PCA analysis section", '"pca_analysis"' in prompt)
    ]
    
    print("\n📋 English Prompt Structure Verification:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🚀 Testing Improved Key Findings Prompt Structure\n")
    
    try:
        # Test Spanish prompt
        spanish_passed = test_prompt_structure()
        
        # Test English prompt
        english_passed = test_english_prompt()
        
        if spanish_passed and english_passed:
            print("\n🎉 All prompt tests passed!")
            print("\n✅ Ready for production with improved narrative structure!")
            print("\n📊 Expected Output Structure:")
            print("1. Executive Summary: Fluid paragraph with key insights")
            print("2. Principal Findings: Doctoral essay integrating all analyses")
            print("3. PCA Analysis: Detailed analytical essay with loadings")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)