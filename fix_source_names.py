#!/usr/bin/env python3
"""
Script to fix the source name mapping issue in the Docker container.
This script updates the app.py file to use consistent source names.
"""

import re

def fix_app_py():
    """Fix the app.py file to use consistent source names"""
    with open('dashboard_app/app.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic line in create_temporal_2d_figure
    # The issue is that the function tries to access columns with translated names
    # but the columns were created with original database names
    
    # Fix 1: Update the debug message to show actual column names
    content = re.sub(
        r'debug_message = f"Processing source: \{source\}"',
        'debug_message = f"Processing source: {source} (Column: {original_column_name if original_column_name else \'Not found\'})"',
        content
    )
    
    # Fix 2: Update the column access logic in create_temporal_2d_figure
    old_pattern = r'if source in filtered_data\.columns:\s+debug_message = f"Processing source: \{source\}"\s+source_data = filtered_data\[source\]\s+source_name = source'
    new_code = '''# Check if source exists in columns (with original or translated name)
            original_column_name = source
            if source not in filtered_data.columns:
                # Try to find the original column name from the translated one
                for col in filtered_data.columns:
                    if col.replace(' - ', ' ').replace(' - ', ' ').replace('org', '').lower() == source.replace(' - ', ' ').replace(' - ', ' ').replace('org', '').lower():
                        original_column_name = col
                        break
            
            if original_column_name in filtered_data.columns:
                debug_message = f"Processing source: {source} (Column: {original_column_name})"
                source_data = filtered_data[original_column_name]
                source_name = source'''
    
    content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Fixed app.py to handle source name mapping correctly")

if __name__ == "__main__":
    fix_app_py()