# Utils Directory

This directory contains utility scripts for data processing, normalization, API interaction, analysis, and file management within the Management Tools Analysis project.

## Scripts

### Data Source Processing/Scraping

| Script Name   | Description                                                                                                                                                                |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BS.py`       | Processes Bain Satisfaction data from `rawData/Tabla Python Dimar - Bain - Satisfaccion.csv`, creates `NewDBase/BS_*.csv` files, and generates `NewDBase/BSIndex.csv`.     |
| `BU.py`       | Processes Bain Usability data from `rawData/Tabla Python Dimar - Bain - Usabilidad.csv`, creates `NewDBase/BU_*.csv` files, and generates `NewDBase/BUIndex.csv`.          |
| `crdbase2.py` | Queries the Crossref API based on management tool names and date ranges (monthly, yearly, multi-year) and saves results to JSON files. Includes tool name mapping.         |
| `GB.py`       | Scrapes Google Books Ngram Viewer data for tools in `rawData/...Google Books Ngram.csv` using Selenium, saves data to `NewDBase/GB_*.csv`, creates `NewDBase/GBIndex.csv`. |
| `GT.py`       | Scrapes Google Trends data for tools in `rawData/...Google Trends.csv` using Selenium, saves data to `NewDBase/GT_*.csv`, creates `NewDBase/GTIndex.csv`.                  |

### Data Normalization/Transformation

| Script Name                    | Description                                                                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `BS_Z-scores_normalize_csv.py` | Normalizes `BS_*.csv` files from `dbase-non-indexed/` using Z-scores (fixed mean=3, std=0.89) scaled to 0-100, saving results to `dbase/`. |
| `BS_base100_normalize_csv.py`  | Normalizes `BS_*.csv` files from `dbase-non-indexed/` using a base-100 scale (5 -> 100), saving results to `dbase/`.                       |
| `BS_normalize_csv.py`          | Normalizes `BS_*.csv` files from `dbase-non-indexed/` using a custom scale (5->1000, 3->600), saving results to `dbase/`.                  |
| `convert_to_scientific.py`     | Converts the second column of CSV files in `output/csv_reports/CR_mod/` to scientific notation and overwrites the original files.          |
| `normalize_csv.py`             | Normalizes all CSV files from `dbase-non-indexed/` using Google Trends style (max value = 100), saving results to `dbase/`.                |

### Index & Tool Management

| Script Name                | Description                                                                                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BuildTools.py`            | Reads index files (`GTIndex.csv`, `GBIndex.csv`, etc.) from `NewDBase/` to build a comprehensive `tools.py` dictionary mapping tool names to their data files. |
| `fix_crossref_index.py`    | Updates `NewDBase/CRIndex.csv` by adding a 'Complete' column and determining the status based on log file analysis.                                            |
| `list_incomplete_tools.py` | Lists tools marked as incomplete in `NewDBase/CRIndex.csv`.                                                                                                    |

### Analysis & Processing Utilities

| Script Name                     | Description                                                                                                                                                                  |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `force_reprocess_incomplete.py` | Forces reprocessing of incomplete tools in `CRIndex.csv`, temporarily patching `crossref.py` to use a longer max runtime.                                                    |
| `process_extended_crossref.py`  | Processes remaining incomplete Crossref tools (from `CRIndex.csv`) with extended runtime parameters.                                                                         |
| `process_remaining_crossref.py` | Processes remaining or incomplete Crossref tools by running `crossref.py` for each identified tool.                                                                          |
| `seasonal_analyzer.py`          | Analyzes CSV files (starting with `CR`) in `dbase/`, performs seasonal decomposition, calculates monthly distribution profiles, and saves them to `interpolation_profiles/`. |

### Miscellaneous/File Management

| Script Name        | Description                                                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `createBRS-OLD.py` | (Likely deprecated) Generates random data for specific keywords and creates corresponding `BS_*.csv` files in `dbase/` folder, along with an index file `BSindex.txt`. |
| `pdf_to_ris.py`    | Reads metadata from `Informes/README.md` and scans `Informes/` for PDFs to generate a `catalog.ris` file for bibliographic management.                                 |
