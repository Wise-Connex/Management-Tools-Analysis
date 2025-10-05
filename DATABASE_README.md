# Database Implementation for Management Tools Analysis Dashboard

This document describes the database implementation for the Management Tools Analysis Dashboard, which provides fast access to pre-interpolated time series data for the web application.

## Overview

The database system consists of three main components:

1. **Configuration Management** (`config.py`) - Centralized configuration with environment variable overrides
2. **Database Operations** (`database.py`) - SQLite database management with connection pooling
3. **Data Processing** (`data_processor.py`) - Interpolation algorithms and data preparation
4. **Database Creation Script** (`create_database.py`) - CLI tool for database management

## Architecture

```
Raw Data (CSV files)
    ↓
Data Processor (Interpolation + Normalization)
    ↓
Database (SQLite with pre-computed data)
    ↓
Dashboard (Fast queries for real-time analysis)
```

## Database Schema

The database uses SQLite with the following tables:

- `google_trends` - Google Trends data
- `crossref` - Crossref.org citation data
- `google_books` - Google Books Ngram data
- `bain_usability` - Bain usability survey data
- `bain_satisfaction` - Bain satisfaction survey data
- `metadata` - Database metadata and version information

Each data table has the structure:

```sql
CREATE TABLE source_name (
    date TEXT NOT NULL,
    keyword TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (date, keyword)
)
```

## Data Processing Pipeline

### 1. Raw Data Loading

- CSV files are loaded from the `dbase/` directory
- Automatic datetime conversion based on source type
- Caching system to avoid redundant file I/O

### 2. Interpolation Algorithms

#### Google Trends & Crossref (Monthly Data)

- Data is already monthly - no interpolation needed
- Normalization to 0-100 scale

#### Bain Data (Sparse/Annual)

- **Cubic Spline Interpolation**: For data with 4+ points
- **Linear Interpolation**: Fallback for sparse data
- **Min/Max Clipping**: Prevents extrapolation beyond original data range
- **Monthly Resolution**: Converts sparse data to monthly frequency

#### Google Books (Annual Data)

- **Pattern-Based Interpolation**: Uses keyword-specific monthly distribution patterns
- **CSV Pattern Files**: Located in `interpolation_profiles/` directory
- **Even Distribution**: Fallback when no pattern file exists

### 3. Normalization

All data is normalized to a 0-100 scale using min-max scaling:

```
normalized_value = 100 * (raw_value - min_value) / (max_value - min_value)
```

### 4. Database Storage

- Batch insertion for performance
- Automatic conflict resolution (REPLACE on duplicate keys)
- Metadata tracking for version control

## Configuration

The system uses JSON configuration files in the `config/` directory:

### config/database.json

```json
{
  "path": "dashboard_app/data.db",
  "schema_version": "1.0",
  "indexes": [
    "CREATE INDEX IF NOT EXISTS idx_date ON google_trends(date)",
    "CREATE INDEX IF NOT EXISTS idx_keyword ON google_trends(keyword)"
  ]
}
```

### config/paths.json

```json
{
  "data_sources": "dbase",
  "interpolation_profiles": "interpolation_profiles",
  "logs": "logs"
}
```

### config/server.json

```json
{
  "host": "0.0.0.0",
  "port": 8050,
  "debug": false
}
```

## Usage

### Creating/Updating the Database

```bash
# Check database status
python create_database.py --status

# Create/update database (only processes changed files)
python create_database.py

# Force full rebuild
python create_database.py --force

# Verbose output
python create_database.py --verbose

# Use custom config directory
python create_database.py --config-dir /path/to/config
```

### Environment Variables

```bash
# Override config directory
export DASHBOARD_CONFIG_DIR=/custom/config/path

# Custom database path
export DASHBOARD_DATABASE_PATH=/custom/database.db

# Custom data sources path
export DASHBOARD_DATA_SOURCES=/custom/data/path
```

## Performance Optimizations

### 1. Caching System

- **Raw Data Cache**: Avoids reloading CSV files
- **Pattern Cache**: Caches interpolation profile files
- **Interpolation Cache**: Stores computed interpolation results
- **Automatic Cache Management**: Prevents memory overflow

### 2. Database Optimizations

- **WAL Mode**: Write-Ahead Logging for concurrent access
- **Connection Pooling**: Efficient connection management
- **Batch Operations**: Bulk data insertion
- **Indexes**: Optimized query performance

### 3. Interpolation Optimizations

- **Monthly Resolution**: Direct interpolation to monthly frequency
- **Clipping**: Prevents unrealistic extrapolation
- **Fallback Algorithms**: Graceful degradation for edge cases

## Data Sources

### Supported Data Types

1. **Google Trends (GT)**: Monthly search interest data
2. **Crossref (CR)**: Monthly citation data
3. **Google Books (GB)**: Annual ngram frequency data
4. **Bain Usability (BU)**: Sparse survey data (interpolated to monthly)
5. **Bain Satisfaction (BS)**: Sparse survey data (interpolated to monthly)

### File Naming Convention

```
{SOURCE}_{KEYWORD}_{RANDOM_ID}.csv
```

Examples:

- `GT_Alianzas_y_Capital_de_Riesgo_0589.csv`
- `CR_Benchmarking_monthly_relative.csv`
- `GB_Calidad_Total_9438.csv`
- `BU_Competencias_Centrales_3509.csv`
- `BS_Cuadro_de_Mando_Integral_7880.csv`

## Interpolation Profiles

Keyword-specific monthly distribution patterns are stored in `interpolation_profiles/`:

```
CR_{KEYWORD}_monthly_relative.csv
```

Each file contains a `PercentageDistribution` column with 12 monthly percentages that sum to 100%.

## API Reference

### DatabaseManager

```python
from database import get_database_manager

db = get_database_manager()

# Check if database exists
db.database_exists()

# Get data for keyword and sources
datasets_norm, valid_sources = db.get_data_for_keyword("Benchmarking", [1, 2, 4])

# Get database statistics
stats = db.get_table_stats()

# Update metadata
db.update_metadata("last_updated", "2025-01-01T00:00:00")
```

### DataProcessor

```python
from data_processor import get_data_processor

processor = get_data_processor()

# Process all data
stats = processor.process_all_data(force=True, verbose=True)

# Process specific keyword
data = processor.process_keyword_data("Benchmarking")

# Clear caches
processor.clear_caches()
```

### Configuration

```python
from config import get_config

config = get_config()

# Access paths
db_path = config.database_path
data_path = config.data_sources_path

# Access settings
host = config.server_host
port = config.server_port
```

## Monitoring and Maintenance

### Database Health Checks

```bash
# Check database status
python create_database.py --status

# Vacuum database (reclaim space)
python -c "from database import get_database_manager; get_database_manager().vacuum_database()"
```

### Cache Management

```python
from data_processor import get_data_processor

processor = get_data_processor()

# Check cache sizes
stats = processor.get_cache_stats()

# Clear caches if needed
processor.clear_caches()
```

### Backup and Recovery

```python
from database import get_database_manager
from pathlib import Path

db = get_database_manager()
backup_path = Path("backup.db")
db.backup_database(backup_path)
```

## Troubleshooting

### Common Issues

1. **Database locked errors**: Ensure no other processes are using the database
2. **Memory issues**: Clear caches or increase system memory
3. **Interpolation failures**: Check data quality and pattern files
4. **Missing data sources**: Verify file paths and permissions

### Debug Mode

Enable verbose logging:

```bash
python create_database.py --verbose --force
```

### Performance Tuning

For large datasets, consider:

1. Increasing cache sizes in the configuration
2. Using SSD storage for the database
3. Running the script during off-peak hours
4. Monitoring memory usage with verbose mode

## Future Enhancements

### Planned Features

1. **Parallel Processing**: Multi-threaded data processing
2. **Incremental Updates**: Only process changed files
3. **Data Validation**: Automatic quality checks
4. **Compression**: Database compression for storage efficiency
5. **Query Optimization**: Advanced indexing strategies

### Extension Points

The modular design allows for easy extension:

- Add new data sources by extending the source mapping
- Implement new interpolation algorithms
- Add custom normalization methods
- Extend the configuration system

## Dependencies

- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scipy` - Interpolation algorithms
- `sqlite3` - Database operations (built-in)

## License

This database implementation is part of the Management Tools Analysis Dashboard project.
