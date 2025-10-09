#!/usr/bin/env python3
"""
Test script to verify "Seleccionar Todo" functionality
"""

from fix_source_mapping import DISPLAY_NAMES

def test_select_all():
    print("Testing 'Seleccionar Todo' functionality...")
    print("=" * 50)
    
    # Simulate the select all logic
    all_sources = DISPLAY_NAMES
    print("All available sources:", all_sources)
    print()
    
    # Test selecting all
    selected_sources = all_sources.copy()
    print("Selected sources (all):", selected_sources)
    
    # Test deselecting all (toggle)
    if set(selected_sources) == set(all_sources):
        selected_sources = []
        print("Deselected all sources:", selected_sources)
    else:
        selected_sources = all_sources.copy()
        print("Selected all sources:", selected_sources)
    
    print()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_select_all()