# Technical Context: Management Tools Lifecycle Analysis

## Technologies Used

### Core Technologies

1. **Python Environment**

   - Python 3.x
   - Virtual Environment (venv)
   - pip for package management

2. **Data Processing**

   - Pandas (Data manipulation)
   - NumPy (Numerical computing)
   - SciPy (Scientific computing)

3. **Statistical Analysis**

   - Statsmodels (Statistical models)
   - Scikit-learn (Machine learning)
   - ARIMA (Time series)

4. **Visualization**
   - Dash (Web dashboard)
   - Plotly (Interactive plots)
   - Bootstrap (UI components)

### Development Tools

1. **Version Control**

   - Git
   - GitHub
   - Git LFS for large files

2. **Code Quality**

   - Black (Code formatting)
   - Pylint (Code analysis)
   - mypy (Type checking)

3. **Testing**
   - pytest (Unit testing)
   - Coverage.py (Code coverage)
   - Hypothesis (Property testing)

## Development Setup

### Environment Setup

1. **Python Installation**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   source venv/bin/activate  # Unix
   .\venv\Scripts\activate   # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configuration Files**

   ```python
   # config.py
   class Config:
       DEBUG = False
       TESTING = False
       DATABASE_URI = 'mongodb://localhost:27017/'
       CACHE_TYPE = 'redis'
       LOG_LEVEL = 'INFO'
   ```

3. **Environment Variables**

   ```bash
   # .env
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=mongodb://localhost:27017/
   CACHE_URL=redis://localhost:6379
   ```

4. **Data Source**
   - The primary data sources for this project are CSV files located within the `dbase/` directory. Each file typically represents data for a specific management tool from a particular source (e.g., Google Trends, Bain, Crossref).
   - Data loading and processing logic (e.g., in `correlation.py`) reads directly from these CSV files.

## Technical Constraints

### Performance Requirements

1. **Response Time**

   - Dashboard loading: < 2 seconds
   - Data updates: < 1 second
   - Analysis execution: < 5 seconds

2. **Data Processing**

   - Batch processing: < 10 minutes
   - Real-time updates: < 30 seconds
   - Export generation: < 1 minute

3. **Concurrency**
   - Maximum concurrent users: 100
   - Simultaneous analyses: 20
   - Parallel data processing: 5

### Resource Limits

1. **Memory Usage**

   - Maximum RAM per process: 2GB
   - Cache size limit: 1GB
   - Database connection pool: 50

2. **Storage**

   - Maximum database size: 100GB
   - File storage limit: 50GB
   - Temporary storage: 10GB

3. **Network**
   - Bandwidth limit: 100Mbps
   - Request rate limit: 1000/minute
   - Concurrent connections: 200

## Dependencies

### Core Dependencies

```python
# requirements.txt
pandas>=1.4.0
numpy>=1.21.0
scipy>=1.7.0
statsmodels>=0.13.0
scikit-learn>=1.0.0
dash>=2.0.0
plotly>=5.0.0
flask>=2.0.0
```

### Development Dependencies

```python
# requirements-dev.txt
black>=22.0.0
pylint>=2.12.0
mypy>=0.910
pytest>=7.0.0
coverage>=6.0.0
hypothesis>=6.0.0
```

### Optional Dependencies

```python
# requirements-optional.txt
jupyter>=1.0.0
notebook>=6.0.0
ipython>=8.0.0
```

## API Integration

### External APIs

1. **Google Books Ngram**

   ```python
   class GoogleBooksAPI:
       BASE_URL = "https://books.google.com/ngrams/api"
       def fetch_data(self, query, year_start, year_end):
           # Implementation
           pass
   ```

2. **Crossref API**

   ```python
   class CrossrefAPI:
       BASE_URL = "https://api.crossref.org"
       def search_publications(self, query, date_range):
           # Implementation
           pass
   ```

3. **Google Trends API**

   ```python
   class GoogleTrendsAPI:
       def __init__(self):
           self.pytrends = TrendReq()

       def get_interest_over_time(self, keyword):
           # Implementation
           pass
   ```

### Internal APIs

1. **Analysis API**

   ```python
   class AnalysisAPI:
       @app.route('/api/analyze', methods=['POST'])
       def analyze():
           # Implementation
           pass
   ```

2. **Data API**

   ```python
   class DataAPI:
       @app.route('/api/data', methods=['GET'])
       def get_data():
           # Implementation
           pass
   ```

3. **Export API**

   ```python
   class ExportAPI:
       @app.route('/api/export', methods=['POST'])
       def export_data():
           # Implementation
           pass
   ```

## Deployment

### Local Development

```bash
# Start development server
flask run --debug

# Run tests
pytest

# Check code quality
black .
pylint src/
mypy src/
```

### Production Deployment

```bash
# Build application
python setup.py build

# Start production server
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Monitor application
supervisorctl status
```

### Monitoring

```python
# monitoring.py
class ApplicationMonitor:
    def __init__(self):
        self.metrics = {}

    def track_metric(self, name, value):
        self.metrics[name] = value

    def get_health_status(self):
        return {
            'status': 'healthy',
            'metrics': self.metrics
        }
```

## Dashboard (`dashboard.py`)

This section details the technical aspects of the interactive web dashboard built using Dash.

### Overview

- **Purpose:** Visualize and analyze management tool adoption trends from multiple data sources interactively.
- **Framework:** Dash (Python framework built on Flask, Plotly.js, and React.js).
- **Styling:** Dash Bootstrap Components (`dbc.themes.BOOTSTRAP`) for layout and components, supplemented by custom inline styles.

### Core Libraries & Modules

- **Dash & Plotly:**
  - `dash`, `dash.html`, `dash.dcc`, `dash_table`, `dash_bootstrap_components`: For application structure, components (dropdowns, buttons, graphs, tables), and layout.
  - `plotly.graph_objects`, `plotly.figure_factory`, `plotly.subplots`: For generating all interactive visualizations (line, bar, heatmap, 3D scatter, statistical plots).
- **Data Handling:**
  - `pandas`: Core library for data manipulation, time series handling, combining datasets, and calculations (e.g., `.mean()`, `.corr()`).
  - `numpy`: Numerical computations, array manipulations (e.g., for interpolation, regression).
- **Statistical Analysis & ML:**
  - `scipy.stats`: Linear regression (`linregress`).
  - `scipy.interpolate`: Cubic Spline interpolation (`CubicSpline`) for 3D graph smoothing.
  - `scipy.fft`: Fast Fourier Transform (`fft`, `fftfreq`) for frequency analysis.
  - `statsmodels.tsa.seasonal`: Seasonal decomposition (`seasonal_decompose`).
  - `statsmodels.tsa.arima.model`: ARIMA model implementation.
  - `pmdarima`: Automated ARIMA parameter selection (`auto_arima`).
  - `sklearn.preprocessing`: Polynomial features for regression (`PolynomialFeatures`).
  - `sklearn.linear_model`: Linear regression model (`LinearRegression`).
  - `sklearn.metrics`: Mean Squared Error (`mean_squared_error`) for forecast evaluation.
- **Custom Modules:**
  - `correlation`: Provides functions `get_all_keywords`, `get_file_data2`, `create_combined_dataset` (assumed, based on imports) for data retrieval and initial processing specific to this project.
  - `notas`: Contains predefined text notes (`gt_note`, `gbn_note`, etc.) displayed in the sidebar.
- **Standard Libraries:**
  - `warnings`: Used to suppress warnings (`warnings.filterwarnings('ignore')`).

### Application Structure

- **Initialization:** A `dash.Dash` app instance is created with Bootstrap theme and suppressed callback exceptions. Custom `index_string` is defined for favicon links.
- **Global Variables:**
  - `dbase_options`: Dictionary mapping source IDs (int) to display names (str).
  - `color_map`: Dictionary mapping source names (str) to hex color codes (str).
  - `global_date_range`: Dictionary storing `'start'` and `'end'` timestamps for the user-selected time range (modified by `update_graphs` callback). **Note:** Modifying global state in callbacks is generally discouraged in Dash, especially for multi-user applications, as it can lead to race conditions or unexpected behavior. Consider using dcc.Store for managing shared state.
- **Layout (`app.layout`):**
  - Defined using `dbc.Container`, `dbc.Row`, `dbc.Col`.
  - **Sidebar (`sidebar` variable, `dbc.Col`, width=2):** Fixed position, contains logo, keyword dropdown (`keyword-dropdown`), data source toggle buttons (`toggle-source-{id}`), "Select All" button (`select-all-button`), collapsible notes section (`notes-section`), and a fixed footer. Uses `overflowY: 'auto'` for scrolling long content.
  - **Main Content Area (`dbc.Col`, width=10):**
    - Sticky Header (`membrete` variable): Displays project title and author names.
    - Dynamic Title (`main-title` Div): Updated by callback based on selected keyword.
    - Scrollable Content (`main-content` Div): Populated dynamically by the `update_main_content` callback. Contains all graphs, tables, and controls for analysis visualization. Uses `overflowY: 'auto'`.

### Key Components & Interactivity

- **Keyword Selection:** `dcc.Dropdown` (`keyword-dropdown`) populated by `get_all_keywords()`.
- **Data Source Selection:** `dbc.Button`s (`toggle-source-{id}`) acting as toggles. State managed by `toggle_sources` callback. `select-all-button` controls all source buttons.
- **Time Range Selection:** `dbc.ButtonGroup` with buttons (`btn-5y`, etc.). Interaction managed by `update_graphs` callback, also considering `relayoutData` from the line chart's rangeslider.
- **Notes Display:** `dbc.Collapse` elements controlled by buttons (`toggle-*-note`) for each data source note. The entire section (`notes-section`) visibility is toggled based on user selections.
- **Data Table:** `dash_table.DataTable` within a `dbc.Collapse` (`collapse-table`) toggled by `toggle-table-button`. Displays the combined, filtered data.
- **Graphs:** Various `dcc.Graph` components displaying Plotly figures generated by callbacks. Includes line, bar, heatmap, 3D scatter, regression, ARIMA, seasonal decomposition, and Fourier plots. Many graphs are paired (e.g., two forecast plots, two seasonal plots).
- **3D Graph Controls:** `dcc.Dropdown`s (`y-axis-dropdown`, `z-axis-dropdown`) to select sources for Y and Z axes. `dbc.Button` (`toggle-frequency-button`) to switch between monthly and annual aggregation/view.
- **Loading States:** `dcc.Loading` wrappers around computationally intensive graph components (seasonal, Fourier, forecast) to provide user feedback.

### Data Flow & Processing

1. **Initialization:** Keyword list fetched via `get_all_keywords()`.
2. **User Selection:** User selects a keyword and one or more data sources.
3. **`update_main_content` Callback:**
   - Triggers on keyword or source selection change.
   - Calls `get_file_data2` to fetch normalized data for the selected keyword and sources.
   - Calls `create_combined_dataset` to merge data into a single pandas DataFrame (`combined_dataset`).
   - Formats date column, handles potential Bain/Crossref alignment, drops NaNs for selected sources.
   - Applies filtering based on `global_date_range` (if set).
   - Generates the initial layout for the `main-content` div, including initial states for line and bar charts.
4. **`update_graphs` Callback:**
   - Triggers on time range button clicks, line graph zoom/pan (`relayoutData`), keyword, or source changes.
   - Re-fetches and combines data (similar to `update_main_content`).
   - Determines the target `visible_start` and `visible_end` based on trigger (button or slider).
   - Updates `global_date_range`.
   - Filters `combined_dataset` based on the visible range.
   - Recalculates means for the bar chart (`bar_fig`).
   - Updates the line chart (`line_fig`) `xaxis.range` and `xaxis.rangeslider.range`.
   - Calculates means and relative percentages for different historical periods (`periods_bar_fig`).
   - Returns updated figures for `line-graph`, `bar-graph`, and `periods-bar-graph`.
5. **Other Graph Callbacks (`update_*`):**
   - Trigger on relevant inputs (keyword, sources, axis selections).
   - Fetch/combine data as needed.
   - Perform specific analysis (correlation, regression, ARIMA, seasonal, Fourier).
   - Handle potential errors (e.g., insufficient data) and return appropriate figures or error messages.
   - Utilize helper functions (`create_arima_forecast`, `create_seasonal_decomposition`, `create_fourier_analysis`) to encapsulate plotting logic.

### Statistical Methods Implemented

- **Correlation:** Pearson correlation matrix calculated on the combined dataset (`combined_dataset.corr()`) and visualized as a heatmap (`update_correlation_heatmap`).
- **Regression:** Linear and Polynomial (degree 2) regression performed between two selected sources (`update_regression_plot`). Uses `scipy.stats.linregress` and `sklearn.pipeline.make_pipeline` with `PolynomialFeatures` and `LinearRegression`. R-squared values are displayed.
- **Time Series Forecasting (ARIMA):**
  - `auto_arima` (`pmdarima`) used on training data (excluding last 12 months) to find optimal (p, d, q) order.
  - `ARIMA` model (`statsmodels`) fitted on training data, predictions made for the test period.
  - RMSE calculated on test predictions.
  - Model re-fitted on the full dataset to generate future forecasts (12 steps).
  - Plotted by `create_arima_forecast` function, called by `update_forecast_plots`.
- **Seasonal Decomposition:** Additive model (`statsmodels.tsa.seasonal.seasonal_decompose`) with a period of 12 (monthly) applied to individual source time series. Original, trend, seasonal (last 4 years), and residual components are plotted (`create_seasonal_decomposition`, called by `update_seasonal_graphs`).
- **Fourier Analysis (FFT):**
  - `scipy.fft.fft` applied to individual source time series to identify dominant frequencies/periods.
  - Power spectrum calculated and plotted against period (in months) on a log scale (`create_fourier_analysis`, called by `update_fourier_plots`).
  - Peaks are highlighted.

### Potential Improvements & Considerations

- **Global State (`global_date_range`):** Refactor to use `dcc.Store` for managing the selected date range to avoid potential issues in multi-user or complex scenarios.
- **Callback Efficiency:** Some callbacks re-fetch and re-combine data (`update_graphs`, `update_correlation_heatmap`, etc.). Consider using `dcc.Store` to hold the `combined_dataset` generated by `update_main_content` and have downstream callbacks read from the store, potentially improving performance. This requires careful dependency management.
- **Data Fetching Logic:** The details of `get_file_data2` and `create_combined_dataset` are in `correlation.py`. Understanding their performance and caching strategies (if any) is important for optimization.
- **Error Handling:** Callbacks generally include `try...except` blocks, printing errors and returning empty/error figures. This is good, but could be enhanced with more specific error handling or user feedback.
- **Code Duplication:** There's some repetition in fetching/combining data across callbacks. Using `dcc.Store` could help reduce this. The structure for statistical analysis sections seems defined within `update_main_content` which could potentially be structured more cleanly outside the callback if static elements allow.
- **Complexity:** Some callbacks (`update_graphs`, `update_3d_graph`) are quite long and handle multiple aspects (data processing, figure generation, layout updates). Breaking them down might improve maintainability.
- **Styling:** Relies heavily on inline styles. Consolidating styles into CSS files (in the `assets` folder) could improve organization.
- **Responsiveness:** While Bootstrap provides responsiveness, explicit testing on different screen sizes is recommended, especially for complex layouts with multiple graphs.
- **Hardcoded Values:** Forecast steps (12), test size (12 months), minimum data lengths (e.g., 24 for ARIMA/Seasonal) are hardcoded. Consider making these configurable if needed.
