#!/usr/bin/env python3
"""
Test script to verify source name mapping functionality
"""

from fix_source_mapping import (
    map_display_names_to_source_ids,
    DISPLAY_NAMES,
    DISPLAY_TO_DB_NAME,
    DBASE_OPTIONS
)

def test_mapping():
    print("Testing source name mapping...")
    print("=" * 50)
    
    # Test display names
    print("Display names:", DISPLAY_NAMES)
    print()
    
    # Test display to database name mapping
    print("Display to DB name mapping:")
    for display_name in DISPLAY_NAMES:
        db_name = DISPLAY_TO_DB_NAME.get(display_name, "NOT FOUND")
        print(f"  {display_name} -> {db_name}")
    print()
    
    # Test database options
    print("Database options:")
    for id, name in DBASE_OPTIONS.items():
        print(f"  {id} -> {name}")
    print()
    
    # Test the main mapping function
    print("Testing map_display_names_to_source_ids function:")
    test_cases = [
        ["Google Trends"],
        ["Google Books"],
        ["Bain Usability"],
        ["Bain Satisfaction"],
        ["Crossref"],
        ["Google Trends", "Google Books"],
        ["Bain Usability", "Bain Satisfaction"],
        DISPLAY_NAMES  # All sources
    ]
    
    for test_case in test_cases:
        result = map_display_names_to_source_ids(test_case)
        print(f"  {test_case} -> {result}")
    
    print()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_mapping()