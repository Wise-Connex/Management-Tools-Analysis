#!/usr/bin/env python3
"""
Test script for the improved Key Findings report generation.

This script tests the new structure that generates narrative essays
instead of bullet points, with proper temporal analysis integration.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the dashboard_app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "dashboard_app"))

from dashboard_app.key_findings.prompt_engineer import PromptEngineer
from dashboard_app.key_findings.data_aggregator import DataAggregator
from dashboard_app.key_findings.key_findings_service import KeyFindingsService

# Mock database manager for testing
class MockDBManager:
    def __init__(self):
        self.connection = None
    
    def get_data_for_keyword(self, tool_name, selected_sources):
        """Mock data for testing"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Generate sample data
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
        
        datasets = {}
        for source_id in selected_sources:
            # Create different patterns for each source
            if source_id == 1:  # Google Trends - growing trend
                data = np.linspace(10, 100, len(dates)) + np.random.normal(0, 5, len(dates))
            elif source_id == 2:  # Google Books - stable with some variation
                data = np.full(len(dates), 50) + np.random.normal(0, 10, len(dates))
            elif source_id == 3:  # Bain Usability - declining trend
                data = np.linspace(80, 30, len(dates)) + np.random.normal(0, 5, len(dates))
            elif source_id == 4:  # Crossref - academic pattern
                data = 20 + 10 * np.sin(np.linspace(0, 4*np.pi, len(dates))) + np.random.normal(0, 3, len(dates))
            else:  # Bain Satisfaction - inverse to popularity
                data = np.linspace(70, 20, len(dates)) + np.random.normal(0, 8, len(dates))
            
            # Ensure positive values
            data = np.maximum(data, 1)
            
            df = pd.DataFrame({
                'value': data
            }, index=dates)
            
            datasets[source_id] = df
        
        return datasets, selected_sources

def test_prompt_engineer():
    """Test the improved prompt engineer"""
    print("🧪 Testing Prompt Engineer...")
    
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
    assert "Resumen Ejecutivo" in prompt, "Missing Resumen Ejecutivo section"
    assert "Hallazgos Principales" in prompt, "Missing Hallazgos Principales section"
    assert "Análisis PCA" in prompt, "Missing Análisis PCA section"
    assert "ensayo doctoral" in prompt, "Missing doctoral essay requirement"
    assert "NO USE viñetas" in prompt, "Missing no bullet points instruction"
    assert "integre análisis temporal" in prompt.lower(), "Missing temporal analysis integration"
    
    print("✅ Prompt Engineer test passed!")
    return prompt

def test_new_json_structure():
    """Test the new JSON structure handling"""
    print("🧪 Testing New JSON Structure...")
    
    # Sample new structure
    sample_response = {
        "executive_summary": "El análisis PCA revela una brecha crítica entre la adopción popular y la satisfacción real, con un 80.1% de varianza explicada por los primeros dos componentes.",
        "principal_findings": "El análisis de componentes principales muestra una tensión fundamental entre el interés público en la herramienta de gestión y la satisfacción real de los usuarios. Google Trends presenta una carga positiva de +0.387, indicando fuerte adopción popular, mientras que Bain Satisfaction muestra una carga negativa de -0.380, sugiriendo insatisfacción a pesar de la popularidad. Este patrón revela una brecha teoría-práctica crítica que debe ser abordada.",
        "pca_analysis": "El primer componente principal (58.6% de varianza) captura la dinámica de adopción versus satisfacción. La carga positiva de Google Trends (+0.387) y Google Books (+0.347) indica alineación con el interés público, mientras que la carga negativa de Bain Satisfaction (-0.380) revela desconexión entre popularidad y efectividad. El segundo componente (21.5% de varianza) representa factores independientes como la producción académica (Crossref: +0.321) que operan en un espacio ortogonal al hype comercial."
    }
    
    # Test confidence score calculation
    from dashboard_app.key_findings.key_findings_service import KeyFindingsService
    
    mock_db = MockDBManager()
    service = KeyFindingsService(mock_db)
    
    confidence = service._calculate_confidence_score(sample_response)
    
    assert confidence > 0.5, f"Confidence score too low: {confidence}"
    assert isinstance(confidence, float), "Confidence should be a float"
    assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    
    print("✅ New JSON Structure test passed!")
    return confidence

def test_modal_component():
    """Test the modal component with new structure"""
    print("🧪 Testing Modal Component...")
    
    from dashboard_app.key_findings.modal_component import KeyFindingsModal
    
    # Create mock app and language store
    class MockApp:
        pass
    
    class MockLanguageStore:
        pass
    
    modal = KeyFindingsModal(MockApp(), MockLanguageStore())
    
    # Test new display methods
    sample_report = {
        'executive_summary': 'Test executive summary with variance explanation of 80.1%',
        'principal_findings': 'Test narrative findings integrating temporal and PCA analysis',
        'pca_analysis': 'Test detailed PCA analysis with loading interpretations',
        'model_used': 'test-model',
        'response_time_ms': 1500,
        'data_points_analyzed': 217
    }
    
    # Test new display methods
    executive_section = modal._create_executive_summary_section(sample_report['executive_summary'])
    findings_section = modal._create_principal_findings_narrative_section(sample_report['principal_findings'])
    pca_section = modal._create_pca_analysis_section(sample_report['pca_analysis'])
    
    assert executive_section is not None, "Executive summary section should not be None"
    assert findings_section is not None, "Findings section should not be None"
    assert pca_section is not None, "PCA section should not be None"
    
    print("✅ Modal Component test passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Improved Key Findings Tests\n")
    
    try:
        # Test individual components
        prompt = test_prompt_engineer()
        confidence = test_new_json_structure()
        modal_test = test_modal_component()
        
        print("\n🎉 All tests passed!")
        print(f"📊 Sample confidence score: {confidence:.2f}")
        print("\n📋 Key Improvements Verified:")
        print("✅ New prompt structure with narrative requirements")
        print("✅ Temporal analysis integration instructions")
        print("✅ No bullet points enforcement")
        print("✅ Three-section structure (Executive, Findings, PCA)")
        print("✅ Updated confidence score calculation")
        print("✅ Modal component handles new structure")
        
        print("\n🔧 Ready for production testing!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import numpy as np  # Needed for mock data
    success = main()
    sys.exit(0 if success else 1)