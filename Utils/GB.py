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
import json
import logging
from datetime import datetime
import numpy as np

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gb_scraper.log'),
        logging.StreamHandler()
    ]
)

def clean_filename(name):
    """Clean tool name to create valid filename"""
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name

def generate_random_id():
    """Generate random 4-digit ID"""
    return str(random.randint(0, 9999)).zfill(4)

def format_scientific(value):
    """Format number to scientific notation like 1.44E-07"""
    if value == 0:
        return "0.00E+00"
    exp = int(np.floor(np.log10(abs(value))))
    mantissa = value / (10 ** exp)
    return f"{mantissa:.2f}E{exp:+03d}"

def generate_year_range():
    """Generate year range from 1950 to 2022 in YYYY-01 format"""
    return [f"{year}-01" for year in range(1950, 2023)]

def scrape_google_books_data(url):
    """Scrape data from Google Books Ngram using Selenium"""
    logging.info(f"Starting scrape for URL: {url}")
    
    options = webdriver.ChromeOptions()
    driver = None
    
    try:
        # Configure Chrome options
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-infobars')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), 
                                options=options)
        
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Wait for the script element containing the data
        wait = WebDriverWait(driver, 30)
        script_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/script[2]"))
        )
        
        # Extract and parse the JSON data
        script_content = script_element.get_attribute('innerHTML')
        
        # Find the JSON array in the script content
        json_match = re.search(r'\[{"ngram":.*}\]', script_content)
        if not json_match:
            logging.error("No JSON data found in script")
            return None
            
        json_data = json.loads(json_match.group(0))
        
        if not json_data or not isinstance(json_data, list) or not json_data[0].get('timeseries'):
            logging.error("Invalid JSON structure")
            return None
            
        # Extract the timeseries data
        values = json_data[0]['timeseries']
        
        # Generate year range and create DataFrame
        years = generate_year_range()
        
        if len(values) != len(years):
            logging.error(f"Data length mismatch: {len(values)} values for {len(years)} years")
            return None
            
        # Format values to scientific notation
        formatted_values = [format_scientific(float(v)) for v in values]
        
        df = pd.DataFrame({
            'Year': years,
            'Value': formatted_values
        })
        
        return df
        
    except Exception as e:
        logging.error(f"Error in scrape_google_books_data: {str(e)}", exc_info=True)
        return None
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

def process_data():
    """Process Google Books Ngram data"""
    logging.info("Starting process_data()")
    
    try:
        os.makedirs('../NewDBase', exist_ok=True)
        
        input_file = '../rawData/Tabla Python Dimar - Notas Google Books Ngram.csv'
        logging.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file)
        logging.info(f"Found {len(df)} tools to process")
        
        index_data = {'Keyword': [], 'Filename': []}
        max_retries = 3
        base_delay = 60  # Shorter delay than GT as Google Books has different rate limits
        
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
                    
                    ngram_data = scrape_google_books_data(url)
                    
                    if isinstance(ngram_data, pd.DataFrame) and not ngram_data.empty:
                        clean_name = clean_filename(tool_name)
                        random_id = generate_random_id()
                        filename = f'GB_{clean_name}_{random_id}.csv'
                        
                        output_path = os.path.join('../NewDBase', filename)
                        ngram_data.columns = ['Year', tool_name]
                        ngram_data.to_csv(output_path, index=False)
                        
                        index_data['Keyword'].append(tool_name)
                        index_data['Filename'].append(filename)
                        
                        logging.info(f"Successfully saved data to {filename}")
                        
                        delay = random.uniform(30, 60)  # Shorter delays between requests
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
            index_path = '../NewDBase/GBIndex.csv'
            index_df.to_csv(index_path, index=False)
            logging.info(f"Successfully processed {len(index_data['Keyword'])} tools")
            logging.info(f"Index saved to {index_path}")
        else:
            logging.error("No data was processed successfully")
            
    except Exception as e:
        logging.error(f"Critical error in process_data: {str(e)}", exc_info=True)

if __name__ == '__main__':
    try:
        logging.info("=== Starting Google Books Ngram Scraper ===")
        process_data()
        logging.info("=== Scraper Finished ===")
    except Exception as e:
        logging.error("Critical error in main:", exc_info=True) 