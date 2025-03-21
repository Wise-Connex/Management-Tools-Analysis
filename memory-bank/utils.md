# Utility Modules Documentation

## Overview

The `Utils` directory contains various utility modules for data collection, processing, and analysis. These modules are essential components of the Management Tools Lifecycle Analysis system.

## Core Utility Modules

### 1. Google Books Module (GB.py)

Data collection and processing for Google Books Ngram data.

#### Key Features

- Web scraping using Selenium
- Data cleaning and formatting
- Rate limiting and retry logic
- CSV file generation
- Index management

#### Main Functions

```python
def scrape_google_books_data(url):
    """Scrape data from Google Books Ngram using Selenium"""

def process_data():
    """Process Google Books Ngram data"""

def clean_filename(name):
    """Clean tool name to create valid filename"""

def format_scientific(value):
    """Format number to scientific notation"""
```

### 2. Google Trends Module (GT.py)

Data collection and processing for Google Trends data.

#### Key Features

- Advanced web scraping with Selenium
- Cookie management
- Rate limit handling
- Date parsing for Spanish formats
- Robust error handling

#### Main Functions

```python
def scrape_google_trends_data(url):
    """Scrape data from Google Trends using Selenium"""

def process_data():
    """Process Google Trends data"""

def parse_spanish_date(date_str):
    """Convert Spanish date format to YYYY-MM"""

def save_cookies(driver, cookie_file):
    """Save cookies to file"""
```

### 3. Crossref Modules

Data processing for academic publication data.

#### Files

- `crossref.py` - Base Crossref processing
- `crossref2.py` - Enhanced Crossref processing
- `process_extended_crossref.py` - Extended data processing
- `process_remaining_crossref.py` - Cleanup processing
- `fix_crossref_index.py` - Index maintenance

#### Key Features

- Academic publication data processing
- Citation analysis
- Index management
- Data validation

### 4. Crossref Database Modules

Crossref Database management and operations.

#### Files

- `crdbase.py` - Base database operations
- `crdbase2.py` - Enhanced database operations

#### Key Features

- Database CRUD operations
- Data validation
- Index management
- Error handling

### 5. Build Tools Module (BuildTools.py)

Tool management and configuration.

#### Key Features

- Tool configuration
- Build process management
- Dependency handling

### 6. Utility Scripts

Various utility scripts for specific tasks:

- `force_reprocess_incomplete.py` - Reprocess incomplete data
- `list_incomplete_tools.py` - List tools with incomplete data
- `BS.py` and `BU.py` - Utility scripts for specific operations

## Common Patterns

### 1. Error Handling

```python
try:
    # Operation code
except Exception as e:
    logging.error(f"Error: {str(e)}", exc_info=True)
    # Error recovery code
```

### 2. Logging

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Rate Limiting

```python
def rate_limit_handler():
    base_delay = 60
    max_retries = 3
    for attempt in range(max_retries):
        delay = base_delay * (2 ** attempt)
        time.sleep(delay)
```

## File Organization

```text
Utils/
├── GB.py                         # Google Books processing
├── GT.py                         # Google Trends processing
├── crossref.py                   # Base Crossref processing
├── crossref2.py                  # Enhanced Crossref processing
├── crdbase.py                    # Base database operations
├── crdbase2.py                   # Enhanced database operations
├── BuildTools.py                 # Tool management
├── process_extended_crossref.py  # Extended Crossref processing
├── process_remaining_crossref.py # Remaining data processing
├── force_reprocess_incomplete.py # Reprocessing script
├── list_incomplete_tools.py      # Tool listing script
├── fix_crossref_index.py        # Index fixing script
├── BS.py                        # Utility script
└── BU.py                        # Utility script
```

## Usage Guidelines

### 1. Data Collection

- Use appropriate rate limiting
- Implement proper error handling
- Save data in standardized formats
- Maintain index files

### 2. Data Processing

- Validate input data
- Handle missing values
- Document transformations
- Maintain data integrity

### 3. Error Recovery

- Log all errors with context
- Implement retry mechanisms
- Save partial progress
- Clean up resources

### 4. Performance

- Use efficient data structures
- Implement caching when appropriate
- Monitor resource usage
- Clean up temporary files
