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
    
    # Enhanced mapping for both English and Spanish names
    name_to_id_fallbacks = {
        # English names
        'Bain - Usability': 3,      # Maps to bain_usability table
        'Bain Usability': 3,       # Alternative without dash
        'Bain - Satisfaction': 5,  # Maps to bain_satisfaction table
        'Bain Satisfaction': 5,    # Alternative without dash
        'Google Books': 2,         # Maps to google_books table
        'Google Trends': 1,        # Maps to google_trends table
        'Crossref': 4,             # Maps to crossref table
        
        # Spanish names
        'Bain - Usabilidad': 3,    # Maps to bain_usability table
        'Bain Usabilidad': 3,     # Alternative without dash
        'Bain - Satisfacción': 5,  # Maps to bain_satisfaction table
        'Bain Satisfacción': 5,   # Alternative without dash
        'Google Books Ngrams': 2,  # Maps to google_books table
        'Crossref.org': 4          # Maps to crossref table
    }
    
    # Apply fallbacks for all names
    result_ids = []
    for name in display_names:
        if name in name_to_id_fallbacks:
            result_ids.append(name_to_id_fallbacks[name])
            if name not in ['Bain - Usabilidad', 'Bain - Satisfacción', 'Google Books Ngrams', 'Crossref.org']:
                print(f"Applied mapping: '{name}' -> ID {name_to_id_fallbacks[name]}")
        else:
            print(f"WARNING: No mapping found for '{name}'")
    
    return result_ids

# Replace the standard function for Docker compatibility
map_display_names_to_source_ids = enhanced_display_names_to_ids


# Export the main conversion function for backward compatibility
# Note: This is now handled by the enhanced function above
# map_display_names_to_source_ids = display_names_to_ids