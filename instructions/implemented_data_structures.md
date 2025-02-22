# Implemented Data Structures

## Current Implementation Status

This document tracks the actual data structures currently implemented in the codebase.

## Data Source Implementations

### 1. Dashboard Data Structures

```python
# Core data source mapping
dbase_options = {
    1: "Google Trends",
    4: "Crossref.org",
    2: "Google Books Ngrams",
    3: "Bain - Usabilidad",
    5: "Bain - Satisfacción"
}

# Combined Dataset Structure
combined_dataset = {
    'Fecha': datetime,          # Timestamp column
    'Google_Trends': float,     # Normalized values 0-100
    'Crossref': float,         # Normalized citation counts
    'Google_Books': float,     # Normalized frequency
    'Bain_Usabilidad': float,  # Usage metrics
    'Bain_Satisfaccion': float # Satisfaction scores
}

# Visualization Cache Structure
VisualizationCache = {
    'cache_key': str,
    'plot_type': str,          # e.g., 'time_series', 'correlation_matrix'
    'parameters': {
        'tools': List[str],
        'time_range': Tuple[datetime, datetime],
        'aggregation_level': str,
        'display_options': Dict
    },
    'data': {
        'series': List[Dict],  # Processed plotting data
        'annotations': List[Dict],
        'layout_config': Dict
    }
}
```

### 2. Analysis Data Structures

```python
# Trend Analysis Results
trends_results = {
    'all_data': pd.DataFrame,           # Complete historical data
    'last_20_years_data': pd.DataFrame, # Last 20 years data
    'last_15_years_data': pd.DataFrame, # Last 15 years data
    'last_10_years_data': pd.DataFrame, # Last 10 years data
    'last_5_years_data': pd.DataFrame,  # Last 5 years data
    'last_year_data': pd.DataFrame,     # Last year data
    'mean_last_20': Dict[str, float]    # 20-year averages by source
}

# Analysis Results
AnalysisResults = {
    'temporal_trends': {
        'trend_coefficient': float,
        'moving_average': pd.Series,
        'trend_percentage': float
    },
    'correlation_matrix': pd.DataFrame,  # Source correlations
    'regression_analysis': Dict,         # Pairwise regression results
    'arima_results': Dict,              # ARIMA model outputs
    'seasonal_analysis': Dict,          # Seasonal decomposition
    'fourier_analysis': Dict            # Cyclical patterns
}
```

## Data Processing Flow

1. **Data Ingestion**

   - Raw data loaded from multiple sources
   - Data normalized to 0-100 scale
   - Timestamps standardized

2. **Data Aggregation**

   ```python
   # Time-based aggregation
   combined_dataset = combined_dataset.groupby(pd.Grouper(freq='Y')).agg({
       'Crossref': 'sum',      # Sum for citation counts
       'other_columns': 'mean' # Average for other metrics
   })
   ```

3. **Analysis Pipeline**
   - Temporal trend analysis
   - Cross-source correlation
   - Statistical modeling (ARIMA)
   - Pattern recognition
   - Visualization generation

## Visualization Structures

1. **Line Graph Configuration**

```python
line_fig = {
    'data': [
        {
            'x': dates,
            'y': values,
            'name': source_name,
            'type': 'scatter',
            'mode': 'lines',
            'line': {
                'color': color_code,
                'width': 2
            }
        }
    ],
    'layout': {
        'title': str,
        'xaxis': Dict,  # Date axis config
        'yaxis': Dict,  # Value axis config
        'height': int,
        'margin': Dict,
        'hovermode': str
    }
}
```

2. **Correlation Heatmap**

```python
heatmap = {
    'z': correlation_values,
    'x': source_labels,
    'y': source_labels,
    'colorscale': custom_colorscale,
    'zmin': -1,
    'zmax': 1,
    'zmid': 0,
    'text': correlation_text,
    'hovertemplate': str
}
```

## State Management

1. **User Session State**

   - Selected data sources
   - Time range selections
   - Visualization preferences
   - Analysis parameters

2. **Cache Management**
   - Visualization caching
   - Analysis results caching
   - Data aggregation caching

## Implementation Notes

1. **Data Validation**

   - NaN handling implemented
   - Infinity value filtering
   - Date range validation
   - Source data consistency checks

2. **Performance Optimizations**

   - Data aggregation caching
   - Visualization result caching
   - Efficient data structures for time series

3. **Error Handling**
   - Data availability checks
   - Source validation
   - Analysis parameter validation
   - Visualization error handling
