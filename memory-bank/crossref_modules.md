# Crossref Database Modules Documentation

## Overview

The Crossref database modules (`crdbase.py` and `crdbase2.py`) are responsible for extracting and processing academic publication data from the Crossref API. These modules form a critical part of the Management Tools Lifecycle Analysis system, providing comprehensive data about management tool mentions in academic literature.

## Version Comparison

### Base Version (crdbase.py)

- Focuses on monthly data extraction
- Basic tool name mapping
- Single-pass data processing
- Simple batch processing

### Enhanced Version (crdbase2.py)

- Supports both monthly and yearly analysis
- Advanced tool name mapping
- Multi-pass data processing with validation
- Enhanced batch processing with tool-specific folders
- Improved error handling and recovery
- Extended statistics and reporting

## Core Components

### 1. Tool Name Management

```python
TOOL_NAME_MAPPINGS = {
    # Reengineering variations
    "Reingeniería de Procesos": "Reengineering",
    "BPR": "Reengineering",
    # ... more mappings
}

def map_tool_name(tool_name):
    """Map alternative tool names to their standard name"""
    return TOOL_NAME_MAPPINGS.get(tool_name, tool_name)
```

#### Key Features

- Multilingual support (English/Spanish)
- Acronym handling
- Variant name normalization
- Consistent naming across analysis

### 2. Batch Processing System

```python
class BatchProcessor:
    def __init__(self, tool_name, date):
        self.original_tool_name = tool_name
        self.tool_name = map_tool_name(tool_name)
        self.date = date
        self.batch_id = self._generate_batch_id()
        self.tool_folder_id = self._get_or_create_tool_folder_id()
```

#### Key Features

- Organized folder structure
- Unique batch identification
- Tool-specific folders
- Consistent file naming
- Progress tracking

### 3. API Integration

```python
def query_crossref_api(term, date, max_rows=DEFAULT_ROWS):
    """Query Crossref API with rate limiting and error handling"""
    base_url = "https://api.crossref.org/works"
    params = {
        "query": term,
        "filter": f"from-pub-date:{date},until-pub-date:{date}",
        "rows": max_rows,
        "cursor": "*"
    }
```

#### Key Features

- Rate limiting (1.5s delay between calls)
- Error handling
- Pagination support
- Query optimization
- Response validation

### 4. Data Processing Pipeline

#### Stage 1: Term Processing

```python
def process_individual_terms(terms, date, batch):
    """Process each search term individually"""
    for term in terms:
        results = query_crossref_api(term, date)
        batch.save_json(results, 'term', term)
```

#### Stage 2: Result Merging

```python
def merge_term_results(term_files, batch):
    """Merge results from individual terms"""
    merged = {}
    for file in term_files:
        data = load_json(file)
        update_merged_results(merged, data)
```

#### Stage 3: Boolean Filtering

```python
def apply_boolean_filter(merged_results, boolean_query, batch):
    """Apply boolean logic to filter results"""
    parsed_query = parse_boolean_expression(boolean_query)
    filtered = filter_results(merged_results, parsed_query)
```

#### Stage 4: DOI Processing

```python
def process_dois(filtered_results, batch):
    """Process and validate DOIs"""
    unique_dois = extract_unique_dois(filtered_results)
    validated_results = validate_dois(unique_dois)
```

### 5. Statistical Analysis

```python
def generate_batch_statistics(batch, results):
    """Generate comprehensive statistics for the batch"""
    return {
        "total_publications": len(results),
        "unique_journals": count_unique_journals(results),
        "publication_types": analyze_pub_types(results),
        "citation_metrics": calculate_citations(results)
    }
```

#### Key Metrics

- Total publications
- Unique journals
- Publication types
- Citation metrics
- Source distribution
- Author metrics

### 6. Output Generation

#### File Types

1. Term Results

   ```json
   {
     "term": "management_tool",
     "results": [...],
     "metadata": {...}
   }
   ```

2. Merged Results

   ```json
   {
     "merged_data": [...],
     "statistics": {...},
     "batch_info": {...}
   }
   ```

3. Statistics

   ```json
   {
     "summary": {...},
     "detailed_metrics": {...},
     "trends": {...}
   }
   ```

## Usage Guidelines

### 1. Monthly Analysis

```bash
python crdbase2.py --tool "Tool Name" --date "YY-MM"
```

### 2. Yearly Analysis

```bash
python crdbase2.py --tool "Tool Name" --year "YYYY"
```

### 3. Interactive Mode

```bash
python crdbase2.py
```

## Error Handling

### 1. API Errors

```python
try:
    response = requests.get(url, params=params)
    if response.status_code == 429:  # Rate limit
        time.sleep(CROSSREF_API_DELAY * 2)
        retry_request()
except RequestException as e:
    logging.error(f"API Error: {str(e)}")
```

### 2. Data Validation

```python
def validate_data(data):
    """Validate data structure and content"""
    if not isinstance(data, dict):
        raise ValueError("Invalid data structure")
    if "items" not in data:
        raise ValueError("Missing items in response")
```

### 3. Recovery Mechanisms

```python
def recover_batch_processing(batch_id):
    """Recover from failed batch processing"""
    saved_state = load_saved_state(batch_id)
    resume_processing(saved_state)
```

## Performance Considerations

### 1. Memory Management

- Batch processing of results
- Efficient data structures
- Resource cleanup

### 2. Processing Optimization

- Parallel processing where possible
- Caching of intermediate results
- Query optimization

### 3. Storage Efficiency

- Compressed data storage
- Selective field storage
- Index management
