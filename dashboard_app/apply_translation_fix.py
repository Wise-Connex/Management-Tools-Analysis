#!/usr/bin/env python3
"""
Script to apply translation fixes to app.py for Docker compatibility.

This script will:
1. Backup the original app.py file
2. Apply the necessary fixes to handle translation issues in Docker
3. Create a new app.py file with the fixes applied
"""

import os
import shutil
from datetime import datetime

def apply_fixes():
    """Apply translation fixes to app.py"""
    
    # File paths
    app_py_path = "app.py"
    backup_path = f"app.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=== Docker Translation Fix Application ===")
    print(f"Backing up original app.py to {backup_path}")
    
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
    
    # Apply fixes
    fixes_applied = []
    
    # Fix 1: Update create_combined_dataset2 function
    if "def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):" in content:
        # Read the fixed function
        with open("app_translation_fix.py", 'r', encoding='utf-8') as f:
            fix_content = f.read()
        
        # Extract the fixed function
        start_marker = "def create_combined_dataset2_fixed(datasets_norm, selected_sources, dbase_options, language='es'):"
        end_marker = "\n\ndef "
        start_idx = fix_content.find(start_marker)
        if start_idx != -1:
            end_idx = fix_content.find(end_marker, start_idx + 1)
            if end_idx == -1:
                end_idx = len(fix_content)
            
            fixed_function = fix_content[start_idx:end_idx]
            
            # Replace the original function
            original_start = content.find("def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):")
            original_end = content.find("\n\ndef ", original_start + 1)
            if original_end == -1:
                original_end = len(content)
            
            content = content[:original_start] + fixed_function + content[original_end:]
            fixes_applied.append("✓ create_combined_dataset2 function updated")
    
    # Fix 2: Update create_temporal_2d_figure function (placeholder for now)
    # This would require more complex parsing to apply automatically
    
    # Fix 3: Add translation mapping handling to update_main_content callback
    if "combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)" in content:
        old_line = "combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)"
        new_line = "combined_dataset, translation_mapping = create_combined_dataset2_fixed(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options, language=language)"
        content = content.replace(old_line, new_line)
        fixes_applied.append("✓ update_main_content callback updated to use translation mapping")
    
    # Fix 4: Add debugging for translation issues
    debug_code = """
    # Debug: Check column names vs translated names
    print(f"DEBUG: Combined dataset columns: {list(combined_dataset.columns)}")
    print(f"DEBUG: Selected source names: {selected_source_names}")
    print(f"DEBUG: Translation mapping: {translation_mapping}")
    """
    
    if "selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]" in content:
        insert_point = content.find("selected_source_names = [translate_source_name(dbase_options[src_id], language) for src_id in selected_source_ids]")
        if insert_point != -1:
            # Find the end of the line
            line_end = content.find('\n', insert_point)
            content = content[:line_end] + debug_code + content[line_end:]
            fixes_applied.append("✓ Added debugging for translation issues")
    
    # Write the modified content
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Summary
    print("\n=== Fix Application Summary ===")
    for fix in fixes_applied:
        print(fix)
    
    if fixes_applied:
        print(f"\n✓ Successfully applied {len(fixes_applied)} fixes to app.py")
        print("\nNote: Some additional manual changes may be required:")
        print("1. Update figure creation functions to use translation mapping")
        print("2. Update regression analysis callback to handle translation")
        print("3. Test the application thoroughly")
        print("\nSee app_translation_fix.py for detailed implementation of all fixes")
    else:
        print("\n⚠️ No fixes were applied. Please check if the file has already been modified.")
    
    return len(fixes_applied) > 0


if __name__ == "__main__":
    # Change to the dashboard_app directory
    if os.path.exists("dashboard_app"):
        os.chdir("dashboard_app")
        print("Changed to dashboard_app directory")
    
    success = apply_fixes()
    exit(0 if success else 1)