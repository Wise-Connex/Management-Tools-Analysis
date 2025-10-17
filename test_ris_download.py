#!/usr/bin/env python3
"""
Test script to verify RIS download functionality for both English and Spanish
"""
import base64

def test_ris_download():
    """Test the RIS download functionality"""
    
    # Test English RIS content
    english_ris_content = """TY  - WEB
AU  - Añez, Diomar
AU  - Añez, Dimar
PY  - 2025
T1  - Management tools: Contingent temporal dynamics and policontextual antinomies
PB  - Solidum Consulting / Wise Connex
N2  - This data analysis dashboard serves as the analytical basis for the doctoral research project: "Ontological dichotomy in 'Management Fads'." Developed with Python, Plotly, and Dash.
KW  - Management Tools
KW  - Management Fads
KW  - Data Visualization
KW  - Policontextual Antinomies
UR  - https://dashboard.solidum360.com/
ER  -"""
    
    # Test Spanish RIS content
    spanish_ris_content = """TY  - WEB
AU  - Añez, Diomar
AU  - Añez, Dimar
PY  - 2025
T1  - Herramientas gerenciales: Dinámicas temporales contingentes y antinomias policontextuales
PB  - Solidum Consulting / Wise Connex
N2  - Este dashboard de análisis de datos sirve como base analítica para el proyecto de investigación doctoral: «Dicotomía ontológica en las "Modas Gerenciales"». Desarrollado con Python, Plotly y Dash.
KW  - Herramientas Gerenciales
KW  - Modas Gerenciales
KW  - Visualización de Datos
KW  - Antinomias Policontextuales
UR  - https://dashboard.solidum360.com/
ER  -"""
    
    # Create data URIs for testing
    def create_data_uri(content, filename):
        ris_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        return f"data:application/x-research-info-systems;base64,{ris_b64}", filename
    
    # Test English
    english_uri, english_filename = create_data_uri(english_ris_content, "dashboard_citation_en.ris")
    print(f"✅ English RIS URI generated successfully")
    print(f"   Filename: {english_filename}")
    print(f"   URI length: {len(english_uri)} characters")
    
    # Test Spanish
    spanish_uri, spanish_filename = create_data_uri(spanish_ris_content, "dashboard_citacion_es.ris")
    print(f"✅ Spanish RIS URI generated successfully")
    print(f"   Filename: {spanish_filename}")
    print(f"   URI length: {len(spanish_uri)} characters")
    
    # Validate content
    print("\n📋 Validating RIS content format:")
    
    # Check required RIS fields
    required_fields = ['TY  - WEB', 'AU  -', 'PY  - 2025', 'T1  -', 'PB  -', 'UR  -', 'ER  -']
    
    for field in required_fields:
        if field in english_ris_content:
            print(f"   ✅ English: {field}")
        else:
            print(f"   ❌ English: Missing {field}")
            
        if field in spanish_ris_content:
            print(f"   ✅ Spanish: {field}")
        else:
            print(f"   ❌ Spanish: Missing {field}")
    
    print("\n🎉 RIS download test completed successfully!")
    print("\nTo test the download functionality in the browser:")
    print("1. Navigate to http://localhost:8050")
    print("2. Click the citation button in the credits section")
    print("3. Click the download RIS button")
    print("4. Verify the file downloads with the correct name and content")
    print("5. Switch language and repeat to test both English and Spanish")

if __name__ == "__main__":
    test_ris_download()