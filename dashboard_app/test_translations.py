#!/usr/bin/env python3
"""
Simple test script for the translation system
"""

from translations import get_text, get_tool_name, get_available_languages

def test_translations():
    print("Testing translation system...")

    # Test basic translations
    print(f"Spanish 'select_tool': {get_text('select_tool', 'es')}")
    print(f"English 'select_tool': {get_text('select_tool', 'en')}")

    # Test tool name translations
    print(f"Spanish tool 'Benchmarking': {get_tool_name('Benchmarking', 'es')}")
    print(f"English tool 'Benchmarking': {get_tool_name('Benchmarking', 'en')}")

    # Test parameterized translation
    print(f"Spanish relative_absolute: {get_text('relative_absolute', 'es', max_value=123.45)}")
    print(f"English relative_absolute: {get_text('relative_absolute', 'en', max_value=123.45)}")

    # Test available languages
    print(f"Available languages: {get_available_languages()}")

    print("Translation tests completed successfully!")

if __name__ == "__main__":
    test_translations()