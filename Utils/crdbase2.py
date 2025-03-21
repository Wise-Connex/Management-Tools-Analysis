#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crdbase.py - Management Tool Data Extraction Application

This application allows users to select a management tool and either:
1. A specific date (YY-MM) for monthly analysis
2. A specific year (YYYY) for full year analysis
3. A range of years (YYYY-YYYY) for multi-year analysis
queries the Crossref API with the tool's keywords, and saves the results
to JSON files for later exploration.

Usage:
    python crdbase.py                      # Interactive mode
    python crdbase.py --tool "Tool Name" --date "YY-MM"  # Command line mode (monthly)
    python crdbase.py --tool "Tool Name" --year "YYYY"     # Command line mode (yearly)
    python crdbase.py --tool "Tool Name" --year-range "YYYY-YYYY"  # Command line mode (multi-year)
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
import shutil
import re

# Global constants
APP_NAME = "crdbase"
APP_VERSION = "2.0.0"  # Updated version number
DEFAULT_ROWS = 1000  # Default number of results to return from API per page
CROSSREF_API_DELAY = 1.5  # Delay between API calls in seconds

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

class BatchProcessor:
    """Manages batch processing and file organization"""
    
    def __init__(self, tool_name, date):
        """
        Initialize batch processor
        
        Args:
            tool_name: Name of the management tool
            date: Date in YY-MM format
        """
        # Track start time
        self.start_time = time.time()
        
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        
        # Map tool name if necessary
        self.original_tool_name = tool_name
        self.tool_name = map_tool_name(tool_name)
        if self.tool_name != self.original_tool_name:
            self.logger.info(f"Mapped tool name '{self.original_tool_name}' to '{self.tool_name}'")
        
        self.date = date
        
        # Generate shorter batch ID (5 chars) using timestamp components
        timestamp = datetime.now()
        # Use minute (2 digits) + second (2 digits) + microsecond (1 digit)
        self.batch_id = f"{timestamp.minute:02d}{timestamp.second:02d}{timestamp.microsecond // 100000}"
        
        # Get or create tool folder ID from existing folder or generate new one
        self.tool_folder_id = self._get_or_create_tool_folder_id()
        
        # Setup batch folder after logger is initialized
        self.base_path = self.setup_batch_folder()
        
        self.logger.info(f"Initialized BatchProcessor for {self.original_tool_name} ({date})")
    
    def _get_or_create_tool_folder_id(self):
        """
        Get existing tool folder ID or create a new one if it doesn't exist
        
        Returns:
            str: Tool folder ID
        """
        # Create safe folder name for the tool
        safe_tool_name = self.original_tool_name.replace(' ', '_').replace('/', '_')
        
        # Check if a folder for this tool already exists
        crdata_path = 'crData'
        if os.path.exists(crdata_path):
            # Look for existing folder with this tool name
            for folder in os.listdir(crdata_path):
                if folder.startswith(f"{safe_tool_name}_"):
                    # Extract the existing folder ID
                    folder_id = folder.split('_')[-1]
                    self.logger.info(f"Found existing tool folder with ID: {folder_id}")
                    return folder_id
        
        # If no existing folder found, generate new ID
        new_id = f"{int(time.time() % 10000):04d}"
        self.logger.info(f"Generated new tool folder ID: {new_id}")
        return new_id
        
    def setup_batch_folder(self):
        """Create and setup batch folder structure"""
        # Create safe folder name using original tool name for the parent folder
        safe_tool_name = self.original_tool_name.replace(' ', '_').replace('/', '_')
        parent_folder_name = f"{safe_tool_name}_{self.tool_folder_id}"
        
        # Create safe folder name for the monthly data
        monthly_folder_name = f"{safe_tool_name}_{self.date}_{self.batch_id}"
        
        # Create folder structure
        parent_path = os.path.join('crData', parent_folder_name)
        base_path = os.path.join(parent_path, monthly_folder_name)
        term_results_path = os.path.join(base_path, 'term_results')
        
        # Create directories
        os.makedirs(parent_path, exist_ok=True)
        os.makedirs(term_results_path, exist_ok=True)
        
        self.logger.info(f"Created batch folder structure at {base_path}")
        return base_path
    
    def get_file_path(self, file_type, term=None):
        """
        Generate standardized file paths for batch files
        
        Args:
            file_type: Type of file (term, merged, filtered, final, statistics)
            term: Optional term name for individual term results
            
        Returns:
            str: Full path to the file
        """
        if term:
            # Individual term result file
            safe_term = term.replace(' ', '_').replace('/', '_')
            return os.path.join(self.base_path, 'term_results', f"{safe_term}_results.json")
        
        # Other file types
        return os.path.join(self.base_path, f"{file_type}_results.json")
    
    def get_all_paths(self):
        """
        Get all file paths associated with this batch
        
        Returns:
            dict: Dictionary of all file paths
        """
        return {
            'base_folder': self.base_path,
            'term_results_folder': os.path.join(self.base_path, 'term_results'),
            'merged': self.get_file_path('merged'),
            'filtered': self.get_file_path('filtered'),
            'final': self.get_file_path('final'),
            'statistics': self.get_file_path('statistics')
        }
    
    def save_json(self, data, file_type, term=None):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            file_type: Type of file
            term: Optional term name for individual term results
            
        Returns:
            str: Path to saved file
        """
        file_path = self.get_file_path(file_type, term)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved {file_type} data to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving {file_type} data: {str(e)}")
            raise

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
    parser.add_argument('--year', help='Specific year in YYYY format')
    parser.add_argument('--year-range', help='Year range in YYYY-YYYY format (e.g., 2010-2015)')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--rows', type=int, default=DEFAULT_ROWS, 
                        help=f'Maximum number of results to return per page (default: {DEFAULT_ROWS})')
    parser.add_argument('--max-results', type=int, default=None,
                        help='Maximum total number of results to return (default: all available)')
    parser.add_argument('--all', action='store_true', 
                        help='Retrieve all available results (may take longer for large result sets)')
    parser.add_argument('--post-filter', action='store_true',
                        help='Apply keyword filtering after retrieving results (recommended for complex queries)')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {APP_VERSION}')
    return parser.parse_args()

def print_welcome():
    """Print welcome message and version information"""
    print(f"\nWelcome to {APP_NAME} v{APP_VERSION}")
    print("Management Tool Data Extraction Application")
    print("\nThis application allows you to extract data from the Crossref API")
    print("for specific management tools and dates.")
    print("\nFeatures:")
    print("- Extract data by tool name and date")
    print("- Support for complex boolean keyword expressions")
    print("- Post-query filtering for better result accuracy")
    print("- Automatic pagination handling")
    print("- Progress reporting and error handling")
    print("\nUse --help for command line options\n")

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
            print("Invalid format. Please use YY-MM format (e.g., 21-05 for May 2021)")
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

def validate_year_format(year_str):
    """
    Validate year string format (YYYY)
    
    Args:
        year_str: Year string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check if it's exactly 4 digits
    if not (len(year_str) == 4 and year_str.isdigit()):
        return False
    
    # Convert to int for validation
    year = int(year_str)
    
    # Check if year is within reasonable range (1950 to current year)
    current_year = datetime.now().year
    if not 1950 <= year <= current_year:
        return False
    
    return True

def get_year_input():
    """
    Get and validate year input in YYYY format
    
    Returns:
        str: Selected year in YYYY format or None if cancelled
    """
    logger = logging.getLogger(__name__)
    
    while True:
        print("\nEnter year in YYYY format (e.g., 2021)")
        print("Or enter 'cancel' to exit")
        
        year_input = input("Year: ").strip().lower()
        
        # Check for cancel
        if year_input == 'cancel':
            logger.info("User cancelled year selection")
            return None
        
        # Validate format
        if not validate_year_format(year_input):
            print("Invalid format. Please use YYYY format (e.g., 2021)")
            continue
        
        logger.info(f"User selected year: {year_input}")
        return year_input

def validate_year_range(start_year, end_year):
    """
    Validate a range of years
    
    Args:
        start_year: Start year in YYYY format
        end_year: End year in YYYY format
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Validate individual years first
    if not (validate_year_format(start_year) and validate_year_format(end_year)):
        return False
    
    # Convert to integers for comparison
    start = int(start_year)
    end = int(end_year)
    
    # Check if range is valid (start <= end)
    if start > end:
        return False
    
    return True

def get_year_range_input():
    """
    Get and validate year range input in YYYY-YYYY format
    
    Returns:
        tuple: (start_year, end_year) in YYYY format or (None, None) if cancelled
    """
    logger = logging.getLogger(__name__)
    
    while True:
        print("\nEnter year range in YYYY-YYYY format (e.g., 2010-2015)")
        print("Or enter 'cancel' to exit")
        
        range_input = input("Year range: ").strip().lower()
        
        # Check for cancel
        if range_input == 'cancel':
            logger.info("User cancelled year range selection")
            return None, None
        
        # Split range
        try:
            start_year, end_year = range_input.split('-')
            
            # Validate range
            if validate_year_range(start_year, end_year):
                logger.info(f"User selected year range: {start_year}-{end_year}")
                return start_year, end_year
            else:
                print("Invalid year range. Please enter years between 1950 and present, with start year <= end year")
        except ValueError:
            print("Invalid format. Please use YYYY-YYYY (e.g., 2010-2015)")
            continue

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

def convert_year(yy):
    """
    Convert 2-digit year to 4-digit year
    - Years 00-49 are assumed to be 2000-2049
    - Years 50-99 are assumed to be 1950-1999
    
    Args:
        yy: Two-digit year string
        
    Returns:
        str: Four-digit year string
    """
    year = int(yy)
    if year >= 50:
        return f"19{yy}"
    else:
        return f"20{yy}"

def query_crossref_api(term, date, max_rows=DEFAULT_ROWS):
    """
    Query Crossref API for a term and date
    
    Args:
        term: Search term
        date: Date in YY-MM format
        max_rows: Maximum rows to return per page
        
    Returns:
        dict: API response data
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Convert date to required format
        date_parts = date.split('-')
        if len(date_parts) != 2:
            raise ValueError("Invalid date format. Expected YY-MM")
            
        year = convert_year(date_parts[0])  # Use new convert_year function
        month = date_parts[1]
        
        logger.info(f"Converting date {date} to {year}-{month}")
        
        # Setup API parameters
        base_url = "https://api.crossref.org/works"
        params = {
            'query': term,
            'rows': max_rows,
            'filter': f"from-pub-date:{year}-{month},until-pub-date:{year}-{month}",
            'cursor': '*'  # Start cursor
        }
        
        all_items = []
        total_results = 0
        items_retrieved = 0
        
        # Process paginated results
        while True:
            # Make API request
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Get total results on first page
            if total_results == 0:
                total_results = data['message']['total-results']
                logger.info(f"Total results for term '{term}': {total_results}")
                
                if total_results == 0:
                    logger.warning("No results found")
                    break
            
            # Process items
            items = data['message']['items']
            current_page_items = len(items)
            if current_page_items == 0:
                break
                
            all_items.extend(items)
            items_retrieved += current_page_items
            
            # Calculate and display progress
            if total_results > 0:
                progress = (items_retrieved / total_results) * 100
                print(f"\rRetrieving results: {items_retrieved}/{total_results} ({progress:.1f}%)", end='')
            
            # Check if we've retrieved all results
            if items_retrieved >= total_results:
                print()  # New line after progress bar is complete
                break
            
            # Get next cursor
            next_cursor = data['message'].get('next-cursor')
            if not next_cursor:
                print()  # New line after progress bar
                break
            
            # Update cursor for next page
            params['cursor'] = next_cursor
            
        # Return results
        return {
            'term': term,
            'total_results': total_results,
            'processed_count': items_retrieved,
            'discarded_count': total_results - items_retrieved if total_results > items_retrieved else 0,
            'items': all_items
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error for term '{term}': {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for term '{term}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing term '{term}': {str(e)}")
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

def extract_crossref_data(tool_name, date, output_path=None, max_rows=DEFAULT_ROWS, max_results=None, post_filter=False):
    """
    Extract data from Crossref API for a specific tool and date
    
    Args:
        tool_name: Name of the management tool
        date: Date in YY-MM format
        output_path: Optional path to save JSON output
        max_rows: Maximum number of results to return per page
        max_results: Maximum total number of results to return
        post_filter: Whether to apply keyword filtering after retrieving results
        
    Returns:
        str: Path to the saved JSON file or None if error
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Extracting data for {tool_name} ({date})")
    
    # Get keywords for the tool
    keywords = get_tool_keywords(tool_name)
    if not keywords:
        print(f"Error: Could not find keywords for tool '{tool_name}'")
        return None
    
    # Query Crossref API
    total_results, items = query_crossref_api(keywords, date, max_rows)
    if not items:
        print(f"Error: Could not retrieve data from Crossref API for {date}")
        return None
    
    # Prepare data for saving
    data = {
        'status': 'ok',
        'message-type': 'work-list',
        'message-version': '1.0.0',
        'message': {
            'total-results': total_results,
            'items': items
        }
    }
    
    # Save data to JSON file
    return save_to_json(data, tool_name, date, output_path)

def get_single_terms(tool_name):
    """
    Get individual search terms from single_term_queries.json
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        list: List of search terms
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Map tool name if necessary
        mapped_tool_name = map_tool_name(tool_name)
        if mapped_tool_name != tool_name:
            logger.info(f"Looking up terms for mapped tool name '{mapped_tool_name}'")
        
        # Load single term queries
        project_root = get_project_root()
        queries_file = os.path.join(project_root, 'crData', 'single_term_queries.json')
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        # Get terms for tool
        if mapped_tool_name not in queries:
            logger.error(f"Tool '{mapped_tool_name}' not found in single_term_queries.json")
            return []
            
        terms = queries[mapped_tool_name]
        logger.info(f"Found {len(terms)} search terms for {mapped_tool_name}")
        return terms
        
    except Exception as e:
        logger.error(f"Error loading single term queries: {str(e)}")
        return []

def process_entry(item):
    """
    Process a single entry from the Crossref API
    
    Args:
        item: API response item
        
    Returns:
        dict: Processed item or None if invalid
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Check required fields
        if not item.get('DOI'):
            logger.debug("Skipping entry: Missing DOI")
            return None
            
        if not item.get('title'):
            logger.debug(f"Skipping entry {item['DOI']}: Missing title")
            return None
        
        # Create processed entry with required fields
        processed = {
            'doi': item['DOI'],
            'title': item['title'],
            'type': item.get('type', ''),
            'container-title': item.get('container-title', []),
            'subject': item.get('subject', []),
            'abstract': item.get('abstract', '')
        }
        
        # Add publication date if available
        if 'published-print' in item:
            date_parts = item['published-print'].get('date-parts', [[]])[0]
            if len(date_parts) >= 2:
                processed['publication_date'] = f"{date_parts[0]}-{date_parts[1]:02d}"
        
        return processed
        
    except Exception as e:
        logger.error(f"Error processing entry: {str(e)}")
        return None

def process_individual_terms(terms, date, batch):
    """
    Process individual search terms
    
    Args:
        terms: List of search terms
        date: Date in YY-MM format
        batch: BatchProcessor instance
        
    Returns:
        list: List of processed term file paths
    """
    logger = logging.getLogger(__name__)
    term_files = []
    
    for term in terms:
        logger.info(f"Processing term: {term}")
        
        # Query API
        api_response = query_crossref_api(term, date)
        
        # Skip if no results or error
        if not api_response:
            logger.warning(f"No results for term: {term}")
            continue
            
        # Process results
        processed_data = {
            'term': term,
            'total_results': api_response['total_results'],
            'processed_count': api_response['processed_count'],
            'discarded_count': api_response['discarded_count'],
            'items': []
        }
        
        # Process each item
        for item in api_response['items']:
            processed_item = process_entry(item)
            if processed_item:
                processed_data['items'].append(processed_item)
        
        # Save term results
        file_path = batch.save_json(processed_data, 'term', term)
        if file_path:
            term_files.append(file_path)
    
    return term_files

def merge_term_results(term_files, batch):
    """
    Merge individual term results
    
    Args:
        term_files: List of term result file paths
        batch: BatchProcessor instance
        
    Returns:
        dict: Merged results
    """
    logger = logging.getLogger(__name__)
    
    merged_items = []
    term_stats = []
    
    for file_path in term_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            merged_items.extend(data['items'])
            term_stats.append({
                'term': data['term'],
                'total_results': data['total_results'],
                'processed_count': data['processed_count'],
                'discarded_count': data['discarded_count']
            })
            
        except Exception as e:
            logger.error(f"Error merging results from {file_path}: {str(e)}")
    
    # Save merged results
    merged_data = {
        'term_statistics': term_stats,
        'total_items': len(merged_items),
        'items': merged_items
    }
    
    batch.save_json(merged_data, 'merged')
    return merged_data

def get_boolean_query(tool_name):
    """
    Get boolean logic query from boolean_logic_queries.json
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        str: Boolean logic query
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Load boolean logic queries
        project_root = get_project_root()
        queries_file = os.path.join(project_root, 'crData', 'boolean_logic_queries.json')
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            queries = json.load(f)
        
        # Get query for tool
        if tool_name not in queries:
            logger.error(f"Tool '{tool_name}' not found in boolean_logic_queries.json")
            return None
            
        query = queries[tool_name]
        logger.info(f"Found boolean query for {tool_name}: {query}")
        return query
        
    except Exception as e:
        logger.error(f"Error loading boolean logic queries: {str(e)}")
        return None

def check_consecutive_terms(text, terms):
    """
    Check if terms appear consecutively in the text as a complete phrase
    
    Args:
        text: Text to search in (title)
        terms: List of terms to find consecutively
        
    Returns:
        bool: True if terms appear consecutively as a complete phrase
    """
    if not text or not terms:
        return False
    
    # Create regex pattern for exact phrase matching with word boundaries
    # Join terms and escape special characters
    phrase = ' '.join(terms).lower()
    pattern = r'\b' + re.escape(phrase) + r'\b'
    text_lower = text.lower()
    
    match = re.search(pattern, text_lower)
    return bool(match)

def apply_boolean_filter(merged_results, boolean_query, batch):
    """
    Apply boolean logic filtering to merged results, checking only titles for exact phrases
    
    Args:
        merged_results: Merged results data
        boolean_query: Boolean logic query
        batch: BatchProcessor instance
        
    Returns:
        dict: Filtered results
    """
    logger = logging.getLogger(__name__)
    
    # If no boolean query provided, pass through all results
    if not boolean_query:
        logger.warning("No boolean query provided, using all results")
        filtered_data = {
            'query': None,
            'total_items': len(merged_results['items']),
            'items': merged_results['items']
        }
        batch.save_json(filtered_data, 'filtered')
        return filtered_data
    
    filtered_items = []
    
    # Convert boolean query to exact phrases to match
    exact_phrases = []
    if boolean_query == '#':
        # Special case: use all results from API
        return merged_results
        
    # Split on OR and convert AND_NEXT to spaces for exact phrases
    for part in boolean_query.split(' OR '):
        # Replace AND_NEXT with a single space and normalize whitespace
        phrase = ' '.join(part.split('AND_NEXT'))
        # Normalize whitespace: remove extra spaces and strip
        phrase = ' '.join(phrase.split()).strip().lower()
        exact_phrases.append(phrase)
    
    logger.info(f"Looking for exact phrases: {exact_phrases}")
    
    # Check each item's title for exact phrases
    for item in merged_results['items']:
        # Get title as single string, lowercase for comparison
        title = ' '.join(item.get('title', [])) if isinstance(item.get('title'), list) else str(item.get('title', ''))
        # Normalize whitespace in title too
        title = ' '.join(title.split()).strip().lower()
        
        # Check if any of our exact phrases appear in the title
        for phrase in exact_phrases:
            if phrase in title:
                logger.debug(f"Matched phrase '{phrase}' in title: {title}")
                filtered_items.append(item)
                break
    
    logger.info(f"Filtered {len(filtered_items)} items from {len(merged_results['items'])} total")
    
    # Save filtered results
    filtered_data = {
        'query': boolean_query,
        'total_items': len(filtered_items),
        'items': filtered_items,
        'exact_phrases': exact_phrases  # Include phrases for debugging
    }
    
    batch.save_json(filtered_data, 'filtered')
    return filtered_data

def process_dois(filtered_results, batch):
    """
    Process and deduplicate DOIs
    
    Args:
        filtered_results: Filtered results data
        batch: BatchProcessor instance
        
    Returns:
        dict: Final results with unique DOIs
    """
    logger = logging.getLogger(__name__)
    
    # Track unique DOIs
    seen_dois = set()
    unique_items = []
    duplicate_count = 0
    
    for item in filtered_results['items']:
        doi = item['doi']
        if doi not in seen_dois:
            seen_dois.add(doi)
            unique_items.append(item)
        else:
            duplicate_count += 1
    
    # Save final results
    final_data = {
        'total_items': len(unique_items),
        'duplicate_count': duplicate_count,
        'items': unique_items
    }
    
    batch.save_json(final_data, 'final')
    return final_data

def get_total_crossref_publications(date):
    """
    Get total number of Crossref publications for the specific month
    
    Args:
        date: Date in YY-MM format
        
    Returns:
        int: Total number of publications
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Convert date to required format (YYYY-MM)
        year = int(f"20{date.split('-')[0]}")
        month = int(date.split('-')[1])
        target_date = f"{year}-{month:02d}"
        
        # Query Crossref API for the specific month
        base_url = "https://api.crossref.org/works"
        params = {
            'filter': f'from-pub-date:{target_date},until-pub-date:{target_date}',
            'rows': 0
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        total = data['message']['total-results']
        logger.info(f"Total Crossref publications for {target_date}: {total:,}")
        return total
        
    except Exception as e:
        logger.error(f"Error getting total Crossref publications: {str(e)}")
        return 0

def generate_batch_statistics(batch, results):
    """
    Generate statistics for batch processing
    
    Args:
        batch: BatchProcessor instance
        results: Dictionary containing processing results
        
    Returns:
        dict: Statistics about the batch processing
    """
    # Get total Crossref publications for comparison
    total_crossref = get_total_crossref_publications(batch.date)
    final_count = len(results.get('items', []))
    
    # Calculate percentages
    crossref_percentage = (final_count / total_crossref * 100) if total_crossref > 0 else 0
    
    # Calculate processing time
    processing_time = time.time() - batch.start_time
    
    statistics = {
        'tool_name': batch.original_tool_name,  # Use original (non-mapped) tool name
        'batch_id': batch.batch_id,
        'date': batch.date,
        'initial_count': results.get('initial_count', 0),
        'filtered_count': results.get('filtered_count', 0),
        'final_count': final_count,
        'duplicate_count': results.get('duplicate_count', 0),
        'terms': results.get('term_counts', {}),
        'file_paths': batch.get_all_paths(),
        'processing_time': processing_time,
        'total_crossref': total_crossref,
        'crossref_percentage': crossref_percentage
    }
    
    return statistics

def print_batch_summary(statistics):
    """
    Print a formatted summary of batch processing results
    
    Args:
        statistics: Dictionary containing batch statistics
    """
    logger = logging.getLogger(__name__)
    
    # Get tool name and record counts
    tool_name = statistics.get('tool_name', 'Unknown Tool')
    final_count = statistics.get('final_count', 0)
    
    # Print header with key information
    print("\n" + "="*80)
    print(f"SUMMARY FOR: {tool_name}")
    print(f"FINAL RECORDS: {final_count}")
    print("="*80 + "\n")
    
    # Print detailed statistics
    print("Processing Details:")
    print("-"*40)
    
    # Batch information
    print(f"Batch ID: {statistics.get('batch_id', 'N/A')}")
    print(f"Date: {statistics.get('date', 'N/A')}")
    
    # Record statistics
    print("\nRecord Statistics:")
    print(f"- Total Raw Records: {statistics.get('initial_count', 0):,}")
    print(f"- Records Before Deduplication: {statistics.get('filtered_count', 0):,}")
    print(f"- Records After Deduplication: {final_count:,}")
    print(f"- Duplicated Records: {statistics.get('duplicate_count', 0):,}")
    
    # Calculate duplication rate
    if statistics.get('filtered_count', 0) > 0:
        duplication_rate = (statistics.get('duplicate_count', 0) / statistics.get('filtered_count', 0)) * 100
        print(f"- Duplication Rate: {duplication_rate:.2f}%")
    
    # Crossref statistics
    total_crossref = statistics.get('total_crossref', 0)
    crossref_percentage = statistics.get('crossref_percentage', 0)
    print(f"- Total Crossref Publications: {total_crossref:,}")
    print(f"- Percentage of Total Crossref: {crossref_percentage:.4f}%")
    
    # Term statistics
    if 'terms' in statistics:
        print("\nTerm Results:")
        for term, count in statistics['terms'].items():
            print(f"- {term}: {count:,} records")
    
    # File paths
    if 'file_paths' in statistics:
        print("\nOutput Files:")
        for file_type, path in statistics['file_paths'].items():
            print(f"- {file_type}: {path}")
    
    # Processing time with better formatting
    if 'processing_time' in statistics:
        processing_time = statistics['processing_time']
        minutes = int(processing_time // 60)
        seconds = processing_time % 60
        if minutes > 0:
            print(f"\nProcessing Time: {minutes} minutes {seconds:.2f} seconds")
        else:
            print(f"\nProcessing Time: {seconds:.2f} seconds")
    
    print("\n" + "="*80)

def process_tool_data(tool_name, date):
    """
    Main processing flow for tool data extraction
    
    Args:
        tool_name: Name of the management tool
        date: Date in YY-MM format
        
    Returns:
        dict: Batch statistics
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting data extraction for {tool_name} ({date})")
    
    try:
        # Initialize batch processor
        batch = BatchProcessor(tool_name, date)
        
        # 1. Get search terms
        terms = get_single_terms(tool_name)
        if not terms:
            raise ValueError(f"No search terms found for {tool_name}")
        
        # 2. Process individual terms
        term_files = process_individual_terms(terms, date, batch)
        if not term_files:
            raise ValueError(f"No results found for any terms")
        
        # 3. Merge results
        merged_results = merge_term_results(term_files, batch)
        
        # 4. Get and apply boolean query - use mapped name for query lookup
        boolean_query = get_boolean_query(batch.tool_name)  # Use mapped name (e.g., 'Balanced Scorecard')
        if boolean_query:
            logger.info(f"Using boolean query from mapped tool '{batch.tool_name}': {boolean_query}")
        filtered_results = apply_boolean_filter(merged_results, boolean_query, batch)
        
        # 5. Process DOIs
        final_results = process_dois(filtered_results, batch)
        
        # 6. Generate statistics
        results = {
            'initial_count': merged_results.get('total_items', 0),
            'filtered_count': filtered_results.get('total_items', 0),
            'items': final_results.get('items', []),
            'term_counts': {stat['term']: stat['total_results'] 
                          for stat in merged_results.get('term_statistics', [])},
            'processing_time': time.time() - batch.start_time if hasattr(batch, 'start_time') else 0
        }
        
        statistics = generate_batch_statistics(batch, results)
        
        # Save statistics
        batch.save_json(statistics, 'statistics')
        
        # Print summary
        print_batch_summary(statistics)
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error processing {tool_name}: {str(e)}")
        raise

def process_tool_year_data(tool_name, year):
    """
    Process data for an entire year, month by month
    
    Args:
        tool_name: Name of the tool to process
        year: Year to process (YYYY format)
        
    Returns:
        Dictionary containing annual statistics
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting annual data extraction for {tool_name} ({year})")
    
    statistics = {
        'tool_name': tool_name,
        'year': year,
        'monthly_stats': {},
        'total_duplicates': 0,
        'monthly_files': {}
    }
    
    try:
        # Process each month
        for month in range(1, 13):
            date = f"{str(year)[-2:]}-{month:02d}"
            print(f"\nProcessing {date}...")
            
            try:
                monthly_stats = process_tool_data(tool_name, date)
                statistics['monthly_stats'][date] = monthly_stats
                statistics['total_duplicates'] += monthly_stats.get('duplicate_count', 0)
                statistics['monthly_files'][date] = monthly_stats.get('file_paths', {})
                
                # Calculate Crossref percentage for the month
                if monthly_stats.get('total_crossref', 0) > 0:
                    crossref_percentage = (monthly_stats.get('final_count', 0) / monthly_stats.get('total_crossref', 0) * 100)
                    monthly_stats['crossref_percentage'] = crossref_percentage
                    
            except Exception as e:
                logger.error(f"Error processing {date}: {str(e)}")
                statistics['monthly_stats'][date] = {'error': str(e)}
                
            # Add a small delay between months to avoid API rate limits
            time.sleep(CROSSREF_API_DELAY)
        
        # Generate and print annual summary
        print_annual_summary(statistics)
        
        # Save annual statistics
        save_annual_statistics(statistics, tool_name, year)
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error processing annual data: {str(e)}")
        raise

def print_annual_summary(statistics):
    """
    Print a formatted summary of annual processing results
    
    Args:
        statistics: Dictionary containing annual statistics
    """
    print("\n" + "="*80)
    print(f"ANNUAL SUMMARY FOR: {statistics['tool_name']}")
    print(f"YEAR: {statistics['year']}")
    print("="*80 + "\n")
    
    print("Monthly Statistics:")
    print("-"*40)
    
    total_records = 0
    total_crossref = 0
    successful_months = 0
    
    for date, stats in sorted(statistics['monthly_stats'].items()):
        if 'error' in stats:
            print(f"\n{date}: ERROR - {stats['error']}")
            continue
            
        records = stats.get('final_count', 0)
        total_records += records
        total_crossref += stats.get('total_crossref', 0)
        successful_months += 1
        
        print(f"\n{date}:")
        print(f"- Records: {records:,}")
        print(f"- Duplicates: {stats.get('duplicate_count', 0):,}")
        if stats.get('crossref_percentage'):
            print(f"- % of Crossref: {stats['crossref_percentage']:.4f}%")
    
    print("\n" + "="*40)
    print("Annual Totals:")
    print(f"- Total Records: {total_records:,}")
    print(f"- Total Duplicates: {statistics['total_duplicates']:,}")
    if total_crossref > 0:
        yearly_crossref_percentage = (total_records / total_crossref * 100)
        print(f"- % of Crossref: {yearly_crossref_percentage:.4f}%")
    if successful_months == 12:
        print("- All months were successfully processed")
    else:
        print(f"- Processed {successful_months} out of 12 months")
    print("="*80 + "\n")

def save_annual_statistics(statistics, tool_name, year):
    """
    Save annual statistics to JSON file
    
    Args:
        statistics: Annual statistics dictionary
        tool_name: Name of the tool
        year: Year in YYYY format
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create safe filename
        safe_tool_name = tool_name.replace(' ', '_').replace('/', '_')
        filename = f"{safe_tool_name}_{year}_annual_statistics.json"
        
        # Get project root and create output directory
        project_root = get_project_root()
        output_dir = os.path.join(project_root, 'output', 'annual_statistics')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save statistics
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Annual statistics saved to {output_path}")
        print(f"\nAnnual statistics saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving annual statistics: {str(e)}")
        print(f"Error saving annual statistics: {str(e)}")

def process_tool_year_range(tool_name, start_year, end_year):
    """
    Process tool data for a range of years
    
    Args:
        tool_name: Name of the management tool
        start_year: Start year in YYYY format
        end_year: End year in YYYY format
        
    Returns:
        dict: Multi-year statistics
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting multi-year data extraction for {tool_name} ({start_year}-{end_year})")
    
    multi_year_statistics = {
        'tool_name': tool_name,
        'start_year': start_year,
        'end_year': end_year,
        'yearly_stats': {},
        'total_records': 0,
        'total_duplicates': 0,
        'yearly_files': {}
    }
    
    try:
        # Process each year in range
        for year in range(int(start_year), int(end_year) + 1):
            print(f"\nProcessing year {year}...")
            
            try:
                # Process year data
                yearly_stats = process_tool_year_data(tool_name, str(year))
                
                # Calculate year totals from monthly stats
                year_total_records = 0
                year_total_duplicates = 0
                year_successful_months = 0
                year_total_crossref = 0
                
                for month_stats in yearly_stats['monthly_stats'].values():
                    if 'error' not in month_stats:
                        year_total_records += month_stats.get('final_count', 0)
                        year_total_duplicates += month_stats.get('duplicate_count', 0)
                        year_total_crossref += month_stats.get('total_crossref', 0)
                        year_successful_months += 1
                
                # Update yearly statistics
                yearly_stats['total_records'] = year_total_records
                yearly_stats['total_duplicates'] = year_total_duplicates
                yearly_stats['successful_months'] = year_successful_months
                yearly_stats['total_crossref'] = year_total_crossref
                
                # Add to multi-year statistics
                multi_year_statistics['yearly_stats'][str(year)] = yearly_stats
                multi_year_statistics['total_records'] += year_total_records
                multi_year_statistics['total_duplicates'] += year_total_duplicates
                multi_year_statistics['yearly_files'][str(year)] = yearly_stats.get('monthly_files', {})
                
            except Exception as e:
                logger.error(f"Error processing year {year}: {str(e)}")
                print(f"Error processing year {year}: {str(e)}")
                multi_year_statistics['yearly_stats'][str(year)] = {'error': str(e)}
            
            # Add a small delay between years to avoid API rate limits
            time.sleep(CROSSREF_API_DELAY * 2)  # Double delay between years
        
        # Generate and print multi-year summary
        print_multi_year_summary(multi_year_statistics)
        
        # Save multi-year statistics
        save_multi_year_statistics(multi_year_statistics, tool_name)
        
        return multi_year_statistics
        
    except Exception as e:
        logger.error(f"Error processing multi-year data: {str(e)}")
        raise

def print_multi_year_summary(statistics):
    """
    Print a formatted summary of multi-year processing results
    
    Args:
        statistics: Dictionary containing multi-year statistics
    """
    print("\n" + "="*80)
    print(f"MULTI-YEAR SUMMARY FOR: {statistics['tool_name']}")
    print(f"YEARS: {statistics['start_year']} - {statistics['end_year']}")
    print("="*80 + "\n")
    
    print("Yearly Statistics:")
    print("-"*40)
    
    total_records = 0
    total_duplicates = 0
    total_crossref = 0
    successful_years = 0
    
    for year, stats in sorted(statistics['yearly_stats'].items()):
        if 'error' in stats:
            print(f"\n{year}: ERROR - {stats['error']}")
            continue
            
        records = stats.get('total_records', 0)
        duplicates = stats.get('total_duplicates', 0)
        successful_months = stats.get('successful_months', 0)
        year_total_crossref = stats.get('total_crossref', 0)
        
        total_records += records
        total_duplicates += duplicates
        total_crossref += year_total_crossref
        if successful_months > 0:
            successful_years += 1
        
        print(f"\n{year}:")
        print(f"- Records: {records:,}")
        print(f"- Duplicates: {duplicates:,}")
        if year_total_crossref > 0:
            yearly_crossref_percentage = (records / year_total_crossref * 100)
            print(f"- % of Crossref: {yearly_crossref_percentage:.4f}%")
        if successful_months == 12:
            print("- All months were successfully processed")
        else:
            print(f"- Processed {successful_months} out of 12 months")
    
    print("\n" + "="*40)
    print("Multi-Year Totals:")
    print(f"- Total Records: {total_records:,}")
    print(f"- Total Duplicates: {total_duplicates:,}")
    if total_crossref > 0:
        total_crossref_percentage = (total_records / total_crossref * 100)
        print(f"- % of Crossref: {total_crossref_percentage:.4f}%")
    print(f"- Successfully Processed Years: {successful_years}/{len(statistics['yearly_stats'])}")
    print("="*80 + "\n")

def save_multi_year_statistics(statistics, tool_name):
    """
    Save multi-year statistics to JSON file
    
    Args:
        statistics: Multi-year statistics dictionary
        tool_name: Name of the tool
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create safe filename
        safe_tool_name = tool_name.replace(' ', '_').replace('/', '_')
        filename = f"{safe_tool_name}_{statistics['start_year']}-{statistics['end_year']}_multi_year_statistics.json"
        
        # Get project root and create output directory
        project_root = get_project_root()
        output_dir = os.path.join(project_root, 'output', 'multi_year_statistics')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save statistics
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Multi-year statistics saved to {output_path}")
        print(f"\nMulti-year statistics saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving multi-year statistics: {str(e)}")
        print(f"Error saving multi-year statistics: {str(e)}")

def main():
    """Main entry point"""
    # Set up logging
    logger = setup_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract Crossref API data for management tools')
    parser.add_argument('--tool', help='Specific tool name to extract data for')
    parser.add_argument('--date', help='Specific date in YY-MM format')
    parser.add_argument('--year', help='Specific year in YYYY format')
    parser.add_argument('--year-range', help='Year range in YYYY-YYYY format (e.g., 2010-2015)')
    parser.add_argument('--version', action='version', version=f'{APP_NAME} {APP_VERSION}')
    args = parser.parse_args()
    
    try:
        # Print welcome message
        print(f"\nWelcome to {APP_NAME} v{APP_VERSION}")
        print("Management Tool Data Extraction Application\n")
        
        if args.tool:
            # Command line mode
            if sum(bool(x) for x in [args.date, args.year, args.year_range]) != 1:
                raise ValueError("Please specify exactly one of: --date, --year, or --year-range")
                
            if args.date:
                # Monthly processing
                logger.info(f"Running in command line mode with tool='{args.tool}' date='{args.date}'")
                
                # Validate date format
                if not validate_date_format(args.date):
                    raise ValueError("Invalid date format. Please use YY-MM format (e.g., 24-01)")
                
                # Process tool data for specific month
                statistics = process_tool_data(args.tool, args.date)
                
            elif args.year:
                # Yearly processing
                logger.info(f"Running in command line mode with tool='{args.tool}' year='{args.year}'")
                
                # Validate year format
                if not validate_year_format(args.year):
                    raise ValueError("Invalid year format. Please use YYYY format (e.g., 2021)")
                
                # Process tool data for entire year
                statistics = process_tool_year_data(args.tool, args.year)
                
            elif args.year_range:
                # Year range processing
                logger.info(f"Running in command line mode with tool='{args.tool}' year_range='{args.year_range}'")
                
                try:
                    start_year, end_year = args.year_range.split('-')
                    if not validate_year_range(start_year, end_year):
                        raise ValueError("Invalid year range format. Please use YYYY-YYYY format (e.g., 2010-2015)")
                    
                    # Process tool data for year range
                    statistics = process_tool_year_range(args.tool, start_year, end_year)
                except ValueError as e:
                    raise ValueError(f"Invalid year range: {str(e)}")
            
            else:
                raise ValueError("Please specify either --date, --year, or --year-range")
        
        else:
            # Interactive mode
            logger.info("Running in interactive mode")
            
            # Get available tools
            tools = get_available_tools()
            if not tools:
                raise ValueError("No tools available")
            
            # Display tool menu
            print("\nAvailable tools:")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool}")
            
            # Get tool selection
            while True:
                try:
                    selection = input("\nSelect a tool (number): ")
                    tool_index = int(selection) - 1
                    if 0 <= tool_index < len(tools):
                        selected_tool = tools[tool_index]
                        break
                    print(f"Invalid selection. Please enter a number between 1 and {len(tools)}")
                except ValueError:
                    print("Invalid input. Please enter a number")
            
            # Ask user if they want to process a specific month, entire year, or year range
            while True:
                mode = input("\nDo you want to process a specific month (M), entire year (Y), or year range (R)? ").strip().upper()
                if mode in ['M', 'Y', 'R']:
                    break
                print("Invalid input. Please enter 'M' for month, 'Y' for year, or 'R' for range")
            
            if mode == 'M':
                # Get specific month
                while True:
                    date = input("\nEnter date (YY-MM format, e.g., 24-01): ")
                    if validate_date_format(date):
                        break
                    print("Invalid date format. Please use YY-MM format")
                
                # Process tool data for specific month
                statistics = process_tool_data(selected_tool, date)
            
            elif mode == 'Y':
                # Get year
                year = get_year_input()
                if not year:
                    return 1
                
                # Process tool data for entire year
                statistics = process_tool_year_data(selected_tool, year)
            
            else:  # mode == 'R'
                # Get year range
                start_year, end_year = get_year_range_input()
                if not start_year or not end_year:
                    return 1
                
                # Process tool data for year range
                statistics = process_tool_year_range(selected_tool, start_year, end_year)
        
        logger.info("Processing completed successfully")
        return 0
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\nError: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 