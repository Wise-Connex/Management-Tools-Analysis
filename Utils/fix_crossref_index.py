#!/usr/bin/env python3
"""
Script to fix the CRIndex.csv file by adding completion status information.
This script analyzes the log files and CSV files to determine which tools have complete data.
"""

import os
import sys
import csv
import re
import logging
from datetime import datetime

# Add parent directory to path to import crossref module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.crossref import get_project_root, setup_logging

def setup_script_logging():
    """Setup logging specific to this script"""
    logger = logging.getLogger(__name__)
    
    # Create a log file specific to this script
    log_dir = os.path.join(get_project_root(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'fix_index_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def read_index_file():
    """Read the current CRIndex.csv file"""
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    
    if not os.path.exists(index_path):
        return None
    
    index_data = []
    with open(index_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            if row and len(row) >= 2:
                # Ensure row has at least 3 columns (add empty completion status if needed)
                while len(row) < 3:
                    row.append('')
                index_data.append(row)
    
    return index_data

def analyze_log_files():
    """Analyze log files to determine which tools have complete data"""
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    
    # Dictionary to store tool completion status
    tool_status = {}
    
    # Look for log files
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log') and 'crossref' in f.lower()]
    
    if not log_files:
        logger.warning("No crossref log files found")
        return tool_status
    
    # Patterns to match in log files
    complete_pattern = re.compile(r'All expected batches processed.*?Processing tool: (.*?)$', re.MULTILINE | re.DOTALL)
    incomplete_pattern = re.compile(r'Maximum runtime.*?exceeded.*?Failed to get.*?data for (.*?),', re.MULTILINE | re.DOTALL)
    saved_pattern = re.compile(r'Data saved to .*?CR_.*?\.csv.*?Updated index with (.*?) ->', re.MULTILINE | re.DOTALL)
    
    # Process each log file
    for log_file in log_files:
        log_path = os.path.join(logs_dir, log_file)
        logger.info(f"Analyzing log file: {log_path}")
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
                # Find complete tools
                for match in complete_pattern.finditer(log_content):
                    tool_name = match.group(1).strip()
                    if tool_name and tool_name not in tool_status:
                        tool_status[tool_name] = True
                        logger.info(f"Found complete tool: {tool_name}")
                
                # Find incomplete tools
                for match in incomplete_pattern.finditer(log_content):
                    tool_name = match.group(1).strip()
                    if tool_name and tool_name not in tool_status:
                        tool_status[tool_name] = False
                        logger.info(f"Found incomplete tool: {tool_name}")
                
                # Find saved tools (might be complete or incomplete)
                for match in saved_pattern.finditer(log_content):
                    tool_name = match.group(1).strip()
                    if tool_name and tool_name not in tool_status:
                        # Check if this was a complete save
                        context_before = log_content[:match.start()].split('\n')[-5:]
                        context_before = '\n'.join(context_before)
                        
                        if 'All expected batches processed' in context_before:
                            tool_status[tool_name] = True
                            logger.info(f"Found complete tool (from save): {tool_name}")
                        else:
                            tool_status[tool_name] = False
                            logger.info(f"Found incomplete tool (from save): {tool_name}")
        
        except Exception as e:
            logger.error(f"Error processing log file {log_file}: {str(e)}")
    
    return tool_status

def analyze_csv_files():
    """Analyze CSV files to determine which tools have data"""
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    dbase_dir = os.path.join(project_root, 'NewDBase')
    
    # Dictionary to store tool -> filename mapping
    tool_files = {}
    
    # Look for CSV files
    csv_files = [f for f in os.listdir(dbase_dir) if f.startswith('CR_') and f.endswith('.csv')]
    
    if not csv_files:
        logger.warning("No CR_*.csv files found")
        return tool_files
    
    # Read the index file to get tool -> filename mapping
    index_path = os.path.join(dbase_dir, 'CRIndex.csv')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and len(row) >= 2:
                    tool_name = row[0]
                    filename = row[1]
                    tool_files[tool_name] = filename
    
    return tool_files

def update_index_file(index_data, tool_status):
    """Update the CRIndex.csv file with completion status"""
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    
    # Create backup of original file
    backup_path = os.path.join(project_root, 'NewDBase', f'CRIndex_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        logger.info(f"Created backup of CRIndex.csv at {backup_path}")
    
    # Update completion status in index data
    updated_count = 0
    for row in index_data:
        tool_name = row[0]
        if tool_name in tool_status:
            row[2] = str(tool_status[tool_name])
            updated_count += 1
    
    # Write updated index file
    with open(index_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Keyword', 'Filename', 'Complete'])
        writer.writerows(index_data)
    
    logger.info(f"Updated CRIndex.csv with completion status for {updated_count} tools")
    return updated_count

def main():
    """Main function to fix the CRIndex.csv file"""
    # Setup logging
    setup_logging()
    logger = setup_script_logging()
    logger.info("Starting process to fix CRIndex.csv file")
    
    # Read current index file
    index_data = read_index_file()
    if not index_data:
        logger.error("CRIndex.csv file not found or empty")
        return
    
    logger.info(f"Found {len(index_data)} tools in CRIndex.csv")
    
    # Analyze log files to determine completion status
    tool_status = analyze_log_files()
    logger.info(f"Determined completion status for {len(tool_status)} tools from logs")
    
    # Get tool -> filename mapping from CSV files
    tool_files = analyze_csv_files()
    logger.info(f"Found {len(tool_files)} tools with CSV files")
    
    # For tools without status from logs, check if they have CSV files
    for tool_name in tool_files:
        if tool_name not in tool_status:
            # Assume incomplete if we couldn't determine from logs
            tool_status[tool_name] = False
            logger.info(f"Assuming incomplete status for tool with CSV file: {tool_name}")
    
    # Update index file with completion status
    updated_count = update_index_file(index_data, tool_status)
    
    # Log summary
    logger.info(f"Fixed CRIndex.csv file with completion status for {updated_count} tools")
    logger.info(f"Complete tools: {sum(1 for status in tool_status.values() if status)}")
    logger.info(f"Incomplete tools: {sum(1 for status in tool_status.values() if not status)}")
    
    # Print instructions for next steps
    print("\nCRIndex.csv has been updated with completion status information.")
    print(f"Complete tools: {sum(1 for status in tool_status.values() if status)}")
    print(f"Incomplete tools: {sum(1 for status in tool_status.values() if not status)}")
    print("\nTo process incomplete tools, run:")
    print("python Utils/process_remaining_crossref.py --incomplete")

if __name__ == "__main__":
    main() 