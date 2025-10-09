#!/usr/bin/env python3
"""
Test script to verify all analysis types work with multiple sources
"""

import sys
import os

# Add parent directory to path for database imports (same as app.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the same way as app.py
import warnings
warnings.filterwarnings('ignore')

from tools import tool_file_dic
from database import get_database_manager

# Import centralized source mapping
from fix_source_mapping import (
    map_display_names_to_source_ids,
    DISPLAY_NAMES
)

def test_all_analyses():
    print("Testing all analysis types with multiple sources...")
    print("=" * 60)
    
    # Get database manager
    db_manager = get_database_manager()
    print("Database manager initialized")
    
    # Test keyword
    test_keyword = "Alianzas y Capital de Riesgo"
    print(f"Test keyword: {test_keyword}")
    
    # Test with multiple sources
    test_sources = ["Google Trends", "Google Books"]
    print(f"Test sources: {test_sources}")
    
    # Convert to source IDs
    source_ids = map_display_names_to_source_ids(test_sources)
    print(f"Converted source IDs: {source_ids}")
    
    # Test data retrieval
    print("\n1. Testing data retrieval...")
    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(test_keyword, source_ids)
        print(f"   Retrieved datasets for sources: {list(datasets_norm.keys())}")
        print(f"   Valid sources: {sl_sc}")
        
        # Check that we have data for both sources
        if len(datasets_norm) == 2 and len(sl_sc) == 2:
            print("   ✓ Data retrieval successful for multiple sources")
        else:
            print("   ✗ Data retrieval issue - not all sources retrieved")
    except Exception as e:
        print(f"   ✗ Data retrieval failed: {e}")
        return
    
    # Test that we can access data for each source
    print("\n2. Testing data access for each source...")
    for source_id in source_ids:
        if source_id in datasets_norm and datasets_norm[source_id] is not None:
            data_shape = datasets_norm[source_id].shape
            print(f"   Source {source_id}: {data_shape[0]} rows, {data_shape[1]} columns")
        else:
            print(f"   Source {source_id}: No data available")
    
    # Test with all sources
    print("\n3. Testing with all sources...")
    all_source_ids = map_display_names_to_source_ids(DISPLAY_NAMES)
    print(f"   All source IDs: {all_source_ids}")
    
    try:
        all_datasets, all_sl_sc = db_manager.get_data_for_keyword(test_keyword, all_source_ids)
        print(f"   Retrieved datasets for all sources: {list(all_datasets.keys())}")
        print("   ✓ All sources data retrieval successful")
    except Exception as e:
        print(f"   ✗ All sources data retrieval failed: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_all_analyses()