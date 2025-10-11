#!/usr/bin/env python3
"""
Script to fix the translation issue in create_temporal_2d_figure function.
This applies the same translation mapping logic that was documented in COLUMN_MAPPING_FIX_SUMMARY.md
"""

import re

def fix_create_temporal_2d_figure():
    """Fix the create_temporal_2d_figure function to handle translated source names"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Find the create_temporal_2d_figure function
    # We need to add the translation mapping logic at the beginning of the function
    
    # Pattern to find the function definition and first debug print
    pattern = r"(def create_temporal_2d_figure\(data, sources, language='es', start_date=None, end_date=None\):\s+print\(f\"DEBUG: create_temporal_2d_figure called\"\))"
    
    # Replacement with translation mapping
    replacement = r"""\1
    
    # Create mapping between translated names and original column names
    # This handles the case where UI is in English but DataFrame columns are in Spanish
    translated_to_original = {}
    for source in sources:
        # Try to find the original column name in the data
        if source in data.columns:
            translated_to_original[source] = source
        else:
            # Search for a matching column using normalize_source_name logic
            source_normalized = source.replace(' - ', ' ').replace('org', '').lower()
            for col in data.columns:
                col_normalized = col.replace(' - ', ' ').replace('org', '').lower()
                if source_normalized == col_normalized:
                    translated_to_original[source] = col
                    break"""
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Now update the part where it checks if source is in filtered_data.columns
    # We need to use the mapped name instead of the direct source name
    old_check = r"if source in filtered_data.columns:\s+source_data = filtered_data\[source\]"
    new_check = """# Use the mapped column name (handles English->Spanish translation)
        column_name = translated_to_original.get(source, source)
        if column_name in filtered_data.columns:
            source_data = filtered_data[column_name]"""
    
    # Apply the fix
    content = re.sub(old_check, new_check, content, flags=re.MULTILINE)
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Fixed create_temporal_2d_figure to handle translated source names")

if __name__ == "__main__":
    fix_create_temporal_2d_figure()