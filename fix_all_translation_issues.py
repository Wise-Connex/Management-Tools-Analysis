#!/usr/bin/env python3
"""
Script to fix all translation issues in the app.py file.
This applies the translation mapping logic to all functions that access source data.
"""

import re

def fix_mean_analysis_function():
    """Fix the mean analysis function to handle translated source names"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Find the mean analysis function
    # We need to add the translation mapping logic at the beginning of the function
    
    # Pattern to find the function where mean analysis is done
    pattern = r"(for range_name, years_back, actual_years in time_ranges:\s+if years_back is None:\s+# Full range\s+mean_val = data\[source\]\.mean\(\))"
    
    # Replacement with translation mapping
    replacement = r"""# Create mapping between translated names and original column names
    # This handles the case where UI is in English but DataFrame columns are in Spanish
    translated_to_original = {}
    for src in sources:
        # Try to find the original column name in the data
        if src in data.columns:
            translated_to_original[src] = src
        else:
            # Search for a matching column using normalize_source_name logic
            src_normalized = src.replace(' - ', ' ').replace('org', '').lower()
            for col in data.columns:
                col_normalized = col.replace(' - ', ' ').replace('org', '').lower()
                if src_normalized == col_normalized:
                    translated_to_original[src] = col
                    break
    
    # Map source to its original column name
    original_source = translated_to_original.get(source, source)
    
    for range_name, years_back, actual_years in time_ranges:
        if years_back is None:
            # Full range
            mean_val = data[original_source].mean()"""
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Also fix the filtered_data access
    old_filtered = r"filtered_data = data\[mask\]\[source\]"
    new_filtered = "filtered_data = data[mask][original_source]"
    
    # Apply the fix
    content = re.sub(old_filtered, new_filtered, content)
    
    return content

def fix_pca_function():
    """Fix the PCA function to handle translated source names"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Find the PCA function
    # We need to add the translation mapping logic at the beginning of the function
    
    # Pattern to find the function definition
    pattern = r"(def create_pca_figure\(data, sources, language='es'\):\s+# Prepare data for PCA\s+pca_data = data\[sources\]\.dropna\(\))"
    
    # Replacement with translation mapping
    replacement = r"""def create_pca_figure(data, sources, language='es'):
    print(f"DEBUG: create_pca_figure called with sources: {sources}")
    
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
    original_sources = [translated_to_original.get(source, source) for source in sources]
    
    # Prepare data for PCA
    pca_data = data[original_sources].dropna()"""
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content

def fix_all_functions():
    """Fix all functions that have translation issues"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Apply all fixes
    content = fix_mean_analysis_function()
    content = fix_pca_function()
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Fixed all translation issues in app.py")

if __name__ == "__main__":
    fix_all_functions()