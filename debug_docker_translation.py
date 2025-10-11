#!/usr/bin/env python3
"""
Debug script to identify the translation issue in Docker environment.
This script will help diagnose why 'Bain - Usability' and 'Bain - Satisfaction' 
are not found in the index when running in Docker but work locally.
"""

import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path

# Add dashboard_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))

def analyze_database_structure():
    """Analyze the database structure and content"""
    print("="*60)
    print("DATABASE STRUCTURE ANALYSIS")
    print("="*60)
    
    # Try different potential database paths
    potential_paths = [
        "dashboard_app/data.db",
        "/app/dashboard_app/data.db",
        "./data.db",
        "data.db"
    ]
    
    db_path = None
    for path in potential_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {path}")
            break
    
    if not db_path:
        print("ERROR: Database file not found in any expected location!")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")
        
        # Check for Bain-related tables
        bain_tables = [t for t in tables if 'bain' in t.lower()]
        print(f"Bain-related tables: {bain_tables}")
        
        # Check table schemas
        for table in bain_tables:
            print(f"\nSchema for {table}:")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col}")
            
            # Check sample data
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  Total records: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT DISTINCT keyword FROM {table} LIMIT 5")
                keywords = [row[0] for row in cursor.fetchall()]
                print(f"  Sample keywords: {keywords}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR analyzing database: {e}")

def analyze_source_mapping():
    """Analyze the source mapping configuration"""
    print("\n" + "="*60)
    print("SOURCE MAPPING ANALYSIS")
    print("="*60)
    
    try:
        from fix_source_mapping import DISPLAY_NAMES, DISPLAY_TO_DB_NAME, DBASE_OPTIONS
        
        print("Display Names:", DISPLAY_NAMES)
        print("Display to DB Name Mapping:", DISPLAY_TO_DB_NAME)
        print("DBASE_OPTIONS:", DBASE_OPTIONS)
        
        # Check for Bain entries
        print("\nBain entries in mappings:")
        for name in DISPLAY_NAMES:
            if 'bain' in name.lower():
                db_name = DISPLAY_TO_DB_NAME.get(name)
                print(f"  {name} -> {db_name}")
                
                # Check if this DB name exists in DBASE_OPTIONS
                for id, db_opt in DBASE_OPTIONS.items():
                    if db_opt == db_name:
                        print(f"    Found in DBASE_OPTIONS with ID {id}")
                        break
                else:
                    print(f"    NOT FOUND in DBASE_OPTIONS!")
        
    except Exception as e:
        print(f"ERROR analyzing source mapping: {e}")
        import traceback
        traceback.print_exc()

def analyze_translation_system():
    """Analyze the translation system"""
    print("\n" + "="*60)
    print("TRANSLATION SYSTEM ANALYSIS")
    print("="*60)
    
    try:
        from translations import translate_source_name, TRANSLATIONS
        
        print("Testing translate_source_name function:")
        
        # Test Spanish names
        spanish_names = ["Bain - Usabilidad", "Bain - Satisfacción"]
        for name in spanish_names:
            translated = translate_source_name(name, 'en')
            print(f"  '{name}' (es) -> '{translated}' (en)")
        
        # Test English names
        english_names = ["Bain - Usability", "Bain - Satisfaction"]
        for name in english_names:
            translated = translate_source_name(name, 'es')
            print(f"  '{name}' (en) -> '{translated}' (es)")
        
        # Check if English translations exist in TRANSLATIONS
        print("\nChecking for English Bain translations in TRANSLATIONS dict:")
        en_trans = TRANSLATIONS.get('en', {})
        bain_keys = [k for k in en_trans.keys() if 'bain' in k.lower()]
        print(f"  Bain-related keys in English translations: {bain_keys}")
        
    except Exception as e:
        print(f"ERROR analyzing translation system: {e}")
        import traceback
        traceback.print_exc()

def simulate_data_retrieval():
    """Simulate the data retrieval process that's failing"""
    print("\n" + "="*60)
    print("DATA RETRIEVAL SIMULATION")
    print("="*60)
    
    try:
        from database import get_database_manager
        from fix_source_mapping import map_display_names_to_source_ids
        
        # Test with English Bain names
        english_sources = ["Bain - Usability", "Bain - Satisfaction"]
        print(f"Testing with English sources: {english_sources}")
        
        # Map to source IDs
        source_ids = map_display_names_to_source_ids(english_sources)
        print(f"Mapped to source IDs: {source_ids}")
        
        # Try to retrieve data
        db_manager = get_database_manager()
        test_keyword = "Benchmarking"  # Common keyword that should exist
        
        print(f"Attempting to retrieve data for keyword: {test_keyword}")
        datasets_norm, valid_sources = db_manager.get_data_for_keyword(test_keyword, source_ids)
        
        print(f"Retrieved datasets for sources: {list(datasets_norm.keys())}")
        print(f"Valid sources: {valid_sources}")
        
        # Check if we got the expected data
        for source_id in source_ids:
            if source_id in datasets_norm:
                df = datasets_norm[source_id]
                print(f"  Source {source_id}: {len(df)} records")
                if not df.empty:
                    print(f"    Date range: {df.index.min()} to {df.index.max()}")
                    print(f"    Sample values: {df.iloc[:3, 0].tolist()}")
            else:
                print(f"  Source {source_id}: NO DATA RETRIEVED")
        
    except Exception as e:
        print(f"ERROR in data retrieval simulation: {e}")
        import traceback
        traceback.print_exc()

def check_environment_differences():
    """Check for environment differences that might affect the app"""
    print("\n" + "="*60)
    print("ENVIRONMENT DIFFERENCES CHECK")
    print("="*60)
    
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    
    # Check for environment variables
    env_vars = [
        'DASHBOARD_DATABASE_PATH',
        'PYTHONPATH',
        'LANG',
        'LC_ALL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        print(f"{var}: {value}")
    
    # Check if we're in Docker
    docker_indicator = '/.dockerenv'
    if os.path.exists(docker_indicator):
        print("Running inside Docker container")
    else:
        print("NOT running in Docker container")

def main():
    """Main function to run all checks"""
    print("DOCKER TRANSLATION ISSUE DEBUG SCRIPT")
    print(f"Running at: {pd.Timestamp.now()}")
    
    check_environment_differences()
    analyze_database_structure()
    analyze_source_mapping()
    analyze_translation_system()
    simulate_data_retrieval()
    
    print("\n" + "="*60)
    print("DEBUGGING COMPLETE")
    print("="*60)
    print("\nSUMMARY:")
    print("1. Check if Bain tables exist in the database")
    print("2. Verify source mapping is correct for English names")
    print("3. Confirm translation system works as expected")
    print("4. Identify any missing data or mapping issues")

if __name__ == "__main__":
    main()