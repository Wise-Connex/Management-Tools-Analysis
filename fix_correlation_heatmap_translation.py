#!/usr/bin/env python3
"""
Script to fix the translation issue in create_correlation_heatmap function.
This applies the same translation mapping logic to handle English->Spanish column names.
"""

import re

def fix_create_correlation_heatmap():
    """Fix the create_correlation_heatmap function to handle translated source names"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Find the create_correlation_heatmap function
    # We need to add the translation mapping logic at the beginning of the function
    
    # Pattern to find the function definition and first debug print
    pattern = r"(def create_correlation_heatmap\(data, sources, language='es'\):\s+print\(f\"DEBUG: create_correlation_heatmap called with sources: \{sources\}\"\))"
    
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
                    break
    
    # Map sources to their original column names
    original_sources = [translated_to_original.get(source, source) for source in sources]"""
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Now update the part where it accesses data[sources]
    old_access = r"corr_data = data\[sources\].corr\(\)"
    new_access = "corr_data = data[original_sources].corr()"
    
    # Apply the fix
    content = re.sub(old_access, new_access, content)
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Fixed create_correlation_heatmap to handle translated source names")

if __name__ == "__main__":
    fix_create_correlation_heatmap()