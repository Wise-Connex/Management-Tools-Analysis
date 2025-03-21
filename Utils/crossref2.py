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
from datetime import datetime
import time
from urllib.parse import quote_plus
import random

# Tool name mappings
TOOL_NAME_MAPPINGS = {
    # Reengineering variations
    "Reingeniería de Procesos": "Reengineering",
    "BPR": "Reengineering",
    "Process Reengineering": "Reengineering",
    "Business Reengineering": "Reengineering",
    "Reingeniería": "Reengineering",
    
    # Supply Chain Management variations
    "Gestión de la Cadena de Suministro": "Supply Chain Management",
    "SCM": "Supply Chain Management",
    "Supply Chain": "Supply Chain Management",
    "Cadena de Suministro": "Supply Chain Management",
    
    # Scenario Planning variations
    "Planificación de Escenarios": "Scenario Planning",
    "Scenario Analysis": "Scenario Planning",
    "Scenario-based Planning": "Scenario Planning",
    "Planificación por Escenarios": "Scenario Planning",
    
    # Strategic Planning variations
    "Planificación Estratégica": "Strategic Planning",
    "Strategic Management": "Strategic Planning",
    "Strategic Plan": "Strategic Planning",
    
    # Customer Experience/CRM variations
    "Experiencia del Cliente": "Customer Relationship Management",
    "CRM": "Customer Relationship Management",
    "Customer Relations": "Customer Relationship Management",
    "Gestión de Relaciones con Clientes": "Customer Relationship Management",
    
    # Total Quality Management variations
    "Calidad Total": "Total Quality Management",
    "TQM": "Total Quality Management",
    "Total Quality": "Total Quality Management",
    "Gestión de Calidad Total": "Total Quality Management",
    
    # Mission/Vision variations
    "Propósito y Visión": "Mission Statements",
    "Mission and Vision": "Mission Statements",
    "Mission Statement": "Mission Statements",
    "Misión y Visión": "Mission Statements",
    
    # Core Competencies variations
    "Competencias Centrales": "Core Competencies",
    "Core Competency": "Core Competencies",
    "Core Capability": "Core Competencies",
    "Core Capabilities": "Core Competencies",
    
    # Balanced Scorecard variations
    "Cuadro de Mando Integral": "Balanced Scorecard",
    "CMI": "Balanced Scorecard",
    "BSC": "Balanced Scorecard",
    
    # Strategic Alliances/Venture Capital variations
    "Alianzas y Capital de Riesgo": "Corporate Venture Capital",
    "CVC": "Corporate Venture Capital",
    "Corporate Venturing": "Corporate Venture Capital",
    "Strategic Alliance": "Corporate Venture Capital",
    "Strategic Alliances": "Corporate Venture Capital",
    
    # Customer Segmentation variations
    "Segmentación de Clientes": "Customer Segmentation",
    "Market Segmentation": "Customer Segmentation",
    "Segmentación": "Customer Segmentation",
    
    # Mergers and Acquisitions variations
    "Fusiones y Adquisiciones": "Mergers and Acquisitions",
    "M&A": "Mergers and Acquisitions",
    "Mergers & Acquisitions": "Mergers and Acquisitions",
    
    # Activity Based Management variations
    "Gestión de Costos": "Activity Based Management",
    "ABM": "Activity Based Management",
    "Activity-Based Management": "Activity Based Management",
    "Activity Based Costing": "Activity Based Management",
    
    # Zero Based Budgeting variations
    "Presupuesto Base Cero": "Zero Based Budgeting",
    "ZBB": "Zero Based Budgeting",
    "Zero-Based Budgeting": "Zero Based Budgeting",
    
    # Growth Strategies variations
    "Estrategias de Crecimiento": "Growth Strategies",
    "Growth Strategy": "Growth Strategies",
    "Growth Strategy Tools": "Growth Strategies",
    
    # Knowledge Management variations
    "Gestión del Conocimiento": "Knowledge Management",
    "KM": "Knowledge Management",
    "Knowledge Transfer": "Knowledge Management",
    "Intellectual Capital Management": "Knowledge Management",
    
    # Change Management variations
    "Gestión del Cambio": "Change Management Programs",
    "Change Programs": "Change Management Programs",
    "Change Management": "Change Management Programs",
    
    # Price Optimization variations
    "Optimización de Precios": "Price Optimization",
    "Pricing Optimization": "Price Optimization",
    "Price Management": "Price Optimization",
    "Dynamic Pricing": "Price Optimization",
    "Optimal Pricing": "Price Optimization",
    
    # Customer Loyalty variations
    "Lealtad del Cliente": "Loyalty Management",
    "Customer Loyalty": "Loyalty Management",
    "Loyalty Programs": "Loyalty Management",
    "Customer Retention": "Loyalty Management",
    "Satisfaction and Loyalty": "Loyalty Management",
    
    # Design Thinking/Innovation variations
    "Innovación Colaborativa": "Design Thinking",
    "Design-Thinking": "Design Thinking",
    "Design Innovation": "Design Thinking",
    "Open Innovation": "Design Thinking",
    "Collaborative Innovation": "Design Thinking",
    "Market Innovation": "Design Thinking",
    
    # Corporate Code of Ethics/Employee Engagement variations
    "Talento y Compromiso": "Corporate Code of Ethics",
    "Code of Ethics": "Corporate Code of Ethics",
    "Corporate Ethics": "Corporate Code of Ethics",
    "Employee Engagement": "Corporate Code of Ethics",
    "Employee Engagement Programs": "Corporate Code of Ethics"
}

def map_tool_name(tool_name):
    """
    Map alternative tool names to their standard name
    
    Args:
        tool_name: Input tool name
        
    Returns:
        str: Standardized tool name
    """
    return TOOL_NAME_MAPPINGS.get(tool_name, tool_name)

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
    print("TESTING MODE: You will be prompted to enter a specific year for testing.")
    print("Use --all to process all available management tools (Herramientas Gerenciales).")
    print("=" * 70)

def get_test_year():
    """
    Get test year from user input
    
    Returns:
        int: Year to use for testing (between 1950 and current year)
    """
    logger = logging.getLogger(__name__)
    current_year = datetime.now().year
    
    while True:
        try:
            print("\nTESTING MODE - Year Selection")
            print("=" * 30)
            print(f"Enter a year between 1950 and {current_year}")
            print("Or press Enter to use default year (1950)")
            year_input = input("Test year: ").strip()
            
            # Use default if empty
            if not year_input:
                logger.info("Using default test year: 1950")
                return 1950
            
            # Parse and validate year
            year = int(year_input)
            if 1950 <= year <= current_year:
                logger.info(f"User selected test year: {year}")
                return year
            else:
                print(f"\nError: Year must be between 1950 and {current_year}")
        except ValueError:
            print("\nError: Please enter a valid year")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 1950

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
        tuple: (selection_type, tool_name) where:
            - selection_type: 'all', 'first_half', 'second_half', 'single', or None if cancelled
            - tool_name: Selected tool name for 'single' type, or None for other types
    """
    logger = logging.getLogger(__name__)
    
    if not tools:
        logger.error("No tools available to display")
        return None, None
    
    # Sort tools alphabetically for better user experience
    sorted_tools = sorted(tools)
    
    while True:
        # Clear screen (print newlines)
        print("\n" * 2)
        
        # Print header
        print("╔══════════════════════════════════════╗")
        print("║   Management Tools Analysis Menu     ║")
        print("╚══════════════════════════════════════╝")
        
        # Print special options
        print("\n[Special Options]")
        print("─" * 20)
        print("A) Process ALL Tools")
        print("F) Process First Half of Tools")
        print("S) Process Second Half of Tools")
        print("Q) Quit/Cancel")
        
        # Print tool list with better formatting
        print("\n[Available Tools]")
        print("─" * 20)
        
        # Calculate padding for tool numbers based on total number of tools
        num_width = len(str(len(sorted_tools)))
        
        # Display tools in two columns if there are many
        tools_per_column = (len(sorted_tools) + 1) // 2
        for i in range(tools_per_column):
            # First column
            num1 = str(i + 1).rjust(num_width)
            tool1 = sorted_tools[i]
            line = f"{num1}) {tool1}"
            
            # Second column if available
            if i + tools_per_column < len(sorted_tools):
                num2 = str(i + tools_per_column + 1).rjust(num_width)
                tool2 = sorted_tools[i + tools_per_column]
                # Pad first column to create even spacing
                line = f"{line:<50}{num2}) {tool2}"
            
            print(line)
        
        # Get user selection
        try:
            print("\n" + "─" * 60)
            selection = input("Enter your choice (A/F/S/Q or tool number): ").strip().upper()
            
            # Check for special options
            if selection == 'Q':
                logger.info("User cancelled tool selection")
                return None, None
            elif selection == 'A':
                logger.info("User selected to process all tools")
                return 'all', None
            elif selection == 'F':
                logger.info("User selected to process first half of tools")
                return 'first_half', None
            elif selection == 'S':
                logger.info("User selected to process second half of tools")
                return 'second_half', None
            
            # Handle individual tool selection
            try:
                index = int(selection) - 1
                if 0 <= index < len(sorted_tools):
                    selected_tool = sorted_tools[index]
                    logger.info(f"User selected individual tool: {selected_tool}")
                    return 'single', selected_tool
                else:
                    print("\nInvalid selection!")
                    print(f"Please enter A/F/S/Q for special options")
                    print(f"Or enter a number between 1 and {len(sorted_tools)} for individual tools")
                    input("\nPress Enter to continue...")
            except ValueError:
                print("\nInvalid selection!")
                print(f"Please enter A/F/S/Q for special options")
                print(f"Or enter a number between 1 and {len(sorted_tools)} for individual tools")
                input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            logger.info("Tool selection cancelled by user (KeyboardInterrupt)")
            return None, None

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

def query_crossref_api_by_year(keywords, year):
    """
    Query Crossref API for an entire year, getting monthly breakdowns
    
    Args:
        keywords: Search keywords
        year: Year to query
        
    Returns:
        dict: Monthly counts for the year or None if error
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Remove quotes from keywords if they exist
        clean_keywords = keywords.replace('"', '')
        
        # Set up date range for entire year
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        # Prepare the query parameters
        params = {
            'query': clean_keywords,
            'filter': f'from-pub-date:{start_date},until-pub-date:{end_date}',
            'rows': 0,  # We only need counts
            'facet': 'published-print:month',  # Request monthly breakdown
            'mailto': 'dimar.habeych@udea.edu.co'  # Good practice to identify yourself
        }
        
        # Construct the URL
        base_url = "https://api.crossref.org/works"
        query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        logger.info(f"Querying Crossref API for year {year}: {url}")
        
        # Make the request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Initialize monthly counts
        monthly_counts = {f"{year}-{month:02d}": 0 for month in range(1, 13)}
        
        # Extract monthly counts from facets
        if 'message' in data and 'facets' in data['message']:
            facets = data['message']['facets']
            if 'published-print' in facets:
                for entry in facets['published-print']['values']:
                    month = entry['value']
                    count = entry['count']
                    date_key = f"{year}-{month}"
                    monthly_counts[date_key] = count
        
        logger.info(f"Successfully retrieved monthly counts for {year}")
        return monthly_counts
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error for year {year}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error processing API response for year {year}: {str(e)}")
        return None

def split_search_terms(keywords):
    """
    Split a search expression into individual terms
    
    Args:
        keywords: Search expression that might contain multiple terms
        
    Returns:
        list: List of individual search terms
    """
    logger = logging.getLogger(__name__)
    
    # Remove outer quotes if present
    keywords = keywords.strip()
    if keywords.startswith('"') and keywords.endswith('"'):
        keywords = keywords[1:-1]
    
    # Split by OR and AND
    terms = []
    
    # First split by OR
    or_parts = [p.strip() for p in keywords.split(' OR ')]
    
    # Then split each OR part by AND
    for or_part in or_parts:
        and_parts = [p.strip() for p in or_part.split(' AND ')]
        terms.extend(and_parts)
    
    # Clean up terms
    clean_terms = []
    for term in terms:
        # Remove parentheses
        term = term.replace('(', '').replace(')', '')
        # Remove quotes
        term = term.replace('"', '')
        # Remove leading/trailing whitespace
        term = term.strip()
        if term:
            clean_terms.append(term)
    
    logger.info(f"Split search terms: {keywords} -> {clean_terms}")
    return clean_terms

def query_crossref_api_detailed(term, year, month, tool_name):
    """
    Query Crossref API for detailed publication data for a specific month and single term
    
    Args:
        term: Single search term (no boolean operators)
        year: Year to query
        month: Month to query (1-12)
        tool_name: Name of the tool (needed for saving JSON)
        
    Returns:
        dict: API response with full publication details or None if error
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Verify we have a single term
        if ' AND ' in term or ' OR ' in term:
            logger.error(f"Complex search term received: {term}. Should be split before calling this function.")
            return None
        
        # Remove quotes if present
        clean_term = term.replace('"', '')
        
        # Set up date range for the month
        start_date = f"{year}-{month:02d}-01"
        # Calculate end date considering month lengths
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        # Prepare the query parameters
        params = {
            'query': clean_term,
            'filter': f'from-pub-date:{start_date},until-pub-date:{end_date}',
            'rows': 1000,  # Get full publication details
            'mailto': 'dimar.habeych@udea.edu.co',
            'select': 'DOI,title,type,container-title,subject,abstract,published-print'  # Select specific fields
        }
        
        # Construct the URL
        base_url = "https://api.crossref.org/works"
        query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        logger.info(f"Querying Crossref API for term '{clean_term}' {year}-{month:02d}: {url}")
        
        # Make the request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Add term information to the response
        if 'message' in data:
            data['message']['search_term'] = clean_term
        
        # Save the raw JSON data
        json_file = save_monthly_json(data, tool_name, year, month)
        if json_file:
            logger.info(f"Saved JSON data for term '{clean_term}' to {json_file}")
        
        return data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error for term '{term}' {year}-{month:02d}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error processing API response for term '{term}' {year}-{month:02d}: {str(e)}")
        return None

def save_monthly_json(data, tool_name, year, month):
    """
    Save monthly JSON data to file
    
    Args:
        data: API response data
        tool_name: Name of the tool
        year: Year
        month: Month
        
    Returns:
        str: Path to saved JSON file or None if error
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create directory structure
        project_root = get_project_root()
        json_dir = os.path.join(project_root, 'JsonData', tool_name, f"{year}")
        os.makedirs(json_dir, exist_ok=True)
        
        # Create filename
        filename = f"{year}_{month:02d}.json"
        file_path = os.path.join(json_dir, filename)
        
        # Add metadata to the data
        enriched_data = {
            'metadata': {
                'tool': tool_name,
                'year': year,
                'month': month,
                'extraction_time': datetime.now().isoformat(),
                'total_results': data.get('message', {}).get('total-results', 0)
            },
            'data': data
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved JSON data to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving JSON data for {year}-{month:02d}: {str(e)}")
        return None

def get_single_terms(tool_name):
    """
    Get single search terms for a tool from single_term_queries.json
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        list: List of search terms or None if not found
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Map the tool name to its standardized version
        mapped_tool_name = map_tool_name(tool_name)
        logger.info(f"Mapped tool name '{tool_name}' to '{mapped_tool_name}'")
        
        # Load single term queries
        project_root = get_project_root()
        queries_file = os.path.join(project_root, 'crData', 'single_term_queries.json')
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        # Get terms for tool using mapped name
        if mapped_tool_name not in queries:
            logger.error(f"Tool '{mapped_tool_name}' not found in single_term_queries.json")
            return None
            
        terms = queries[mapped_tool_name]
        logger.info(f"Found terms for {mapped_tool_name}: {terms}")
        return terms
        
    except Exception as e:
        logger.error(f"Error loading single term queries: {str(e)}")
        return None

def merge_term_results(term_files, tool_name):
    """
    Merge results from multiple term queries
    
    Args:
        term_files: List of term result file paths
        tool_name: Name of the tool
        
    Returns:
        dict: Merged results data
    """
    logger = logging.getLogger(__name__)
    
    try:
        all_items = []
        term_statistics = []
        
        # Process each term file
        for file_path in term_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                term_data = json.load(f)
                
            # Add items to combined list
            all_items.extend(term_data['items'])
            
            # Add term statistics
            term_statistics.append({
                'term': term_data['term'],
                'total_results': term_data['total_results'],
                'processed_count': term_data['processed_count'],
                'discarded_count': term_data['discarded_count']
            })
        
        # Create merged results
        merged_data = {
            'tool_name': tool_name,
            'total_items': len(all_items),
            'items': all_items,
            'term_statistics': term_statistics
        }
        
        # Save merged results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(get_project_root(), 'crData', 'results', tool_name, 'merged')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"merged_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2)
            
        logger.info(f"Merged results saved to: {output_file}")
        return merged_data
        
    except Exception as e:
        logger.error(f"Error merging term results: {str(e)}")
        return None

def process_dois(filtered_results, tool_name):
    """
    Process DOIs to remove duplicates
    
    Args:
        filtered_results: Filtered results data
        tool_name: Name of the tool
        
    Returns:
        dict: Results with unique DOIs
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Extract items with DOIs
        items_with_doi = {}  # Use dict for O(1) lookup
        
        for item in filtered_results['items']:
            doi = item.get('doi')
            if doi:
                # If we already have this DOI, keep the one with more complete data
                if doi in items_with_doi:
                    existing_item = items_with_doi[doi]
                    # Compare items and keep the one with more data
                    if len(json.dumps(item)) > len(json.dumps(existing_item)):
                        items_with_doi[doi] = item
                else:
                    items_with_doi[doi] = item
        
        # Convert back to list
        unique_items = list(items_with_doi.values())
        
        # Create final results
        final_data = {
            'tool_name': tool_name,
            'total_items': len(unique_items),
            'items': unique_items
        }
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(get_project_root(), 'crData', 'results', tool_name, 'final')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"final_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)
            
        logger.info(f"Final results saved to: {output_file}")
        return final_data
        
    except Exception as e:
        logger.error(f"Error processing DOIs: {str(e)}")
        return None

def process_tool(tool_name, start_year=1950, end_year=None, output_path=None):
    """
    Process a tool by extracting historical data and saving to CSV and JSON files
    
    Args:
        tool_name: Name of the tool to process
        start_year: Start year (default: 1950)
        end_year: End year (default: current year)
        output_path: Path to save CSV file (default: auto-generated with timestamp)
        
    Returns:
        tuple: (CSV file path, list of JSON file paths)
    """
    logger = logging.getLogger(__name__)
    
    # Get current year if end_year not specified
    if not end_year:
        end_year = datetime.now().year
    
    # Map the tool name to its standardized version
    mapped_tool_name = map_tool_name(tool_name)
    logger.info(f"Processing tool: '{tool_name}' (mapped to '{mapped_tool_name}')")
    
    # 1. Get search terms
    terms = get_single_terms(mapped_tool_name)
    if not terms:
        logger.error(f"No search terms found for {mapped_tool_name}")
        return None, []
    
    json_files = []
    csv_created = False
    total_results_found = 0
    
    try:
        # Process each month in the date range
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                logger.info(f"Processing {year}-{month:02d}")
                
                # 2. Process individual terms
                term_results = []
                
                # Split each term into individual search terms
                for complex_term in terms:
                    individual_terms = split_search_terms(complex_term)
                    logger.info(f"Processing complex term: {complex_term} -> {individual_terms}")
                    
                    # Query API for each individual term
                    for term in individual_terms:
                        monthly_data = query_crossref_api_detailed(term, year, month, mapped_tool_name)
                        if monthly_data and 'message' in monthly_data:
                            results_count = monthly_data['message'].get('total-results', 0)
                            if results_count > 0:
                                term_results.append({
                                    'term': term,
                                    'total_results': results_count,
                                    'items': monthly_data['message'].get('items', [])
                                })
                                logger.info(f"Found {results_count} results for term '{term}'")
                        
                        # Sleep between API calls to avoid rate limiting
                        time.sleep(1)
                
                if not term_results:
                    logger.info(f"No results found for {year}-{month:02d}")
                    continue
                
                # 3. Merge term results
                merged_data = {
                    'total_items': sum(r['total_results'] for r in term_results),
                    'items': [item for r in term_results for item in r['items']]
                }
                logger.info(f"Merged {len(merged_data['items'])} items from {len(term_results)} terms")
                
                # 4. Apply boolean filtering
                boolean_query = get_boolean_query(mapped_tool_name)
                if boolean_query:
                    filtered_data = filter_monthly_results({'message': merged_data}, boolean_query)
                    filtered_count = len(filtered_data['message']['items'])
                    logger.info(f"Filtered results: {filtered_count} items match boolean query")
                else:
                    filtered_data = {'message': merged_data}
                    filtered_count = len(merged_data['items'])
                    logger.info("No boolean filtering applied")
                
                # 5. Process DOIs (remove duplicates)
                final_data = {
                    'total_results': filtered_count,
                    'items': filtered_data['message']['items']
                }
                
                # Save results if we have any
                if final_data['total_results'] > 0:
                    total_results_found += final_data['total_results']
                    
                    # Save to JSON
                    json_file = save_monthly_json(final_data, mapped_tool_name, year, month)
                    if json_file:  # Only append if save was successful
                        json_files.append(json_file)
                        logger.info(f"Saved JSON data to {json_file}")
                    
                    # Create CSV file if not exists
                    if not csv_created:
                        if not output_path:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_path = os.path.join(get_project_root(), 'crData', 'results', f"{mapped_tool_name}_{timestamp}.csv")
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        # Create CSV with headers
                        with open(output_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Tool', 'Year', 'Month', 'Publications'])
                        csv_created = True
                        logger.info(f"Created CSV file: {output_path}")
                    
                    # Append to CSV
                    try:
                        with open(output_path, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow([mapped_tool_name, year, month, final_data['total_results']])
                            logger.info(f"Added {final_data['total_results']} results to CSV for {year}-{month:02d}")
                    except Exception as e:
                        logger.error(f"Error writing to CSV file: {str(e)}")
        
        # Final status report
        if total_results_found > 0:
            logger.info(f"Successfully processed tool {mapped_tool_name}")
            logger.info(f"Total results found: {total_results_found}")
            logger.info(f"CSV file saved to: {output_path}")
            logger.info(f"JSON files saved: {len(json_files)}")
            return output_path, json_files
        else:
            logger.warning(f"No results found for tool {mapped_tool_name} in the specified date range")
            return None, json_files
        
    except Exception as e:
        logger.error(f"Error processing tool {mapped_tool_name}: {str(e)}")
        return None, json_files

def process_tools_subset(tools, subset_type, start_year=None, end_year=None):
    """
    Process a subset of tools based on the selection type
    
    Args:
        tools: List of all tool names
        subset_type: 'all', 'first_half', or 'second_half'
        start_year: Starting year for historical data (default: from user input)
        end_year: Ending year for historical data (default: same as start_year)
        
    Returns:
        list: List of paths to saved CSV files
    """
    logger = logging.getLogger(__name__)
    
    # Get test year if not provided
    if start_year is None:
        start_year = get_test_year()
    if end_year is None:
        end_year = start_year
    
    # Sort tools alphabetically for consistent ordering
    sorted_tools = sorted(tools)
    
    # Determine which tools to process
    if subset_type == 'all':
        tools_to_process = sorted_tools
        subset_name = "ALL"
    elif subset_type == 'first_half':
        mid_point = len(sorted_tools) // 2
        tools_to_process = sorted_tools[:mid_point]
        subset_name = "FIRST HALF"
    elif subset_type == 'second_half':
        mid_point = len(sorted_tools) // 2
        tools_to_process = sorted_tools[mid_point:]
        subset_name = "SECOND HALF"
    else:
        logger.error(f"Invalid subset type: {subset_type}")
        return []
    
    total_tools = len(tools_to_process)
    logger.info(f"Processing {subset_name} of tools ({total_tools} tools)")
    
    print(f"\n{'='*50}")
    print(f"TESTING MODE - PROCESSING {subset_name} OF TOOLS")
    print(f"{'='*50}")
    print(f"Tools to process: {total_tools}")
    print(f"Test year: {start_year}")
    print(f"Output directory: NewDBase")
    print(f"{'='*50}\n")
    
    output_files = []
    successful_tools = []
    failed_tools = []
    
    for i, tool_name in enumerate(tools_to_process, 1):
        print(f"\n{'-'*50}")
        print(f"[{i}/{total_tools}] Processing tool: {tool_name}")
        print(f"{'-'*50}")
        
        try:
            output_file, json_files = process_tool(tool_name, start_year, end_year)
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
    print(f"\n{'='*50}")
    print(f"TESTING MODE - PROCESSING SUMMARY FOR {subset_name}")
    print(f"{'='*50}")
    print(f"Total tools: {total_tools}")
    print(f"Successfully processed: {len(successful_tools)}")
    print(f"Failed: {len(failed_tools)}")
    print(f"Test year: {start_year}")
    
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

def parse_boolean_expression(expression):
    """
    Parse a boolean expression into a structured format that can be evaluated
    
    Args:
        expression: Boolean expression string
        
    Returns:
        dict: Parsed expression structure
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Parsing boolean expression: {expression}")
    
    # Clean up the expression
    # Replace double quotes with single quotes for easier parsing
    clean_expr = expression.replace('""', '"')
    
    # Split by AND first
    and_parts = []
    current_part = ""
    paren_level = 0
    
    # Handle nested parentheses in AND splitting
    for char in clean_expr:
        if char == '(' and current_part.strip() == "":
            paren_level += 1
            if paren_level > 1:
                current_part += char
        elif char == '(':
            paren_level += 1
            current_part += char
        elif char == ')':
            paren_level -= 1
            if paren_level >= 0:
                current_part += char
        elif char == 'A' and paren_level == 0 and len(current_part) >= 4 and current_part[-4:] == " AND":
            # Found " AND" at paren_level 0, split here
            and_parts.append(current_part[:-4].strip())
            current_part = ""
        else:
            current_part += char
    
    # Add the last part if not empty
    if current_part.strip():
        and_parts.append(current_part.strip())
    
    # If no AND parts were found, try the simpler approach
    if not and_parts:
        and_parts = [part.strip() for part in clean_expr.split(' AND ')]
    
    parsed = {
        'type': 'AND',
        'parts': []
    }
    
    for and_part in and_parts:
        # Check if this part has OR conditions
        if ' OR ' in and_part:
            # Handle parentheses if present
            if and_part.startswith('(') and and_part.endswith(')'):
                and_part = and_part[1:-1].strip()
            
            # Split by OR
            or_parts = []
            current_or = ""
            or_paren_level = 0
            
            # Handle nested parentheses in OR splitting
            for char in and_part:
                if char == '(':
                    or_paren_level += 1
                    current_or += char
                elif char == ')':
                    or_paren_level -= 1
                    current_or += char
                elif char == 'O' and or_paren_level == 0 and len(current_or) >= 3 and current_or[-3:] == " OR":
                    # Found " OR" at paren_level 0, split here
                    or_parts.append(current_or[:-3].strip())
                    current_or = ""
                else:
                    current_or += char
            
            # Add the last part if not empty
            if current_or.strip():
                or_parts.append(current_or.strip())
            
            # If no OR parts were found, try the simpler approach
            if not or_parts:
                or_parts = [part.strip() for part in and_part.split(' OR ')]
            
            parsed['parts'].append({
                'type': 'OR',
                'parts': or_parts
            })
        else:
            # Single term (no OR)
            parsed['parts'].append(and_part.strip())
    
    logger.info(f"Parsed expression: {parsed}")
    return parsed

def evaluate_boolean_expression(item, parsed_expr):
    """
    Evaluate if an item matches a parsed boolean expression
    
    Args:
        item: Item to evaluate (dict with metadata)
        parsed_expr: Parsed boolean expression
        
    Returns:
        bool: True if item matches the expression, False otherwise
    """
    # Helper function to check if a term is in an item's metadata
    def term_matches(term, item):
        # Remove quotes and parentheses if present
        term = term.replace('"', '').replace('(', '').replace(')', '').strip()
        
        # Skip empty terms
        if not term:
            return True
        
        # Check in title
        if 'title' in item and isinstance(item['title'], list) and len(item['title']) > 0:
            title = ' '.join(item['title']).lower()
            if term.lower() in title:
                return True
        
        # Check in abstract
        if 'abstract' in item and item['abstract']:
            if isinstance(item['abstract'], str):
                abstract = item['abstract'].lower()
                if term.lower() in abstract:
                    return True
            elif isinstance(item['abstract'], list):
                abstract = ' '.join(item['abstract']).lower()
                if term.lower() in abstract:
                    return True
        
        # Check in subject
        if 'subject' in item and isinstance(item['subject'], list):
            subjects = ' '.join(item['subject']).lower()
            if term.lower() in subjects:
                return True
            
        # Check in container-title (journal name)
        if 'container-title' in item and isinstance(item['container-title'], list) and len(item['container-title']) > 0:
            container_title = ' '.join(item['container-title']).lower()
            if term.lower() in container_title:
                return True
        
        return False
    
    # Evaluate AND expression
    if parsed_expr['type'] == 'AND':
        for part in parsed_expr['parts']:
            if isinstance(part, dict) and part['type'] == 'OR':
                # Evaluate OR expression
                or_result = False
                for or_part in part['parts']:
                    if term_matches(or_part, item):
                        or_result = True
                        break
                
                if not or_result:
                    return False
            else:
                # Evaluate single term
                if not term_matches(part, item):
                    return False
        
        return True
    
    return False

def get_boolean_query(tool_name):
    """
    Get boolean logic query from boolean_logic_queries.json
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        str: Boolean logic query or None if not found
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Map the tool name to its standardized version
        mapped_tool_name = map_tool_name(tool_name)
        logger.info(f"Mapped tool name '{tool_name}' to '{mapped_tool_name}'")
        
        # Load boolean logic queries
        project_root = get_project_root()
        queries_file = os.path.join(project_root, 'crData', 'boolean_logic_queries.json')
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        # Get query for tool using mapped name
        if mapped_tool_name not in queries:
            logger.error(f"Tool '{mapped_tool_name}' not found in boolean_logic_queries.json")
            return None
            
        query = queries[mapped_tool_name]
        logger.info(f"Found boolean query for {mapped_tool_name}: {query}")
        return query
        
    except Exception as e:
        logger.error(f"Error loading boolean logic queries: {str(e)}")
        return None

def filter_monthly_results(monthly_data, boolean_query):
    """
    Filter monthly results using boolean logic
    
    Args:
        monthly_data: API response data
        boolean_query: Boolean logic query
        
    Returns:
        dict: Filtered results
    """
    logger = logging.getLogger(__name__)
    
    if not boolean_query or boolean_query == '#':
        # No filtering needed
        return monthly_data
    
    try:
        # Parse boolean expression
        parsed_expr = parse_boolean_expression(boolean_query)
        
        # Get items from response
        if not monthly_data or 'message' not in monthly_data or 'items' not in monthly_data['message']:
            return monthly_data
        
        items = monthly_data['message']['items']
        filtered_items = []
        
        # Filter items
        for item in items:
            if evaluate_boolean_expression(item, parsed_expr):
                filtered_items.append(item)
        
        # Update response with filtered items
        filtered_data = monthly_data.copy()
        filtered_data['message']['items'] = filtered_items
        filtered_data['message']['total-results'] = len(filtered_items)
        
        return filtered_data
        
    except Exception as e:
        logger.error(f"Error filtering results: {str(e)}")
        return monthly_data

def main():
    """Main function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description=f'{APP_NAME} v{APP_VERSION}')
    parser.add_argument('--start-year', type=int, help='Start year (default: prompt for test year)')
    parser.add_argument('--end-year', type=int, help='End year (default: same as start year)')
    parser.add_argument('--output', help='Output file path (default: auto-generated)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Print welcome message
    print_welcome()
    
    try:
        # Get test year if not provided in arguments
        test_year = args.start_year if args.start_year is not None else get_test_year()
        end_year = args.end_year if args.end_year is not None else test_year
        
        # Get available tools
        tools = get_available_tools()
        if not tools:
            print("Error: No tools found in keywords file")
            return 1
        
        # Display menu and get selection
        selection_type, selected_tool = display_tool_menu(tools)
        
        if not selection_type:
            print("\nOperation cancelled by user")
            return 0
        
        if selection_type == 'single':
            # Process single tool
            output_file, json_files = process_tool(selected_tool, test_year, end_year, args.output)
            if output_file:
                print(f"\nTool processed successfully")
                print(f"Test year: {test_year}")
                print(f"CSV results saved to: {output_file}")
                if json_files:
                    print(f"JSON files saved: {len(json_files)}")
                    print("JSON files location examples:")
                    for i, f in enumerate(json_files[:3]):
                        print(f"- {f}")
                    if len(json_files) > 3:
                        print(f"... and {len(json_files) - 3} more files")
                return 0
            else:
                print("\nError processing tool")
                return 1
        else:
            # Process subset of tools
            output_files = process_tools_subset(tools, selection_type, test_year, end_year)
            if output_files:
                return 0
            else:
                print("\nError processing tools")
                return 1
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
