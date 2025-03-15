#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crdbase.py - Management Tool Data Extraction Application

This application allows users to select a management tool and a specific date (YY-MM),
queries the Crossref API with the tool's keywords for that date, and saves the results
to a JSON file for later exploration.

Usage:
    python crdbase.py                      # Interactive mode
    python crdbase.py --tool "Tool Name" --date "YY-MM"  # Command line mode
    python crdbase.py --help               # Show help
"""

import os
import sys
import csv
import json
import logging
import argparse
import requests
from datetime import datetime
from urllib.parse import quote_plus
import time

# Global constants
APP_NAME = "crdbase"
APP_VERSION = "1.0.0"
DEFAULT_ROWS = 1000  # Default number of results to return from API per page

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
    parser = argparse.ArgumentParser(description='Extract Crossref API data for management tools')
    parser.add_argument('--tool', help='Specific tool name to extract data for')
    parser.add_argument('--date', help='Specific date in YY-MM format')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--rows', type=int, default=DEFAULT_ROWS, 
                        help=f'Maximum number of results to return per page (default: {DEFAULT_ROWS})')
    parser.add_argument('--max-results', type=int, default=None,
                        help='Maximum total number of results to return (default: all available)')
    parser.add_argument('--all', action='store_true', 
                        help='Retrieve all available results (may take longer for large result sets)')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {APP_VERSION}')
    return parser.parse_args()

def print_welcome():
    """Print welcome message"""
    print(f"\n{APP_NAME.upper()} v{APP_VERSION} - Management Tool Data Extraction")
    print("=" * 50)
    print("This application queries the Crossref API for specific management tools and dates.")
    print("Results are saved as JSON files for later exploration.")
    print("By default, up to 1000 results are retrieved. Use --all to retrieve all available results.")
    print("=" * 50)

# ===== SECTION 2: TOOL SELECTION MENU (REVISED) =====

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

# ===== SECTION 3: DATE SELECTION INTERFACE (REVISED) =====

def validate_date_format(date_str):
    """
    Validate date string format (YY-MM)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check basic format
    if not (len(date_str) == 5 and date_str[2] == '-'):
        return False
    
    # Check if year and month are digits
    year_str, month_str = date_str.split('-')
    if not (year_str.isdigit() and month_str.isdigit()):
        return False
    
    # Check if month is valid
    month = int(month_str)
    if not 1 <= month <= 12:
        return False
    
    return True

def convert_date_format(date_str, to_format='YYYY-MM'):
    """
    Convert date format between YY-MM and YYYY-MM
    
    Args:
        date_str: Date string to convert
        to_format: Target format ('YYYY-MM' or 'YY-MM')
        
    Returns:
        str: Converted date string or None if invalid
    """
    logger = logging.getLogger(__name__)
    
    try:
        if to_format == 'YYYY-MM':
            # Convert from YY-MM to YYYY-MM
            if len(date_str) == 5 and date_str[2] == '-':
                year_str, month_str = date_str.split('-')
                year = int(year_str)
                month = int(month_str)
                
                # Assume 20YY for years less than 50, 19YY otherwise
                # This is a simple heuristic and might need adjustment
                century = 20 if year < 50 else 19
                full_year = century * 100 + year
                
                return f"{full_year}-{month:02d}"
            else:
                logger.warning(f"Invalid YY-MM format: {date_str}")
                return None
        
        elif to_format == 'YY-MM':
            # Convert from YYYY-MM to YY-MM
            if len(date_str) == 7 and date_str[4] == '-':
                year_str, month_str = date_str.split('-')
                year = int(year_str)
                month = int(month_str)
                
                # Get last two digits of year
                short_year = year % 100
                
                return f"{short_year:02d}-{month:02d}"
            else:
                logger.warning(f"Invalid YYYY-MM format: {date_str}")
                return None
        
        else:
            logger.error(f"Invalid target format: {to_format}")
            return None
    
    except Exception as e:
        logger.error(f"Error converting date format: {str(e)}")
        return None

def validate_date_range(date_str):
    """
    Validate if date is within acceptable range (1950 to present)
    
    Args:
        date_str: Date string in YYYY-MM format
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        year_str, month_str = date_str.split('-')
        year = int(year_str)
        
        # Check if year is within range
        current_year = datetime.now().year
        if not 1950 <= year <= current_year:
            return False
        
        # If it's current year, check if month is not in future
        if year == current_year:
            current_month = datetime.now().month
            if int(month_str) > current_month:
                return False
        
        return True
    
    except Exception:
        return False

def get_date_input():
    """
    Get and validate date input in YY-MM format
    
    Returns:
        str: Selected date in YYYY-MM format or None if cancelled
    """
    logger = logging.getLogger(__name__)
    
    while True:
        print("\nEnter date in YY-MM format (e.g., 21-05 for May 2021)")
        print("Or enter 'cancel' to exit")
        
        date_input = input("Date: ").strip().lower()
        
        # Check for cancel
        if date_input == 'cancel':
            logger.info("User cancelled date selection")
            return None
        
        # Validate format
        if not validate_date_format(date_input):
            print("Invalid format. Please use YY-MM (e.g., 21-05 for May 2021)")
            continue
        
        # Convert to YYYY-MM for validation and storage
        full_date = convert_date_format(date_input, 'YYYY-MM')
        if not full_date:
            print("Error converting date format. Please try again.")
            continue
        
        # Validate date range
        if not validate_date_range(full_date):
            print(f"Invalid date range. Please enter a date between 1950 and present.")
            continue
        
        logger.info(f"User selected date: {full_date}")
        return full_date

# ===== SECTION 4: DATA EXTRACTION FROM CROSSREF API =====

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

def query_crossref_api(keywords, date, max_rows=DEFAULT_ROWS, max_results=None):
    """
    Query Crossref API with keywords for a specific date
    
    Args:
        keywords: Search keywords
        date: Date in YYYY-MM format
        max_rows: Maximum number of results to return per request
        max_results: Maximum total number of results to return (None for all)
        
    Returns:
        dict: API response data or None if error
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Parse the date to get year and month
        year, month = date.split('-')
        
        # Calculate the start and end dates for the month
        start_date = f"{year}-{month}-01"
        
        # Calculate end date (last day of month)
        if month == '12':
            end_date = f"{int(year)+1}-01-01"
        else:
            end_month = int(month) + 1
            end_date = f"{year}-{end_month:02d}-01"
        
        # Prepare the query parameters
        # Remove quotes from keywords if they exist
        clean_keywords = keywords.replace('"', '')
        
        # Initialize variables for pagination
        cursor = "*"  # Start with the first page
        all_items = []
        total_results = 0
        page_count = 0
        
        # Loop until we've retrieved all results or reached a limit
        while cursor:
            params = {
                'query': clean_keywords,
                'filter': f'from-pub-date:{start_date},until-pub-date:{end_date}',
                'rows': max_rows,
                'cursor': cursor,
                'select': 'DOI,title,published,author,container-title,type,subject,abstract'
            }
            
            # Construct the URL
            base_url = "https://api.crossref.org/works"
            query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
            url = f"{base_url}?{query_string}"
            
            page_count += 1
            logger.info(f"Querying Crossref API (page {page_count}): {url}")
            if page_count == 1:
                print(f"Querying Crossref API for {date}...")
            else:
                print(f"Retrieving page {page_count}...")
            
            # Make the request
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Check if we have results
            if 'message' in data and 'items' in data['message']:
                items = data['message']['items']
                if page_count == 1:
                    # Get total results from first page
                    total_results = data['message'].get('total-results', 0)
                    logger.info(f"Found {total_results} total results")
                    print(f"Found {total_results} total results")
                
                # Add items to our collection
                all_items.extend(items)
                logger.info(f"Retrieved {len(items)} items from page {page_count}")
                print(f"Retrieved {len(items)} items from page {page_count} (total: {len(all_items)})")
                
                # Check if we've reached the maximum results limit
                if max_results is not None and len(all_items) >= max_results:
                    logger.info(f"Reached maximum results limit of {max_results}")
                    print(f"Reached maximum results limit of {max_results}")
                    # Trim excess results if needed
                    if len(all_items) > max_results:
                        all_items = all_items[:max_results]
                    break
                
                # Get next cursor for pagination
                next_cursor = data['message'].get('next-cursor')
                
                # Check if we should continue pagination
                if next_cursor and len(all_items) < total_results:
                    cursor = next_cursor
                    # Add a small delay to avoid rate limiting
                    time.sleep(1)
                else:
                    # No more pages or we've reached our limit
                    cursor = None
            else:
                logger.warning("No results found in API response")
                print("No results found in API response")
                return None
        
        # Create a new response with all items
        result = {
            'status': 'ok',
            'message-type': 'work-list',
            'message-version': '1.0.0',
            'message': {
                'total-results': total_results,
                'items': all_items
            }
        }
        
        logger.info(f"Retrieved {len(all_items)} items in total across {page_count} pages")
        print(f"Retrieved {len(all_items)} items in total across {page_count} pages")
        
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        print(f"Error querying Crossref API: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"Error processing API response: {str(e)}")
        print(f"Error processing API response: {str(e)}")
        return None

def save_to_json(data, tool_name, date, output_path=None):
    """
    Save API response data to JSON file
    
    Args:
        data: API response data
        tool_name: Name of the tool
        date: Date in YYYY-MM format
        output_path: Optional output file path
        
    Returns:
        str: Path to the saved file or None if error
    """
    logger = logging.getLogger(__name__)
    
    if not data:
        logger.error("No data to save")
        return None
    
    try:
        # Generate default output path if not provided
        if not output_path:
            project_root = get_project_root()
            output_dir = os.path.join(project_root, 'output', 'crossref_data')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename with tool and date
            tool_name_safe = tool_name.replace(' ', '_').replace('/', '_')
            output_path = os.path.join(output_dir, f"{tool_name_safe}_{date}.json")
        
        # Add metadata to the data
        enriched_data = {
            'metadata': {
                'tool': tool_name,
                'date': date,
                'extraction_time': datetime.now().isoformat(),
                'total_results': data.get('message', {}).get('total-results', 0)
            },
            'data': data
        }
        
        # Write data to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to {output_path}")
        print(f"\nData successfully saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        print(f"\nError saving data: {str(e)}")
        return None

def extract_crossref_data(tool_name, date, output_path=None, max_rows=DEFAULT_ROWS, max_results=None):
    """
    Extract data from Crossref API for a specific tool and date
    
    Args:
        tool_name: Name of the tool
        date: Date in YYYY-MM format
        output_path: Optional output file path
        max_rows: Maximum number of results to return per request
        max_results: Maximum total number of results to return (None for all)
        
    Returns:
        str: Path to the saved file or None if error
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Extracting Crossref data for {tool_name} on {date}")
    
    # Get keywords for the tool
    keywords = get_tool_keywords(tool_name)
    if not keywords:
        print(f"Error: Could not find keywords for {tool_name}")
        return None
    
    # Query Crossref API
    data = query_crossref_api(keywords, date, max_rows, max_results)
    if not data:
        print(f"Error: Could not retrieve data from Crossref API for {date}")
        return None
    
    # Save data to JSON file
    return save_to_json(data, tool_name, date, output_path)

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Parse arguments and print welcome message
    args = parse_arguments()
    print_welcome()
    
    # Handle the --all flag (set max_results to None)
    if args.all:
        args.max_results = None
        logger.info("--all flag specified, retrieving all available results")
    
    # Process command line arguments
    if args.tool and args.date:
        # Find tool by name
        tools = get_available_tools()
        if not tools:
            print("No tools available. Please check the keywords file.")
            sys.exit(1)
        
        tool = find_tool_by_name(tools, args.tool)
        if not tool:
            print(f"Tool not found: {args.tool}")
            sys.exit(1)
        
        # Validate and convert date
        if not validate_date_format(args.date):
            print(f"Invalid date format: {args.date}. Please use YY-MM format.")
            sys.exit(1)
        
        date = convert_date_format(args.date, 'YYYY-MM')
        if not date:
            print(f"Error converting date: {args.date}")
            sys.exit(1)
        
        # Validate date range
        if not validate_date_range(date):
            print(f"Invalid date range. Please enter a date between 1950 and present.")
            sys.exit(1)
        
        print(f"Selected tool: {tool}")
        print(f"Selected date: {date}")
        
        # Extract data
        output_file = extract_crossref_data(tool, date, args.output, args.rows, args.max_results)
        if not output_file:
            print("Failed to extract data.")
            sys.exit(1)
        
    else:
        # Interactive mode
        tools = get_available_tools()
        if not tools:
            print("No tools available. Please check the keywords file.")
            sys.exit(1)
        
        # Display tool selection menu
        selected_tool = display_tool_menu(tools)
        if not selected_tool:
            print("No tool selected. Exiting.")
            sys.exit(0)
        
        print(f"Selected tool: {selected_tool}")
        
        # Get date input
        selected_date = get_date_input()
        if not selected_date:
            print("No date selected. Exiting.")
            sys.exit(0)
        
        print(f"Selected date: {selected_date}")
        
        # Extract data
        output_file = extract_crossref_data(selected_tool, selected_date, args.output, args.rows, args.max_results)
        if not output_file:
            print("Failed to extract data.")
            sys.exit(1)
        
        print("\nData extraction completed successfully.") 