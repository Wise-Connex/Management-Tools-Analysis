import requests
import csv
from datetime import datetime, timedelta
import paramiko
from io import StringIO
from habanero import Crossref
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_crossref_data(keyword):
    """
    Retrieves publication data from Crossref based on the given keyword.
    
    Args:
    keyword (str): The search term to query Crossref.
    
    Returns:
    list of tuples: Each tuple contains (datetime, count), where datetime is the publication date
                    and count is always 1 (representing one publication).
    """
    cr = Crossref()
    results = []
    
    current_year = datetime.now().year
    batch_size = 1000
    cursor = '*'
    
    logger.debug(f"Starting Crossref query for keyword: {keyword}")
    
    while cursor:
        logger.debug(f"Querying Crossref with cursor: {cursor}")
        query_result = cr.works(query=keyword, select=['published', 'abstract'], 
                                limit=batch_size, cursor=cursor,
                                filter={'from-pub-date': '1950', 'until-pub-date': str(current_year)})
        
        logger.debug(f"Query result type: {type(query_result)}")
        
        # Check if query_result is a list or a dictionary
        if isinstance(query_result, list):
            items = query_result
            logger.debug(f"Query result is a list with {len(items)} items")
            # If it's a list, we need to extract the actual items
            if items and isinstance(items[0], dict) and 'message' in items[0]:
                items = items[0].get('message', {}).get('items', [])
                logger.debug(f"Extracted {len(items)} items from the list")
        else:
            items = query_result.get('message', {}).get('items', [])
            logger.debug(f"Query result is a dictionary with {len(items)} items")
        
        if not items:
            logger.debug("No items found in this batch, breaking the loop")
            break
        
        for item in items:
            logger.debug(f"Processing item: {item}")
            if isinstance(item, dict) and 'published' in item and 'date-parts' in item['published']:
                date = item['published']['date-parts'][0]
                if len(date) >= 2:
                    year, month = date[0], date[1]
                    results.append((datetime(year, month, 1), 1))
                    logger.debug(f"Added result for date: {year}-{month}")
            else:
                logger.debug(f"Skipped item due to missing or invalid date: {item.get('published', 'No published data')}")
        
        # Update cursor for next iteration
        if isinstance(query_result, dict):
            cursor = query_result.get('message', {}).get('next-cursor')
            logger.debug(f"Updated cursor to: {cursor}")
        else:
            cursor = None
            logger.debug("No cursor found, ending query")
        
        if not cursor:
            logger.debug("No more results, breaking the loop")
            break
    
    logger.debug(f"Total results collected: {len(results)}")
    return results

def group_by_month(data):
    """
    Groups the input data by month, including all months from 1950 to the current month.
    
    Args:
    data (list of tuples): Each tuple contains (datetime, count) as returned by get_crossref_data.
    
    Returns:
    dict: A dictionary with keys as 'YYYY-MM' strings and values as the count of publications for that month.
    """
    grouped = {}
    start_date = datetime(1950, 1, 1)
    current_date = datetime.now().replace(day=1)
    
    date = start_date
    while date <= current_date:
        key = date.strftime("%Y-%m")
        grouped[key] = 0
        date += timedelta(days=32)
        date = date.replace(day=1)
    
    for date, count in data:
        if date <= current_date:
            key = date.strftime("%Y-%m")
            grouped[key] += count
    
    return grouped

def save_to_csv(data, keyword):
    """
    Converts the grouped data into CSV format.
    
    Args:
    data (dict): The grouped data as returned by group_by_month.
    keyword (str): The search keyword used, which becomes a column header.
    
    Returns:
    str: CSV formatted string of the data.
    """
    csv_data = StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["Date", keyword])
    for date, count in sorted(data.items()):
        writer.writerow([date, count])
    return csv_data.getvalue()

def upload_to_ftp(csv_content, filename, hostname, username, private_key_path, port, remotepath):
    """
    Uploads the CSV content to an FTP server using SFTP.
    
    Args:
    csv_content (str): The CSV data to upload.
    filename (str): The name of the file to create on the server.
    hostname (str): The FTP server's hostname or IP address.
    username (str): The username for FTP authentication.
    private_key_path (str): Path to the private key file for authentication.
    port (int): The port number for the FTP connection.
    remotepath (str): The path on the remote server where the file should be uploaded.
    
    Returns:
    None
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, key_filename=private_key_path)

    ftp = ssh.open_sftp()
    full_path = remotepath + filename
    # Check if file exists and remove it
    try:
        ftp.stat(full_path)
        ftp.remove(full_path)
    except IOError:
        pass  # File doesn't exist, so we can proceed to create it
    
    with ftp.file(full_path, "w") as f:
        f.write(csv_content)
    ftp.close()
    ssh.close()
    
def main(keyword, hostname, username, private_key_path, port, remotepath):
    """
    Main function that orchestrates the entire process.
    
    Args:
    keyword (str): The search term for Crossref query.
    hostname (str): The FTP server's hostname or IP address.
    username (str): The username for FTP authentication.
    private_key_path (str): Path to the private key file for authentication.
    port (int): The port number for the FTP connection.
    remotepath (str): The path on the remote server where the file should be uploaded.
    
    Returns:
    None
    """
    print(f"Retrieving data for keyword: {keyword}")
    data = get_crossref_data(keyword)
    print(f"Data retrieved: {len(data)} items")
    if data:
        print("Sample of data:")
        for item in data[:5]:  # Print first 5 items
            print(item)
    grouped_data = group_by_month(data)
    csv_content = save_to_csv(grouped_data, keyword)
    
    filename = f"CR_{keyword.replace(' ', '_')}.csv"
    print(f"Uploading data to FTP server: {filename}")
    upload_to_ftp(csv_content, filename, hostname, username, private_key_path, port, remotepath)
    print("Upload complete")

if __name__ == "__main__":
    keyword = input("Por favor, ingrese la Herramienta Gerencial a buscar: ")
    hostname = "129.146.107.0"
    username = "ubuntu"
    private_key_path = "./WC-VSCODE-Private.key"
    remotepath = "/home/ubuntu/GTrendsData/"
    port = 22
    main(keyword, hostname, username, private_key_path, port, remotepath)