# Management Tools Analysis Dashboard

A comprehensive web-based dashboard for analyzing the lifecycle and adoption patterns of management tools using multiple data sources.

## Features

### 1. Temporal Analysis 2D

- Line charts showing trends over time for multiple data sources
- Interactive visualization of tool adoption patterns

### 2. Mean Analysis

- Bar charts displaying average values across different periods
- Comparative analysis of tool metrics

### 3. Temporal Analysis 3D

- 3D scatter plots for comparing two sources over time
- Interactive axis selection for different variables

### 4. Seasonal Analysis

- Time series decomposition showing trend, seasonal, and residual components
- Individual analysis for each data source

### 5. Fourier Analysis (Periodogram)

- Frequency domain analysis using Fast Fourier Transform
- Identification of periodic patterns in the data

### 6. PCA Analysis

- Principal Component Analysis for dimensionality reduction
- Visualization of component loadings and explained variance

### 7. Correlation Heatmap

- Interactive correlation matrix showing relationships between sources
- Color-coded correlation coefficients

### 8. Regression Analysis

- Click on heatmap cells to perform linear regression
- Scatter plots with regression lines and R-squared values

## Data Sources

- **Google Trends**: Search interest data for management tools
- **Google Books Ngrams**: Publication frequency in academic literature
- **Bain - Usability**: User experience and usability metrics
- **Bain - Satisfaction**: User satisfaction scores
- **Crossref.org**: Academic citation data

## Installation

### Prerequisites

- Python 3.8+
- UV package manager

### Setup

```bash
# Clone or navigate to the project directory
cd dashboard_app

# Install dependencies using UV
uv sync

# Run the application
uv run python app.py
```

### Alternative Setup (without UV)

```bash
# Install dependencies manually
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **Select a Management Tool**: Choose from the dropdown menu in the sidebar
2. **Select Data Sources**: Click on the source buttons to include/exclude data sources
3. **Time Range Filtering**: Use the time range buttons (5y, 10y, 15y, 20y, All) to filter data
4. **Explore Analyses**: Navigate through the different analysis sections
5. **Interactive Features**:
   - Click on correlation heatmap cells to generate regression plots
   - Use dropdowns to select variables for 3D analysis
   - Toggle data table visibility

## Project Structure

```
dashboard_app/
├── app.py                 # Main Dash application
├── pyproject.toml         # UV project configuration
├── requirements.txt       # Alternative dependency list
├── README.md             # This file
├── assets/               # Static assets (logos, icons)
└── data/                 # Data files (if needed locally)
```

## Dependencies

- **Dash**: Web framework for Python
- **Plotly**: Interactive plotting library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning algorithms
- **Statsmodels**: Statistical modeling and time series analysis

## Data Processing

The application includes standalone data processing functions:

- `tools.py`: Defines available management tools and data source mappings
- Built-in data loading and processing functions for CSV data
- Normalization and analysis utilities

## Deployment

### Local Development

```bash
cd dashboard_app
uv run python app.py
```

The application will start on `http://127.0.0.1:8050/`

### Production Deployment

For production deployment, the application is already configured for production use. The app runs with debug=False by default when not in development mode.

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY app.py .

RUN pip install uv
RUN uv sync --no-dev

EXPOSE 8050

CMD ["uv", "run", "python", "app.py"]
```

## API Reference

### Main Functions

- `update_main_content()`: Updates the main dashboard content based on user selections
- `create_temporal_2d_figure()`: Generates 2D temporal analysis plots
- `create_pca_figure()`: Performs and visualizes PCA analysis
- `create_correlation_heatmap()`: Creates interactive correlation heatmaps

### Data Loading

- `get_all_keywords()`: Retrieves available management tools
- `get_file_data2()`: Loads and processes data for selected tools and sources
- `create_combined_dataset2()`: Combines data from multiple sources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Management Tools Analysis research project.

## Authors

- **Diomar Anez**: PhD Researcher, Data Analysis
- **Dimar Anez**: Python Developer, Dashboard Implementation

## Acknowledgments

This dashboard is part of a doctoral research project on the ontological dichotomy in management tools adoption patterns.
