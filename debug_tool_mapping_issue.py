#!/usr/bin/env python3
"""
Debug script to investigate the tool mapping issue with 'Alianzas y Capital de Riesgo'
in Key Findings vs main database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database_manager
from dashboard_app.key_findings.data_aggregator import DataAggregator
from dashboard_app.key_findings.database_manager import KeyFindingsDBManager
from dashboard_app.translations import get_text

def main():
    print("🔍 Debugging Tool Mapping Issue")
    print("=" * 50)
    
    # Initialize database managers
    db_manager = get_database_manager()
    kf_db_manager = KeyFindingsDBManager('./dashboard_app/data/key_findings.db')
    data_aggregator = DataAggregator(db_manager, kf_db_manager)
    
    # Test tool name variations
    tool_variations = [
        "Alianzas y Capital de Riesgo",
        "Alliances and Venture Capital",  # English translation
        "Strategic Alliance, Strategic Alliances, Corporate Venture Capital",
        "Corporate Venture Capital",
        "CVC"
    ]
    
    print("\n1. Checking available keywords in database:")
    print("-" * 40)
    
    # Get all keywords from database
    all_keywords = db_manager.get_keywords_list()
    print(f"Total keywords in database: {len(all_keywords)}")
    
    # Find keywords containing "Alianzas" or "Capital" or "Venture"
    matching_keywords = [k for k in all_keywords if any(term in k.lower() for term in ['alianzas', 'capital', 'riesgo', 'venture', 'alliance', 'cvc'])]
    print(f"\nKeywords matching tool variations: {len(matching_keywords)}")
    for kw in matching_keywords[:10]:  # Show first 10
        print(f"  - {kw}")
    
    print("\n2. Testing tool name variations with data retrieval:")
    print("-" * 40)
    
    # Test each variation with a sample source
    test_sources = [1]  # Google Trends
    
    for tool_name in tool_variations:
        print(f"\nTesting: '{tool_name}'")
        try:
            # Test with data aggregator
            test_datasets, test_sl_sc = data_aggregator.db_manager.get_data_for_keyword(tool_name, test_sources)
            if test_datasets:
                print(f"  ✅ Found data: {len(test_datasets)} sources")
                for source_id, df in test_datasets.items():
                    print(f"    - Source {source_id}: {len(df)} data points")
            else:
                print(f"  ❌ No data found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n3. Checking translation mappings:")
    print("-" * 40)
    
    # Check Spanish to English translation
    spanish_name = "Alianzas y Capital de Riesgo"
    english_name = get_text(spanish_name, 'en')
    print(f"Spanish: '{spanish_name}'")
    print(f"English: '{english_name}'")
    
    # Check if English name exists in database
    try:
        test_datasets, test_sl_sc = data_aggregator.db_manager.get_data_for_keyword(english_name, test_sources)
        if test_datasets:
            print(f"  ✅ English name found in database")
        else:
            print(f"  ❌ English name not found in database")
    except Exception as e:
        print(f"  ❌ Error with English name: {e}")
    
    print("\n4. Checking Key Findings scenario hash generation:")
    print("-" * 40)
    
    # Test scenario hash generation with different names
    test_sources_display = ["Google Trends"]
    
    for tool_name in tool_variations[:2]:  # Test first 2 variations
        scenario_hash = kf_db_manager.generate_scenario_hash(
            tool_name, test_sources_display, language='es'
        )
        print(f"Tool: '{tool_name}'")
        print(f"  Scenario hash: {scenario_hash[:16]}...")
        
        # Check if cached report exists
        cached_report = kf_db_manager.get_cached_report(scenario_hash)
        if cached_report:
            print(f"  ✅ Cached report found")
        else:
            print(f"  ❌ No cached report")
    
    print("\n5. Recommendations:")
    print("-" * 40)
    
    if matching_keywords:
        print("✅ Found matching keywords in database:")
        for kw in matching_keywords[:3]:
            print(f"  - Consider using: '{kw}'")
    else:
        print("❌ No matching keywords found in database")
        print("  - Tool may not be properly imported into database")
    
    print("\n🔧 Potential fixes:")
    print("1. Add tool name mapping in fix_source_mapping.py")
    print("2. Update translation mappings in translations.py")
    print("3. Ensure consistent naming across all components")

if __name__ == "__main__":
    main()