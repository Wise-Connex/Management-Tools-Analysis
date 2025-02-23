import pandas as pd
import os
import random
import unicodedata
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from urllib.parse import quote
import pickle
import os.path
from bs4 import BeautifulSoup
import logging

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to see more output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gt_scraper.log'),
        logging.StreamHandler()  # This will also print to console
    ]
)

def clean_filename(name):
    """Clean tool name to create valid filename"""
    # Remove accents and convert to ASCII
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Replace spaces with underscores and remove special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name

def generate_random_id():
    """Generate random 4-digit ID"""
    return str(random.randint(0, 9999)).zfill(4)

def parse_spanish_date(date_str):
    """Convert Spanish date format to YYYY-MM"""
    # Spanish month abbreviations mapping
    month_map = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }
    
    try:
        # Clean the input string - remove hidden characters and normalize spaces
        date_str = ''.join(char for char in date_str if char.isprintable())
        date_str = ' '.join(date_str.split())  # Normalize spaces
        
        # Split the date string
        parts = date_str.lower().split()
        if len(parts) != 2:  # If format is "1 ene. 2004"
            parts = date_str.lower().replace('.', '').split()
        
        # Extract month and year
        month_abbr = parts[1][:3]  # Take first 3 letters of month
        month = month_map.get(month_abbr, '01')  # Default to '01' if not found
        
        # Clean up the year - remove any non-digit characters
        year = ''.join(char for char in parts[2] if char.isdigit())
        
        if not year or not month:
            raise ValueError(f"Invalid date parts: month={month}, year={year}")
            
        return f"{year}-{month}"
        
    except Exception as e:
        logging.error(f"Error parsing date '{date_str}': {str(e)}")
        raise

def save_cookies(driver, cookie_file):
    """Save cookies to file"""
    if driver.get_cookies():
        with open(cookie_file, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
            print("Cookies saved successfully")

def load_cookies(driver, cookie_file):
    """Load cookies from file if they exist and are not expired"""
    if os.path.exists(cookie_file):
        with open(cookie_file, 'rb') as f:
            try:
                cookies = pickle.load(f)
                now = datetime.now()
                # Only load non-expired cookies
                for cookie in cookies:
                    if 'expiry' in cookie:
                        expiry = datetime.fromtimestamp(cookie['expiry'])
                        if expiry > now:
                            driver.add_cookie(cookie)
                print("Cookies loaded successfully")
                return True
            except Exception as e:
                print(f"Error loading cookies: {str(e)}")
    return False

def scrape_google_trends_data(url):
    """Scrape data from Google Trends using Selenium with rate limiting handling"""
    logging.info(f"Starting scrape for URL: {url}")
    
    options = webdriver.ChromeOptions()
    driver = None
    
    try:
        # Make it look more like a real browser
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-infobars')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # Required for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), 
                                options=options)
        
        logging.info("Starting page load...")
        driver.set_page_load_timeout(60)
        
        # First visit Google homepage
        logging.info("Loading Google homepage...")
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))
        
        # Load trends page
        logging.info(f"Loading Google Trends URL...")
        driver.get(url)
        
        # Initial wait for page load
        time.sleep(10)  # Give page time to start loading
        
        # Check for common issues
        logging.info("Checking page content...")
        if "429" in driver.title:
            logging.error("Rate limit (429) detected")
            return "RATE_LIMITED"
        
        if "trends.google.com" not in driver.current_url:
            logging.error(f"Unexpected URL: {driver.current_url}")
            return None
            
        # Wait for table to be present with multiple attempts
        logging.info("Waiting for data table...")
        max_table_wait = 5
        wait = WebDriverWait(driver, 30)
        
        # Specific XPath for the Google Trends table
        trends_table_xpath = "//div[2]/div[2]/div/md-content/div/div/div[1]/trends-widget/ng-include/widget/div/div/ng-include/div/ng-include/div/line-chart-directive/div[1]/div/div[1]/div/div/table"
        
        # Alternative XPaths in case the structure changes slightly
        table_xpaths = [
            trends_table_xpath,
            "//line-chart-directive//table",  # More general version
            "//trends-widget//table",         # Even more general
            "//div[contains(@class, 'line-chart')]//table",  # Class-based
            "//table"                         # Fallback
        ]
        
        for attempt in range(max_table_wait):
            try:
                # Try each XPath in order
                table_found = False
                for xpath in table_xpaths:
                    try:
                        logging.info(f"Trying XPath: {xpath}")
                        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                        logging.info(f"Found table with XPath: {xpath}")
                        table_found = True
                        break
                    except TimeoutException:
                        continue
                
                if not table_found:
                    # Check iframes if table not found in main document
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        logging.info(f"Found {len(iframes)} iframes, checking each...")
                        for iframe in iframes:
                            try:
                                driver.switch_to.frame(iframe)
                                for xpath in table_xpaths:
                                    try:
                                        if driver.find_elements(By.XPATH, xpath):
                                            logging.info(f"Found table in iframe with XPath: {xpath}")
                                            table_found = True
                                            break
                                    except:
                                        continue
                                if table_found:
                                    break
                                driver.switch_to.default_content()
                            except:
                                driver.switch_to.default_content()
                                continue
                
                if table_found:
                    # Wait for data to be populated
                    time.sleep(5)
                    break
                else:
                    # Try to trigger data load
                    actions = [
                        lambda: driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"),
                        lambda: driver.execute_script("window.scrollTo(0, 0);"),
                        lambda: time.sleep(5)
                    ]
                    
                    for action in actions:
                        action()
                        # Check if table appeared after action
                        for xpath in table_xpaths:
                            try:
                                if driver.find_elements(By.XPATH, xpath):
                                    logging.info(f"Found table after interaction with XPath: {xpath}")
                                    table_found = True
                                    break
                            except:
                                continue
                        if table_found:
                            break
                    
                    if not table_found:
                        raise TimeoutException("Table not found after interactions")
                    
            except TimeoutException:
                if attempt < max_table_wait - 1:
                    logging.warning(f"Table wait attempt {attempt + 1} failed, retrying...")
                    time.sleep(10)
                    continue
                else:
                    logging.error("All attempts to find table failed")
                    screenshot_file = f"failed_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot_file)
                    logging.error(f"Saved screenshot to {screenshot_file}")
                    return None
        
        # Get page source and parse
        logging.info("Parsing page content...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Try to find table using the same XPaths in BeautifulSoup
        table = None
        for xpath in table_xpaths:
            try:
                # Convert XPath to CSS selector (simplified version)
                css_selector = xpath.replace('//table', 'table').replace('//', ' ').replace('/', ' > ')
                table = soup.select_one(css_selector)
                if table:
                    logging.info(f"Found table with CSS selector: {css_selector}")
                    break
            except:
                continue
        
        if not table:
            # Fallback to simple table search
            table = soup.find('table')
        
        if not table:
            logging.error("No table found in parsed page")
            debug_file = f"debug_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            logging.error(f"Saved page source to {debug_file}")
            return None
            
        # Extract data with progress logging
        data = []
        rows = table.find_all('tr')[1:]  # Skip header
        total_rows = len(rows)
        logging.info(f"Found {total_rows} rows to process")
        
        for idx, row in enumerate(rows, 1):
            if idx % 50 == 0:  # Log progress every 50 rows
                logging.info(f"Processing row {idx}/{total_rows}")
                
            cols = row.find_all('td')
            if len(cols) >= 2:
                date_text = cols[0].get_text().strip()
                value_text = cols[1].get_text().strip()
                
                if date_text and value_text:
                    try:
                        parsed_date = parse_spanish_date(date_text)
                        data.append({
                            'Month': parsed_date,
                            'Value': int(value_text)
                        })
                    except Exception as e:
                        logging.warning(f"Error parsing row {idx}: {str(e)}")
                        continue
        
        if not data:
            logging.error("No data extracted from table")
            return None
            
        # Before creating the DataFrame, validate the data
        if data:
            logging.info("Validating parsed dates...")
            for item in data:
                if '‬' in item['Month']:  # Check for specific hidden character
                    item['Month'] = item['Month'].replace('‬', '')
                # Remove any other hidden characters
                item['Month'] = ''.join(char for char in item['Month'] if char.isprintable())
        
        df = pd.DataFrame(data)
        
        # Validate the DataFrame
        if not df.empty:
            logging.info("Validating DataFrame...")
            logging.debug(f"Month column values:\n{df['Month'].head()}")
            
            # Clean up Month column
            df['Month'] = df['Month'].str.replace(r'[^\x00-\x7F]+', '')  # Remove non-ASCII
            df['Month'] = df['Month'].str.strip()  # Remove leading/trailing whitespace
            
            logging.debug(f"Cleaned Month column values:\n{df['Month'].head()}")
        
        return df
        
    except Exception as e:
        logging.error(f"Error in scrape_google_trends_data: {str(e)}", exc_info=True)
        return None
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

def process_data():
    """Process Google Trends data with rate limiting handling"""
    logging.info("Starting process_data()")
    
    try:
        os.makedirs('../NewDBase', exist_ok=True)
        
        input_file = '../rawData/Tabla Python Dimar - Notas Google Trends.csv'
        logging.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file)
        logging.info(f"Found {len(df)} tools to process")
        
        index_data = {'Keyword': [], 'Filename': []}
        max_retries = 3
        base_delay = 180
        
        for idx, row in df.iterrows():
            tool_name = row['Herramienta Gerencial']
            url = row['Link']
            
            logging.info(f"\nProcessing tool {idx + 1}/{len(df)}: {tool_name}")
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        delay = base_delay * (2 ** attempt)
                        logging.info(f"Retry delay: {delay:.0f} seconds")
                        time.sleep(delay)
                    
                    trends_data = scrape_google_trends_data(url)
                    
                    if isinstance(trends_data, str) and trends_data == "RATE_LIMITED":
                        logging.warning("Rate limit detected, long delay...")
                        time.sleep(base_delay * 3)
                        continue
                    
                    if isinstance(trends_data, pd.DataFrame) and not trends_data.empty:
                        clean_name = clean_filename(tool_name)
                        random_id = generate_random_id()
                        filename = f'GT_{clean_name}_{random_id}.csv'
                        
                        output_path = os.path.join('../NewDBase', filename)
                        trends_data.columns = ['Month', tool_name]
                        trends_data.to_csv(output_path, index=False)
                        
                        index_data['Keyword'].append(tool_name)
                        index_data['Filename'].append(filename)
                        
                        logging.info(f"Successfully saved data to {filename}")
                        
                        delay = random.uniform(60, 120)
                        logging.info(f"Waiting {delay:.0f} seconds before next tool")
                        time.sleep(delay)
                        break
                    else:
                        logging.warning(f"Attempt {attempt + 1} failed: Invalid/empty data")
                        
                except Exception as e:
                    logging.error(f"Error on attempt {attempt + 1}: {str(e)}", exc_info=True)
                    
                if attempt < max_retries - 1:
                    logging.info("Retrying...")
            else:
                logging.error(f"Failed all {max_retries} attempts for {tool_name}")
        
        if index_data['Keyword']:
            index_df = pd.DataFrame(index_data)
            index_path = '../NewDBase/GTIndex.csv'
            index_df.to_csv(index_path, index=False)
            logging.info(f"Successfully processed {len(index_data['Keyword'])} tools")
            logging.info(f"Index saved to {index_path}")
        else:
            logging.error("No data was processed successfully")
            
    except Exception as e:
        logging.error(f"Critical error in process_data: {str(e)}", exc_info=True)

if __name__ == '__main__':
    try:
        logging.info("=== Starting Google Trends Scraper ===")
        process_data()
        logging.info("=== Scraper Finished ===")
    except Exception as e:
        logging.error("Critical error in main:", exc_info=True) 