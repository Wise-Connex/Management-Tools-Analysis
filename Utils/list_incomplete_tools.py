#!/usr/bin/env python3
"""
Script to list all incomplete tools from the CRIndex.csv file.
This helps users identify which tools need to be reprocessed.
"""

import os
import sys
import csv
import logging
from datetime import datetime

# Add parent directory to path to import crossref module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.crossref import get_project_root, setup_logging

def list_incomplete_tools():
    """List all incomplete tools from the CRIndex.csv file"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get project root
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    
    if not os.path.exists(index_path):
        logger.error("CRIndex.csv file not found")
        print("Error: CRIndex.csv file not found")
        return
    
    # Read the index file
    incomplete_tools = []
    complete_tools = []
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            # Check if the file has the Complete column
            if len(header) < 3 or header[2].lower() != 'complete':
                logger.error("CRIndex.csv does not have a Complete column")
                print("Error: CRIndex.csv does not have a Complete column")
                print("Run 'python Utils/fix_crossref_index.py' to fix the index file")
                return
            
            # Read all rows
            for row in reader:
                if row and len(row) >= 3:
                    tool_name = row[0]
                    filename = row[1]
                    complete_status = row[2].lower() == 'true'
                    
                    if complete_status:
                        complete_tools.append((tool_name, filename))
                    else:
                        incomplete_tools.append((tool_name, filename))
    
    except Exception as e:
        logger.error(f"Error reading CRIndex.csv: {str(e)}")
        print(f"Error reading CRIndex.csv: {str(e)}")
        return
    
    # Print results
    print("\n=== Crossref Data Collection Status ===\n")
    
    print(f"Total tools: {len(complete_tools) + len(incomplete_tools)}")
    print(f"Complete tools: {len(complete_tools)}")
    print(f"Incomplete tools: {len(incomplete_tools)}")
    
    if incomplete_tools:
        print("\n=== Incomplete Tools ===\n")
        for i, (tool_name, filename) in enumerate(incomplete_tools, 1):
            print(f"{i}. {tool_name} -> {filename}")
        
        print("\nTo process all incomplete tools, run:")
        print("python Utils/process_remaining_crossref.py --incomplete")
        print("\nTo process a specific tool, run:")
        print("python Utils/crossref.py --tool \"Tool Name\" --force")
    else:
        print("\nAll tools have complete data!")
    
    if complete_tools:
        print("\n=== Complete Tools ===\n")
        for i, (tool_name, filename) in enumerate(complete_tools, 1):
            print(f"{i}. {tool_name} -> {filename}")

if __name__ == "__main__":
    list_incomplete_tools() 