#!/usr/bin/env python3
"""
Complete fix for the source name mapping issue.
This script updates the fix_source_mapping.py file to ensure consistent naming.
"""

def update_fix_source_mapping():
    """Update the fix_source_mapping.py file to ensure consistent naming"""
    with open('dashboard_app/fix_source_mapping.py', 'r') as f:
        content = f.read()
    
    # Update the DISPLAY_TO_DB_NAME mapping to ensure consistency
    old_mapping = """# Mapping from display names to database table names
DISPLAY_TO_DB_NAME = {
    'Google Trends': 'Google Trends',
    'Google Books': 'Google Books Ngrams',
    'Bain Usability': 'Bain - Usabilidad',
    'Bain Satisfaction': 'Bain - Satisfacción',
    'Crossref': 'Crossref.org'
}"""
    
    new_mapping = """# Mapping from display names to database table names
DISPLAY_TO_DB_NAME = {
    'Google Trends': 'Google Trends',
    'Google Books': 'Google Books Ngrams',
    'Bain Usability': 'Bain - Usabilidad',
    'Bain Satisfaction': 'Bain - Satisfacción',
    'Crossref': 'Crossref.org'
}

# Reverse mapping for consistent column access
DB_NAME_TO_DISPLAY = {
    'Google Trends': 'Google Trends',
    'Google Books Ngrams': 'Google Books',
    'Bain - Usabilidad': 'Bain Usability',
    'Bain - Satisfacción': 'Bain Satisfaction',
    'Crossref.org': 'Crossref'
}"""
    
    # Replace the mapping
    content = content.replace(old_mapping, new_mapping)
    
    # Add a function to get consistent column names
    new_function = """
def get_consistent_column_name(display_name, db_name):
    \"\"\"Get a consistent column name for both display and database names\"\"\"
    # Always use the database name for column access
    return db_name

def normalize_source_name(name):
    \"\"\"Normalize source name for comparison\"\"\"
    return name.replace(' - ', ' ').replace('org', '').lower()
"""
    
    # Add the new function before the last line
    content = content.replace("map_display_names_to_source_ids = display_names_to_ids", 
                            new_function + "\n\n# Export the main conversion function for backward compatibility\nmap_display_names_to_source_ids = display_names_to_ids")
    
    # Save the updated content
    with open('dashboard_app/fix_source_mapping.py', 'w') as f:
        f.write(content)
    
    print("Updated fix_source_mapping.py with consistent naming")

def update_app_py():
    """Update app.py to use the consistent source name mapping"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Add import for the new function
    if "from dashboard_app.fix_source_mapping import normalize_source_name" not in content:
        # Find the import section for fix_source_mapping
        import_pattern = r"(from dashboard_app\.fix_source_mapping import .*)"
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, r"\1, normalize_source_name", content)
        else:
            # Add new import if not found
            content = re.sub(r"(from dashboard_app\.fix_source_mapping import map_display_names_to_source_ids)",
                           r"from dashboard_app.fix_source_mapping import map_display_names_to_source_ids, normalize_source_name",
                           content)
    
    # Update the create_temporal_2d_figure function to use normalized names
    old_pattern = r"for source in sources:\s+# Check if source exists in columns.*?source_data = filtered_data\[source\]"
    new_pattern = """for source in sources:
            # Check if source exists in columns (with normalized comparison)
            column_found = False
            source_data = None
            
            # First try direct match
            if source in filtered_data.columns:
                source_data = filtered_data[source]
                column_found = True
            else:
                # Try to find matching column using normalized names
                source_normalized = normalize_source_name(source)
                for col in filtered_data.columns:
                    if normalize_source_name(col) == source_normalized:
                        source_data = filtered_data[col]
                        column_found = True
                        break
            
            if not column_found or source_data is None:
                # Skip this source if column not found
                continue"""
    
    # Apply the fix
    content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE | re.DOTALL)
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Updated app.py to use normalized source names")

if __name__ == "__main__":
    import re
    update_fix_source_mapping()
    update_app_py()
    print("Complete fix applied successfully!")