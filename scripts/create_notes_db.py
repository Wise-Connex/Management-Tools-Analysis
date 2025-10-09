import pandas as pd
import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_notes_database():
    """Create a database with DOI links and notes for management tools from Excel file"""

    # Read the Excel file with notes data
    excel_path = 'pub-assets/Tabla Phyton - Dimar v11.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Tabla Notas', header=3)

    # The columns are already correctly named from the Excel file
    # We just need to use the correct column names

    # Transform the data into the format expected by the database
    notes_rows = []

    for _, row in df.iterrows():
        herramienta = row['Herramienta_Gerencial']

        # Google Trends
        if pd.notna(row.get('Google_Trends_Notas')) and str(row['Google_Trends_Notas']).strip():
            notes_rows.append({
                'Herramienta': herramienta,
                'Source': 'Google_Trends',
                'DOI': None,
                'Notes': str(row['Google_Trends_Notas']),
                'Links': str(row.get('Google_Trends_Links', '')),
                'Keywords': str(row.get('Google_Trends_Keywords', ''))
            })

        # Google Books
        if pd.notna(row.get('Google_Books_Notas')) and str(row['Google_Books_Notas']).strip():
            notes_rows.append({
                'Herramienta': herramienta,
                'Source': 'Google_Books',
                'DOI': None,
                'Notes': str(row['Google_Books_Notas']),
                'Links': str(row.get('Google_Books_Links', '')),
                'Keywords': str(row.get('Google_Books_Keywords', ''))
            })

        # Crossref
        if pd.notna(row.get('Crossref_Notas')) and str(row['Crossref_Notas']).strip():
            notes_rows.append({
                'Herramienta': herramienta,
                'Source': 'Crossref',
                'DOI': None,
                'Notes': str(row['Crossref_Notas']),
                'Links': str(row.get('Crossref_Links', '')),
                'Keywords': str(row.get('Crossref_Keywords', ''))
            })

        # BAIN Usability
        if pd.notna(row.get('BAIN_Ind_Usabilidad_Notas')) and str(row['BAIN_Ind_Usabilidad_Notas']).strip():
            notes_rows.append({
                'Herramienta': herramienta,
                'Source': 'BAIN_Ind_Usabilidad',
                'DOI': None,
                'Notes': str(row['BAIN_Ind_Usabilidad_Notas']),
                'Links': '',
                'Keywords': str(row.get('BAIN_Ind_Usabilidad_Keyboards', ''))
            })

        # BAIN Satisfaction
        if pd.notna(row.get('BAIN_Ind_Satisfacción_Notas')) and str(row['BAIN_Ind_Satisfacción_Notas']).strip():
            notes_rows.append({
                'Herramienta': herramienta,
                'Source': 'BAIN_Ind_Satisfacción',
                'DOI': None,
                'Notes': str(row['BAIN_Ind_Satisfacción_Notas']),
                'Links': '',
                'Keywords': str(row.get('BAIN_Ind_Satisfacción_Keyboards', ''))
            })

    # Create DataFrame
    notes_df = pd.DataFrame(notes_rows)

    # Get the correct database path (same directory as main database)
    from config import get_config
    config = get_config()
    db_dir = config.database_path.parent
    db_path = db_dir / "notes_and_doi.db"

    # Create SQLite database
    if db_path.exists():
        db_path.unlink()  # Remove if exists

    conn = sqlite3.connect(str(db_path))
    notes_df.to_sql('tool_notes', conn, if_exists='replace', index=False)

    # Create indexes for better performance
    conn.execute('CREATE INDEX idx_herramienta ON tool_notes(Herramienta)')
    conn.execute('CREATE INDEX idx_source ON tool_notes(Source)')
    conn.execute('CREATE INDEX idx_herramienta_source ON tool_notes(Herramienta, Source)')

    conn.close()

    print(f"Notes database created successfully with {len(notes_df)} records")
    print(f"Database saved to: {db_path}")

    return notes_df

if __name__ == "__main__":
    create_notes_database()