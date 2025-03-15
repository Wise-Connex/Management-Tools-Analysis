#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crossref2.py - Management Tool Historical Data Extraction

This script extracts historical data from Crossref API for management tools,
searching month by month from 1950 to present, and saves the results in a CSV file.

Usage:
    python crossref2.py                      # Interactive mode
    python crossref2.py --tool "Tool Name"   # Process specific tool
    python crossref2.py --all                # Process all tools
    python crossref2.py --help               # Show help
"""

import os
import sys
import csv
import json
import logging
import argparse
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import quote_plus
import time
import random

# Global constants
APP_NAME = "crossref2"
APP_VERSION = "1.0.0"
DEFAULT_ROWS = 0  # We only need count, not actual results
START_YEAR = 1950  # Starting year for historical data

def get_project_root():
    """Get the project root directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def setup_logging():
    """Setup enhanced logging configuration"""
    project_root = get_project_root()
    log_dir = os.path.join(project_root, 'logs')
    log_file = os.path.join(log_dir, f'{APP_NAME}.log')
    
    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Extract historical Crossref data for management tools')
    parser.add_argument('--tool', help='Specific tool name to extract data for')
    parser.add_argument('--all', action='store_true', help='Process all available tools')
    parser.add_argument('--output', help='Output CSV file path')
    parser.add_argument('--start-year', type=int, default=START_YEAR, help=f'Starting year for historical data (default: {START_YEAR})')
    parser.add_argument('--end-year', type=int, help='Ending year for historical data (default: current year)')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {APP_VERSION}')
    return parser.parse_args()

def print_welcome():
    """Print welcome message"""
    print(f"\n{APP_NAME.upper()} v{APP_VERSION} - Management Tool Historical Data Extraction")
    print("=" * 70)
    print("This application extracts historical data from Crossref API for management tools.")
    print("It searches month by month from 1950 to present and saves results in a CSV file.")
    print("Use --all to process all available management tools (Herramientas Gerenciales).")
    print("=" * 70)

def get_available_tools():
    """
    Get list of available tools from the keywords CSV file
    
    Returns:
        list: List of tool names
    """
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    keywords_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
    tools = []
    
    if not os.path.exists(keywords_file):
        logger.error(f"Keywords file not found: {keywords_file}")
        print(f"Error: Keywords file not found: {keywords_file}")
        return []
    
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check if the row has the required column
                if 'Herramienta Gerencial' not in row:
                    logger.warning("CSV file missing required column 'Herramienta Gerencial'")
                    continue
                
                tool_name = row['Herramienta Gerencial']
                if tool_name and tool_name not in tools:
                    tools.append(tool_name)
        
        logger.info(f"Found {len(tools)} tools in keywords file")
        return tools
    
    except Exception as e:
        logger.error(f"Error reading keywords file: {str(e)}")
        print(f"Error reading keywords file: {str(e)}")
        return []

def display_tool_menu(tools):
    """
    Display menu of available tools and get user selection
    
    Args:
        tools: List of tool names
        
    Returns:
        str: Selected tool name or None if cancelled
    """
    logger = logging.getLogger(__name__)
    
    if not tools:
        logger.error("No tools available to display")
        return None
    
    # Sort tools alphabetically by name for better user experience
    sorted_tools = sorted(tools)
    
    while True:
        print("\nAvailable Management Tools:")
        print("---------------------------")
        
        # Display tools
        for i, tool_name in enumerate(sorted_tools, 1):
            print(f"{i:2d}. {tool_name}")
        
        print("\n 0. Cancel and exit")
        
        # Get user selection
        try:
            selection = input("\nSelect a tool (number): ")
            
            # Check for exit
            if selection.strip() == '0':
                logger.info("User cancelled tool selection")
                return None
            
            # Convert to index
            index = int(selection) - 1
            
            if 0 <= index < len(sorted_tools):
                selected_tool = sorted_tools[index]
                logger.info(f"User selected tool: {selected_tool}")
                return selected_tool
            else:
                print(f"Invalid selection. Please enter a number between 0 and {len(sorted_tools)}.")
        
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            logger.info("Tool selection cancelled by user (KeyboardInterrupt)")
            return None

def find_tool_by_name(tools, tool_name):
    """
    Find a tool by name in the tools list
    
    Args:
        tools: List of tool names
        tool_name: Name of the tool to find
        
    Returns:
        str: Tool name or None if not found
    """
    logger = logging.getLogger(__name__)
    
    # Try exact match first
    if tool_name in tools:
        return tool_name
    
    # Try case-insensitive match
    for tool in tools:
        if tool.lower() == tool_name.lower():
            logger.info(f"Found case-insensitive match for '{tool_name}': '{tool}'")
            return tool
    
    # Try partial match if no exact match found
    matches = []
    for tool in tools:
        if tool_name.lower() in tool.lower():
            matches.append(tool)
    
    if len(matches) == 1:
        logger.info(f"Found partial match for '{tool_name}': '{matches[0]}'")
        return matches[0]
    elif len(matches) > 1:
        logger.warning(f"Multiple matches found for '{tool_name}': {matches}")
        print(f"Multiple tools match '{tool_name}':")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match}")
        
        try:
            selection = input("Please select the correct tool (number): ")
            index = int(selection) - 1
            if 0 <= index < len(matches):
                return matches[index]
        except (ValueError, IndexError):
            logger.error(f"Invalid selection for multiple matches of '{tool_name}'")
            print("Invalid selection.")
    
    logger.error(f"Tool not found: '{tool_name}'")
    return None

def get_tool_keywords(tool_name):
    """
    Get search keywords for a specific tool from the CSV file
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        str: Keywords for the tool or None if not found
    """
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    keywords_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
    
    if not os.path.exists(keywords_file):
        logger.error(f"Keywords file not found: {keywords_file}")
        print(f"Error: Keywords file not found: {keywords_file}")
        return None
    
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Check if the row has the required columns
                if 'Herramienta Gerencial' not in row or 'Keywords' not in row:
                    logger.warning("CSV file missing required columns")
                    continue
                
                # Check if this is the tool we're looking for
                if row['Herramienta Gerencial'] == tool_name:
                    keywords = row['Keywords']
                    logger.info(f"Found keywords for {tool_name}: {keywords}")
                    return keywords
        
        logger.error(f"Tool not found in keywords file: {tool_name}")
        return None
    
    except Exception as e:
        logger.error(f"Error reading keywords file: {str(e)}")
        return None

def generate_date_ranges(start_year, end_year=None):
    """
    Generate month-by-month date ranges from start_year to end_year
    
    Args:
        start_year: Starting year (e.g., 1950)
        end_year: Ending year (default: current year)
        
    Returns:
        list: List of (start_date, end_date, display_date) tuples
    """
    logger = logging.getLogger(__name__)
    
    # Set end_year to current year if not specified
    if not end_year:
        end_year = datetime.now().year
    
    # Validate years
    if start_year < 1950:
        logger.warning(f"Start year {start_year} is before 1950, setting to 1950")
        start_year = 1950
    
    if end_year > datetime.now().year:
        logger.warning(f"End year {end_year} is in the future, setting to current year")
        end_year = datetime.now().year
    
    # Generate date ranges
    date_ranges = []
    
    # Start from January of start_year
    current_date = datetime(start_year, 1, 1)
    
    # End at the current month of end_year or December if end_year is past
    if end_year == datetime.now().year:
        end_date = datetime(end_year, datetime.now().month, 1)
    else:
        end_date = datetime(end_year, 12, 1)
    
    # Generate month-by-month ranges
    while current_date <= end_date:
        # Calculate next month
        next_month = current_date + relativedelta(months=1)
        
        # Format dates for API query
        start_date_str = current_date.strftime("%Y-%m-%d")
        end_date_str = next_month.strftime("%Y-%m-%d")
        
        # Format display date (YYYY-MM)
        display_date = current_date.strftime("%Y-%m")
        
        # Add to list
        date_ranges.append((start_date_str, end_date_str, display_date))
        
        # Move to next month
        current_date = next_month
    
    logger.info(f"Generated {len(date_ranges)} date ranges from {start_year} to {end_year}")
    return date_ranges

def query_crossref_api_count(keywords, start_date, end_date):
    """
    Query Crossref API with keywords for a specific date range and get only the count
    
    Args:
        keywords: Search keywords
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        int: Number of results found or 0 if error
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Remove quotes from keywords if they exist
        clean_keywords = keywords.replace('"', '')
        
        # Prepare the query parameters
        params = {
            'query': clean_keywords,
            'filter': f'from-pub-date:{start_date},until-pub-date:{end_date}',
            'rows': 0  # We only need the count, not the actual results
        }
        
        # Construct the URL
        base_url = "https://api.crossref.org/works"
        query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        logger.info(f"Querying Crossref API for count: {url}")
        
        # Make the request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Get the total count
        if 'message' in data and 'total-results' in data['message']:
            total_results = data['message']['total-results']
            logger.info(f"Found {total_results} results for {start_date} to {end_date}")
            return total_results
        else:
            logger.warning("No results count found in API response")
            return 0
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        return 0
    
    except Exception as e:
        logger.error(f"Error processing API response: {str(e)}")
        return 0

def process_tool(tool_name, start_year, end_year=None, output_path=None):
    """
    Process a single tool: extract historical data and save to CSV
    
    Args:
        tool_name: Name of the tool
        start_year: Starting year for historical data
        end_year: Ending year for historical data (default: current year)
        output_path: Optional output file path
        
    Returns:
        str: Path to the saved CSV file or None if error
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Processing tool: {tool_name} from {start_year} to {end_year or 'present'}")
    print(f"\nProcessing tool: {tool_name} from {start_year} to {end_year or 'present'}")
    
    # Get keywords for the tool
    keywords = get_tool_keywords(tool_name)
    if not keywords:
        print(f"Error: Could not find keywords for {tool_name}")
        return None
    
    # Generate date ranges
    date_ranges = generate_date_ranges(start_year, end_year)
    if not date_ranges:
        print("Error: Could not generate date ranges")
        return None
    
    # Prepare data for CSV
    data = []
    total_ranges = len(date_ranges)
    
    # Process each date range
    for i, (start_date, end_date, display_date) in enumerate(date_ranges, 1):
        # Show progress
        progress = f"[{i}/{total_ranges}]"
        print(f"{progress} Querying {display_date}...", end="\r")
        
        # Query API for count
        count = query_crossref_api_count(keywords, start_date, end_date)
        
        # Add to data
        data.append({
            'Date': display_date,
            tool_name: count
        })
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    print("\nQuery process completed.                ")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Generate default output path if not provided
    if not output_path:
        project_root = get_project_root()
        output_dir = os.path.join(project_root, 'NewDBase')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate 4 random digits
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Create filename with tool and random digits
        tool_name_safe = tool_name.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(output_dir, f"CR_{tool_name_safe}_{random_digits}.csv")
    
    # Save to CSV
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")
        print(f"\nData successfully saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        print(f"\nError saving data: {str(e)}")
        return None

def process_all_tools(tools, start_year, end_year=None):
    """
    Process all tools and save results to individual CSV files
    
    Args:
        tools: List of tool names
        start_year: Starting year for historical data
        end_year: Ending year for historical data (default: current year)
        
    Returns:
        list: List of paths to saved CSV files
    """
    logger = logging.getLogger(__name__)
    total_tools = len(tools)
    logger.info(f"Processing all {total_tools} tools")
    
    print(f"\n{'='*30}")
    print(f"PROCESSING ALL {total_tools} MANAGEMENT TOOLS")
    print(f"{'='*30}")
    print(f"Date range: {start_year} to {end_year or 'present'}")
    print(f"Output directory: NewDBase")
    print(f"{'='*30}\n")
    
    output_files = []
    successful_tools = []
    failed_tools = []
    
    # Sort tools alphabetically for better user experience
    sorted_tools = sorted(tools)
    
    for i, tool_name in enumerate(sorted_tools, 1):
        print(f"\n{'-'*50}")
        print(f"[{i}/{total_tools}] Processing tool: {tool_name}")
        print(f"{'-'*50}")
        
        try:
            output_file = process_tool(tool_name, start_year, end_year)
            if output_file:
                output_files.append(output_file)
                successful_tools.append((tool_name, output_file))
            else:
                failed_tools.append(tool_name)
        except Exception as e:
            logger.error(f"Error processing tool {tool_name}: {str(e)}")
            print(f"Error processing tool {tool_name}: {str(e)}")
            failed_tools.append(tool_name)
    
    # Print summary
    print(f"\n{'='*30}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*30}")
    print(f"Total tools: {total_tools}")
    print(f"Successfully processed: {len(successful_tools)}")
    print(f"Failed: {len(failed_tools)}")
    
    if successful_tools:
        print(f"\nSuccessfully processed tools:")
        for i, (tool_name, file_path) in enumerate(successful_tools, 1):
            filename = os.path.basename(file_path)
            print(f"{i}. {tool_name} -> {filename}")
    
    if failed_tools:
        print(f"\nFailed tools:")
        for i, tool_name in enumerate(failed_tools, 1):
            print(f"{i}. {tool_name}")
    
    print(f"\nAll output files are saved in the 'NewDBase' directory.")
    
    return output_files

def main():
    """Main function"""
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Parse arguments and print welcome message
    args = parse_arguments()
    print_welcome()
    
    # Get available tools
    tools = get_available_tools()
    if not tools:
        print("No tools available. Please check the keywords file.")
        sys.exit(1)
    
    # Set end year
    end_year = args.end_year or datetime.now().year
    
    # Process based on arguments
    if args.all:
        # Process all tools
        logger.info(f"Running in 'all tools' mode with {len(tools)} tools")
        print(f"\nRunning in 'all tools' mode. Found {len(tools)} management tools.")
        
        output_files = process_all_tools(tools, args.start_year, end_year)
        if not output_files:
            print("Failed to process any tools.")
            sys.exit(1)
    elif args.tool:
        # Find tool by name
        tool = find_tool_by_name(tools, args.tool)
        if not tool:
            print(f"Tool not found: {args.tool}")
            sys.exit(1)
        
        # Process single tool
        output_file = process_tool(tool, args.start_year, end_year, args.output)
        if not output_file:
            print("Failed to process tool.")
            sys.exit(1)
    else:
        # Interactive mode
        # Display tool selection menu
        selected_tool = display_tool_menu(tools)
        if not selected_tool:
            print("No tool selected. Exiting.")
            sys.exit(0)
        
        # Process selected tool
        output_file = process_tool(selected_tool, args.start_year, end_year, args.output)
        if not output_file:
            print("Failed to process tool.")
            sys.exit(1)
    
    print("\nHistorical data extraction completed successfully.")

if __name__ == "__main__":
    main()
