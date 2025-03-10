# CSV Processing for Management Tools Analysis

This directory contains scripts for processing and analyzing CSV files for the Management Tools Lifecycle Analysis project.

## Overview

The project analyzes data from multiple sources to track and forecast management tool adoption patterns. The data is stored in CSV files with semicolon delimiters and Spanish text, which requires specific handling for proper encoding and processing.

## Files and Scripts

### `fix_csv_encoding.py`

This script fixes encoding issues in CSV files by:

1. Detecting the original encoding (typically ISO-8859-1/Latin-1 for Spanish)
2. Converting files to UTF-8 encoding
3. Maintaining semicolon delimiters
4. Creating backups of original files

Usage:

```bash
python fix_csv_encoding.py
```

### `csv_reader.py`

This utility script provides functions to read, process, and analyze the CSV files:

1. Reads all CSV files with proper encoding and delimiter settings
2. Extracts and consolidates management tools data
3. Creates a unified DataFrame with all data sources
4. Generates visualizations of the data
5. Outputs processed data to CSV files

Usage:

```bash
python csv_reader.py
```

## Data Sources

The project includes data from five main sources:

1. **Google Trends (GT)**: Search frequency data indicating public interest
2. **Google Books Ngram (GB)**: Term frequency in published literature
3. **Crossref Academic Publications (CR)**: Academic research metrics
4. **Bain & Company Usability (BU)**: Tool adoption and implementation data
5. **Bain & Company Satisfaction (BS)**: User satisfaction and perception data

Each source provides insights about 23 different management tools.

## Management Tools

The analysis covers 23 management tools:

1. Reingeniería de Procesos (Process Reengineering)
2. Gestión de la Cadena de Suministro (Supply Chain Management)
3. Planificación de Escenarios (Scenario Planning)
4. Planificación Estratégica (Strategic Planning)
5. Experiencia del Cliente (Customer Experience)
6. Calidad Total (Total Quality Management)
7. Propósito y Visión (Purpose and Vision)
8. Benchmarking
9. Competencias Centrales (Core Competencies)
10. Cuadro de Mando Integral (Balanced Scorecard)
11. Alianzas y Capital de Riesgo (Strategic Alliances and Venture Capital)
12. Outsourcing
13. Segmentación de Clientes (Customer Segmentation)
14. Fusiones y Adquisiciones (Mergers and Acquisitions)
15. Gestión de Costos (Cost Management)
16. Presupuesto Base Cero (Zero-Based Budgeting)
17. Estrategias de Crecimiento (Growth Strategies)
18. Gestión del Conocimiento (Knowledge Management)
19. Gestión del Cambio (Change Management)
20. Optimización de Precios (Price Optimization)
21. Lealtad del Cliente (Customer Loyalty)
22. Innovación Colaborativa (Collaborative Innovation)
23. Talento y Compromiso (Talent and Engagement)

## Output Files

### Processed Data

The `csv_reader.py` script generates a consolidated CSV file:

- `processed_data/management_tools.csv`: Contains all management tools data from all sources

### Visualizations

The script also generates visualizations:

- `visualizations/tools_by_source.png`: Bar chart showing the count of management tools by data source

## Requirements

The scripts require the following Python packages:

- pandas
- numpy
- matplotlib
- seaborn
- chardet (for encoding detection)

These dependencies can be installed using:

```bash
pip install pandas numpy matplotlib seaborn chardet
```

## Data Structure

The consolidated data includes the following columns:

- **Source**: Name of the data source (e.g., "Google Trends")
- **SourceCode**: Short code for the data source (e.g., "GT")
- **Tool**: Name of the management tool
- **ToolCode**: Code for the tool (e.g., "01-GT")
- **Title**: Title of the analysis
- **Subtitle**: Detailed description of the analysis

## Future Work

Potential enhancements for the data processing:

1. Add time series analysis for adoption patterns
2. Implement cross-source correlation analysis
3. Create interactive dashboards for data exploration
4. Develop prediction models for future tool adoption
5. Add multilingual support for generated reports

## Troubleshooting

If you encounter encoding issues:

1. Check if the CSV files use semicolon (`;`) delimiters instead of commas
2. Verify the encoding of the original files (often ISO-8859-1 for Spanish)
3. Run `fix_csv_encoding.py` to convert files to UTF-8
4. Check the backup directory for original files
