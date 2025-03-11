#!/usr/bin/env python3
"""
Script to process remaining incomplete Crossref tools with extended runtime and optimized parameters.
"""
import os
import sys
import logging
import time
from pathlib import Path
import argparse

# Add parent directory to path to import crossref module
sys.path.append(str(Path(__file__).parent.parent))
from Utils.crossref import process_specific_tool, setup_logging, get_incomplete_tools

def main():
    """Process all incomplete tools with extended parameters"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process incomplete Crossref tools with extended parameters')
    parser.add_argument('--delay', type=int, default=120, 
                        help='Delay between tools in seconds (default: 120)')
    parser.add_argument('--tool', type=str, help='Process a specific tool instead of all incomplete tools')
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("Starting process for remaining incomplete Crossref tools with EXTENDED parameters")
    
    # Get list of incomplete tools or use specified tool
    if args.tool:
        incomplete_tools = [args.tool]
        logger.info(f"Processing specific tool in extended mode: {args.tool}")
    else:
        incomplete_tools = get_incomplete_tools()
        logger.info(f"Found {len(incomplete_tools)} incomplete tools: {', '.join(incomplete_tools)}")
    
    if not incomplete_tools:
        logger.info("No incomplete tools found. All tools are complete!")
        return
    
    # Process each incomplete tool with extended runtime
    for i, tool_name in enumerate(incomplete_tools, 1):
        logger.info(f"Processing incomplete tool {i}/{len(incomplete_tools)}: {tool_name}")
        logger.info(f"Using extended runtime and optimized parameters")
        
        # Set environment variable to signal extended processing
        os.environ['CROSSREF_EXTENDED_MODE'] = 'TRUE'
        
        # Process the tool with force flag
        success = process_specific_tool(tool_name, force_reprocess=True)
        
        # Reset environment variable
        os.environ.pop('CROSSREF_EXTENDED_MODE', None)
        
        if not success:
            logger.error(f"Failed to process {tool_name} even with extended parameters")
        else:
            logger.info(f"Successfully processed {tool_name}")
        
        # Add delay between tools to avoid rate limiting
        if i < len(incomplete_tools):  # Skip delay after last tool
            logger.info(f"Waiting {args.delay} seconds before processing next tool...")
            time.sleep(args.delay)
    
    logger.info("Completed processing of remaining tools with extended parameters")

if __name__ == "__main__":
    main() 