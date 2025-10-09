# Notes and DOI Integration for Management Tools Dashboard

## Overview

This document describes the integration of DOI links and detailed notes for management tools in the Management Tools Analysis Dashboard.

## Features Implemented

### 1. DOI Display Next to Tool Names

- When a management tool is selected, the DOI link to the IC Report appears next to the tool name in the sidebar
- The DOI is displayed as a clickable link that opens the Zenodo page for the corresponding research report

### 2. Data Source Selection Buttons with Info Icons

- **Restored Original Button Design**: Data sources are selected using colored buttons (Google Trends, Google Books, Bain Usability, Bain Satisfaction, Crossref)
- **IC Special Case**: IC is not a selectable data source - it only provides DOI links below the tool selector
- **Visual Selection Feedback**: Selected buttons are highlighted with bold text and blue border glow
- **Info Icons Beside Each Button**: Each data source button has an info icon (ℹ️) next to it
- **Modal Information**: Clicking the info icon opens a modal with detailed notes about the data source for the selected tool
- **Comprehensive Modal Content**:
  - Detailed methodological notes explaining how the data was collected and processed
  - Links to the original data sources
  - DOI links to academic publications (when available)
  - Tool-specific information for each data source combination

### 3. Database Structure

- Created a SQLite database (`pub-assets/notes_and_doi.db`) to store all notes and DOI information
- The database contains 138 records covering all management tools and data sources
- Optimized with indexes for fast querying

## Database Schema

### Table: `tool_notes`

- `Herramienta`: Spanish name of the management tool
- `DOI`: Digital Object Identifier for the IC report
- `Source`: Data source (Google_Trends, Google_Books, IC, BAIN_Ind_Usabilidad, BAIN_Ind_Satisfacción, Crossref)
- `Notes`: Detailed methodological notes in Spanish
- `Links`: URLs to original data sources
- `Keywords`: Search keywords used for data collection

## Files Created/Modified

### New Files:

- `scripts/create_notes_db.py`: Script to create the notes and DOI database
- `pub-assets/notes_and_doi.db`: SQLite database with all notes and DOI information
- `pub-assets/notes_and_doi_spanish.csv`: CSV export of the database (for reference)

### Modified Files:

- `database.py`: Added `get_tool_notes_and_doi()` method to retrieve notes and DOI information
- `dashboard_app/app.py`: Updated callbacks to use the new database instead of CSV files

## Usage

1. **DOI Display**: Select a management tool from the dropdown - the DOI link to the IC Report will appear automatically below the tool selector
2. **Data Source Selection**: Click the colored buttons to select/deselect data sources (Google Trends, Google Books, Bain Usability, Bain Satisfaction, Crossref - IC is not selectable)
3. **Info Icons**: Click the info icon (ℹ️) next to any data source button to view detailed notes and links
4. **Modal Content**: The modal displays comprehensive information about data collection methodology, sources, and academic references for the selected tool-source combination

## Data Sources Covered

- **Google Trends**: Search interest data with methodological details (selectable button)
- **Google Books Ngrams**: Literary analysis data from digitized books (selectable button)
- **IC Reports**: Institutional research reports with DOI links (not selectable - DOI appears below tool selector)
- **Bain Usability**: Executive survey data on tool adoption (selectable button)
- **Bain Satisfaction**: Executive satisfaction ratings (selectable button)
- **Crossref**: Academic publication data from scholarly sources (selectable button)

## Technical Implementation

- **Database**: SQLite with WAL mode for concurrent access
- **Query Optimization**: Indexed columns for fast retrieval
- **UI Integration**: Bootstrap modals and FontAwesome icons
- **Error Handling**: Graceful fallbacks when data is unavailable

## Benefits

1. **Transparency**: Users can understand the data collection methodology for each source
2. **Academic Integrity**: DOI links provide direct access to research reports
3. **User Education**: Detailed notes help users understand data limitations and context
4. **Research Traceability**: Complete audit trail from raw data to dashboard visualizations

## Future Enhancements

- Add more detailed tool descriptions
- Include data quality metrics
- Add export functionality for citations
- Implement search functionality within notes
