#!/usr/bin/env python3
"""
Script to process remaining Crossref tools one by one.
This script identifies which tools haven't been processed yet or have incomplete data and processes them individually.
"""

import os
import sys
import csv
import subprocess
import time
import logging
import argparse
from datetime import datetime, timedelta

# Add parent directory to path to import crossref module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.crossref import get_indexed_tools, get_incomplete_tools, read_input_csv, get_project_root, setup_logging

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

def process_tool(tool_name, force=False):
    """Process a single tool using the crossref.py script
    
    Args:
        tool_name: Name of the tool to process
        force: Whether to force reprocessing even if already indexed
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Processing tool: {tool_name}")
    
    # Get project root
    project_root = get_project_root()
    
    # Build command
    crossref_script = os.path.join(project_root, 'Utils', 'crossref.py')
    cmd = [sys.executable, crossref_script, '--tool', tool_name]
    
    # Add force flag if needed
    if force:
        cmd.append('--force')
    
    # Run command
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        print(f"\n{'='*80}")
        print(f"STARTING TOOL: {tool_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Use Popen to capture output in real-time
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Track progress indicators
        start_time = datetime.now()
        batch_info = {"current": 0, "total": 0}
        
        # Process output in real-time
        for line in process.stdout:
            # Log the line
            logger.debug(line.strip())
            
            # Print the line
            print(line.strip())
            
            # Extract batch information if available
            if "Processing batch" in line:
                try:
                    parts = line.split("Processing batch")[1].split("of")
                    batch_info["current"] = int(parts[0].strip())
                    batch_info["total"] = int(parts[1].strip())
                except:
                    pass
            
            # Print progress summary every 10 minutes
            elapsed = datetime.now() - start_time
            if elapsed.seconds % 600 < 1:  # Every ~10 minutes
                if batch_info["total"] > 0:
                    progress = (batch_info["current"] / batch_info["total"]) * 100
                    eta = "unknown"
                    if batch_info["current"] > 0:
                        time_per_batch = elapsed.total_seconds() / batch_info["current"]
                        remaining_batches = batch_info["total"] - batch_info["current"]
                        eta_seconds = time_per_batch * remaining_batches
                        eta = str(timedelta(seconds=int(eta_seconds)))
                    
                    print(f"\nPROGRESS UPDATE: {progress:.1f}% complete ({batch_info['current']}/{batch_info['total']} batches)")
                    print(f"Elapsed time: {str(elapsed).split('.')[0]}, Estimated time remaining: {eta}")
        
        # Wait for process to complete
        process.wait()
        
        end_time = datetime.now()
        elapsed = end_time - start_time
        
        print(f"\n{'='*80}")
        print(f"COMPLETED TOOL: {tool_name} at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {str(elapsed).split('.')[0]}")
        print(f"{'='*80}\n")
        
        if process.returncode == 0:
            logger.info(f"Successfully processed tool: {tool_name}")
            return True
        else:
            logger.error(f"Failed to process tool: {tool_name} (exit code: {process.returncode})")
            return False
    except Exception as e:
        logger.error(f"Exception while processing tool {tool_name}: {str(e)}")
        return False

def main():
    """Main function to process remaining tools"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process remaining or incomplete Crossref tools')
    parser.add_argument('--incomplete', action='store_true', help='Process only incomplete tools')
    parser.add_argument('--all', action='store_true', help='Process all tools, including complete ones')
    parser.add_argument('--delay', type=int, default=30, help='Delay between tools in seconds (default: 30)')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting process to handle Crossref tools")
    
    # Create a log file specific to this script
    log_dir = os.path.join(get_project_root(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'process_remaining_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Set console logging level based on verbose flag
    console_handler = next((h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None)
    if console_handler:
        console_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    
    # Determine which tools to process
    if args.incomplete:
        # Process only incomplete tools
        tools_to_process = get_incomplete_tools()
        logger.info(f"Found {len(tools_to_process)} incomplete tools")
        force = True  # Force reprocessing for incomplete tools
    else:
        # Process remaining tools
        tools_to_process = get_remaining_tools()
        logger.info(f"Found {len(tools_to_process)} remaining tools")
        force = args.all  # Force reprocessing only if --all is specified
    
    if not tools_to_process:
        logger.info("No tools to process")
        print("\nNo tools to process. All tools are either complete or already indexed.")
        return
    
    logger.info(f"Will process {len(tools_to_process)} tools: {', '.join(tools_to_process)}")
    
    # Print summary before starting
    print("\n" + "="*80)
    print(f"PROCESSING SUMMARY")
    print("="*80)
    print(f"Total tools to process: {len(tools_to_process)}")
    print(f"Processing mode: {'Incomplete tools only' if args.incomplete else 'Remaining tools'}")
    print(f"Force reprocessing: {'Yes for all tools' if args.all else 'Yes' if args.incomplete else 'No'}")
    print(f"Delay between tools: {args.delay} seconds")
    print(f"Log file: {log_file}")
    print("="*80)
    print("\nTools to process:")
    for i, tool in enumerate(tools_to_process, 1):
        print(f"{i}. {tool}")
    print("="*80 + "\n")
    
    # Process each tool
    success_count = 0
    failure_count = 0
    start_time = datetime.now()
    
    for i, tool_name in enumerate(tools_to_process, 1):
        tool_start_time = datetime.now()
        elapsed = tool_start_time - start_time
        
        # Print progress header
        print("\n" + "="*80)
        print(f"TOOL {i}/{len(tools_to_process)}: {tool_name}")
        print(f"Started at: {tool_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall progress: {i-1}/{len(tools_to_process)} tools completed ({(i-1)/len(tools_to_process)*100:.1f}%)")
        print(f"Elapsed time: {str(elapsed).split('.')[0]}")
        print("="*80 + "\n")
        
        logger.info(f"Processing tool {i}/{len(tools_to_process)}: {tool_name}")
        
        # Process the tool
        success = process_tool(tool_name, force=force)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
        
        # Wait between tools to avoid rate limiting
        if i < len(tools_to_process):
            print(f"\nWaiting {args.delay} seconds before processing next tool...")
            time.sleep(args.delay)
    
    # Calculate total time
    end_time = datetime.now()
    total_time = end_time - start_time
    
    # Log and print summary
    summary = f"""
{'='*80}
PROCESSING COMPLETE
{'='*80}
Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Total time: {str(total_time).split('.')[0]}

Tools processed: {len(tools_to_process)}
Successfully processed: {success_count}
Failed: {failure_count}

Detailed log saved to: {log_file}
{'='*80}
"""
    
    logger.info(f"Processing complete. Successfully processed {success_count}/{len(tools_to_process)} tools.")
    if failure_count > 0:
        logger.warning(f"Failed to process {failure_count} tools. Check logs for details.")
    
    logger.info(f"Detailed log saved to: {log_file}")
    print(summary)

if __name__ == "__main__":
    main() 