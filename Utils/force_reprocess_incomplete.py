#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to force reprocess the incomplete tools with extended runtime.
This script specifically targets the tools that are marked as incomplete in CRIndex.csv
and attempts to process them with an extended runtime to ensure completion.
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import utility functions from crossref.py
from Utils.crossref import (
    setup_logging, 
    get_project_root, 
    get_crossref_data, 
    process_specific_tool,
    get_incomplete_tools
)

def setup_arg_parser():
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(description='Force reprocess incomplete tools with extended runtime')
    parser.add_argument('--max-runtime', type=int, default=36000,
                        help='Maximum runtime in seconds for each tool (default: 36000 - 10 hours)')
    parser.add_argument('--specific-tool', type=str, default=None,
                        help='Process only this specific tool (default: process all incomplete tools)')
    return parser

def patch_crossref_max_runtime(max_runtime):
    """
    Temporarily patch the crossref.py file to use an extended max_runtime
    
    Args:
        max_runtime: The new maximum runtime in seconds
        
    Returns:
        tuple: (original_content, patched_content) of the crossref.py file
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Patching crossref.py to use max_runtime={max_runtime}")
    
    # Get the path to crossref.py
    crossref_path = os.path.join(get_project_root(), 'Utils', 'crossref.py')
    
    # Read the original content
    with open(crossref_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Patch the content to use the extended max_runtime
    patched_content = original_content.replace(
        'result = get_crossref_data(query, max_runtime=18000)',
        f'result = get_crossref_data(query, max_runtime={max_runtime})'
    )
    
    # Write the patched content
    with open(crossref_path, 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    return original_content, patched_content

def restore_crossref_file(original_content):
    """
    Restore the original content of crossref.py
    
    Args:
        original_content: The original content to restore
    """
    logger = logging.getLogger(__name__)
    logger.info("Restoring original crossref.py content")
    
    # Get the path to crossref.py
    crossref_path = os.path.join(get_project_root(), 'Utils', 'crossref.py')
    
    # Write the original content
    with open(crossref_path, 'w', encoding='utf-8') as f:
        f.write(original_content)

def main():
    """Main function to force reprocess incomplete tools with extended runtime"""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting forced reprocessing of incomplete tools with extended runtime")
    
    # Parse command line arguments
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # Get the list of tools to process
    if args.specific_tool:
        tools_to_process = [args.specific_tool]
        logger.info(f"Processing specific tool: {args.specific_tool}")
    else:
        tools_to_process = get_incomplete_tools()
        logger.info(f"Found {len(tools_to_process)} incomplete tools to process: {', '.join(tools_to_process)}")
    
    if not tools_to_process:
        logger.info("No incomplete tools found. Exiting.")
        return
    
    # Patch crossref.py to use extended max_runtime
    original_content, _ = patch_crossref_max_runtime(args.max_runtime)
    
    try:
        # Process each tool
        for i, tool_name in enumerate(tools_to_process):
            logger.info(f"Processing tool {i+1}/{len(tools_to_process)}: {tool_name}")
            
            # Process the tool with force flag
            success = process_specific_tool(tool_name, force_reprocess=True)
            
            if success:
                logger.info(f"Successfully processed {tool_name}")
            else:
                logger.error(f"Failed to process {tool_name}")
            
            # Wait between tools (except for the last one)
            if i < len(tools_to_process) - 1:
                wait_time = 60  # 1 minute
                logger.info(f"Waiting {wait_time} seconds before processing next tool...")
                time.sleep(wait_time)
    
    finally:
        # Restore the original content of crossref.py
        restore_crossref_file(original_content)
    
    logger.info("Completed forced reprocessing of incomplete tools")

if __name__ == "__main__":
    main() 