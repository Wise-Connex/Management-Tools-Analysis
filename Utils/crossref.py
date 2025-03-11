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
    os.makedirs(os.path.dirname(state_file), exist_ok=True)  # Ensure directory exists
    with open(state_file, 'w') as f:
        json.dump(processed_tools, f)
    logging.getLogger(__name__).info(f"Saved state with {len(processed_tools)} processed tools")

def load_state():
    """Load progress state from file"""
    project_root = get_project_root()
    state_file = os.path.join(project_root, 'NewDBase', '.crossref_state.json')
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return []

def get_indexed_tools(include_completion_status=False):
    """Get list of tools already indexed in CRIndex.csv
    
    Args:
        include_completion_status: If True, returns a dictionary with tool names as keys
                                  and completion status as values
    """
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    indexed_tools = [] if not include_completion_status else {}
    
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Get header
                
                # Check if we have the completion status column
                has_completion_column = len(header) >= 3 and header[2] == 'Complete'
                
                for row in reader:
                    if row and len(row) >= 1:
                        if include_completion_status:
                            # If the file has a completion column, use it; otherwise assume incomplete
                            is_complete = (row[2].lower() == 'true') if has_completion_column and len(row) >= 3 else False
                            indexed_tools[row[0]] = is_complete
                        else:
                            indexed_tools.append(row[0])
        except Exception as e:
            logging.getLogger(__name__).error(f"Error reading CRIndex.csv: {str(e)}")
    
    return indexed_tools

def get_incomplete_tools():
    """Get list of tools that have incomplete data"""
    indexed_tools = get_indexed_tools(include_completion_status=True)
    return [tool for tool, is_complete in indexed_tools.items() if not is_complete]

def normalize_filename(name):
    """Normalize filename to ASCII characters, replace spaces with underscore"""
    normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
    normalized = '_'.join(normalized.split())
    return ''.join(c for c in normalized if c.isalnum() or c in '_-')

def read_input_csv(filepath):
    """Read the input CSV file and extract tool names and queries"""
    try:
        df = pd.read_csv(filepath)
        # Check if the expected columns exist
        if 'Herramienta Gerencial' in df.columns and 'Keywords' in df.columns:
            return list(zip(df['Herramienta Gerencial'], df['Keywords']))
        else:
            # Try alternative column names
            tool_col = next((col for col in df.columns if 'herramienta' in col.lower() or 'tool' in col.lower()), None)
            keyword_col = next((col for col in df.columns if 'keyword' in col.lower()), None)
            
            if tool_col and keyword_col:
                return list(zip(df[tool_col], df[keyword_col]))
            else:
                logging.getLogger(__name__).error(f"Could not find required columns in CSV. Available columns: {df.columns.tolist()}")
                return []
    except Exception as e:
        logging.getLogger(__name__).error(f"Error reading input CSV: {str(e)}")
        return []

def get_crossref_data(query, max_runtime=7200):
    """Get data from Crossref API with enhanced error handling and resume capability"""
    logger = logging.getLogger(__name__)
    
    # Check for extended mode
    if os.environ.get('CROSSREF_EXTENDED_MODE') == 'TRUE':
        # Extend runtime to 10 hours for problematic queries
        max_runtime = 36000  # 10 hours
        logger.info(f"Running in EXTENDED mode with {max_runtime/3600} hour timeout")
    
    results = []
    
    current_year = datetime.now().year
    # Modify batch size for extended mode to reduce load
    rows = 500 if os.environ.get('CROSSREF_EXTENDED_MODE') == 'TRUE' else 1000
    cursor = '*'
    total_items = 0
    completed_successfully = False
    batch_counter = 0  # Initialize batch_counter here
    empty_batch_counter = 0  # Track consecutive empty batches
    max_empty_batches = 5  # Maximum number of consecutive empty batches before stopping
    cursor_expired = False  # Flag to track if cursor has expired
    
    # Set maximum runtime for a single query (in seconds)
    start_time = time.time()
    
    # Load saved state if exists
    state_file = os.path.join(get_project_root(), 'NewDBase', '.crossref_batch_state.json')
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                saved_state = json.load(f)
                if saved_state['query'] == query:
                    cursor = saved_state['cursor']
                    # Convert saved date strings back to datetime objects
                    results = [(datetime.strptime(date, "%Y-%m-%d"), count) 
                             for date, count in saved_state['results']]
                    total_items = saved_state['total_items']
                    batch_counter = saved_state['batch_counter']
                    logger.info(f"Resuming from batch {batch_counter} with {len(results)} results")
                else:
                    os.remove(state_file)  # Remove state file if query doesn't match
        except Exception as e:
            logger.error(f"Error loading state: {str(e)}")
            if os.path.exists(state_file):
                os.remove(state_file)
    
    logger.info(f"Starting/Resuming Crossref query: {query}")
    logger.info(f"Maximum runtime set to {max_runtime} seconds")
    
    # Initialize total batches
    total_batches = None
    
    max_retries = 3  # Maximum number of retries per batch
    base_delay = 5   # Base delay in seconds for exponential backoff

    try:
        while cursor:
            # Don't increment batch counter if we're restarting due to expired cursor
            if not cursor_expired:
                batch_counter += 1
            cursor_expired = False  # Reset the flag
            
            retry_count = 0
            
            while retry_count < max_retries:
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
                    
                    # Use requests with timeout
                    response = requests.get(full_url, timeout=45)  # Increased timeout from 30 to 45 seconds
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
                    
                    # Update total_batches if we've already exceeded it but still getting results
                    if batch_counter > total_batches and len(items) > 0:
                        logger.warning(f"Received more batches than expected ({batch_counter} > {total_batches}). Adjusting expectations.")
                        total_batches = batch_counter + 10  # Add some buffer
                    
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
                    
                    # Track consecutive empty batches
                    if len(items) == 0:
                        empty_batch_counter += 1
                        if empty_batch_counter >= max_empty_batches:
                            logger.info(f"Received {max_empty_batches} consecutive empty batches. Assuming end of data reached.")
                            completed_successfully = True
                            if os.path.exists(state_file):
                                os.remove(state_file)  # Clean up state file
                            break
                    else:
                        empty_batch_counter = 0  # Reset counter when non-empty batch is received
                    
                    # Check if we've exceeded the maximum runtime
                    elapsed_time = time.time() - start_time
                    if elapsed_time > max_runtime:
                        logger.warning(f"Maximum runtime of {max_runtime} seconds exceeded. Saving progress and stopping.")
                        # Don't mark as completed_successfully to allow resuming later
                        break
                    
                    # Check if shutdown was requested
                    if shutdown_requested:
                        logger.info("Shutdown requested. Saving progress and stopping.")
                        break
                    
                    # Save state after each successful batch
                    # Convert datetime objects to strings for JSON serialization
                    serializable_results = [(dt.strftime("%Y-%m-%d"), count) 
                                         for dt, count in results]
                    state = {
                        'query': query,
                        'cursor': next_cursor,
                        'results': serializable_results,
                        'total_items': total_items,
                        'batch_counter': batch_counter
                    }
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(state_file), exist_ok=True)
                    
                    with open(state_file, 'w') as f:
                        json.dump(state, f)
                    
                    if batch_counter >= total_batches:
                        logger.info("All expected batches processed")
                        completed_successfully = True
                        if os.path.exists(state_file):
                            os.remove(state_file)  # Clean up state file after completion
                        break  # Break retry loop
                    
                    cursor = next_cursor
                    if not cursor:
                        logger.info("No more results available")
                        completed_successfully = True
                        if os.path.exists(state_file):
                            os.remove(state_file)  # Clean up state file after completion
                        break  # Break retry loop
                    
                    # Add additional delay between requests in extended mode
                    time_delay = 2 if os.environ.get('CROSSREF_EXTENDED_MODE') == 'TRUE' else 1
                    time.sleep(time_delay)  # Rate limiting
                    break  # Break retry loop on success
                
                except requests.HTTPError as e:
                    # Check if this is a 404 error (likely expired cursor)
                    if hasattr(e, 'response') and e.response.status_code == 404 and cursor != '*':
                        logger.warning(f"Cursor expired (404 error). Restarting with a fresh cursor.")
                        cursor = '*'
                        cursor_expired = True
                        # Don't count this as a retry - we're starting fresh
                        break
                    
                    # For other HTTP errors, follow the normal retry process
                    retry_count += 1
                    if retry_count < max_retries:
                        delay = base_delay * (2 ** retry_count)
                        logger.warning(f"HTTP error: {str(e)}. Retrying in {delay} seconds... (Attempt {retry_count + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries reached for HTTP error: {str(e)}")
                        # Save state before raising exception
                        serializable_results = [(dt.strftime("%Y-%m-%d"), count) 
                                             for dt, count in results]
                        state = {
                            'query': query,
                            'cursor': cursor,  # Keep the same cursor to retry this batch
                            'results': serializable_results,
                            'total_items': total_items,
                            'batch_counter': batch_counter - 1  # Revert batch counter so we retry this batch
                        }
                        
                        os.makedirs(os.path.dirname(state_file), exist_ok=True)
                        with open(state_file, 'w') as f:
                            json.dump(state, f)
                        logger.info(f"Saved state before HTTP error. Will resume from batch {batch_counter-1} on next run.")
                        raise  # Re-raise to be caught by outer try-except
                    
                except requests.Timeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        delay = base_delay * (2 ** retry_count)  # Exponential backoff
                        logger.warning(f"Timeout occurred. Retrying in {delay} seconds... (Attempt {retry_count + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        logger.error("Max retries reached for timeout")
                        # Save state before raising exception
                        serializable_results = [(dt.strftime("%Y-%m-%d"), count) 
                                             for dt, count in results]
                        state = {
                            'query': query,
                            'cursor': cursor,  # Keep the same cursor to retry this batch
                            'results': serializable_results,
                            'total_items': total_items,
                            'batch_counter': batch_counter - 1  # Revert batch counter so we retry this batch
                        }
                        
                        os.makedirs(os.path.dirname(state_file), exist_ok=True)
                        with open(state_file, 'w') as f:
                            json.dump(state, f)
                        logger.info(f"Saved state before timeout error. Will resume from batch {batch_counter-1} on next run.")
                        raise  # Re-raise to be caught by outer try-except
                        
                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        delay = base_delay * (2 ** retry_count)
                        logger.warning(f"Request error: {str(e)}. Retrying in {delay} seconds... (Attempt {retry_count + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries reached for request error: {str(e)}")
                        # Save state before raising exception
                        serializable_results = [(dt.strftime("%Y-%m-%d"), count) 
                                             for dt, count in results]
                        state = {
                            'query': query,
                            'cursor': cursor,  # Keep the same cursor to retry this batch
                            'results': serializable_results,
                            'total_items': total_items,
                            'batch_counter': batch_counter - 1  # Revert batch counter so we retry this batch
                        }
                        
                        os.makedirs(os.path.dirname(state_file), exist_ok=True)
                        with open(state_file, 'w') as f:
                            json.dump(state, f)
                        logger.info(f"Saved state before request error. Will resume from batch {batch_counter-1} on next run.")
                        raise  # Re-raise to be caught by outer try-except

            # Handle case where we're restarting with a fresh cursor
            if cursor_expired:
                continue  # Skip the rest of the while loop and try again with the new cursor

            # Add this check to break out of the outer while loop
            if batch_counter >= total_batches or not cursor or completed_successfully or (time.time() - start_time) > max_runtime or shutdown_requested:
                break

        logger.info(f"Total items queried: {total_items}")
        logger.info(f"Total results collected: {len(results)}")
        
        # Return the results along with completion status
        return {
            'results': results,
            'completed': completed_successfully,
            'total_batches': total_batches,
            'processed_batches': batch_counter
        }

    except Exception as e:
        logger.error(f"Error during data collection: {str(e)}")
        # Save state before returning
        if results:  # Only save if we have results
            serializable_results = [(dt.strftime("%Y-%m-%d"), count) 
                                 for dt, count in results]
            state = {
                'query': query,
                'cursor': cursor,
                'results': serializable_results,
                'total_items': total_items,
                'batch_counter': batch_counter - 1  # Revert batch counter to retry the failed batch
            }
            
            os.makedirs(os.path.dirname(state_file), exist_ok=True)
            with open(state_file, 'w') as f:
                json.dump(state, f)
            logger.info(f"Saved state after error. You can resume from batch {batch_counter-1}.")
        return None

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

def save_to_csv(data, tool_name, is_complete=False):
    """Save data to CSV with normalized filename
    
    Args:
        data: Dictionary of date -> count mappings
        tool_name: Name of the tool
        is_complete: Whether the data collection was completed successfully
    
    Returns:
        filename: Name of the saved file
    """
    logger = logging.getLogger(__name__)
    
    # Create NewDBase directory if it doesn't exist
    project_root = get_project_root()
    dbase_dir = os.path.join(project_root, 'NewDBase')
    os.makedirs(dbase_dir, exist_ok=True)
    
    # Generate normalized filename
    normalized_name = normalize_filename(tool_name)
    random_suffix = format(random.randint(0, 9999), '04d')
    
    # Add suffix for incomplete data
    filename = f"CR_{normalized_name}_{random_suffix}.csv"
    filepath = os.path.join(dbase_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", tool_name])
        for date, count in sorted(data.items()):
            writer.writerow([date, count])
    
    logger.info(f"Data saved to {filepath}")
    return filename

def update_index(tool_name, filename, is_complete=False):
    """Update or create index file with tool name, filename, and completion status
    
    Args:
        tool_name: Name of the tool
        filename: Name of the CSV file
        is_complete: Whether the data collection was completed successfully
    """
    logger = logging.getLogger(__name__)
    
    project_root = get_project_root()
    index_path = os.path.join(project_root, 'NewDBase', 'CRIndex.csv')
    
    # Read existing index if it exists
    existing_data = []
    header = ['Keyword', 'Filename', 'Complete']
    
    if os.path.exists(index_path):
        with open(index_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header_row = next(reader, None)
            
            # Check if we need to update the header
            if header_row:
                if len(header_row) < 3:
                    header_row = header  # Use new header with Complete column
                
                # Read existing data
                for row in reader:
                    if row:  # Skip empty rows
                        # Ensure row has 3 columns
                        while len(row) < 3:
                            row.append('')
                        existing_data.append(row)
    
    # Remove existing entry for this tool if it exists
    existing_data = [row for row in existing_data if row[0] != tool_name]
    
    # Add new entry
    existing_data.append([tool_name, filename, str(is_complete)])
    
    # Write updated index
    with open(index_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(existing_data)
    
    logger.info(f"Updated index with {tool_name} -> {filename} (Complete: {is_complete})")

def process_specific_tool(tool_name, force_reprocess=False):
    """Process a specific tool by name
    
    Args:
        tool_name: Name of the tool to process
        force_reprocess: If True, reprocess even if already indexed
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    logger = setup_logging()
    logger.info(f"Processing specific tool: {tool_name}")
    
    # Check for extended mode
    extended_mode = os.environ.get('CROSSREF_EXTENDED_MODE') == 'TRUE'
    if extended_mode:
        logger.info("Running in EXTENDED mode with optimized parameters")
    
    try:
        # Read input CSV from project root
        project_root = get_project_root()
        input_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
        logger.info(f"Reading input file: {input_file}")
        
        tools_data = read_input_csv(input_file)
        
        # Find the specific tool
        tool_data = None
        for name, query in tools_data:
            if name.lower() == tool_name.lower():
                tool_data = (name, query)
                break
        
        if not tool_data:
            logger.error(f"Tool '{tool_name}' not found in input CSV")
            return False
        
        # Check if tool is already indexed and complete
        if not force_reprocess:
            indexed_tools = get_indexed_tools(include_completion_status=True)
            if tool_name in indexed_tools and indexed_tools[tool_name]:
                logger.info(f"Tool '{tool_name}' is already indexed and complete. Use force_reprocess=True to reprocess.")
                return True
        
        # Process the tool
        name, query = tool_data
        logger.info(f"Found tool: {name} with query: {query}")
        
        # Get data from Crossref with runtime based on mode
        max_runtime = 36000 if extended_mode else 18000  # 10 hours in extended mode, 5 hours otherwise
        result = get_crossref_data(query, max_runtime=max_runtime)
        if result is None:
            logger.error(f"Failed to get data for {name}")
            return False
        
        results = result['results']
        is_complete = result['completed']
        
        # Check if results are empty
        if not results:
            logger.warning(f"No results found for {name}")
            return False
        
        # Process and save results
        grouped_data = group_by_month(results)
        filename = save_to_csv(grouped_data, name, is_complete)
        update_index(name, filename, is_complete)
        
        completion_status = "complete" if is_complete else "incomplete"
        logger.info(f"Successfully processed {name} ({completion_status})")
        
        # If data is incomplete, log a warning
        if not is_complete:
            logger.warning(f"Data collection for {name} is incomplete ({result['processed_batches']}/{result['total_batches']} batches). Run again later to complete.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing specific tool: {str(e)}", exc_info=True)
        return False

def main():
    """Main function to process the input CSV and generate results"""
    logger = setup_logging()
    logger.info("Starting Crossref data collection process")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--tool' and len(sys.argv) > 2:
            tool_name = sys.argv[2]
            force_reprocess = '--force' in sys.argv
            success = process_specific_tool(tool_name, force_reprocess)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--incomplete':
            # Process all incomplete tools
            incomplete_tools = get_incomplete_tools()
            logger.info(f"Found {len(incomplete_tools)} incomplete tools: {', '.join(incomplete_tools)}")
            
            for tool_name in incomplete_tools:
                logger.info(f"Reprocessing incomplete tool: {tool_name}")
                success = process_specific_tool(tool_name, force_reprocess=True)
                if not success:
                    logger.error(f"Failed to reprocess {tool_name}")
                time.sleep(5)  # Small delay between tools
            
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python crossref.py                   # Process all tools")
            print("  python crossref.py --tool 'Tool Name'  # Process specific tool")
            print("  python crossref.py --tool 'Tool Name' --force  # Force reprocessing of a tool")
            print("  python crossref.py --incomplete      # Reprocess all incomplete tools")
            sys.exit(0)
    
    try:
        # Read input CSV from project root
        project_root = get_project_root()
        input_file = os.path.join(project_root, 'rawData', 'Tabla Python Dimar - Notas Crossref.csv')
        logger.info(f"Reading input file: {input_file}")
        
        tools_data = read_input_csv(input_file)
        logger.info(f"Found {len(tools_data)} tools to process")
        
        # Load previously processed tools from state file
        processed_tools = load_state()
        logger.info(f"Found {len(processed_tools)} previously processed tools in state file")
        
        # Get tools already indexed in CRIndex.csv with completion status
        indexed_tools_status = get_indexed_tools(include_completion_status=True)
        indexed_tools = list(indexed_tools_status.keys())
        complete_tools = [tool for tool, is_complete in indexed_tools_status.items() if is_complete]
        
        logger.info(f"Found {len(indexed_tools)} tools already indexed in CRIndex.csv")
        logger.info(f"Of which {len(complete_tools)} are marked as complete")
        
        # Combine both lists to get all tools to skip (only skip complete tools)
        tools_to_skip = list(set(processed_tools + complete_tools))
        logger.info(f"Total {len(tools_to_skip)} tools will be skipped (already processed or complete)")
        
        for tool_name, query in tools_data:
            # Skip if already processed or complete
            if tool_name in tools_to_skip:
                logger.info(f"Skipping already processed or complete tool: {tool_name}")
                continue
                
            logger.info(f"Processing tool: {tool_name}")
            
            # Check for shutdown request
            if shutdown_requested:
                logger.info("Shutdown requested. Saving state and exiting...")
                save_state(processed_tools)
                sys.exit(0)
            
            # Get data from Crossref with runtime based on mode
            max_runtime = 36000 if extended_mode else 18000  # 10 hours in extended mode, 5 hours otherwise
            result = get_crossref_data(query, max_runtime=max_runtime)
            if result is None:
                logger.error(f"Failed to get data for {tool_name}, skipping CSV generation")
                continue
            
            results = result['results']
            is_complete = result['completed']
            
            # Check if results are empty
            if not results:
                logger.warning(f"No results found for {tool_name}")
                # Still mark as processed to avoid repeated attempts
                processed_tools.append(tool_name)
                save_state(processed_tools)
                continue
            
            # Process and save results
            grouped_data = group_by_month(results)
            filename = save_to_csv(grouped_data, tool_name, is_complete)
            update_index(tool_name, filename, is_complete)
            
            # Update processed tools list and save state
            processed_tools.append(tool_name)
            save_state(processed_tools)
            
            completion_status = "complete" if is_complete else "incomplete"
            logger.info(f"Completed processing {tool_name} ({completion_status})")
            
            # If data is incomplete, log a warning
            if not is_complete:
                logger.warning(f"Data collection for {tool_name} is incomplete ({result['processed_batches']}/{result['total_batches']} batches). Run again later to complete.")
            
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
