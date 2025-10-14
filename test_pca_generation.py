#!/usr/bin/env python3
"""
Test script to generate actual Key Findings and verify PCA Analysis structure
"""

import sys
import os
import json
sys.path.append('dashboard_app')

from dashboard_app.key_findings.key_findings_service import KeyFindingsService

def test_pca_analysis_generation():
    """Test actual PCA Analysis generation with 3-paragraph structure"""
    
    print("🧪 Testing actual PCA Analysis generation...")
    
    # Initialize service with required dependencies
    from dashboard_app.key_findings.database_manager import KeyFindingsDBManager
    import pathlib
    
    # Use local database path for testing
    local_db_path = pathlib.Path("./test_key_findings.db")
    db_manager = KeyFindingsDBManager(db_path=local_db_path)
    service = KeyFindingsService(db_manager)
    
    # Test parameters
    tool_name = "Cuadro de Mando Integral"
    sources = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    language = "es"
    
    print(f"📝 Generating analysis for: {tool_name}")
    print(f"📊 Sources: {', '.join(sources)}")
    print(f"🌐 Language: {language}")
    
    try:
        # Generate analysis
        result = service.generate_key_findings(tool_name, sources, language)
        
        if result and 'pca_analysis' in result:
            pca_analysis = result['pca_analysis']
            
            print(f"\n📄 Generated PCA Analysis ({len(pca_analysis)} characters):")
            print("=" * 80)
            print(pca_analysis)
            print("=" * 80)
            
            # Count paragraphs
            paragraphs = [p.strip() for p in pca_analysis.split('\n\n') if p.strip()]
            
            print(f"\n📊 Analysis Results:")
            print(f"📝 Total paragraphs: {len(paragraphs)}")
            
            for i, paragraph in enumerate(paragraphs, 1):
                print(f"\n📌 Paragraph {i} ({len(paragraph)} characters):")
                print(f"   {paragraph[:100]}...")
                
                # Check paragraph content
                if i == 1:
                    # Should contain technical interpretation
                    if any(keyword in paragraph.lower() for keyword in ['carga', 'loading', 'componente', 'varianza']):
                        print("   ✅ Contains technical interpretation")
                    else:
                        print("   ⚠️  May be missing technical interpretation")
                        
                elif i == 2:
                    # Should contain relationships
                    if any(keyword in paragraph.lower() for keyword in ['relación', 'interacción', 'conexión', 'patrón']):
                        print("   ✅ Contains relationships analysis")
                    else:
                        print("   ⚠️  May be missing relationships analysis")
                        
                elif i == 3:
                    # Should contain implications
                    if any(keyword in paragraph.lower() for keyword in ['implicación', 'estratégico', 'práctico', 'implementación']):
                        print("   ✅ Contains implications")
                    else:
                        print("   ⚠️  May be missing implications")
            
            # Check if exactly 3 paragraphs
            if len(paragraphs) == 3:
                print(f"\n🎉 SUCCESS: Generated exactly 3 paragraphs as required!")
                return True
            else:
                print(f"\n⚠️  ISSUE: Expected 3 paragraphs, got {len(paragraphs)}")
                return False
                
        else:
            print("❌ Failed to generate PCA Analysis")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

if __name__ == "__main__":
    success = test_pca_analysis_generation()
    sys.exit(0 if success else 1)