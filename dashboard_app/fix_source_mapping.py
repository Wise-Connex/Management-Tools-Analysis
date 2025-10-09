"""
Utility module to handle consistent source name mapping across the dashboard.
This centralizes all source name conversions to avoid inconsistencies.
"""

# Display names shown in the UI
DISPLAY_NAMES = [
    'Google Trends',
    'Google Books', 
    'Bain Usability',
    'Bain Satisfaction',
    'Crossref'
]

# Mapping from display names to database table names
DISPLAY_TO_DB_NAME = {
    'Google Trends': 'Google Trends',
    'Google Books': 'Google Books Ngrams',
    'Bain Usability': 'Bain - Usabilidad',
    'Bain Satisfaction': 'Bain - Satisfacción',
    'Crossref': 'Crossref.org'
}

# Database options (ID to database name mapping)
DBASE_OPTIONS = {
    1: "Google Trends",
    4: "Crossref.org",
    2: "Google Books Ngrams",
    3: "Bain - Usabilidad",
    5: "Bain - Satisfacción"
}

def get_display_names():
    """Get list of display names for UI"""
    return DISPLAY_NAMES.copy()

def display_to_db_names(display_names):
    """Convert display names to database names"""
    if not display_names:
        return []
    return [DISPLAY_TO_DB_NAME.get(name, name) for name in display_names]

def db_names_to_ids(db_names):
    """Convert database names to numeric IDs"""
    if not db_names:
        return []
    # Create reverse mapping
    db_name_to_id = {v: k for k, v in DBASE_OPTIONS.items()}
    return [db_name_to_id[name] for name in db_names if name in db_name_to_id]

def display_names_to_ids(display_names):
    """Convert display names directly to numeric IDs"""
    if not display_names:
        return []
    db_names = display_to_db_names(display_names)
    return db_names_to_ids(db_names)

def ids_to_db_names(ids):
    """Convert numeric IDs to database names"""
    if not ids:
        return []
    return [DBASE_OPTIONS.get(id) for id in ids if id in DBASE_OPTIONS]

def ids_to_display_names(ids):
    """Convert numeric IDs to display names"""
    if not ids:
        return []
    db_names = ids_to_db_names(ids)
    # Create reverse mapping
    db_to_display = {v: k for k, v in DISPLAY_TO_DB_NAME.items()}
    return [db_to_display.get(name, name) for name in db_names]

# Export the main conversion function for backward compatibility
map_display_names_to_source_ids = display_names_to_ids