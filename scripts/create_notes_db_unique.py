import pandas as pd
import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path for config imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_notes_database():
    """Create a database with unique DOI links and notes for each tool-source combination"""

    # Read the Excel file with notes data
    excel_path = 'pub-assets/Tabla Phyton - Dimar v11.xlsx'
    df = pd.read_excel(excel_path, sheet_name='Tabla Notas', header=3)

    # Read the complete batch CSV with unique DOI data for each source
    doi_df = pd.read_csv('pub-assets/complete_batch_all_138 copy.csv')

    # Create a mapping from English tool names to Spanish tool names
    tool_mapping = {
        'Reengineering, Business Process Reengineering': 'Reingeniería de Procesos',
        'Supply Chain Integration, Supply Chain Management': 'Gestión de la Cadena de Suministro',
        'Scenario Planning, Scenario and Contingency Planning, Scenario Analysis and Contingency Planning': 'Planificación de Escenarios',
        'Strategic Planning, Dynamic Strategic Planning and Budgeting': 'Planificación Estratégica',
        'Customer Satisfaction Surveys, Customer Satisfaction Measurement, Customer Relationship Management, CRM, CRM (Customer Relationship Management), Customer Experience Management': 'Experiencia del Cliente',
        'Total Quality Management, TQM': 'Calidad Total',
        'Mission/Vision, Mission and Vision Statements, Mission & Vision Statements, Purpose, Mission, and Vision Statements': 'Propósito y Visión',
        'Benchmarking': 'Benchmarking',
        'Core Competencies': 'Competencias Centrales',
        'Balanced Scorecard': 'Cuadro de Mando Integral',
        'Strategic Alliance, Strategic Alliances, Corporate Venture Capital': 'Alianzas y Capital de Riesgo',
        'Outsourcing': 'Outsourcing',
        'Customer Segmentation': 'Segmentación de Clientes',
        'Mergers and Acquisitions, Mergers & Acquisitions': 'Fusiones y Adquisiciones',
        'Activity-Based Costing, Activity-Based Management, Activity Based Management': 'Gestión de Costos',
        'Zero-Based Budgeting': 'Presupuesto Base Cero',
        'Growth Strategies, Growth Strategy Tools': 'Estrategias de Crecimiento',
        'Knowledge Management': 'Gestión del Conocimiento',
        'Change Management Programs': 'Gestión del Cambio',
        'Price Optimization Models': 'Optimización de Precios',
        'Loyalty Management + Customer Loyalty + Satisfaction and Loyalty + Customer Retention': 'Lealtad del Cliente',
        'Open-Market Innovation, Collaborative Innovation, Open Innovation, Design Thinking': 'Innovación Colaborativa',
        'Corporate Code of Ethics, Employee Engagement Surveys, Employee Engagement Systems': 'Talento y Compromiso'
    }

    # Create DOI lookup dictionary for each source
    doi_lookup = {}
    for _, row in doi_df.iterrows():
        title = row['title']
        doi = row['doi']
        
        # Extract tool name and source from title
        if ' - Google Trends Analysis' in title:
            tool_name = title.replace(' - Google Trends Analysis', '')
            source = 'Google_Trends'
        elif ' - Google Books Ngram Analysis' in title:
            tool_name = title.replace(' - Google Books Ngram Analysis', '')
            source = 'Google_Books'
        elif ' - Crossref Academic Publications Analysis' in title:
            tool_name = title.replace(' - Crossref Academic Publications Analysis', '')
            source = 'Crossref'
        elif ' - Bain & Company Usability Analysis' in title:
            tool_name = title.replace(' - Bain & Company Usability Analysis', '')
            source = 'BAIN_Ind_Usabilidad'
        elif ' - Bain & Company Satisfaction Analysis' in title:
            tool_name = title.replace(' - Bain & Company Satisfaction Analysis', '')
            source = 'BAIN_Ind_Satisfacción'
        else:
            # Main tool records (without source)
            tool_name = title
            source = 'Main'
        
        # Map to Spanish tool name
        spanish_tool = tool_mapping.get(tool_name, tool_name)
        doi_lookup[(spanish_tool, source)] = doi

    # Transform the data into the format expected by the database
    notes_rows = []

    for _, row in df.iterrows():
        herramienta_excel = row['Herramienta_Gerencial']
        
        # Get the Spanish tool name
        herramienta_spanish = tool_mapping.get(herramienta_excel, herramienta_excel)

        # Google Trends
        if pd.notna(row.get('Google_Trends_Notas')) and str(row['Google_Trends_Notas']).strip():
            doi = doi_lookup.get((herramienta_spanish, 'Google_Trends'), None)
            notes_rows.append({
                'Herramienta': herramienta_spanish,
                'Source': 'Google_Trends',
                'DOI': doi,
                'Notes': str(row['Google_Trends_Notas']),
                'Links': str(row.get('Google_Trends_Links', '')),
                'Keywords': str(row.get('Google_Trends_Keywords', ''))
            })

        # Google Books
        if pd.notna(row.get('Google_Books_Notas')) and str(row['Google_Books_Notas']).strip():
            doi = doi_lookup.get((herramienta_spanish, 'Google_Books'), None)
            notes_rows.append({
                'Herramienta': herramienta_spanish,
                'Source': 'Google_Books',
                'DOI': doi,
                'Notes': str(row['Google_Books_Notas']),
                'Links': str(row.get('Google_Books_Links', '')),
                'Keywords': str(row.get('Google_Books_Keywords', ''))
            })

        # Crossref
        if pd.notna(row.get('Crossref_Notas')) and str(row['Crossref_Notas']).strip():
            doi = doi_lookup.get((herramienta_spanish, 'Crossref'), None)
            notes_rows.append({
                'Herramienta': herramienta_spanish,
                'Source': 'Crossref',
                'DOI': doi,
                'Notes': str(row['Crossref_Notas']),
                'Links': str(row.get('Crossref_Links', '')),
                'Keywords': str(row.get('Crossref_Keywords', ''))
            })

        # BAIN Usability
        if pd.notna(row.get('BAIN_Ind_Usabilidad_Notas')) and str(row['BAIN_Ind_Usabilidad_Notas']).strip():
            doi = doi_lookup.get((herramienta_spanish, 'BAIN_Ind_Usabilidad'), None)
            notes_rows.append({
                'Herramienta': herramienta_spanish,
                'Source': 'BAIN_Ind_Usabilidad',
                'DOI': doi,
                'Notes': str(row['BAIN_Ind_Usabilidad_Notas']),
                'Links': '',
                'Keywords': str(row.get('BAIN_Ind_Usabilidad_Keyboards', ''))
            })

        # BAIN Satisfaction
        if pd.notna(row.get('BAIN_Ind_Satisfacción_Notas')) and str(row['BAIN_Ind_Satisfacción_Notas']).strip():
            doi = doi_lookup.get((herramienta_spanish, 'BAIN_Ind_Satisfacción'), None)
            notes_rows.append({
                'Herramienta': herramienta_spanish,
                'Source': 'BAIN_Ind_Satisfacción',
                'DOI': doi,
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
    
    # Print some sample data for verification
    print("\nSample records:")
    for _, row in notes_df.head(10).iterrows():
        print(f"{row['Herramienta']} - {row['Source']}: DOI {row['DOI']}")

    return notes_df

if __name__ == "__main__":
    create_notes_database()