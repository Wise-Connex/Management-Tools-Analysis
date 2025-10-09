import pandas as pd
import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_notes_database_with_reformatted():
    """Update the database with reformatted notes from the CSV file"""

    # Read the original CSV file
    csv_path = 'pub-assets/notes_and_doi_spanish.csv'
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} records from {csv_path}")

    # Get the correct database path (same directory as main database)
    from config import get_config
    config = get_config()
    db_dir = config.database_path.parent
    db_path = db_dir / "notes_and_doi.db"

    print(f"Updating database at: {db_path}")

    # Connect to the database
    conn = sqlite3.connect(str(db_path))

    # Update the Notes column in the database
    updated_count = 0
    for _, row in df.iterrows():
        herramienta = row['Herramienta']
        source = row['Source']
        notes = row['Notes']

        # Update the notes for this herramienta and source
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tool_notes
            SET Notes = ?
            WHERE Herramienta = ? AND Source = ?
        """, (notes, herramienta, source))

        if cursor.rowcount > 0:
            updated_count += 1

    conn.commit()
    conn.close()

    print(f"Successfully updated {updated_count} records in the database")

    return updated_count

if __name__ == "__main__":
    update_notes_database_with_reformatted()