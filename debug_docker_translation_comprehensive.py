#!/usr/bin/env python3
"""
Comprehensive debugging script for Docker translation issues.
This script will help identify the exact cause of translation errors when switching to English.
"""

import os
import sys
import json
import sqlite3
import traceback
from pathlib import Path

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_translation_function():
    """Test the translation functions directly"""
    print_section("TRANSLATION FUNCTION TESTING")
    
    try:
        from translations import get_text, translate_source_name, enhanced_translate_source_name
        
        # Test basic get_text function
        print("Testing get_text function:")
        test_keys = ['select_tool', 'select_sources', 'data_table']
        for key in test_keys:
            es_text = get_text(key, 'es')
            en_text = get_text(key, 'en')
            print(f"  {key}: es='{es_text}', en='{en_text}'")
        
        # Test source name translation
        print("\nTesting translate_source_name function:")
        test_sources = [
            ('Bain - Usabilidad', 'en'),
            ('Bain - Satisfacción', 'en'),
            ('Bain - Usability', 'es'),
            ('Bain - Satisfaction', 'es')
        ]
        
        for source, lang in test_sources:
            translated = translate_source_name(source, lang)
            print(f"  '{source}' -> '{translated}' (lang={lang})")
        
        # Test enhanced translation if available
        print("\nTesting enhanced_translate_source_name function:")
        try:
            for source, lang in test_sources:
                translated = enhanced_translate_source_name(source, lang)
                print(f"  '{source}' -> '{translated}' (enhanced, lang={lang})")
        except Exception as e:
            print(f"  Enhanced translation not available or failed: {e}")
            
    except Exception as e:
        print(f"ERROR testing translation functions: {e}")
        traceback.print_exc()

def test_source_mapping():
    """Test the source mapping functions"""
    print_section("SOURCE MAPPING TESTING")
    
    try:
        from fix_source_mapping import (
            DISPLAY_NAMES, 
            DISPLAY_TO_DB_NAME, 
            DBASE_OPTIONS,
            display_names_to_ids,
            enhanced_display_names_to_ids,
            map_display_names_to_source_ids
        )
        
        print("Display Names:", DISPLAY_NAMES)
        print("Display to DB Name Mapping:", DISPLAY_TO_DB_NAME)
        print("DBASE_OPTIONS:", DBASE_OPTIONS)
        
        # Test with English names
        print("\nTesting with English display names:")
        english_names = ["Bain - Usability", "Bain - Satisfaction", "Google Trends"]
        
        # Standard mapping
        standard_ids = display_names_to_ids(english_names)
        print(f"  Standard mapping: {english_names} -> {standard_ids}")
        
        # Enhanced mapping
        enhanced_ids = enhanced_display_names_to_ids(english_names)
        print(f"  Enhanced mapping: {english_names} -> {enhanced_ids}")
        
        # Current map function (what's actually being used)
        current_ids = map_display_names_to_source_ids(english_names)
        print(f"  Current mapping: {english_names} -> {current_ids}")
        
        # Test with Spanish names
        print("\nTesting with Spanish display names:")
        spanish_names = ["Bain - Usabilidad", "Bain - Satisfacción", "Google Trends"]
        
        standard_ids_es = display_names_to_ids(spanish_names)
        print(f"  Standard mapping: {spanish_names} -> {standard_ids_es}")
        
        enhanced_ids_es = enhanced_display_names_to_ids(spanish_names)
        print(f"  Enhanced mapping: {spanish_names} -> {enhanced_ids_es}")
        
        current_ids_es = map_display_names_to_source_ids(spanish_names)
        print(f"  Current mapping: {spanish_names} -> {current_ids_es}")
        
    except Exception as e:
        print(f"ERROR testing source mapping: {e}")
        traceback.print_exc()

def test_database_access():
    """Test database access with different source names"""
    print_section("DATABASE ACCESS TESTING")
    
    # Find database file
    db_paths = [
        "dashboard_app/data.db",
        "/app/dashboard_app/data.db",
        "./data.db",
        "data.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {path}")
            break
    
    if not db_path:
        print("ERROR: Database file not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")
        
        # Check for Bain-related tables
        bain_tables = [t for t in tables if 'bain' in t.lower()]
        print(f"Bain-related tables: {bain_tables}")
        
        # Test data retrieval with database manager
        try:
            from database import get_database_manager
            from fix_source_mapping import map_display_names_to_source_ids
            
            db_manager = get_database_manager()
            
            # Test with English names
            print("\nTesting data retrieval with English names:")
            english_sources = ["Bain - Usability", "Bain - Satisfaction"]
            source_ids = map_display_names_to_source_ids(english_sources)
            print(f"  English sources: {english_sources}")
            print(f"  Mapped to IDs: {source_ids}")
            
            # Try to get data for a common keyword
            test_keyword = "Benchmarking"
            datasets_norm, valid_sources = db_manager.get_data_for_keyword(test_keyword, source_ids)
            
            print(f"  Retrieved data for {len(datasets_norm)} sources")
            for source_id, data in datasets_norm.items():
                print(f"    Source ID {source_id}: {len(data)} records")
            
            # Test with Spanish names
            print("\nTesting data retrieval with Spanish names:")
            spanish_sources = ["Bain - Usabilidad", "Bain - Satisfacción"]
            source_ids_es = map_display_names_to_source_ids(spanish_sources)
            print(f"  Spanish sources: {spanish_sources}")
            print(f"  Mapped to IDs: {source_ids_es}")
            
            datasets_norm_es, valid_sources_es = db_manager.get_data_for_keyword(test_keyword, source_ids_es)
            
            print(f"  Retrieved data for {len(datasets_norm_es)} sources")
            for source_id, data in datasets_norm_es.items():
                print(f"    Source ID {source_id}: {len(data)} records")
                
        except Exception as e:
            print(f"ERROR with database manager: {e}")
            traceback.print_exc()
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR accessing database: {e}")
        traceback.print_exc()

def test_app_imports():
    """Test if the app can import and use the enhanced functions"""
    print_section("APP IMPORTS TESTING")
    
    try:
        # Check if enhanced functions are loaded in app.py
        app_path = Path("dashboard_app/app.py")
        if app_path.exists():
            with open(app_path, 'r') as f:
                content = f.read()
            
            has_enhanced_imports = "DOCKER_FIX: Enhanced imports for Docker" in content
            has_enhanced_translation = "enhanced_translate_source_name" in content
            has_enhanced_mapping = "enhanced_display_names_to_ids" in content
            
            print(f"Has enhanced imports: {has_enhanced_imports}")
            print(f"Has enhanced translation: {has_enhanced_translation}")
            print(f"Has enhanced mapping: {has_enhanced_mapping}")
            
            if has_enhanced_imports:
                print("\nEnhanced imports block found in app.py")
            else:
                print("\nWARNING: Enhanced imports NOT found in app.py")
        
        # Try to import app modules
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))
            from app import app
            print("Successfully imported app from app.py")
            
            # Check if translation functions are properly overridden
            from app import translate_source_name, map_display_names_to_source_ids
            
            # Test the functions
            test_result = translate_source_name("Bain - Usabilidad", "en")
            print(f"translate_source_name in app: 'Bain - Usabilidad' -> '{test_result}' (en)")
            
            test_ids = map_display_names_to_source_ids(["Bain - Usability"])
            print(f"map_display_names_to_source_ids in app: ['Bain - Usability'] -> {test_ids}")
            
        except Exception as e:
            print(f"ERROR importing app: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"ERROR testing app imports: {e}")
        traceback.print_exc()

def check_environment():
    """Check environment variables and settings"""
    print_section("ENVIRONMENT CHECK")
    
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:5]}...")
    
    # Check if we're in Docker
    docker_indicator = '/.dockerenv'
    if os.path.exists(docker_indicator):
        print("Running inside Docker container")
    else:
        print("NOT running in Docker container")
    
    # Check relevant environment variables
    env_vars = [
        'PYTHONPATH',
        'LANG',
        'LC_ALL',
        'FLASK_ENV',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        print(f"{var}: {value}")

def simulate_language_switch():
    """Simulate what happens when language is switched to English"""
    print_section("LANGUAGE SWITCH SIMULATION")
    
    try:
        # Simulate the callback that updates language
        from translations import get_text
        
        # Test UI elements translation
        ui_elements = [
            'select_tool', 'select_sources', 'select_all', 
            'data_table', 'temporal_analysis_2d'
        ]
        
        print("UI elements in Spanish:")
        for element in ui_elements:
            print(f"  {element}: {get_text(element, 'es')}")
        
        print("\nUI elements in English:")
        for element in ui_elements:
            print(f"  {element}: {get_text(element, 'en')}")
        
        # Simulate data source translation
        from fix_source_mapping import map_display_names_to_source_ids
        
        # This is what happens when sources are selected in English
        english_sources = ["Bain - Usability", "Bain - Satisfaction"]
        print(f"\nSelected sources in English: {english_sources}")
        
        # Map to source IDs
        source_ids = map_display_names_to_source_ids(english_sources)
        print(f"Mapped to source IDs: {source_ids}")
        
        # Check if any IDs are None (indicating mapping failure)
        if None in source_ids:
            print("ERROR: Some sources could not be mapped to IDs!")
            for i, source_id in enumerate(source_ids):
                if source_id is None:
                    print(f"  Failed to map: {english_sources[i]}")
        else:
            print("All sources successfully mapped to IDs")
            
    except Exception as e:
        print(f"ERROR simulating language switch: {e}")
        traceback.print_exc()

def main():
    """Run all debugging tests"""
    print("DOCKER TRANSLATION COMPREHENSIVE DEBUG")
    print(f"Running at: {os.popen('date').read().strip()}")
    
    check_environment()
    test_translation_function()
    test_source_mapping()
    test_database_access()
    test_app_imports()
    simulate_language_switch()
    
    print_section("SUMMARY")
    print("This debugging script has tested:")
    print("1. Translation functions (standard and enhanced)")
    print("2. Source mapping functions")
    print("3. Database access with different source names")
    print("4. App imports and function overrides")
    print("5. Environment configuration")
    print("6. Language switch simulation")
    print("\nCheck the output above for any errors or warnings that might")
    print("indicate the source of the translation issue in Docker.")

if __name__ == "__main__":
    main()