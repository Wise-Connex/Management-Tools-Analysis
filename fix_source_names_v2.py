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
    
    # Find the create_temporal_2d_figure function
    # We need to update the part where it checks if source is in filtered_data.columns
    
    # Pattern to find the problematic section
    pattern = r'(for source in sources:\s+# Check if source exists in columns).*?(source_data = filtered_data\[source\])'
    
    # Replacement with proper source name handling
    replacement = r'''\1
            # Handle source name mapping - try original name first, then find matching column
            original_column_name = source
            if source not in filtered_data.columns:
                # Try to find the original column name from the translated one
                # Remove common differences between display and database names
                source_normalized = source.replace(' - ', ' ').replace('org', '').lower()
                for col in filtered_data.columns:
                    col_normalized = col.replace(' - ', ' ').replace('org', '').lower()
                    if source_normalized == col_normalized:
                        original_column_name = col
                        break
            
            # Use the found column name
            if original_column_name in filtered_data.columns:
                source_data = filtered_data[original_column_name]
            else:
                # Skip this source if column not found
                continue\2'''
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Save the updated content
    with open('dashboard_app/app.py', 'w') as f:
        f.write(content)
    
    print("Fixed app.py to handle source name mapping correctly")

if __name__ == "__main__":
    fix_app_py()