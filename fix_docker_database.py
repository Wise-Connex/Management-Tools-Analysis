#!/usr/bin/env python3
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
