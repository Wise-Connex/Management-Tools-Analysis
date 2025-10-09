# Source Name Mapping Solution

## Problem Description

The dashboard application was experiencing issues with data retrieval when multiple sources were selected. The root cause was inconsistent source name mapping throughout the codebase:

1. **Display Names**: What users see in the UI (e.g., "Google Trends", "Google Books")
2. **Database Names**: Actual table names in the database (e.g., "Google Trends", "Google Books Ngrams")
3. **Numeric IDs**: Internal identifiers used in database queries (e.g., 1, 2, 3, 4, 5)

The application was inconsistently converting between these different representations, leading to data retrieval failures.

## Solution Overview

We created a centralized mapping system in `fix_source_mapping.py` that handles all conversions between display names, database names, and numeric IDs.

## Mapping Definitions

### Display Names (UI)

These are the names shown to users in the interface:

- Google Trends
- Google Books
- Bain Usability
- Bain Satisfaction
- Crossref

### Database Names (Tables)

These are the actual table names in the database:

- Google Trends
- Google Books Ngrams
- Bain - Usabilidad
- Bain - Satisfacción
- Crossref.org

### Numeric IDs (Internal)

These are the internal identifiers used for database queries:

- 1: Google Trends
- 2: Google Books Ngrams
- 3: Bain - Usabilidad
- 4: Crossref.org
- 5: Bain - Satisfacción

## Implementation Details

### Centralized Mapping Module

The `fix_source_mapping.py` module contains all mapping logic:

```python
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
```

### Conversion Functions

The module provides several utility functions:

1. `display_to_db_names(display_names)` - Convert display names to database names
2. `db_names_to_ids(db_names)` - Convert database names to numeric IDs
3. `display_names_to_ids(display_names)` - Convert display names directly to numeric IDs (main function used)
4. `ids_to_db_names(ids)` - Convert numeric IDs to database names
5. `ids_to_display_names(ids)` - Convert numeric IDs to display names

### Usage in the Application

The main function `map_display_names_to_source_ids()` is imported and used throughout the application:

```python
from fix_source_mapping import map_display_names_to_source_ids

# In callbacks and data retrieval functions
selected_source_ids = map_display_names_to_source_ids(selected_sources)
```

## Benefits of This Solution

1. **Consistency**: All source name conversions now use the same centralized logic
2. **Maintainability**: Changes to mappings only need to be made in one place
3. **Debugging**: Clear traceability of source name conversions
4. **Reliability**: Eliminates inconsistent mapping that caused data retrieval failures

## Testing

The solution has been verified with comprehensive tests that confirm:

- Data retrieval works correctly with multiple sources
- All analysis types function properly with the new mapping
- The "Seleccionar Todo" button works as expected
- Individual source selection works correctly

## Files Modified

1. `app.py` - Updated to use centralized mapping functions
2. `fix_source_mapping.py` - New module with all mapping logic
3. Test files created to verify the solution works correctly

This solution ensures that the dashboard application can reliably retrieve and display data from all sources when selected by the user.
