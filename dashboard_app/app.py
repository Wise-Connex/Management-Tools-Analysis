import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.fft import fft, fftfreq
import warnings
import os
import sys

warnings.filterwarnings('ignore')

# Import tools dictionary
from tools import tool_file_dic

# Standalone helper functions (simplified versions without heavy dependencies)
def get_all_keywords():
    """Extract all keywords from tool_file_dic"""
    all_keywords = []
    for tool_list in tool_file_dic.values():
        for keyword in tool_list[1]:
            if keyword not in all_keywords:
                all_keywords.append(keyword)
    return all_keywords

# Global caches for performance optimization
_raw_data_cache = {}  # Cache for loaded CSV data
_pattern_cache = {}   # Cache for CSV pattern files
_interpolation_cache = {}  # Cache for interpolation results

def cubic_interpolation(df, kw):
    """Optimized cubic interpolation for Bain data with caching and min/max clipping"""
    # Create cache key based on data content
    cache_key = f"{kw}_{hash(str(df[kw].values.tobytes()) if hasattr(df[kw].values, 'tobytes') else str(df[kw].values))}_{df.index.min()}_{df.index.max()}"

    # Check cache first
    if cache_key in _interpolation_cache:
        return _interpolation_cache[cache_key].copy()

    # Extract actual data points (non-NaN values)
    actual_data = df[~df[kw].isna()]

    if actual_data.empty or len(actual_data) < 4:  # Cubic spline requires at least 4 points
        result = linear_interpolation(df, kw)
        _interpolation_cache[cache_key] = result.copy()
        return result

    # Get the min and max values from original data for STRICT clipping
    original_min = actual_data[kw].min()
    original_max = actual_data[kw].max()
    # NO MARGIN - Clip strictly to original data range
    clip_min = original_min
    clip_max = original_max

    # Ensure index is sorted AND has correct type (datetime64[ns])
    actual_data = actual_data.sort_index()
    actual_data.index = pd.to_datetime(actual_data.index)

    # Convert dates to numerical values (days since epoch)
    x = (actual_data.index - pd.Timestamp('1970-01-01')).days.values.astype(float)
    y = actual_data[kw].values

    # Create Cubic Spline
    from scipy.interpolate import CubicSpline
    cs = CubicSpline(x, y, bc_type='natural')

    # --- Optimized: Interpolate directly at MONTHLY frequency instead of daily ---
    monthly_date_range = pd.date_range(
        start=actual_data.index.min(),
        end=actual_data.index.max(),
        freq='MS'  # Monthly start frequency
    )

    if monthly_date_range.empty and not actual_data.empty:
        monthly_date_range = pd.date_range(start=actual_data.index.min(), periods=1, freq='MS')
    if monthly_date_range.empty:
        empty_result = pd.DataFrame(columns=[kw], index=pd.to_datetime([]))
        _interpolation_cache[cache_key] = empty_result.copy()
        return empty_result

    x_interp_monthly = (monthly_date_range - pd.Timestamp('1970-01-01')).days.values.astype(float)
    y_interp_monthly = cs(x_interp_monthly)

    # --- Clip monthly values STRICTLY ---
    y_interp_monthly_clipped = np.clip(y_interp_monthly, clip_min, clip_max)
    df_monthly = pd.DataFrame(y_interp_monthly_clipped, index=monthly_date_range, columns=[kw])

    # --- Force original points into MONTHLY data ---
    for idx, val in actual_data[kw].items():
        idx_ts = pd.Timestamp(idx).normalize()

        # Force original value into monthly data
        if idx_ts in df_monthly.index:
            df_monthly.loc[idx_ts, kw] = val
        else:
            df_monthly.loc[idx_ts] = val

    df_monthly = df_monthly.sort_index()

    # Cache the result
    _interpolation_cache[cache_key] = df_monthly.copy()

    return df_monthly

def linear_interpolation(df, kw):
    """Linear interpolation for sparse data with caching"""
    # Create cache key
    cache_key = f"linear_{kw}_{hash(str(df[kw].values.tobytes()) if hasattr(df[kw].values, 'tobytes') else str(df[kw].values))}_{df.index.min()}_{df.index.max()}"

    # Check cache first
    if cache_key in _interpolation_cache:
        return _interpolation_cache[cache_key].copy()

    # Extract actual data points (non-NaN values)
    actual_data = df[~df[kw].isna()]

    if actual_data.empty:
        result = df.copy()  # Return original if no actual data
        _interpolation_cache[cache_key] = result.copy()
        return result

    x = actual_data.index  # Keep index as DatetimeIndex for actual points only
    y = actual_data[kw].values

    # Use numpy.interp for linear interpolation, but only within the range of actual data
    # Create date range only between first and last actual data points
    x_interp = pd.date_range(actual_data.index.min().date(), actual_data.index.max().date(), freq='MS')
    y_interp = np.interp(x_interp, x, y)

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])

    # Preserve original values at actual data points to ensure accuracy
    for idx in actual_data.index:
        if idx in df_interpolated.index:
            df_interpolated.loc[idx, kw] = actual_data.loc[idx, kw]

    # Cache the result
    _interpolation_cache[cache_key] = df_interpolated.copy()

    return df_interpolated

def manage_cache_size(max_size=50):
    """Limit cache size to prevent memory issues"""
    global _interpolation_cache
    if len(_interpolation_cache) > max_size:
        # Remove oldest entries (simple FIFO)
        items_to_remove = len(_interpolation_cache) - max_size
        keys_to_remove = list(_interpolation_cache.keys())[:items_to_remove]
        for key in keys_to_remove:
            del _interpolation_cache[key]

def get_csv_filename_for_keyword(keyword):
    """Map keyword names to their corresponding CSV pattern filenames"""
    # Create mapping from keyword to CSV filename
    keyword_to_csv = {
        'Alianzas y Capital de Riesgo': 'CR_AlianzasyCapitaldeRiesgo_monthly_relative.csv',
        'Benchmarking': 'CR_Benchmarking_monthly_relative.csv',
        'Calidad Total': 'CR_CalidadTotal_monthly_relative.csv',
        'Competencias Centrales': 'CR_CompetenciasCentrales_monthly_relative.csv',
        'Cuadro de Mando Integral': 'CR_CuadrodeMandoIntegral_monthly_relative.csv',
        'Estrategias de Crecimiento': 'CR_EstrategiasdeCrecimiento_monthly_relative.csv',
        'Experiencia del Cliente': 'CR_ExperienciadelCliente_monthly_relative.csv',
        'Fusiones y Adquisiciones': 'CR_FusionesyAdquisiciones_monthly_relative.csv',
        'Gestión de Costos': 'CR_GestióndeCostos_monthly_relative.csv',
        'Gestión de la Cadena de Suministro': 'CR_GestióndelaCadenadeSuministro_monthly_relative.csv',
        'Gestión del Cambio': 'CR_GestióndelCambio_monthly_relative.csv',
        'Gestión del Conocimiento': 'CR_GestióndelConocimiento_monthly_relative.csv',
        'Innovación Colaborativa': 'CR_InnovaciónColaborativa_monthly_relative.csv',
        'Lealtad del Cliente': 'CR_LealtaddelCliente_monthly_relative.csv',
        'Optimización de Precios': 'CR_OptimizacióndePrecios_monthly_relative.csv',
        'Outsourcing': 'CR_Outsourcing_monthly_relative.csv',
        'Planificación Estratégica': 'CR_PlanificaciónEstratégica_monthly_relative.csv',
        'Planificación de Escenarios': 'CR_PlanificacióndeEscenarios_monthly_relative.csv',
        'Presupuesto Base Cero': 'CR_PresupuestoBaseCero_monthly_relative.csv',
        'Propósito y Visión': 'CR_PropósitoyVisión_monthly_relative.csv',
        'Reingeniería de Procesos': 'CR_ReingenieríadeProcesos_monthly_relative.csv',
        'Segmentación de Clientes': 'CR_SegmentacióndeClientes_monthly_relative.csv',
        'Talento y Compromiso': 'CR_TalentoyCompromiso_monthly_relative.csv'
    }

    return keyword_to_csv.get(keyword)

def load_pattern_file(csv_filename):
    """Load and cache CSV pattern files for performance"""
    global _pattern_cache

    if csv_filename in _pattern_cache:
        return _pattern_cache[csv_filename]

    pattern_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'interpolation_profiles',
                               csv_filename)

    if os.path.exists(pattern_file):
        try:
            pattern_df = pd.read_csv(pattern_file)
            if 'PercentageDistribution' in pattern_df.columns and len(pattern_df) >= 12:
                # Extract and normalize monthly percentages
                monthly_percentages = pattern_df['PercentageDistribution'].values[:12]
                monthly_percentages = monthly_percentages / monthly_percentages.sum() * 100

                # Cache the result
                _pattern_cache[csv_filename] = monthly_percentages
                return monthly_percentages
        except Exception as e:
            print(f"Warning: Could not load pattern file {csv_filename}: {e}")

    return None

def interpolate_gb_to_monthly(gb_df, keyword):
    """Interpolate annual GB data to monthly using keyword-specific CSV patterns (with caching)"""
    if gb_df.empty:
        return gb_df

    # Get the column name
    gb_col = gb_df.columns[0]

    # Create monthly index for all years in GB data
    gb_years = gb_df.index.year.unique()
    monthly_index = pd.date_range(start=f'{gb_years.min()}-01-01',
                                  end=f'{gb_years.max()}-12-31',
                                  freq='MS')

    # Get the correct CSV filename for this keyword
    csv_filename = get_csv_filename_for_keyword(keyword)

    monthly_percentages = None
    if csv_filename:
        # Use cached pattern loading
        monthly_percentages = load_pattern_file(csv_filename)
        if monthly_percentages is not None:
            print(f"Using cached CSV pattern for keyword '{keyword}' from {csv_filename}")
        else:
            print(f"Warning: No valid pattern found for keyword '{keyword}' in {csv_filename}")
    else:
        print(f"Warning: No CSV mapping found for keyword '{keyword}'")

    # If no valid pattern found, use even distribution
    if monthly_percentages is None:
        monthly_percentages = np.full(12, 100/12)  # Even distribution
        print(f"Using even distribution for keyword '{keyword}' (no valid pattern found)")

    # Initialize monthly data
    monthly_data = []

    for year in gb_years:
        annual_value = gb_df.loc[gb_df.index.year == year, gb_col].iloc[0] if not gb_df.loc[gb_df.index.year == year].empty else 0

        # Apply monthly percentages to annual value
        monthly_values = (monthly_percentages / 100) * annual_value

        # Add monthly values for this year
        year_start = pd.Timestamp(f'{year}-01-01')
        for month in range(12):
            monthly_data.append({
                'date': year_start + pd.DateOffset(months=month),
                gb_col: monthly_values[month]
            })

    # Create DataFrame with monthly data
    result_df = pd.DataFrame(monthly_data)
    result_df = result_df.set_index('date')
    result_df.index.name = gb_df.index.name

    return result_df

def interpolate_gb_to_monthly_even(gb_df):
    """Interpolate annual GB data to monthly by distributing evenly across 12 months"""
    if gb_df.empty:
        return gb_df

    # Get the column name
    gb_col = gb_df.columns[0]

    # Create monthly index for all years in GB data
    gb_years = gb_df.index.year.unique()
    monthly_index = pd.date_range(start=f'{gb_years.min()}-01-01',
                                  end=f'{gb_years.max()}-12-31',
                                  freq='MS')

    # Initialize monthly data
    monthly_data = []

    for year in gb_years:
        annual_value = gb_df.loc[gb_df.index.year == year, gb_col].iloc[0] if not gb_df.loc[gb_df.index.year == year].empty else 0

        # Distribute annual value evenly across 12 months
        monthly_value = annual_value / 12

        # Add monthly values for this year
        year_start = pd.Timestamp(f'{year}-01-01')
        for month in range(12):
            monthly_data.append({
                'date': year_start + pd.DateOffset(months=month),
                gb_col: monthly_value
            })

    # Create DataFrame with monthly data
    result_df = pd.DataFrame(monthly_data)
    result_df = result_df.set_index('date')
    result_df.index.name = gb_df.index.name

    return result_df

def clear_all_caches():
    """Clear all caches to free memory"""
    global _raw_data_cache, _pattern_cache, _interpolation_cache
    _raw_data_cache.clear()
    _pattern_cache.clear()
    _interpolation_cache.clear()
    print("All caches cleared")

def get_cache_stats():
    """Get cache statistics for performance monitoring"""
    global _raw_data_cache, _pattern_cache, _interpolation_cache
    return {
        'raw_data_cache': len(_raw_data_cache),
        'pattern_cache': len(_pattern_cache),
        'interpolation_cache': len(_interpolation_cache),
        'total_cached_items': len(_raw_data_cache) + len(_pattern_cache) + len(_interpolation_cache)
    }

def manage_all_cache_sizes():
    """Manage all cache sizes to prevent memory issues"""
    global _raw_data_cache, _pattern_cache, _interpolation_cache

    # Raw data cache: keep max 20 items
    while len(_raw_data_cache) > 20:
        oldest_key = next(iter(_raw_data_cache))
        del _raw_data_cache[oldest_key]

    # Pattern cache: keep max 25 items (all patterns)
    while len(_pattern_cache) > 25:
        oldest_key = next(iter(_pattern_cache))
        del _pattern_cache[oldest_key]

    # Interpolation cache: keep max 50 items
    while len(_interpolation_cache) > 50:
        oldest_key = next(iter(_interpolation_cache))
        del _interpolation_cache[oldest_key]

# Backward compatibility
def clear_interpolation_cache():
    """Clear the interpolation cache to free memory (backward compatibility)"""
    global _interpolation_cache
    _interpolation_cache.clear()

def load_raw_data(source, filename):
    """Load and cache raw CSV data for a specific source"""
    global _raw_data_cache

    cache_key = f"{source}_{filename}"
    if cache_key in _raw_data_cache:
        return _raw_data_cache[cache_key].copy()

    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbase", filename)

    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None

    try:
        # Read CSV file
        df = pd.read_csv(file_path, index_col=0)
        df.index = df.index.str.strip()

        # Convert index to datetime based on source type
        if source == 2:  # Google Books Ngrams - keep as annual for now
            df.index = pd.to_datetime(df.index.str.split('-').str[0], format='%Y')
        else:  # Other sources
            df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')

        # Cache the raw data
        _raw_data_cache[cache_key] = df.copy()

        # Limit cache size
        if len(_raw_data_cache) > 20:  # Keep only 20 most recent raw data files
            oldest_key = next(iter(_raw_data_cache))
            del _raw_data_cache[oldest_key]

        return df
    except Exception as e:
        print(f"Error loading data for source {source}: {e}")
        return None

def get_file_data2(selected_keyword, selected_sources):
    """Optimized data loading function with lazy loading and caching"""
    # Map source IDs to file indices
    source_index_map = {1: 0, 2: 2, 3: 3, 4: 4, 5: 5}

    # Get filenames for the selected keyword and sources
    filenames = {}
    for source in selected_sources:
        index = source_index_map[source]
        for key, value in tool_file_dic.items():
            if selected_keyword in value[1]:
                filenames[source] = value[index]
                break

    datasets = {}
    all_raw_datasets = {}

    # Load data for each selected source (lazy loading)
    for source in selected_sources:
        filename = filenames.get(source, 'Archivo no encontrado')

        # Load raw data with caching
        df = load_raw_data(source, filename)
        if df is None:
            continue

        # Apply cubic interpolation for Bain data (sources 3 and 5) - now cached
        if source == 3 or source == 5:
            print(f"Applying interpolation for Bain source {source}...")
            interpolated_data = pd.DataFrame()
            for column in df.columns:
                interpolated = cubic_interpolation(df, column)
                interpolated_data[column] = interpolated[column]

            # Set the index to datetime format
            interpolated_data.index = pd.to_datetime(interpolated_data.index)

            df = interpolated_data

        all_raw_datasets[source] = df

    # Special processing for GB data: ALWAYS interpolate to monthly using CSV patterns
    if 2 in selected_sources and 2 in all_raw_datasets:  # GB selected
        gb_df = all_raw_datasets[2]
        # Find the keyword for this GB data
        keyword = None
        for key, value in tool_file_dic.items():
            if selected_keyword in value[1]:  # Check if selected_keyword is in the keywords list
                keyword = key
                break

        if keyword:
            print(f"Interpolating Google Books data to monthly using patterns for '{keyword}'...")
            all_raw_datasets[2] = interpolate_gb_to_monthly(gb_df, keyword)
        else:
            print(f"Warning: Could not find keyword mapping for '{selected_keyword}', using even distribution")
            all_raw_datasets[2] = interpolate_gb_to_monthly_even(gb_df)

    # Process datasets (preserve individual date ranges)
    for source in selected_sources:
        if source in all_raw_datasets:
            df = all_raw_datasets[source]
            datasets[source] = df

    # Normalize datasets to 0-100 scale
    datasets_norm = {}
    for source, df in datasets.items():
        df_norm = df.copy()
        for col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            if max_val != min_val:
                df_norm[col] = 100 * (df_norm[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 50  # Default value if no variation
        datasets_norm[source] = df_norm

    # Manage all cache sizes to prevent memory issues
    manage_all_cache_sizes()

    return datasets_norm, selected_sources

def create_combined_dataset(datasets_norm, selected_sources, dbase_options):
    """Create combined dataset with common date range"""
    combined_data = pd.DataFrame()

    for source in selected_sources:
        if source in datasets_norm:
            df = datasets_norm[source]
            column_name = dbase_options[source]
            combined_data[column_name] = df.iloc[:, 0]  # Use first column

    return combined_data

def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):
    """Create combined dataset with all dates from all sources"""
    combined_dataset2 = pd.DataFrame()

    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)

    # Sort dates
    all_dates = sorted(list(all_dates))

    # Create DataFrame with all dates
    combined_dataset2 = pd.DataFrame(index=all_dates)

    # Add data from each source - use source name directly as column name
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            source_data = datasets_norm[source].reindex(all_dates)
            # Use just the source name as the column name (not source_name_col)
            combined_dataset2[source_name] = source_data.iloc[:, 0]

    return combined_dataset2

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title='Management Tools Analysis Dashboard',
    update_title=None  # Suppress title updates to reduce console noise
)

# Suppress React warnings in development mode
try:
    if app.config.get('DEBUG', False):
        import logging
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        # Suppress some React warnings by setting environment variable
        import os
        os.environ['REACT_DISABLE_STRICT_MODE_WARNINGS'] = 'true'
except KeyError:
    # Fallback if DEBUG key doesn't exist
    pass

# Add custom CSS to suppress some browser console warnings
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .nav-link:hover {
                background-color: #e9ecef !important;
                color: #0056b3 !important;
                text-decoration: none !important;
            }
            .nav-link {
                transition: all 0.2s ease;
                font-size: 10px !important;
            }
            html {
                scroll-behavior: smooth;
            }
            .section-anchor {
                scroll-margin-top: 100px;
            }
            /* Suppress some Plotly canvas warnings */
            canvas {
                will-change: auto !important;
            }
            /* Responsive section spacing to prevent overlaps */
            .section-anchor {
                margin-bottom: 20px;
                clear: both;
            }
            #section-mean-analysis {
                min-height: 700px;
                margin-bottom: 60px !important;
            }
            #section-temporal-3d {
                margin-top: 80px !important;
                min-height: 600px;
            }
            /* Responsive adjustments for different screen sizes */
            @media (max-width: 1200px) {
                #section-mean-analysis {
                    min-height: 650px;
                    margin-bottom: 50px !important;
                }
                #section-temporal-3d {
                    margin-top: 60px !important;
                    min-height: 550px;
                }
            }
            @media (max-width: 768px) {
                #section-mean-analysis {
                    min-height: 600px;
                    margin-bottom: 40px !important;
                }
                #section-temporal-3d {
                    margin-top: 50px !important;
                    min-height: 500px;
                }
            }
            /* Ensure graphs maintain their heights */
            .js-plotly-plot {
                min-height: inherit !important;
            }
            /* Prevent margin collapse and ensure section separation */
            .section-anchor + .section-anchor {
                margin-top: 20px;
            }
            /* Force section separation */
            #section-mean-analysis + #section-temporal-3d {
                margin-top: 80px !important;
            }
            /* Ensure content flows properly */
            .w-100 {
                box-sizing: border-box;
            }
        </style>
        <script>
            // Suppress React warnings in console
            const originalWarn = console.warn;
            console.warn = function(...args) {
                if (args[0] && typeof args[0] === 'string' &&
                    (args[0].includes('componentWillMount') ||
                     args[0].includes('componentWillReceiveProps') ||
                     args[0].includes('findDOMNode'))) {
                    return; // Suppress these specific warnings
                }
                originalWarn.apply(console, args);
            };
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Define database options
dbase_options = {
    1: "Google Trends",
    4: "Crossref.org",
    2: "Google Books Ngrams",
    3: "Bain - Usabilidad",
    5: "Bain - Satisfacción"
}

# Define color palette
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f'
]

color_map = {
    dbase_options[key]: colors[i % len(colors)]
    for i, key in enumerate(dbase_options.keys())
}

# Note: Date range filtering removed to avoid callback reference issues

# Sidebar layout
sidebar = html.Div([
    html.Div([
        html.A(
            html.Img(
                src='assets/logo-ulac.png',
                style={
                    'width': '80%',
                    'marginBottom': '20px',
                    'display': 'block',
                    'marginLeft': 'auto',
                    'marginRight': 'auto'
                }
            ),
            href='https://ulac.edu.ve/',
            target='_blank'
        ),
        html.Hr(),
        html.Div([
            html.Label("Seleccione una Herramienta:", style={'fontSize': '12px'}),
            dcc.Dropdown(
                id='keyword-dropdown',
                options=[
                    {'label': keyword, 'value': keyword}
                    for keyword in get_all_keywords()
                ],
                value=None,
                placeholder="Seleccione una Herramienta Gerencial",
                className="mb-4",
                style={'fontSize': '12px'}
            ),
            html.Div(id='keyword-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
        html.Div([
            html.Label("Seleccione las Fuentes de Datos: ", className="form-label", style={'fontSize': '12px'}),
            dbc.Button(
                "Seleccionar Todo",
                id="select-all-button",
                color="secondary",
                outline=True,
                size="sm",
                className="mb-2 w-100",
                style={'fontSize': '12px'}
            ),
            html.Div([
                dbc.Button(
                    source,
                    id=f"toggle-source-{id}",
                    color="primary",
                    outline=True,
                    size="sm",
                    className="me-2 mb-2",
                    style={
                        'fontSize': '12px',
                        'borderColor': color_map[source],
                        'color': color_map[source],
                    }
                ) for id, source in dbase_options.items()
            ], id='source-buttons-container'),
            html.Div(id='datasources-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
        html.Div(id='navigation-section', style={'display': 'none'}),
        html.Div([
            html.P([
                "Dashboard de Análisis de ",
                html.B("Herramientas Gerenciales")
            ], style={'marginBottom': '2px', 'fontSize': '8px', 'textAlign': 'center'}),
            html.P([
                "Desarrollado con Python, Plotly y Dash"
            ], style={'fontSize': '8px', 'textAlign': 'center', 'marginTop': '0px', 'marginBottom': '2px'}),
            html.P([
                "por: ",
                html.A("Dimar Anez", href="https://wiseconnex.com", target="_blank", style={'color': '#6c757d', 'textDecoration': 'none'})
            ], style={'fontSize': '7px', 'textAlign': 'center', 'marginTop': '0px', 'color': '#6c757d'})
        ], style={
            'position': 'absolute',
            'bottom': 0,
            'left': 0,
            'right': 0,
            'backgroundColor': '#f3f4f6',
            'padding': '10px 20px',
            'borderTop': '1px solid #dee2e6'
        })
    ], style={
        'overflowY': 'auto',
        'overflowX': 'hidden',
        'height': 'calc(100vh - 80px)',
        'paddingRight': '10px'
    }),
], style={
    'backgroundColor': '#f3f4f6',
    'padding': '20px',
    'height': '100vh',
    'position': 'fixed',
    'width': 'inherit',
    'display': 'flex',
    'flexDirection': 'column',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'boxShadow': '2px 0 5px rgba(0,0,0,0.1)'
})

# Header
header = html.Div([
    html.H4("Análisis Estadístico Correlacional: Técnicas y Herramientas Gerenciales", className="mb-0"),
    html.P([
        "Tesista: ", html.B("Diomar Anez")
    ], className="mb-0"),
], style={
    'position': 'sticky',
    'top': 0,
    'zIndex': 1000,
    'backgroundColor': '#f8f9fa',
    'padding': '10px 20px',
    'borderBottom': '1px solid #dee2e6',
    'fontSize': '12px',
    'textAlign': 'center',
    'width': '100%',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'height': 'auto',
    'marginBottom': '15px'
})

# Main layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([sidebar], width=2, className="bg-light"),
        dbc.Col([
            header,
            html.Div(id='main-title', style={
                'fontSize': '18px',
                'marginBottom': '10px'
            }),
            dcc.Loading(
                id="loading-main-content",
                type="circle",
                children=[
                    html.Div(id='main-content', className="w-100", style={
                        'height': 'calc(100vh - 200px)',
                        'overflowY': 'auto',
                        'overflowX': 'hidden',
                        'paddingRight': '10px',
                        'scrollBehavior': 'smooth'
                    })
                ],
                style={'height': 'calc(100vh - 200px)'}
            )
        ], width=10, className="px-4", style={
            'height': '100vh',
            'overflow': 'hidden'
        })
    ], style={'height': '100vh'})
], fluid=True, className="px-0", style={'height': '100vh'})

# Callbacks

# Main content update callback
@app.callback(
    Output('main-content', 'children'),
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()],
    Input('keyword-dropdown', 'value')
)
def update_main_content(*args):
    button_states = args[:-1]
    selected_keyword = args[-1]

    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or not selected_sources:
        return html.Div("Por favor, seleccione una Herramienta y al menos una Fuente de Datos.")

    try:
        # Get data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        # Process data
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})
        # Keep Fecha as datetime for calculations, format only for display in table
        combined_dataset_fecha_formatted = combined_dataset.copy()
        combined_dataset_fecha_formatted['Fecha'] = combined_dataset_fecha_formatted['Fecha'].dt.strftime('%Y-%m-%d')

        # No longer need Bain/Crossref alignment since we preserve individual date ranges

        # Filter out rows where ALL selected sources are NaN (preserve partial data)
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Create content sections
        content = []

        # Create content sections
        content = []

        # Create content sections
        content = []

        # 1. Temporal Analysis 2D
        content.append(html.Div([
            html.Div([
                html.H6("1. Análisis Temporal 2D", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#007bff',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            html.Div([
                html.Label("Rango de Fechas:", style={'marginRight': '12px', 'fontSize': '14px'}),
                dbc.ButtonGroup([
                    dbc.Button("Todo", id="temporal-2d-all", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                    dbc.Button("20 años", id="temporal-2d-20y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                    dbc.Button("15 años", id="temporal-2d-15y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                    dbc.Button("10 años", id="temporal-2d-10y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                    dbc.Button("5 años", id="temporal-2d-5y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                ], className="mb-3")
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Rango Personalizado:", style={'marginRight': '12px', 'fontSize': '12px'}),
                dcc.RangeSlider(
                    id='temporal-2d-date-range',
                    min=0,
                    max=100,  # Default values, will be updated by callback
                    value=[0, 100],
                    marks={},
                    step=1,
                    allowCross=False,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': '15px'}),
            dcc.Graph(
                id='temporal-2d-graph',
                style={'height': '400px'},
                config={'displaylogo': False, 'responsive': True}
            ),
            html.Div(id='temporal-2d-slider-container', style={'display': 'none'})  # Hidden container for slider updates
        ], id='section-temporal-2d', className='section-anchor'))

        # 2. Mean Analysis
        content.append(html.Div([
            html.Div([
                html.H6("2. Análisis de Medias", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#28a745',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            dcc.Graph(
                id='mean-analysis-graph',
                figure=create_mean_analysis_figure(combined_dataset, selected_source_names),
                style={'height': '600px', 'marginBottom': '30px', 'minHeight': '600px'},
                config={'displaylogo': False, 'responsive': True}
            )
        ], id='section-mean-analysis', className='section-anchor', style={'marginBottom': '40px'}))

        # 3. Temporal Analysis 3D (if 2+ sources)
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.Div([
                    html.H6("3. Análisis Temporal 3D", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
                ], style={
                    'backgroundColor': '#dc3545',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '30px',
                    'marginTop': '60px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    html.Label("Frecuencia de Datos:", style={'marginRight': '12px', 'fontSize': '14px'}),
                    dbc.ButtonGroup([
                        dbc.Button("Mensual", id="temporal-3d-monthly", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                        dbc.Button("Anual", id="temporal-3d-annual", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                    ], className="mb-3")
                ], style={'marginBottom': '10px'}),
                html.Div([
                    dcc.Dropdown(
                        id='y-axis-3d',
                        options=[{'label': src, 'value': src} for src in selected_source_names],
                        value=selected_source_names[0] if selected_source_names else None,
                        placeholder="Eje Y",
                        style={'width': '48%', 'display': 'inline-block'}
                    ),
                    dcc.Dropdown(
                        id='z-axis-3d',
                        options=[{'label': src, 'value': src} for src in selected_source_names],
                        value=selected_source_names[1] if len(selected_source_names) > 1 else None,
                        placeholder="Eje Z",
                        style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}
                    )
                ], style={'marginBottom': '10px'}),
                dcc.Graph(
                    id='temporal-3d-graph',
                    style={'height': '500px', 'width': '80%'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ], id='section-temporal-3d', className='section-anchor'))

        # 4. Seasonal Analysis
        content.append(html.Div([
            html.Div([
                html.H6("4. Análisis Estacional", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#ffc107',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            html.Div([
                dcc.Dropdown(
                    id='seasonal-source-select',
                    options=[{'label': src, 'value': src} for src in selected_source_names],
                    value=selected_source_names[0] if selected_source_names else None,
                    placeholder="Seleccione fuente",
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                dcc.Graph(
                    id='seasonal-analysis-graph',
                    style={'height': '600px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ])
        ], id='section-seasonal', className='section-anchor'))

        # 5. Fourier Analysis
        content.append(html.Div([
            html.Div([
                html.H6("5. Análisis de Fourier (Periodograma)", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#6f42c1',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            html.Div([
                dcc.Dropdown(
                    id='fourier-source-select',
                    options=[{'label': src, 'value': src} for src in selected_source_names],
                    value=selected_source_names[0] if selected_source_names else None,
                    placeholder="Seleccione fuente",
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                dcc.Graph(
                    id='fourier-analysis-graph',
                    style={'height': '500px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ])
        ], id='section-fourier', className='section-anchor'))

        # 6. Correlation Heatmap
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.Div([
                    html.H6("6. Mapa de Calor (Correlación)", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
                ], style={
                    'backgroundColor': '#17a2b8',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                dcc.Graph(
                    id='correlation-heatmap',
                    figure=create_correlation_heatmap(combined_dataset, selected_source_names),
                    style={'height': '400px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ], id='section-correlation', className='section-anchor'))

        # 7. Regression Analysis (clickable from heatmap)
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.Div([
                    html.H6("7. Análisis de Regresión", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
                ], style={
                    'backgroundColor': '#fd7e14',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    html.P("Haga clic en el mapa de calor para seleccionar variables para regresión", style={'fontSize': '12px'}),
                    html.Div([
                        dcc.Graph(
                            id='regression-graph',
                            style={'height': '700px', 'flex': '1'},
                            config={'displaylogo': False, 'responsive': True}
                        ),
                        html.Div(
                            html.P("Haga clic en el mapa de calor para ver las ecuaciones de regresión"),
                            id='regression-equations',
                            style={
                                'padding': '8px',
                                'backgroundColor': '#f8f9fa',
                                'border': '1px solid #007bff',
                                'borderRadius': '6px',
                                'fontSize': '11px',
                                'fontFamily': 'monospace',
                                'minHeight': '50px',
                                'width': 'auto',
                                'maxWidth': '300px',
                                'marginLeft': '20px',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                'alignSelf': 'center'
                            }
                        )
                    ], style={'display': 'flex', 'alignItems': 'flex-start'})
                ])
            ], id='section-regression', className='section-anchor'))

        # 8. PCA Analysis
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.Div([
                    html.H6("8. Análisis PCA (Cargas y Componentes)", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
                ], style={
                    'backgroundColor': '#20c997',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                dcc.Graph(
                    id='pca-analysis-graph',
                    figure=create_pca_figure(combined_dataset, selected_source_names),
                    style={'height': '500px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ], id='section-pca', className='section-anchor'))

        # Data table
        content.append(html.Div([
            html.Div([
                html.H6("Tabla de Datos", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#6c757d',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            dbc.Button(
                "Ocultar Tabla",
                id="toggle-table-button",
                color="primary",
                size="sm",
                className="mb-2",
                style={'fontSize': '12px'}
            ),
            dbc.Collapse(
                html.Div([
                    dash_table.DataTable(
                        data=combined_dataset_fecha_formatted.to_dict('records'),
                        columns=[{"name": str(col), "id": str(col)} for col in combined_dataset_fecha_formatted.columns],
                        style_table={'overflowX': 'auto', 'overflowY': 'auto', 'height': '400px'},
                        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'width': '120px', 'maxWidth': '150px'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        page_size=12
                    )
                ]),
                id="collapse-table",
                is_open=True
            )
        ], id='section-data-table', className='section-anchor'))

        # Performance Monitoring Section
        cache_stats = get_cache_stats()
        content.append(html.Div([
            html.Div([
                html.H6("Monitor de Rendimiento", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#17a2b8',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            html.Div([
                html.P(f"📊 Datos crudos en caché: {cache_stats['raw_data_cache']} archivos", style={'margin': '5px 0', 'fontSize': '12px'}),
                html.P(f"📈 Patrones en caché: {cache_stats['pattern_cache']} archivos CSV", style={'margin': '5px 0', 'fontSize': '12px'}),
                html.P(f"🔢 Interpolaciones en caché: {cache_stats['interpolation_cache']} cálculos", style={'margin': '5px 0', 'fontSize': '12px'}),
                html.P(f"💾 Total elementos en caché: {cache_stats['total_cached_items']}", style={'margin': '5px 0', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.Hr(style={'margin': '10px 0'}),
                html.P("💡 Optimizaciones activas:", style={'margin': '5px 0', 'fontSize': '11px', 'fontWeight': 'bold'}),
                html.Ul([
                    html.Li("Carga diferida de datos (solo fuentes seleccionadas)", style={'fontSize': '10px'}),
                    html.Li("Caché de patrones CSV para interpolación GB", style={'fontSize': '10px'}),
                    html.Li("Caché de resultados de interpolación compleja", style={'fontSize': '10px'}),
                    html.Li("Gestión automática de memoria caché", style={'fontSize': '10px'})
                ], style={'paddingLeft': '20px', 'margin': '5px 0'})
            ], style={'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ], id='section-performance', className='section-anchor'))

        return html.Div(content)

    except Exception as e:
        return html.Div(f"Error: {str(e)}")

# Helper functions for creating figures
def create_temporal_2d_figure(data, sources, start_date=None, end_date=None):
    # Filter data by date range if provided
    filtered_data = data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Fecha'] >= pd.to_datetime(start_date)) &
            (filtered_data['Fecha'] <= pd.to_datetime(end_date))
        ]

    fig = go.Figure()

    # Add traces with solid lines and decreasing opacity for layering visibility
    opacities = [1.0, 0.9, 0.8, 0.7, 0.6]  # Decreasing opacity for layering

    for i, source in enumerate(sources):
        if source in filtered_data.columns:
            # Use solid lines with decreasing opacity to ensure visibility
            opacity = opacities[i % len(opacities)]

            # Create mask for non-NaN values to ensure all data points are plotted
            source_data = filtered_data[source]
            valid_mask = ~source_data.isna()

            if valid_mask.any():
                fig.add_trace(go.Scatter(
                    x=filtered_data['Fecha'][valid_mask],
                    y=source_data[valid_mask],
                    mode='lines+markers',
                    name=source,
                    line=dict(
                        color=color_map.get(source, '#000000'),
                        width=2
                    ),
                    marker=dict(
                        size=3,
                        opacity=opacity
                    ),
                    opacity=opacity,
                    connectgaps=False  # Don't connect across NaN gaps
                ))

    # Calculate dynamic tick spacing based on date range
    date_range_days = (filtered_data['Fecha'].max() - filtered_data['Fecha'].min()).days

    if date_range_days <= 365:  # Less than 1 year
        dtick = "M1"  # Monthly ticks
        tickformat = "%Y-%m"
    elif date_range_days <= 365 * 3:  # 1-3 years
        dtick = "M3"  # Quarterly ticks
        tickformat = "%Y-%m"
    elif date_range_days <= 365 * 5:  # 3-5 years
        dtick = "M6"  # Biannual ticks
        tickformat = "%Y-%m"
    else:  # More than 5 years
        dtick = "M12"  # Annual ticks
        tickformat = "%Y"

    # Update layout with legend at bottom and dynamic ticks
    fig.update_layout(
        title="Análisis Temporal 2D",
        xaxis_title="Fecha",
        yaxis_title="Valor",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            tickformat=tickformat,
            dtick=dtick,
            tickangle=45
        )
    )
    return fig

def create_mean_analysis_figure(data, sources):
    """Create 100% stacked bar chart showing relative contribution of each source"""
    # Calculate total years in dataset for "Todo" range
    total_years = (data['Fecha'].max() - data['Fecha'].min()).days / 365.25

    # Define time ranges with actual year counts
    time_ranges = [
        ("Todo", None, total_years),  # Full range - actual total years
        ("20 años", 20, 20),
        ("15 años", 15, 15),
        ("10 años", 10, 10),
        ("5 años", 5, 5)
    ]

    # Calculate means for each source and time range
    results = []
    for source in sources:
        if source in data.columns:
            for range_name, years_back, actual_years in time_ranges:
                if years_back is None:
                    # Full range
                    mean_val = data[source].mean()
                else:
                    # Calculate date range
                    end_date = data['Fecha'].max()
                    start_date = end_date - pd.DateOffset(years=years_back)
                    mask = (data['Fecha'] >= start_date) & (data['Fecha'] <= end_date)
                    filtered_data = data[mask][source]
                    mean_val = filtered_data.mean() if not filtered_data.empty else 0

                results.append({
                    'Source': source,
                    'Time_Range': range_name,
                    'Mean': mean_val,
                    'Years': actual_years
                })

    # Create DataFrame for plotting
    results_df = pd.DataFrame(results)

    # Find the maximum mean value across all sources and time ranges for 100% reference
    max_mean_value = results_df['Mean'].max()

    # Create single figure with 100% stacked bars
    fig = go.Figure()

    # Calculate width scale based on years
    max_years = max(r[2] for r in time_ranges)
    width_scale = 1.2 / max_years  # Increased max width to 1.2 for wider bars

    # Add stacked bars for each time range (no legend entries)
    for range_name, _, actual_years in time_ranges:
        range_data = results_df[results_df['Time_Range'] == range_name]
        bar_width = actual_years * width_scale

        # Calculate percentages relative to max value
        for _, row in range_data.iterrows():
            percentage = (row['Mean'] / max_mean_value) * 100 if max_mean_value > 0 else 0

            fig.add_trace(
                go.Bar(
                    x=[range_name],
                    y=[percentage],
                    name=row['Source'],  # Same name as lines for unified legend
                    width=bar_width,  # Proportional width based on years
                    marker_color=color_map.get(row['Source'], '#000000'),
                    showlegend=False,  # Don't show bars in legend
                    opacity=0.7  # Make bars slightly transparent for line visibility
                )
            )

    # Add line traces for actual values (secondary y-axis) - these will show in legend
    for source in sources:
        source_data = results_df[results_df['Source'] == source]
        x_values = source_data['Time_Range']
        y_values = source_data['Mean']

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                name=source,  # Clean source name for legend
                line=dict(
                    color=color_map.get(source, '#000000'),
                    width=3
                ),
                marker=dict(size=8),
                yaxis='y2',  # Use secondary y-axis
                showlegend=True  # Only lines show in legend
            )
        )

    # Update layout for combo chart
    fig.update_layout(
        title=f"Análisis de Medias: Relativo (100% = {max_mean_value:.2f}) + Absoluto",
        xaxis_title="Rango Temporal",
        yaxis_title="Contribución Relativa (%)",
        yaxis2=dict(
            title="Valor Absoluto",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        height=600,  # Fixed height to prevent dynamic resizing
        barmode='stack',  # Stack bars to 100%
        legend_title="Fuentes de Datos",
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.6,  # Lower position (3 lines below)
            xanchor="center",
            x=0.5
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=80, b=150)  # Consistent margins
    )

    # Set primary y-axis to 0-100%
    fig.update_yaxes(range=[0, 100])

    return fig

def create_pca_figure(data, sources):
    # Prepare data for PCA
    pca_data = data[sources].dropna()
    if len(pca_data) < 2:
        return go.Figure()

    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pca_data)

    # Perform PCA
    pca = PCA()
    pca_result = pca.fit_transform(scaled_data)

    # Create subplot
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Cargas de Componentes', 'Varianza Explicada'),
        specs=[[{"type": "scatter"}, {"type": "bar"}]]
    )

    # Loadings plot with arrows from origin
    for i, source in enumerate(sources):
        # Add arrow line from origin to point
        fig.add_trace(
            go.Scatter(
                x=[0, pca.components_[0, i]],  # From origin to loading
                y=[0, pca.components_[1, i]],  # From origin to loading
                mode='lines',
                line=dict(color=color_map.get(source, '#000000'), width=2),
                showlegend=False
            ),
            row=1, col=1
        )

        # Add point with label
        fig.add_trace(
            go.Scatter(
                x=[pca.components_[0, i]],
                y=[pca.components_[1, i]],
                mode='markers+text',
                text=[source],
                textposition="top center",
                name=source,
                marker=dict(color=color_map.get(source, '#000000'), size=8)
            ),
            row=1, col=1
        )

    # Explained variance with both cumulative and inverse lines
    explained_var = pca.explained_variance_ratio_ * 100
    pc_labels = [f'PC{i+1}' for i in range(len(explained_var))]
    cumulative_var = explained_var.cumsum()  # Cumulative sum

    # Add bars
    fig.add_trace(
        go.Bar(
            x=pc_labels,
            y=explained_var,
            name='Varianza Explicada (%)',
            marker_color='lightblue',
            showlegend=True
        ),
        row=1, col=2
    )

    # Add cumulative line (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=pc_labels,
            y=cumulative_var,
            mode='lines+markers',
            name='Varianza Acumulativa (%)',
            line=dict(color='orange', width=3),
            marker=dict(color='orange', size=8),
            yaxis='y2'  # Use secondary y-axis
        ),
        row=1, col=2
    )

    # Add inverse line (tertiary y-axis) - not normalized
    if len(explained_var) > 1:
        max_var = explained_var.max()
        inverse_values = max_var / explained_var  # Higher variance = lower inverse value

        fig.add_trace(
            go.Scatter(
                x=pc_labels,
                y=inverse_values,
                mode='lines+markers',
                name='Relación Inversa',
                line=dict(color='red', width=2, dash='dash'),
                marker=dict(color='red', size=6),
                yaxis='y3'  # Use tertiary y-axis for inverse
            ),
            row=1, col=2
        )

    # Update layout with multiple y-axes
    fig.update_layout(
        height=500,
        showlegend=True,
        yaxis2=dict(
            title="Varianza Acumulativa (%)",
            overlaying='y',
            side='right',
            range=[0, 100],
            showgrid=False
        ),
        yaxis3=dict(
            title="Relación Inversa",
            overlaying='y',
            side='right',
            position=0.85,  # Position further right
            showgrid=False,
            anchor='free'
        )
    )

    # Set legend at bottom for each subplot
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    # Add origin lines to loadings plot
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)

    # Update legend for loadings plot (left subplot)
    fig.update_layout(
        legend2=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.25,  # Center on left subplot
            xref="paper"
        )
    )

    return fig

def create_correlation_heatmap(data, sources):
    corr_data = data[sources].corr()

    # Create custom annotations with better contrast
    annotations = []
    for i, row in enumerate(corr_data.values):
        for j, val in enumerate(row):
            # Determine text color based on background intensity
            # For RdBu colorscale: negative values are blue, positive are red, zero is white
            if abs(val) < 0.3:
                # Light background - use dark text
                text_color = 'black'
            else:
                # Dark background - use white text
                text_color = 'white'

            annotations.append(
                dict(
                    x=sources[j],
                    y=sources[i],
                    text=f"{val:.2f}",
                    showarrow=False,
                    font=dict(
                        color=text_color,
                        size=12,
                        weight='bold'
                    )
                )
            )

    fig = ff.create_annotated_heatmap(
        z=corr_data.values,
        x=sources,
        y=sources,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        annotation_text=[[f"{val:.2f}" for val in row] for row in corr_data.values],
        showscale=True
    )

    # Update annotations with better contrast
    fig.update_layout(
        title="Mapa de Calor de Correlación",
        height=400,
        annotations=annotations
    )

    return fig

# Callback for Temporal Analysis 2D with date range filtering
@app.callback(
    [Output('temporal-2d-graph', 'figure'),
     Output('temporal-2d-date-range', 'value')],
    [Input('temporal-2d-date-range', 'value'),
     Input('temporal-2d-all', 'n_clicks'),
     Input('temporal-2d-20y', 'n_clicks'),
     Input('temporal-2d-15y', 'n_clicks'),
     Input('temporal-2d-10y', 'n_clicks'),
     Input('temporal-2d-5y', 'n_clicks'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_temporal_2d_analysis(slider_values, all_clicks, y20_clicks, y15_clicks, y10_clicks, y5_clicks, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or not selected_sources:
        return {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # No longer need Bain/Crossref alignment since we preserve individual date ranges

        # Filter out rows where ALL selected sources are NaN (preserve partial data)
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Determine date range based on button clicks or slider values
        ctx = dash.callback_context
        start_date = None
        end_date = None
        slider_value = slider_values  # Default to current slider value

        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id in ['temporal-2d-all', 'temporal-2d-20y', 'temporal-2d-15y', 'temporal-2d-10y', 'temporal-2d-5y']:
                # Button was clicked - calculate new date range and slider position
                if trigger_id == 'temporal-2d-all':
                    start_date = combined_dataset['Fecha'].min().date()
                    end_date = combined_dataset['Fecha'].max().date()
                    slider_value = [0, len(combined_dataset) - 1]
                else:
                    # Calculate years back from end
                    years_back = int(trigger_id.split('-')[-1].replace('y', ''))
                    end_date = combined_dataset['Fecha'].max().date()
                    start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=years_back)).date()

                    # Find the closest indices for the date range
                    start_idx = (combined_dataset['Fecha'] - pd.to_datetime(start_date)).abs().idxmin()
                    end_idx = len(combined_dataset) - 1
                    slider_value = [start_idx, end_idx]
            elif trigger_id == 'temporal-2d-date-range':
                # Slider was moved - convert indices to dates
                start_idx, end_idx = slider_values
                start_date = combined_dataset['Fecha'].iloc[start_idx].date()
                end_date = combined_dataset['Fecha'].iloc[end_idx].date()
                slider_value = slider_values  # Keep the slider value as is

        # If no trigger or initial load, default to full date range
        if start_date is None and end_date is None:
            start_date = combined_dataset['Fecha'].min().date()
            end_date = combined_dataset['Fecha'].max().date()
            slider_value = [0, len(combined_dataset) - 1]

        return create_temporal_2d_figure(combined_dataset, selected_source_names, start_date, end_date), slider_value
    except Exception as e:
        return {}

# Callback to update the slider properties when data changes (only min, max, marks)
@app.callback(
    Output('temporal-2d-date-range', 'min'),
    Output('temporal-2d-date-range', 'max'),
    Output('temporal-2d-date-range', 'marks'),
    [Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_temporal_slider_properties(selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or not selected_sources:
        return 0, 100, {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # No longer need Bain/Crossref alignment since we preserve individual date ranges

        # Filter out rows where ALL selected sources are NaN (preserve partial data)
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        # Create marks for the slider
        n_marks = min(5, len(combined_dataset))  # Limit to 5 marks
        mark_indices = [int(i * (len(combined_dataset) - 1) / (n_marks - 1)) for i in range(n_marks)]
        marks = {
            idx: combined_dataset['Fecha'].iloc[idx].strftime('%Y-%m')
            for idx in mark_indices
        }

        return 0, len(combined_dataset) - 1, marks
    except Exception as e:
        return 0, 100, {}

# Additional callbacks for specific analyses
def aggregate_data_for_3d(data, frequency, source_name):
    """Aggregate data based on frequency and source type"""
    if frequency == 'monthly':
        return data  # Return as-is for monthly

    # Annual aggregation with different methods per source
    if 'Google Trends' in source_name:
        # GT: Average
        return data.resample('Y').mean()
    elif 'Crossref' in source_name:
        # CR: Sum
        return data.resample('Y').sum()
    elif 'Google Books' in source_name:
        # GB: Sum
        return data.resample('Y').sum()
    else:
        # Bain (BU/BS): Average
        return data.resample('Y').mean()

@app.callback(
    Output('temporal-3d-graph', 'figure'),
    [Input('y-axis-3d', 'value'),
     Input('z-axis-3d', 'value'),
     Input('temporal-3d-monthly', 'n_clicks'),
     Input('temporal-3d-annual', 'n_clicks'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_3d_plot(y_axis, z_axis, monthly_clicks, annual_clicks, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}

    # Determine frequency based on button clicks
    ctx = dash.callback_context
    frequency = 'monthly'  # Default

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'temporal-3d-annual':
            frequency = 'annual'
        elif trigger_id == 'temporal-3d-monthly':
            frequency = 'monthly'

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})
        combined_dataset = combined_dataset.set_index('Fecha')

        # Apply aggregation based on frequency and source type
        y_data = aggregate_data_for_3d(combined_dataset[y_axis], frequency, y_axis)
        z_data = aggregate_data_for_3d(combined_dataset[z_axis], frequency, z_axis)

        # Align the data (they might have different date ranges after aggregation)
        common_index = y_data.index.intersection(z_data.index)
        y_data = y_data.loc[common_index]
        z_data = z_data.loc[common_index]

        fig = go.Figure(data=[
            go.Scatter3d(
                x=common_index,
                y=y_data.values,
                z=z_data.values,
                mode='lines',
                line=dict(color=color_map.get(y_axis, '#000000'), width=3),
                name=f'{y_axis} vs {z_axis} ({frequency})'
            )
        ])

        fig.update_layout(
            title=f'Análisis Temporal 3D: {y_axis} vs {z_axis} ({frequency.capitalize()})',
            scene=dict(
                xaxis_title='Fecha',
                yaxis_title=y_axis,
                zaxis_title=z_axis
            ),
            height=500
        )
        return fig
    except Exception as e:
        print(f"Error in regression analysis: {e}")
        # Return empty figure instead of empty dict
        fig = go.Figure()
        fig.update_layout(
            title="Error en el análisis de regresión",
            xaxis_title="",
            yaxis_title="",
            height=500
        )
        return fig

@app.callback(
    Output('seasonal-analysis-graph', 'figure'),
    [Input('seasonal-source-select', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_seasonal_analysis(selected_source, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not all([selected_source, selected_keyword]) or not selected_sources:
        return {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        if selected_source not in combined_dataset.columns:
            return {}

        ts_data = combined_dataset[selected_source].dropna()
        if len(ts_data) < 24:
            return {}

        decomposition = seasonal_decompose(ts_data, model='additive', period=12)

        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=['Serie Original', 'Tendencia', 'Estacional', 'Residuos'],
            vertical_spacing=0.1
        )

        fig.add_trace(go.Scatter(x=combined_dataset['Fecha'], y=ts_data, name='Original'), row=1, col=1)
        fig.add_trace(go.Scatter(x=combined_dataset['Fecha'], y=decomposition.trend, name='Tendencia'), row=2, col=1)
        fig.add_trace(go.Scatter(x=combined_dataset['Fecha'], y=decomposition.seasonal, name='Estacional'), row=3, col=1)
        fig.add_trace(go.Scatter(x=combined_dataset['Fecha'], y=decomposition.resid, name='Residuos'), row=4, col=1)

        fig.update_layout(height=600, title=f'Análisis Estacional: {selected_source}', showlegend=False)
        return fig
    except Exception as e:
        return {}


@app.callback(
    [Output('regression-graph', 'figure'),
     Output('regression-equations', 'children')],
    [Input('correlation-heatmap', 'clickData'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_regression_analysis(click_data, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or len(selected_sources) < 2 or not click_data:
        # Return empty figure and empty equations
        fig = go.Figure()
        fig.update_layout(
            title="Haga clic en el mapa de calor para ver el análisis de regresión",
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig, ""

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Get clicked variables from heatmap
        if 'points' not in click_data or len(click_data['points']) == 0:
            return {}

        x_var = click_data['points'][0]['x']
        y_var = click_data['points'][0]['y']

        # Debug: print available columns and clicked variables
        print(f"Available columns: {list(combined_dataset.columns)}")
        print(f"Clicked variables: x='{x_var}', y='{y_var}'")

        if x_var not in combined_dataset.columns or y_var not in combined_dataset.columns:
            print(f"Variables not found in dataset: x='{x_var}', y='{y_var}'")
            # Return empty figure instead of empty dict
            fig = go.Figure()
            fig.update_layout(
                title=f"Variables no encontradas: {x_var} vs {y_var}",
                xaxis_title="",
                yaxis_title="",
                height=500
            )
            return fig

        # Perform regression analysis with multiple polynomial degrees
        valid_data = combined_dataset[[x_var, y_var]].dropna()
        if len(valid_data) < 2:
            return {}

        X = valid_data[x_var].values.reshape(-1, 1)
        y = valid_data[y_var].values

        # Colors for different polynomial degrees
        poly_colors = ['red', 'blue', 'green', 'orange']
        degree_names = ['Lineal', 'Cuadrática', 'Cúbica', 'Cuártica']

        fig = go.Figure()

        # Add scatter plot of original data
        fig.add_trace(go.Scatter(
            x=valid_data[x_var],
            y=valid_data[y_var],
            mode='markers',
            name='Datos',
            marker=dict(color='gray', size=6, opacity=0.7)
        ))

        # Sort X for smooth polynomial curves
        X_sorted = np.sort(X.flatten())
        X_sorted_reshaped = X_sorted.reshape(-1, 1)

        # Annotations for formulas and R-squared
        annotations = []

        for degree in range(1, 5):  # Degrees 1, 2, 3, 4
            try:
                # Ensure data is numeric and properly shaped
                X_clean = X.astype(float)
                y_clean = y.astype(float)

                # Fit polynomial regression
                poly_features = PolynomialFeatures(degree=degree)
                X_poly = poly_features.fit_transform(X_clean)

                model = LinearRegression()
                model.fit(X_poly, y_clean)

                # Predict on sorted X values for smooth curve
                X_poly_sorted = poly_features.transform(X_sorted_reshaped)
                y_pred_sorted = model.predict(X_poly_sorted)

                # Calculate R-squared
                y_pred = model.predict(X_poly)
                r_squared = r2_score(y_clean, y_pred)

                # Create polynomial formula string with proper mathematical formatting
                coefs = model.coef_
                intercept = model.intercept_

                if degree == 1:
                    # Linear: y = mx + b
                    formula = f"y = {coefs[1]:.3f}x {'+' if intercept >= 0 else ''}{intercept:.3f}"
                else:
                    # Polynomial: y = a + bx + cx² + dx³ + ...
                    terms = []
                    # Intercept term
                    if abs(intercept) > 0.001:
                        terms.append(f"{intercept:.3f}")

                    # Polynomial terms
                    for i in range(1, len(coefs)):
                        if abs(coefs[i]) > 0.001:  # Only show significant coefficients
                            coef_str = f"{coefs[i]:+.3f}"
                            if i == 1:
                                terms.append(f"{coef_str}x")
                            else:
                                terms.append(f"{coef_str}x<sup>{i}</sup>")

                    # Join terms with proper spacing
                    formula = f"y = {' '.join(terms)}"

                # Add regression line
                fig.add_trace(go.Scatter(
                    x=X_sorted,
                    y=y_pred_sorted,
                    mode='lines',
                    name=f'{degree_names[degree-1]} (R² = {r_squared:.3f})',
                    line=dict(color=poly_colors[degree-1], width=2)
                ))

                # Add annotation for this degree
                annotations.append(
                    f"<b>{degree_names[degree-1]}:</b><br>"
                    f"{formula}<br>"
                    f"R² = {r_squared:.3f}"
                )
            except Exception as poly_e:
                print(f"Error fitting degree {degree} polynomial: {poly_e}")
                # Add error annotation for this degree
                annotations.append(
                    f"<b>{degree_names[degree-1]}:</b><br>"
                    f"Error fitting polynomial<br>"
                    f"R² = N/A"
                )

        # Update layout with increased height for legend and equations
        fig.update_layout(
            title={
                'text': f'Análisis de Regresión Polinomial: {y_var} vs {x_var}',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title=x_var,
            yaxis_title=y_var,
            height=600,  # Increased height to accommodate legend and equations
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,  # Moved 2 lines below the graph
                xanchor="center",
                x=0.5
            )
        )

        # Store annotation text for later use
        annotation_text = "<br><br>".join(annotations)
        print(f"Annotation text preview: {annotation_text[:200]}...")

        print(f"Returning regression figure with {len(fig.data)} traces")
        print(f"Equations content length: {len(annotation_text)}")

        # Create proper Dash components for HTML rendering
        if annotation_text:
            # Parse the annotation text and create proper components
            components = []
            for block in annotation_text.split('<br><br>'):
                if block.strip():
                    lines = block.split('<br>')
                    for i, line in enumerate(lines):
                        if i == 0:  # First line with bold text
                            if '<b>' in line and '</b>' in line:
                                # Extract bold text
                                bold_text = line.replace('<b>', '').replace('</b>', '')
                                components.append(html.P([
                                    html.Strong(bold_text)
                                ], style={'margin': '2px 0', 'lineHeight': '1.3'}))
                            else:
                                components.append(html.P(line, style={'margin': '2px 0', 'lineHeight': '1.3'}))
                        else:  # Other lines
                            # Handle superscript tags
                            if '<sup>' in line and '</sup>' in line:
                                # Split by superscript
                                parts = line.split('<sup>')
                                processed_parts = []
                                for j, part in enumerate(parts):
                                    if j == 0:
                                        processed_parts.append(part)
                                    else:
                                        if '</sup>' in part:
                                            sup_text, remaining = part.split('</sup>', 1)
                                            processed_parts.append(html.Sup(sup_text))
                                            processed_parts.append(remaining)
                                components.append(html.P(processed_parts, style={'margin': '2px 0', 'lineHeight': '1.3'}))
                            else:
                                components.append(html.P(line, style={'margin': '2px 0', 'lineHeight': '1.3'}))

            equations_content = html.Div(components, style={'textAlign': 'left'})
        else:
            equations_content = html.P("Haga clic en el mapa de calor para ver las ecuaciones de regresión", style={'textAlign': 'left'})

        return fig, equations_content
    except Exception as e:
        print(f"Error in regression analysis: {e}")
        import traceback
        traceback.print_exc()
        # Return empty figure and empty equations
        fig = go.Figure()
        fig.update_layout(
            title="Error en el análisis de regresión",
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig, ""

@app.callback(
    Output('collapse-table', 'is_open'),
    Output('toggle-table-button', 'children'),
    [Input('toggle-table-button', 'n_clicks')],
    [State('collapse-table', 'is_open')]
)
def toggle_table(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        button_text = "Ocultar Tabla" if new_state else "Mostrar Tabla"
        return new_state, button_text
    return is_open, "Ocultar Tabla"
# Callback to toggle individual source buttons
for source_id in dbase_options.keys():
    @app.callback(
        Output(f'toggle-source-{source_id}', 'outline'),
        Output(f'toggle-source-{source_id}', 'style'),
        [Input(f'toggle-source-{source_id}', 'n_clicks')],
        [State(f'toggle-source-{source_id}', 'outline')]
    )
    def toggle_source_button(n_clicks, current_outline, source_id=source_id):
        if n_clicks is None:
            return True, {
                'fontSize': '12px',
                'borderColor': color_map[dbase_options[source_id]],
                'color': color_map[dbase_options[source_id]],
            }
        
        new_outline = not current_outline
        if new_outline:
            # Outlined (not selected)
            return True, {
                'fontSize': '12px',
                'borderColor': color_map[dbase_options[source_id]],
                'color': color_map[dbase_options[source_id]],
            }
        else:
            # Filled (selected)
            return False, {
                'fontSize': '12px',
                'borderColor': color_map[dbase_options[source_id]],
                'backgroundColor': color_map[dbase_options[source_id]],
                'color': 'white',
            }

# Callback for "Select All" button
@app.callback(
    [Output(f'toggle-source-{id}', 'outline', allow_duplicate=True) for id in dbase_options.keys()] +
    [Output(f'toggle-source-{id}', 'style', allow_duplicate=True) for id in dbase_options.keys()],
    [Input('select-all-button', 'n_clicks')],
    prevent_initial_call=True
)
def select_all_sources(n_clicks):
    if n_clicks is None:
        return [dash.no_update] * (len(dbase_options) * 2)

    # Set all buttons to selected (outline=False)
    outlines = [False] * len(dbase_options)
    styles = [
        {
            'fontSize': '12px',
            'borderColor': color_map[dbase_options[id]],
            'backgroundColor': color_map[dbase_options[id]],
            'color': 'white',
        }
        for id in dbase_options.keys()
    ]

    return outlines + styles

# Callback to show/hide navigation menu
@app.callback(
    Output('navigation-section', 'children'),
    Output('navigation-section', 'style'),
    [Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_navigation_visibility(selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if selected_keyword and selected_sources:
        # Show navigation menu
        return [
            html.Hr(),
            html.Div([
                html.Label("Navegación Rápida:", style={'fontSize': '10px', 'fontWeight': 'bold', 'marginBottom': '10px', 'color': 'white'}),
                html.Div([
                    html.Div([
                        html.A("1. Temporal 2D", href="#section-temporal-2d", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#007bff', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("2. Análisis Medias", href="#section-mean-analysis", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#28a745', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("3. Temporal 3D", href="#section-temporal-3d", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#dc3545', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("4. Estacional", href="#section-seasonal", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#ffc107', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("5. Fourier", href="#section-fourier", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#6f42c1', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("6. Correlación", href="#section-correlation", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#17a2b8', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("7. Regresión", href="#section-regression", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#fd7e14', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("8. PCA", href="#section-pca", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#20c997', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("Perf", href="#section-performance", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#17a2b8', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                    html.Div([
                        html.A("Tabla Datos", href="#section-data-table", className="nav-link", style={'color': 'white', 'textDecoration': 'none', 'fontSize': '9px'})
                    ], style={'backgroundColor': '#6c757d', 'padding': '4px 8px', 'borderRadius': '4px', 'margin': '2px', 'display': 'inline-block'}),
                ], style={'marginBottom': '15px'}),
            ], style={
                'backgroundColor': '#343a40',
                'border': '2px solid #495057',
                'borderRadius': '10px',
                'padding': '15px',
                'marginTop': '10px',
                'marginBottom': '10px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], {}
    else:
        # Hide navigation menu
        return [], {'display': 'none'}


# Fourier Analysis callback
@app.callback(
    Output('fourier-analysis-graph', 'figure'),
    Input('fourier-source-select', 'value'),
    Input('keyword-dropdown', 'value'),
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_fourier_analysis(selected_source, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or not selected_sources:
        return go.Figure()

    if not selected_source:
        fig = go.Figure()
        fig.add_annotation(
            text="Seleccione una fuente de datos para ver el análisis de Fourier",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Análisis de Fourier - Periodograma",
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        return fig

    # Map display name back to numeric key
    source_key = None
    for key, name in dbase_options.items():
        if name == selected_source:
            source_key = key
            break

    if source_key is None:
        print(f"Fourier: Could not map display name '{selected_source}' to numeric key")
        return go.Figure()

    try:
        # Get data for the selected source
        datasets_norm, _ = get_file_data2(selected_keyword, selected_sources)

        if source_key not in datasets_norm:
            return go.Figure()
        # Get the data series
        data = datasets_norm[source_key]
        if data.empty:
            print(f"Fourier: Data for source key {source_key} is empty")
            return go.Figure()

        # Extract values and remove NaN
        values = data.iloc[:, 0].dropna().values
        if len(values) < 10:  # Need minimum data points
            return go.Figure()

        # Perform Fourier transform
        from scipy.fft import fft, fftfreq
        import numpy as np

        # Apply FFT
        fft_values = fft(values)
        freqs = fftfreq(len(values))

        # Get magnitude (only positive frequencies)
        n = len(values)
        magnitude = np.abs(fft_values[:n//2])
        frequencies = freqs[:n//2]

        # Perform Fourier transform
        from scipy.fft import fft, fftfreq
        import numpy as np

        # Apply FFT
        fft_values = fft(values)
        freqs = fftfreq(len(values))

        # Get magnitude (only positive frequencies)
        n = len(values)
        magnitude = np.abs(fft_values[:n//2])
        frequencies = freqs[:n//2]

        # Convert frequencies to periods (cycles per unit time)
        # For monthly data, frequency represents cycles per month
        periods = 1 / frequencies[1:]  # Skip DC component (freq=0)
        magnitude = magnitude[1:]      # Skip DC component

        # Calculate statistical significance
        # Use 95% confidence threshold based on chi-squared distribution
        significance_threshold = 0.95

        # Calculate statistical significance
        # Use 95% confidence threshold for chi-squared distribution
        from scipy.stats import chi2
        df = 2  # Degrees of freedom for complex FFT
        chi_squared_threshold = chi2.ppf(0.95, df)

        # Scale threshold by mean magnitude
        mean_magnitude = np.mean(magnitude)
        scaled_threshold = chi_squared_threshold * (mean_magnitude / df)

        # Create figure
        fig = go.Figure()

        # Determine significant components
        significant_mask = magnitude >= scaled_threshold

        # Create stem lines more efficiently using vectorized operations
        # Separate significant and non-significant for better performance
        sig_periods = periods[significant_mask]
        sig_magnitude = magnitude[significant_mask]
        non_sig_periods = periods[~significant_mask]
        non_sig_magnitude = magnitude[~significant_mask]
        
        # Add stems for significant components (red)
        if len(sig_periods) > 0:
            for i in range(len(sig_periods)):
                fig.add_shape(
                    type="line",
                    x0=sig_periods[i], y0=0, x1=sig_periods[i], y1=sig_magnitude[i],
                    line=dict(color="red", width=2),
                    layer='below'
                )
        
        # Add stems for non-significant components (grey)
        if len(non_sig_periods) > 0:
            for i in range(len(non_sig_periods)):
                fig.add_shape(
                    type="line",
                    x0=non_sig_periods[i], y0=0, x1=non_sig_periods[i], y1=non_sig_magnitude[i],
                    line=dict(color="grey", width=1),
                    layer='below'
                )

        # Add markers for all components (lollipop heads)
        fig.add_trace(go.Scatter(
            x=periods,
            y=magnitude,
            mode='markers',
            marker=dict(
                color=['red' if sig else 'grey' for sig in significant_mask],
                size=[8 if sig else 5 for sig in significant_mask],
                symbol='circle'
            ),
            name='Componentes',
            showlegend=True
        ))

        # Add labels for significant components using text mode
        if np.any(significant_mask):
            fig.add_trace(go.Scatter(
                x=periods[significant_mask],
                y=magnitude[significant_mask] + max(magnitude) * 0.08,  # Position above markers
                mode='text',
                text=[f"{p:.1f}m" for p in periods[significant_mask]],
                textfont=dict(color='red', size=10, weight='bold'),
                showlegend=False
            ))

        # Add significance threshold line
        fig.add_trace(go.Scatter(
            x=[periods.min(), periods.max()],
            y=[scaled_threshold, scaled_threshold],
            mode='lines',
            name='Umbral Significancia (95%)',
            line=dict(color='purple', width=2, dash='dot'),
            showlegend=True
        ))

        # Add vertical reference lines for Trimestral, Semestral, Anual
        v_lines = [3, 6, 12]
        v_line_names = ['Trimestral (3m)', 'Semestral (6m)', 'Anual (12m)']
        for val, name in zip(v_lines, v_line_names):
            fig.add_vline(
                x=val, line_width=1, line_dash="dash", line_color="blue",
            )
            fig.add_annotation(
                x=val,
                y=max(magnitude) * 0.85,
                text=name,
                showarrow=False,
                xshift=10,
                font=dict(color='blue', size=9)
            )

        # Add dummy traces for legend (legendonly mode)
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(color='red', size=8),
            name='Componente Significativo',
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(color='grey', size=5),
            name='Componente no Significativo',
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='lines',
            line=dict(color='blue', dash='dash'),
            name='Referencias',
            showlegend=True
        ))


        # Update layout
        fig.update_layout(
            title={
                'text': f'Análisis de Fourier - Periodograma: {selected_source}',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title='Período (meses)',
            yaxis_title='Magnitud',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,  # Moved up 20 lines from -0.5
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                type='log',
                range=[np.log10(max(1, periods.min())), np.log10(periods.max())],
                tickformat=".0f"
            ),
            yaxis=dict(
                autorange=True
            )
        )
        
        return fig

    except Exception as e:
        return go.Figure()

# Note: Time range filtering buttons are displayed but their callbacks are disabled
# to avoid Dash callback reference errors. The full date range is used by default.

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8050
    )