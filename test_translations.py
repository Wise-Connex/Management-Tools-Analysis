#!/usr/bin/env python3
"""
Test script to verify the translation functionality for source notes.
"""

import sys
import os

# Add the dashboard_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

from translations import translate_database_content

def test_bain_satisfaction_translation():
    """Test translation of Bain Satisfaction source notes."""
    spanish_text = """REINGENIERÍA DE PROCESOS: Descriptores lógicos: Reengineering (1993, 1996, 2000, 2002); Business Process Reengineering (2004, 2006, 2008, 2010, 2012, 2014, 2017, 2022). Extracción de datos: [De 07/2024 - 01/2025]. Parámetros de Insumos: Encuesta de Herramientas Gerenciales de Bain & Company (Darrell Rigby); marco temporal: 1993-2022; cobertura global y multisectorial; perfil de encuestados: CEOs (Directores Ejecutivos), CFOs (Directores Financieros), COOs (Directores de Operaciones), y otros líderes senior. Metodología: Encuesta online; cuestionarios estructurados; muestreo probabilístico y estratificado; análisis estadístico. Año/#Encuestados: 1993/500; 1996/784; 2000/214; 2002/708; 2004/960; 2006/1221; 2008/1430; 2010/1230; 2012/1208; 2014/1067; 2017/1268; 2022/1068. Índice de Satisfacción: La métrica se calcula como: Índice de Satisfacción = Promedio de las puntuaciones de satisfacción reportadas por ejecutivos (escala 0-5). Refleja la percepción promedio de los ejecutivos sobre la utilidad e impacto de la herramienta en su ecosistema gerencial, donde una puntuación más alta indica mayor satisfacción. Perfil de Usuarios: Directivos de alto nivel, consultores estratégicos y profesionales de la gestión interesados en la implementación y adopción de metodologías de gestión con un enfoque en la practicidad y el uso real en el campo empresarial, buscando insights sobre las tendencias de la práctica gerencial. Además, especialistas en optimización de procesos, diseño organizacional y mejora continua que buscan medir el impacto de las estrategias de reingeniería en su organización. Limitaciones: El índice de satisfacción es subjetivo y puede estar influenciado por el sesgo de deseabilidad social y autoinforme; la interpretación puede variar entre los encuestados; la terminología puede haber evolucionado y afectar la consistencia longitudinal; y la métrica no mide resultados objetivos ni impacto real. Fuente: Rigby (1994, 2001, 2003); Rigby & Bilodeau (2005, 2007, 2009, 2011, 2013, 2015, 2017); Rigby, Bilodeau, & Ronan (2023)."""
    
    english_text = translate_database_content(spanish_text, 'en')
    
    print("=== Bain Satisfaction Translation Test ===")
    print("\nSpanish Text:")
    print(spanish_text[:200] + "...")
    print("\nEnglish Translation:")
    print(english_text[:200] + "...")
    
    # Check if key terms were translated
    assert "BUSINESS PROCESS REENGINEERING:" in english_text
    assert "Data Extraction:" in english_text
    assert "Satisfaction Index:" in english_text
    assert "User Profile:" in english_text
    assert "Limitations:" in english_text
    assert "Source:" in english_text
    
    print("\n✓ Bain Satisfaction translation test passed!")
    return True

def test_bain_usability_translation():
    """Test translation of Bain Usability source notes."""
    spanish_text = """REINGENIERÍA DE PROCESOS: Descriptores lógicos: Reengineering (1993, 1996, 2000, 2002); Business Process Reengineering (2004, 2006, 2008, 2010, 2012, 2014, 2017, 2022). Extracción de datos: [De 07/2024 - 01/2025]. Parámetros de Insumos: Encuesta de Herramientas Gerenciales de Bain & Company (Darrell Rigby); marco temporal: 1993-2022; cobertura global y multisectorial; perfil de encuestados: CEOs (Directores Ejecutivos), CFOs (Directores Financieros), COOs (Directores de Operaciones), y otros líderes senior. Metodología: Encuesta online; cuestionarios estructurados; muestreo probabilístico y estratificado; análisis estadístico. Año/#Encuestados: 1993/500; 1996/784; 2000/214; 2002/708; 2004/960; 2006/1221; 2008/1430; 2010/1230; 2012/1208; 2014/1067; 2017/1268; 2022/1068. Indicador de Usabilidad: La métrica se calcula como: Indicador de Usabilidad = (Número de ejecutivos que reportan uso de la herramienta en el año de la encuesta / Número total de ejecutivos encuestados en ese año) × 100. Refleja el porcentaje de ejecutivos que indicaron haber utilizado la herramienta de gestión en su organización durante el periodo previo al año de la encuesta. Perfil de Usuarios: Directivos de alto nivel, consultores estratégicos y profesionales de la gestión interesados en la implementación y adopción de metodologías de gestión con un enfoque en la practicidad y el uso real en el campo empresarial, buscando insights sobre las tendencias de la práctica gerencial. Además, especialistas en optimización de procesos, diseño organizacional y mejora continua que buscan identificar estrategias para aumentar la eficiencia y reducir costos. Limitaciones: La variabilidad en el tamaño de la muestra entre los años puede afectar la comparabilidad; el sesgo de selección y autoinforme puede influir en las respuestas; la evolución terminológica puede afectar la consistencia longitudinal; y la medición del uso es un indicador relativo, no absoluto, de la efectividad. Fuente: Rigby (1994, 2001, 2003); Rigby & Bilodeau (2005, 2007, 2009, 2011, 2013, 2015, 2017); Rigby, Bilodeau, & Ronan (2023)."""
    
    english_text = translate_database_content(spanish_text, 'en')
    
    print("\n=== Bain Usability Translation Test ===")
    print("\nSpanish Text:")
    print(spanish_text[:200] + "...")
    print("\nEnglish Translation:")
    print(english_text[:200] + "...")
    
    # Check if key terms were translated
    assert "BUSINESS PROCESS REENGINEERING:" in english_text
    assert "Data Extraction:" in english_text
    assert "Usability Indicator:" in english_text
    assert "User Profile:" in english_text
    assert "Limitations:" in english_text
    assert "Source:" in english_text
    
    print("\n✓ Bain Usability translation test passed!")
    return True

def test_crossref_translation():
    """Test translation of Crossref source notes."""
    spanish_text = """$Herramienta_Gerencial: Descriptores lógicos: $KEYWORDS. Extracción de datos: $Data_Collection_Date. Parámetros de búsqueda: Marco temporal (1950-2025), campos de búsqueda: "Título" y "Resumen (Abstract)". Índice: La métrica es el número de resultados que coinciden con los descriptores en los metadatos de CrossRef. Refleja el volumen de publicaciones académicas (artículos, libros, conferencias, etc.) indexadas. Metodología: La búsqueda en metadatos de CrossRef usa operadores booleanos. Interpretación centrada en el volumen de publicaciones. Proporciona una medida cuantitativa del interés académico y las investigaciones publicadas. Perfil de Usuarios: Refleja el interés académico a través de publicaciones revisadas por pares y arbitradas, e indexadas. Usuarios típicos: investigadores, académicos, expertos, estudiantes y profesionales. Limitaciones: Dependencia de la exhaustividad y precisión de la indexación de CrossRef. Solo refleja volumen, no calidad, relevancia, impacto o citaciones. Descriptores lógicos pueden introducir sesgos. Cobertura limitada: no incluye todas las publicaciones académicas, solo su indexado. Proporciona DOI (Digital Object Identifier) y metadatos básicos, excluyendo datos bibliométricos adicionales. Fuente: $LINK"""
    
    english_text = translate_database_content(spanish_text, 'en')
    
    print("\n=== Crossref Translation Test ===")
    print("\nSpanish Text:")
    print(spanish_text[:200] + "...")
    print("\nEnglish Translation:")
    print(english_text[:200] + "...")
    
    # Check if key terms were translated
    assert "Logical Descriptors:" in english_text
    assert "Search Parameters:" in english_text
    assert "search fields:" in english_text
    assert "User Profile:" in english_text
    assert "Limitations:" in english_text
    assert "Source:" in english_text
    
    print("\n✓ Crossref translation test passed!")
    return True

def test_google_trends_translation():
    """Test translation of Google Trends source notes."""
    spanish_text = """$Herramienta_Gerencial: Descriptores lógicos: $KEYWORDS. Extracción de datos: $Data_Collection_Date. Parámetros de búsqueda: cobertura global, marco temporal 01/2004-01/2025, categorización amplia, tipo de búsqueda web. Índice Relativo: Los datos se normalizan en un índice relativo (0-100; 100 = máximo interés relativo) mediante la fórmula: Índice relativo = (Volumen de búsqueda del término / Volumen total de búsquedas) x 100; mitigando sesgos por heterogeneidad en volúmenes de búsqueda entre regiones y periodos. Metodología: La métrica es comparativa, no absoluta, basada en muestreo probabilístico, lo que introduce variabilidad estadística. La interpretación se centra en tendencias de interés relativo, no en recuentos absolutos. Disponibilidad de datos (desde 2004) permite análisis diacrónico contextualizado en evolución digital y patrones de búsqueda. Perfil de Usuarios: Refleja interés público, popularidad de búsqueda y tendencias emergentes en tiempo real en un perfil de usuarios heterogéneos: investigadores, periodistas, profesionales del marketing, empresarios y usuarios generales. Limitaciones: No hay correlación directa entre interés en búsquedas e implementación efectiva en organizaciones. La evolución terminológica puede afectar la coherencia longitudinal. Fuente: $LINK"""
    
    english_text = translate_database_content(spanish_text, 'en')
    
    print("\n=== Google Trends Translation Test ===")
    print("\nSpanish Text:")
    print(spanish_text[:200] + "...")
    print("\nEnglish Translation:")
    print(english_text[:200] + "...")
    
    # Check if key terms were translated
    assert "Logical Descriptors:" in english_text
    assert "Search Parameters:" in english_text
    assert "global coverage" in english_text
    assert "Relative Index:" in english_text
    assert "User Profile:" in english_text
    assert "Limitations:" in english_text  # This should be translated
    
    print("\n✓ Google Trends translation test passed!")
    return True

if __name__ == "__main__":
    try:
        test_bain_satisfaction_translation()
        test_bain_usability_translation()
        test_crossref_translation()
        test_google_trends_translation()
        
        print("\n🎉 All translation tests passed successfully!")
        print("\nThe translation system is now capable of translating Spanish source notes to English.")
        print("This includes notes from Bain Satisfaction, Bain Usability, Crossref, and Google Trends sources.")
    except AssertionError as e:
        print(f"\n❌ Translation test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)