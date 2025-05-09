# Management Tools Lifecycle Analysis

How do management tools evolve in contemporary organizations? This project conducts longitudinal statistical analyses using Python to examine the life cycle of prominent management tools. The methodology enables the tracking and forecasting of adoption patterns by integrating data from multiple heterogeneous sources to generate a rigorous and reliable quantitative assessment.

*   **Principal Investigator:** Diomar Añez
*   **Python Programming:** Dimar Añez

This analytical system constitutes an essential component of the research corpus for Diomar Añez's doctoral dissertation, titled *Ontological Dichotomy in "Management Fads"* (© 2023-2025), conducted under the academic supervision of **Dr. Elizabeth Pereira.**

The research undertakes a critical analysis of the temporal dynamics of management tools, problematizing the practical and discursive phenomenon of "management fads." It empirically examines their life cycle—emergence, diffusion, and eventual persistence or obsolescence—and evaluates their implications for the strategic and structural configuration of contemporary organizations. The study aims to contribute to theoretical development by providing a profound understanding of the interaction between administrative innovations and the organizational context.

The analysis results are relevant to:
*   **Executives and Managers (Public, private, and NGO organizations):** Informing strategic decisions regarding the selection, implementation, and evaluation of management tools.
*   **Academics and Researchers (Graduate programs and business schools):** Providing a robust empirical basis for studies on organizational dynamics, diffusion of practices, and strategic management theory.
*   **Consultants and Advisors (Strategic management and organizational transformation):** Offering contextual and trend-based insights into the life cycle and relevance of management tools, supporting their professional praxis and strategic recommendations.

## Overview

This project analyzes management tool adoption trends using data from:

- Google Trends
- Crossref.org academic publications
- Google Books Ngrams
- Bain & Company Usability Data
- Bain & Company Satisfaction Ratings

## Features

- **Time Series Analysis:** Track adoption patterns over time
- **Cross-Source Validation:** Compare trends across different data sources
- **Pattern Recognition:** Identify significant patterns in tool adoption
- **Trend Forecasting:** Predict future trends using ARIMA models
- **Multilingual Reporting:** Generate analysis reports in multiple languages
- **Interactive Dashboard:** Visualize and explore data through a web interface

## Tech Stack

### Core Analysis

- Python 3.11+
- Pandas (Data Analysis)
- NumPy (Numerical Computing)
- SciPy (Scientific Computing)
- Statsmodels (Statistical Models)

### Statistical Analysis

- ARIMA (Time Series Modeling)
- Seasonal Decomposition
- Fourier Analysis
- Correlation Analysis

### Dashboard & Visualization

- Dash
- Plotly
- Flask
- Bootstrap

### AI Integration

- Google Gemini API

## Installation

1.Clone the repository:

```bash
git clone https://github.com/Wise-Connex/Management-Tools-Analysis.git
cd management-tools-analysis
```

2.Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3.Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure
```text
├── analisis.py # Core analysis functions
├── dashboard.py # Web dashboard implementation
├── tools.py # Tool definitions and mappings
├── mtalib.py # Utility library
├── data/ # Data storage
│ ├── sources/ # Raw data sources
│ └── processed/ # Processed data
├── prompts/ # AI analysis prompts
└── venv/ # Virtual environment
```
## Databases

- dbase: This folder contains the CSV files with the data of the toll from the different sources databases.
- Each csv use two letter at the beginning to identified the data source:
  - GT: Google Trends
  - GB: Google Books Ngram Viewer
  - CR: Crossref.org
  - BR: Bain Research

## Usage

1.Start the dashboard:

```bash
python dashboard.py
```

2.Run analysis:

```bash
python analisis.py
```

The dashboard will be available at `http://localhost:8050`

## Key Components

### Analysis Module (analisis.py)

- Data preprocessing and normalization
- Statistical analysis implementation
- Time series forecasting
- AI-assisted interpretation
- Report generation

### Dashboard (dashboard.py)

- Interactive data visualization
- Source selection interface
- Real-time analysis updates
- Responsive design
- Notes and documentation system

### Data Processing

- Multiple interpolation methods
- Cross-source data alignment
- Automated validation
- Caching system

## Environment Variables

Create a `.env` file with:

GOOGLE_API_KEY=your_api_key

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

Follow PEP 8 guidelines. Use provided .gitignore and .cursorrules.

## Analysis Features

1. **Temporal Analysis**

   - Trend detection
   - Pattern recognition
   - Seasonality analysis

2. **Cross-Source Validation**

   - Correlation analysis
   - Data consistency checks
   - Source reliability metrics

3. **Forecasting**

   - ARIMA modeling
   - Confidence intervals
   - Trend projections

4. **Visualization**

   - Time series plots
   - Correlation heatmaps
   - Forecast charts
   - Seasonal decomposition

## Dashboard Features

1. **Data Source Selection**

   - Multiple source selection
   - Date range filtering
   - Tool selection

2. **Interactive Visualizations**

   - Real-time updates
   - Custom view options
   - Export capabilities

3. **Analysis Tools**

   - Statistical summaries
   - Trend analysis
   - Pattern detection

4. **Documentation**
   - Source notes
   - Methodology explanations
   - Analysis interpretations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bain & Company for management tools data
- Google Books Ngram Viewer
- Crossref.org API
- Google Trends API

## Contact

For questions and support, please open an issue in the repository.
