#!/usr/bin/env python3
"""
Test script to verify JSON parsing fixes for key findings report.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from key_findings.unified_ai_service import UnifiedAIService

def test_incomplete_json_pattern():
    """Test parsing of incomplete JSON pattern."""
    print("Testing incomplete JSON pattern...")

    # Sample malformed JSON from the user's task
    malformed_json = '''{"executive_summary": "El análisis de la herramienta de gestión 'Competencias Centrales' revela una brecha crítica entre la teoría y la práctica, con los primeros dos componentes explicando el 61.0% de la varianza. La tendencia temporal muestra una dinámica de adopción popular vs satisfacción real, mientras que el análisis de correlación indica una tensión entre fuentes de datos académicas y comerciales.", "principal_findings": [ "• La herramienta de gestión 'Competencias Centra...'''

    service = UnifiedAIService()
    result = service._parse_ai_response(malformed_json)

    print(f"Executive summary: {result.get('executive_summary', 'NOT FOUND')[:100]}...")
    print(f"Principal findings count: {len(result.get('principal_findings', []))}")
    if result.get('principal_findings'):
        print(f"First finding: {result['principal_findings'][0].get('bullet_point', 'NOT FOUND')[:100]}...")
    print(f"Original structure: {result.get('original_structure', 'NOT FOUND')}")
    print()

def test_bullet_json_pattern():
    """Test parsing of bullet point with JSON pattern."""
    print("Testing bullet point with JSON pattern...")

    # Sample bullet point with JSON from the user's task
    bullet_json = '''• {"executive_summary": "El análisis de la herramienta de gestión 'Competencias Centrales' revela una brecha crítica entre la teoría y la práctica, con los primeros dos componentes explicando el 61.0% de la varianza. La tendencia temporal muestra una dinámica de adopción popular vs satisfac...'''

    service = UnifiedAIService()

    # Debug the pattern detection
    is_bullet_pattern = service._is_bullet_with_json_pattern(bullet_json)
    print(f"Is bullet pattern detected: {is_bullet_pattern}")

    # Debug the extraction process
    if is_bullet_pattern:
        # Let's debug step by step
        content = bullet_json.strip()[1:].strip()  # Remove bullet point
        print(f"Content after bullet removal: {content[:100]}...")

        if content.startswith('"'):
            content = content[1:]
            print("Removed leading quote")

        if content.endswith('"'):
            content = content[:-1]
            print("Removed trailing quote")

        print(f"Final content for extraction: {content[:100]}...")

        # Check if it has executive_summary
        has_exec_summary = '"executive_summary":' in content
        print(f"Has executive_summary: {has_exec_summary}")

        extracted = service._extract_from_bullet_json_pattern(bullet_json)
        print(f"Extraction result: {extracted}")
        if extracted:
            print(f"Extracted executive summary: {extracted.get('executive_summary', 'NOT FOUND')[:100]}...")

    result = service._parse_ai_response(bullet_json)

    print(f"Executive summary: {result.get('executive_summary', 'NOT FOUND')[:100]}...")
    print(f"Principal findings count: {len(result.get('principal_findings', []))}")
    if result.get('principal_findings'):
        print(f"First finding: {result['principal_findings'][0].get('bullet_point', 'NOT FOUND')[:100]}...")
    print(f"Original structure: {result.get('original_structure', 'NOT FOUND')}")
    print()

def test_mixed_sections_pattern():
    """Test parsing of mixed markdown sections."""
    print("Testing mixed markdown sections pattern...")

    # Sample mixed content with markdown sections
    mixed_content = '''
📋 Resumen Ejecutivo
```json
{
"executive_summary": "El análisis de la herramienta de gestión 'Competencias Centrales' revela una brecha crítica entre la teoría y la práctica, con los primeros dos componentes explicando el 61.0% de la varianza. La tendencia temporal muestra una dinámica de adopción popular vs satisfacción real, mientras que el análisis de correlación indica una tensión entre fuentes de datos académicas y comerciales.",
"principal_findings": [ "• La herramienta de gestión 'Competencias Centra...
```

🔍 Hallazgos Principales
• {"executive_summary": "El análisis de la herramienta de gestión 'Competencias Centrales' revela una brecha crítica entre la teoría y la práctica, con los primeros dos componentes explicando el 61.0% de la varianza. La tendencia temporal muestra una dinámica de adopción popular vs satisfac...
'''

    service = UnifiedAIService()
    result = service._parse_ai_response(mixed_content)

    print(f"Executive summary: {result.get('executive_summary', 'NOT FOUND')[:100]}...")
    print(f"Principal findings count: {len(result.get('principal_findings', []))}")
    if result.get('principal_findings'):
        print(f"First finding: {result['principal_findings'][0].get('bullet_point', 'NOT FOUND')[:100]}...")
    print(f"Original structure: {result.get('original_structure', 'NOT FOUND')}")
    print()

def test_valid_json():
    """Test parsing of valid JSON to ensure we didn't break normal functionality."""
    print("Testing valid JSON pattern...")

    valid_json = '''{
        "executive_summary": "This is a valid executive summary.",
        "principal_findings": [
            {
                "bullet_point": "This is a valid finding.",
                "reasoning": "This is the reasoning.",
                "data_source": ["Source"],
                "confidence": "high"
            }
        ],
        "pca_insights": {}
    }'''

    service = UnifiedAIService()
    result = service._parse_ai_response(valid_json)

    print(f"Executive summary: {result.get('executive_summary', 'NOT FOUND')}")
    print(f"Principal findings count: {len(result.get('principal_findings', []))}")
    if result.get('principal_findings'):
        print(f"First finding: {result['principal_findings'][0].get('bullet_point', 'NOT FOUND')}")
    print(f"Original structure: {result.get('original_structure', 'NOT FOUND')}")
    print()

def test_realistic_malformed_patterns():
    """Test parsing with realistic malformed patterns that might occur in production."""
    print("Testing realistic malformed patterns from production...")

    # Pattern that might occur when AI generates response but gets cut off
    realistic_patterns = [
        # Pattern 1: JSON cut off mid-principal_findings (very common)
        '''{
            "executive_summary": "El análisis de Competencias Centrales revela patrones interesantes en la adopción empresarial. Los datos muestran una evolución significativa desde su introducción, con diferentes tasas de adopción según el sector industrial.",
            "principal_findings": [ "• La herramienta muestra una correlación positiva con el tamaño de la empresa (r=0.67, p<0.01), sugiriendo que las organizaciones más grandes obtienen mayores beneficios de su implementación. Esta relación se mantiene consistente a lo largo del período de análisis 1990-2023.",
            "• El análisis de componentes principales identifica tres factores principales que explican el 73.2% de la varianza: (1) madurez organizacional, (2) recursos disponibles, y (3) orientación estratégica. El primer componente explica el 45.1% de la varianza total.",
            "• La tendencia temporal indica un punto de inflexión alrededor del año 2010, momento en el que la herramienta comenzó a mostrar beneficios más consistentes. Antes de esta fecha, la implementación era más experimental."
        ]'''

        # Pattern 2: Mixed markdown with JSON fragments
        '''
📋 Resumen Ejecutivo
El análisis de la herramienta de gestión Competencias Centrales revela una evolución significativa en su adopción y aplicación empresarial.

🔍 Hallazgos Principales
• La herramienta muestra una fuerte correlación con el rendimiento organizacional (r=0.72)
• {"executive_summary": "Los datos indican que las empresas que implementan Competencias Centrales de manera sistemática obtienen un 23% mejor rendimiento que aquellas con implementación parcial.",
"principal_findings": [ "• La implementación completa de la herramienta genera beneficios significativos en términos de eficiencia operativa y toma de decisiones estratégicas."
'''
    ]

    service = UnifiedAIService()

    for i, pattern in enumerate(realistic_patterns, 1):
        print(f"\n--- Testing realistic pattern {i} ---")
        result = service._parse_ai_response(pattern)

        print(f"Executive summary: {result.get('executive_summary', 'NOT FOUND')[:100]}...")
        print(f"Principal findings count: {len(result.get('principal_findings', []))}")
        if result.get('principal_findings'):
            print(f"First finding: {result['principal_findings'][0].get('bullet_point', 'NOT FOUND')[:100]}...")
        print(f"Original structure: {result.get('original_structure', 'NOT FOUND')}")

    print()

if __name__ == "__main__":
    print("Testing JSON parsing fixes for key findings report...\n")

    test_incomplete_json_pattern()
    test_bullet_json_pattern()
    test_mixed_sections_pattern()
    test_valid_json()
    test_realistic_malformed_patterns()

    print("All tests completed!")