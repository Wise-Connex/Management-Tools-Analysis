#!/usr/bin/env python3
"""
Script to process remaining Crossref tools one by one.
This script identifies which tools haven't been processed yet and processes them individually.
"""

import os
import sys
import csv
import subprocess
import time
import logging
from datetime import datetime

# Add parent directory to path to import crossref module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.crossref import get_indexed_tools, read_input_csv, get_project_root, setup_logging

def get_remaining_tools():
    """Get list of tools that haven't been indexed yet"""
    logger = logging.getLogger(__name__)
    
    # Get project root
    project_root = get_project_root()
    
    # Read input CSV
    input_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
    logger.info(f"Reading input file: {input_file}")
    
    tools_data = read_input_csv(input_file)
    logger.info(f"Found {len(tools_data)} tools in input CSV")
    
    # Get indexed tools
    indexed_tools = get_indexed_tools()
    logger.info(f"Found {len(indexed_tools)} tools already indexed")
    
    # Find remaining tools
    remaining_tools = []
    for tool_name, _ in tools_data:
        if tool_name not in indexed_tools:
            remaining_tools.append(tool_name)
    
    logger.info(f"Found {len(remaining_tools)} tools remaining to be processed")
    return remaining_tools

def process_tool(tool_name):
    """Process a single tool using the crossref.py script"""
    logger = logging.getLogger(__name__)
    logger.info(f"Processing tool: {tool_name}")
    
    # Get project root
    project_root = get_project_root()
    
    # Build command
    crossref_script = os.path.join(project_root, 'Utils', 'crossref.py')
    cmd = [sys.executable, crossref_script, '--tool', tool_name]
    
    # Run command
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully processed tool: {tool_name}")
            logger.debug(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"Failed to process tool: {tool_name}")
            logger.error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Exception while processing tool {tool_name}: {str(e)}")
        return False

def main():
    """Main function to process remaining tools"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting process to handle remaining Crossref tools")
    
    # Create a log file specific to this script
    log_file = os.path.join('logs', f'process_remaining_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Get remaining tools
    remaining_tools = get_remaining_tools()
    
    if not remaining_tools:
        logger.info("No remaining tools to process")
        return
    
    logger.info(f"Will process {len(remaining_tools)} tools: {', '.join(remaining_tools)}")
    
    # Process each tool
    success_count = 0
    failure_count = 0
    
    for i, tool_name in enumerate(remaining_tools, 1):
        logger.info(f"Processing tool {i}/{len(remaining_tools)}: {tool_name}")
        
        # Process the tool
        success = process_tool(tool_name)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
        
        # Wait between tools to avoid rate limiting
        if i < len(remaining_tools):
            logger.info(f"Waiting 30 seconds before processing next tool...")
            time.sleep(30)
    
    # Log summary
    logger.info(f"Processing complete. Successfully processed {success_count}/{len(remaining_tools)} tools.")
    if failure_count > 0:
        logger.warning(f"Failed to process {failure_count} tools. Check logs for details.")
    
    logger.info(f"Detailed log saved to: {log_file}")

if __name__ == "__main__":
    main() 