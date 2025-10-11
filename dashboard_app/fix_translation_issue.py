#!/usr/bin/env python3
"""
Targeted fix for the Docker translation issue.

The problem: When language is switched to English, the translated source names
don't match the column names in the dataframe, causing errors.

This script applies a minimal fix to handle this issue.
"""

import os
import shutil
from datetime import datetime

def apply_minimal_fix():
    """Apply a minimal fix for the translation issue"""
    
    # File paths
    app_py_path = "app.py"
    backup_path = f"app.py.backup.minimal.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=== Applying Minimal Translation Fix ===")
    print(f"Backing up app.py to {backup_path}")
    
    # Create backup
    if os.path.exists(app_py_path):
        shutil.copy2(app_py_path, backup_path)
        print("✓ Backup created successfully")
    else:
        print(f"❌ Error: {app_py_path} not found")
        return False
    
    # Read the original file
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply minimal fixes
    fixes_applied = []
    
    # Fix 1: Update create_combined_dataset2 to return translation mapping
    if "def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):" in content:
        # Find the function
        start_idx = content.find("def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):")
        if start_idx != -1:
            # Find the end of the function
            end_idx = content.find("\n\ndef ", start_idx + 1)
            if end_idx == -1:
                end_idx = len(content)
            
            # Replace with fixed version
            fixed_function = """def create_combined_dataset2(datasets_norm, selected_sources, dbase_options, language='es'):
    \"\"\"Create combined dataset with all dates from all sources.
    Fixed version that maintains translation mapping between display names and column names.\"\"\"
    import pandas as pd
    from translations import translate_source_name
    
    combined_dataset = pd.DataFrame()

    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)

    # Sort dates
    all_dates = sorted(list(all_dates))

    # Create DataFrame with all dates
    combined_dataset = pd.DataFrame(index=all_dates)

    # Create translation mapping
    translation_mapping = {}
    
    # Add data from each source - use original database name as column name
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            source_data = datasets_norm[source].reindex(all_dates)
            # Use the original database name as the column name
            combined_dataset[source_name] = source_data.iloc[:, 0]
            
            # Create mapping from translated name to original name
            translated_name = translate_source_name(source_name, language)
            translation_mapping[translated_name] = source_name

    return combined_dataset, translation_mapping"""
            
            content = content[:start_idx] + fixed_function + content[end_idx:]
            fixes_applied.append("✓ create_combined_dataset2 function updated to return translation mapping")
    
    # Fix 2: Update update_main_content to use translation mapping
    if "combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)" in content:
        old_line = "combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)"
        new_line = "combined_dataset, translation_mapping = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options, language=language)"
        content = content.replace(old_line, new_line)
        fixes_applied.append("✓ update_main_content callback updated to use translation mapping")
    
    # Fix 3: Add debugging
    if "selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]" in content:
        insert_point = content.find("selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]")
        if insert_point != -1:
            # Find the end of the line
            line_end = content.find('\n', insert_point)
            debug_code = """\n    # Debug: Check column names vs translated names
    print(f"DEBUG: Combined dataset columns: {list(combined_dataset.columns)}")
    print(f"DEBUG: Selected source names: {selected_source_names}")
    print(f"DEBUG: Translation mapping: {translation_mapping}")\n"""
            content = content[:line_end] + debug_code + content[line_end:]
            fixes_applied.append("✓ Added debugging for translation issues")
    
    # Fix 4: Update create_temporal_2d_figure to handle translation mapping
    if "def create_temporal_2d_figure(data, sources, language='es', start_date=None, end_date=None):" in content:
        # Add translation mapping parameter
        old_sig = "def create_temporal_2d_figure(data, sources, language='es', start_date=None, end_date=None):"
        new_sig = "def create_temporal_2d_figure(data, sources, translation_mapping=None, language='es', start_date=None, end_date=None):"
        content = content.replace(old_sig, new_sig)
        
        # Add code to handle translation mapping at the beginning of the function
        start_idx = content.find(new_sig)
        if start_idx != -1:
            # Find the first line of the function body
            first_line = content.find('\n    ', start_idx)
            if first_line != -1:
                mapping_code = """    # Handle translation mapping
    if translation_mapping is None:
        translation_mapping = {}
    
"""
                content = content[:first_line] + mapping_code + content[first_line:]
                fixes_applied.append("✓ create_temporal_2d_figure updated to handle translation mapping")
    
    # Fix 5: Update figure creation calls to pass translation mapping
    if "figure = create_temporal_2d_figure(combined_dataset, selected_source_names, language, start_date, end_date)" in content:
        old_call = "figure = create_temporal_2d_figure(combined_dataset, selected_source_names, language, start_date, end_date)"
        new_call = "figure = create_temporal_2d_figure(combined_dataset, selected_source_names, translation_mapping, language, start_date, end_date)"
        content = content.replace(old_call, new_call)
        fixes_applied.append("✓ Updated temporal 2D figure creation to pass translation mapping")
    
    # Write the modified content
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Summary
    print("\n=== Fix Application Summary ===")
    for fix in fixes_applied:
        print(fix)
    
    if fixes_applied:
        print(f"\n✓ Successfully applied {len(fixes_applied)} fixes to app.py")
        print("\nThe application should now handle translation properly in Docker.")
        print("Test by switching language to English and checking for errors.")
    else:
        print("\n⚠️ No fixes were applied. Please check if the file has already been modified.")
    
    return len(fixes_applied) > 0


if __name__ == "__main__":
    # Change to the dashboard_app directory
    if os.path.exists("dashboard_app"):
        os.chdir("dashboard_app")
        print("Changed to dashboard_app directory")
    
    success = apply_minimal_fix()
    exit(0 if success else 1)