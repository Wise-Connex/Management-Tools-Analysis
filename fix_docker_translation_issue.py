#!/usr/bin/env python3
"""
Fix for the Docker translation issue with 'Bain - Usability' and 'Bain - Satisfaction'.
This script addresses the most likely causes of the problem.
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path

def fix_source_mapping():
    """
    Fix the source mapping to ensure English names are properly handled.
    This addresses the issue where English display names aren't correctly mapped to database IDs.
    """
    print("Fixing source mapping for Docker environment...")
    
    # Read the current fix_source_mapping.py
    fix_mapping_path = Path("dashboard_app/fix_source_mapping.py")
    
    if not fix_mapping_path.exists():
        print(f"ERROR: {fix_mapping_path} not found!")
        return False
    
    with open(fix_mapping_path, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "DOCKER_FIX: Enhanced source mapping for English names" in content:
        print("Source mapping fix already applied.")
        return True
    
    # Add enhanced source mapping for Docker
    enhanced_mapping = '''
# DOCKER_FIX: Enhanced source mapping for English names
# This ensures proper mapping from English display names to database IDs

def enhanced_display_names_to_ids(display_names):
    """
    Enhanced function to handle English display names in Docker environment.
    Provides fallback mappings for common translation issues.
    
    Args:
        display_names: List of display names (can be English or Spanish)
        
    Returns:
        List of numeric source IDs
    """
    if not display_names:
        return []
    
    # Standard mapping first
    ids = display_names_to_ids(display_names)
    
    # Check for unmapped English names and apply fallbacks
    english_to_id_fallbacks = {
        'Bain - Usability': 3,      # Maps to bain_usability table
        'Bain Usability': 3,       # Alternative without dash
        'Bain - Satisfaction': 5,  # Maps to bain_satisfaction table
        'Bain Satisfaction': 5,    # Alternative without dash
        'Google Books': 2,         # Maps to google_books table
        'Google Trends': 1,        # Maps to google_trends table
        'Crossref': 4              # Maps to crossref table
    }
    
    # Apply fallbacks for any unmapped names
    result_ids = []
    for i, name in enumerate(display_names):
        if i < len(ids) and ids[i] is not None:
            result_ids.append(ids[i])
        elif name in english_to_id_fallbacks:
            result_ids.append(english_to_id_fallbacks[name])
            print(f"Applied fallback mapping: '{name}' -> ID {english_to_id_fallbacks[name]}")
        else:
            print(f"WARNING: No mapping found for '{name}'")
    
    return result_ids

# Replace the standard function for Docker compatibility
map_display_names_to_source_ids = enhanced_display_names_to_ids

'''
    
    # Insert the enhanced mapping after the existing functions
    insert_pos = content.find("# Export the main conversion function for backward compatibility")
    if insert_pos == -1:
        print("ERROR: Could not find insertion point in fix_source_mapping.py")
        return False
    
    new_content = content[:insert_pos] + enhanced_mapping + "\n" + content[insert_pos:]
    
    # Write the updated content
    with open(fix_mapping_path, 'w') as f:
        f.write(new_content)
    
    print("Enhanced source mapping applied successfully!")
    return True

def fix_translation_system():
    """
    Fix the translation system to handle English names properly.
    """
    print("Fixing translation system for Docker environment...")
    
    # Read the current translations.py
    translations_path = Path("dashboard_app/translations.py")
    
    if not translations_path.exists():
        print(f"ERROR: {translations_path} not found!")
        return False
    
    with open(translations_path, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "DOCKER_FIX: Enhanced translation for Docker" in content:
        print("Translation system fix already applied.")
        return True
    
    # Add enhanced translation function
    enhanced_translation = '''
# DOCKER_FIX: Enhanced translation for Docker environment
def enhanced_translate_source_name(source_name, language='es'):
    """
    Enhanced translation function that handles more variations and provides fallbacks.
    This addresses Docker-specific issues with source name translation.
    
    Args:
        source_name: Source name to translate
        language: Target language ('es' or 'en')
        
    Returns:
        Translated source name
    """
    # Try the standard translation first
    try:
        return translate_source_name(source_name, language)
    except:
        pass
    
    # Fallback translations for Docker environment
    if language == 'es':
        # English to Spanish
        fallback_translations = {
            'Bain - Usability': 'Bain - Usabilidad',
            'Bain Usability': 'Bain - Usabilidad',
            'Bain - Satisfaction': 'Bain - Satisfacción',
            'Bain Satisfaction': 'Bain - Satisfacción',
            'Google Books': 'Google Books Ngrams',
            'Crossref': 'Crossref.org'
        }
    else:
        # Spanish to English
        fallback_translations = {
            'Bain - Usabilidad': 'Bain - Usability',
            'Bain - Satisfacción': 'Bain - Satisfaction',
            'Google Books Ngrams': 'Google Books',
            'Crossref.org': 'Crossref'
        }
    
    return fallback_translations.get(source_name, source_name)

'''
    
    # Insert the enhanced translation at the end of the file
    new_content = content + "\n" + enhanced_translation
    
    # Write the updated content
    with open(translations_path, 'w') as f:
        f.write(new_content)
    
    print("Enhanced translation system applied successfully!")
    return True

def fix_app_py():
    """
    Fix the app.py file to use enhanced translation functions.
    """
    print("Fixing app.py for Docker environment...")
    
    # Read the current app.py
    app_path = Path("dashboard_app/app.py")
    
    if not app_path.exists():
        print(f"ERROR: {app_path} not found!")
        return False
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "DOCKER_FIX: Enhanced imports for Docker" in content:
        print("App.py fix already applied.")
        return True
    
    # Add enhanced imports at the top
    enhanced_imports = '''
# DOCKER_FIX: Enhanced imports for Docker compatibility
try:
    from translations import enhanced_translate_source_name
    from fix_source_mapping import enhanced_display_names_to_ids
    
    # Replace functions with enhanced versions
    translate_source_name = enhanced_translate_source_name
    map_display_names_to_source_ids = enhanced_display_names_to_ids
    print("Loaded enhanced translation functions for Docker environment")
except ImportError as e:
    print(f"Warning: Could not load enhanced functions: {e}")

'''
    
    # Insert after existing imports
    insert_pos = content.find("# Import translation system")
    if insert_pos == -1:
        print("ERROR: Could not find translation import in app.py")
        return False
    
    # Find the end of the import block
    end_import_pos = content.find("\n\n", insert_pos)
    if end_import_pos == -1:
        end_import_pos = content.find("\n# ", insert_pos)
    
    if end_import_pos == -1:
        print("ERROR: Could not find end of import block in app.py")
        return False
    
    new_content = content[:end_import_pos] + enhanced_imports + content[end_import_pos:]
    
    # Write the updated content
    with open(app_path, 'w') as f:
        f.write(new_content)
    
    print("Enhanced app.py applied successfully!")
    return True

def create_docker_database_fix():
    """
    Create a script to ensure the database has the correct structure in Docker.
    """
    print("Creating Docker database fix script...")
    
    fix_script = '''#!/usr/bin/env python3
"""
Database fix script for Docker environment.
Ensures the database has the correct structure and mappings.
"""

import os
import sys
import sqlite3
from pathlib import Path

def fix_database():
    """Fix database structure for Docker environment"""
    print("Fixing database structure for Docker...")
    
    # Check for database file
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
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Bain tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%bain%'")
        bain_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found Bain tables: {bain_tables}")
        
        # Create Bain tables if they don't exist
        if not bain_tables:
            print("Creating Bain tables...")
            
            # Create bain_usability table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bain_usability (
                    date TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    value REAL NOT NULL,
                    PRIMARY KEY (date, keyword)
                )
            """)
            
            # Create bain_satisfaction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bain_satisfaction (
                    date TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    value REAL NOT NULL,
                    PRIMARY KEY (date, keyword)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bain_usability_keyword_date ON bain_usability(keyword, date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bain_satisfaction_keyword_date ON bain_satisfaction(keyword, date)")
            
            print("Bain tables created successfully!")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database()
'''
    
    with open("fix_docker_database.py", 'w') as f:
        f.write(fix_script)
    
    print("Docker database fix script created!")
    return True

def main():
    """Apply all fixes for the Docker translation issue"""
    print("APPLYING DOCKER TRANSLATION FIXES")
    print("="*50)
    
    success = True
    
    # Apply all fixes
    success &= fix_source_mapping()
    success &= fix_translation_system()
    success &= fix_app_py()
    success &= create_docker_database_fix()
    
    if success:
        print("\n" + "="*50)
        print("ALL FIXES APPLIED SUCCESSFULLY!")
        print("="*50)
        print("\nThe following fixes have been applied:")
        print("1. Enhanced source mapping for English names")
        print("2. Enhanced translation system with fallbacks")
        print("3. Updated app.py to use enhanced functions")
        print("4. Created database fix script")
        print("\nTo complete the fix:")
        print("1. Rebuild the Docker image")
        print("2. Run the database fix script inside the container")
        print("3. Test the application with English language selected")
    else:
        print("\nERROR: Some fixes could not be applied!")
    
    return success

if __name__ == "__main__":
    main()