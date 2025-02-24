import requests
import csv
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import time
import json
from urllib.parse import quote_plus, urlencode
import hashlib
import unicodedata
import random
import signal
import sys

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle interrupt signal"""
    global shutdown_requested
    print("\nShutdown requested. Will stop after current tool completes...")
    shutdown_requested = True

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def get_project_root():
    """Get the project root directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def setup_logging():
    """Setup enhanced logging configuration"""
    project_root = get_project_root()
    log_file = os.path.join(project_root, 'logs', 'crossref_search.log')
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_state(processed_tools):
    """Save progress state to file"""
    project_root = get_project_root()
    state_file = os.path.join(project_root, 'NewDBase', '.crossref_state.json')
    with open(state_file, 'w') as f:
        json.dump(processed_tools, f)

def load_state():
    """Load progress state from file"""
    project_root = get_project_root()
    state_file = os.path.join(project_root, 'NewDBase', '.crossref_state.json')
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return []

def normalize_filename(name):
    """Normalize filename to ASCII characters, replace spaces with underscore"""
    normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
    normalized = '_'.join(normalized.split())
    return ''.join(c for c in normalized if c.isalnum() or c in '_-')

def read_input_csv(filepath):
    """Read the input CSV file and extract tool names and queries"""
    df = pd.read_csv(filepath)
    return list(zip(df['Herramienta Gerencial'], df['Keywords']))

def get_crossref_data(query):
    """Get data from Crossref API with enhanced error handling"""
    logger = logging.getLogger(__name__)
    results = []
    
    current_year = datetime.now().year
    rows = 1000
    cursor = '*'
    total_items = 0
    
    logger.info(f"Starting Crossref query: {query}")
    
    # Initialize batch counter and total batches
    batch_counter = 0
    total_batches = None

    while cursor:
        batch_counter += 1
        try:
            params = {
                'query': query,
                'rows': rows,
                'cursor': cursor,
                'filter': f'from-pub-date:1950,until-pub-date:{current_year}',
                'select': 'DOI,title,published'
            }
            
            full_url = f"https://api.crossref.org/works?{urlencode(params)}"
            logger.debug(f"Requesting URL: {full_url}")
            
            response = requests.get(full_url)
            response.raise_for_status()
            data = response.json()
            
            message = data.get('message', {})
            items = message.get('items', [])
            next_cursor = message.get('next-cursor')
            total_results = message.get('total-results', 0)
            
            if total_batches is None:
                total_batches = -(-total_results // rows)
                logger.info(f"Total expected results: {total_results}")
                logger.info(f"Total expected batches: {total_batches}")
            
            logger.info(f"Processing batch {batch_counter} of {total_batches}")
            
            selected_items = 0
            for item in items:
                if 'published' in item and 'date-parts' in item['published']:
                    date = item['published']['date-parts'][0]
                    if len(date) >= 2:
                        year, month = date[0], date[1]
                        results.append((datetime(year, month, 1), 1))
                        selected_items += 1
            
            total_items += len(items)
            logger.info(f"Batch {batch_counter}: {len(items)} items retrieved, {selected_items} selected")
            
            if batch_counter >= total_batches:
                logger.info("All expected batches processed")
                break
            
            cursor = next_cursor
            if not cursor:
                logger.info("No more results available")
                break
            
            time.sleep(1)  # Rate limiting
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Crossref: {str(e)}")
            logger.error(f"Request URL: {full_url}")
            if 'response' in locals():
                logger.error(f"Server response: {response.text}")
            return None

    logger.info(f"Total items queried: {total_items}")
    logger.info(f"Total results collected: {len(results)}")
    return results

def group_by_month(data):
    """Groups data by month from 1950 to present"""
    grouped = {}
    start_date = datetime(1950, 1, 1)
    current_date = datetime.now().replace(day=1)
    
    # Initialize all months with zero
    date = start_date
    while date <= current_date:
        key = date.strftime("%Y-%m")
        grouped[key] = 0
        date += timedelta(days=32)
        date = date.replace(day=1)
    
    # Add actual counts
    for date, count in data:
        if date <= current_date:
            key = date.strftime("%Y-%m")
            grouped[key] += count
    
    return grouped

def save_to_csv(data, tool_name):
    """Save data to CSV with normalized filename"""
    logger = logging.getLogger(__name__)
    
    # Create NewDBase directory if it doesn't exist
    project_root = get_project_root()
    dbase_dir = os.path.join(project_root, 'NewDBase')
    os.makedirs(dbase_dir, exist_ok=True)
    
    # Generate normalized filename
    normalized_name = normalize_filename(tool_name)
    random_suffix = format(random.randint(0, 9999), '04d')
    filename = f"CR_{normalized_name}_{random_suffix}.csv"
    filepath = os.path.join(dbase_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", tool_name])
        for date, count in sorted(data.items()):
            writer.writerow([date, count])
    
    logger.info(f"Data saved to {filepath}")
    return filename

def update_index(tool_name, filename):
    """Update or create the CRIndex.csv file"""
    logger = logging.getLogger(__name__)
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    
    # Create new index file if it doesn't exist
    if not os.path.exists(index_path):
        with open(index_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Keyword', 'Filename'])
    
    # Append new entry
    with open(index_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([tool_name, filename])
    
    logger.info(f"Index updated with {filename}")

def main():
    """Main function to process the input CSV and generate results"""
    logger = setup_logging()
    logger.info("Starting Crossref data collection process")
    
    try:
        # Read input CSV from project root
        project_root = get_project_root()
        input_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
        logger.info(f"Reading input file: {input_file}")
        
        tools_data = read_input_csv(input_file)
        logger.info(f"Found {len(tools_data)} tools to process")
        
        # Load previously processed tools
        processed_tools = load_state()
        logger.info(f"Found {len(processed_tools)} previously processed tools")
        
        for tool_name, query in tools_data:
            # Skip if already processed
            if tool_name in processed_tools:
                logger.info(f"Skipping already processed tool: {tool_name}")
                continue
                
            logger.info(f"Processing tool: {tool_name}")
            
            # Check for shutdown request
            if shutdown_requested:
                logger.info("Shutdown requested. Saving state and exiting...")
                save_state(processed_tools)
                sys.exit(0)
            
            # Get data from Crossref
            results = get_crossref_data(query)
            if results is None:
                logger.error(f"Failed to get data for {tool_name}")
                continue
            
            # Process and save results
            grouped_data = group_by_month(results)
            filename = save_to_csv(grouped_data, tool_name)
            update_index(tool_name, filename)
            
            # Update processed tools list and save state
            processed_tools.append(tool_name)
            save_state(processed_tools)
            
            logger.info(f"Completed processing {tool_name}")
            time.sleep(2)  # Delay between tools to avoid rate limiting
        
        # Remove state file when all tools are processed
        state_file = os.path.join(project_root, 'NewDBase', '.crossref_state.json')
        if os.path.exists(state_file):
            os.remove(state_file)
        logger.info("All tools processed successfully")
    
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}", exc_info=True)
        save_state(processed_tools)  # Save state on error
        raise

if __name__ == "__main__":
    main()
