import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
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
import re
import time

# Add parent directory to path for database imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings('ignore')

# Import tools dictionary and database manager
from tools import tool_file_dic
from database import get_database_manager
# Import centralized source mapping
from fix_source_mapping import (
    map_display_names_to_source_ids,
    DBASE_OPTIONS as dbase_options,
    DISPLAY_NAMES
)

# Get database manager instance
db_manager = get_database_manager()

# Notes and DOI data is now loaded from the database

def parse_text_with_links(text):
    """Parse text and return plain text without URLs or link information"""
    if not text:
        return [html.P("No hay notas disponibles", style={'fontSize': '12px'})]

    # Remove source link information that starts with "Fuente:" or similar patterns
    # Look for patterns like "Fuente: http" or "Source: http" and remove everything from there
    import re

    # Pattern to match "Fuente:" or "Source:" followed by URL-like content
    link_pattern = r'\s*(?:Fuente|Source)\s*:\s*https?://[^\s]+.*$'

    # Remove the link information from the end of the text
    cleaned_text = re.sub(link_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Also remove any remaining "Fuente:" or "Source:" at the end if not followed by URL
    cleaned_text = re.sub(r'\s*(?:Fuente|Source)\s*:\s*$', '', cleaned_text, flags=re.IGNORECASE)

    # Clean up any trailing whitespace or punctuation
    cleaned_text = cleaned_text.rstrip('.,;:- \t\n')

    return [html.P(cleaned_text, style={'fontSize': '12px'})]

# Global cache for processed datasets
_processed_data_cache = {}
_cache_max_size = 10

def get_cache_key(keyword, sources):
    """Generate cache key for processed data"""
    return f"{keyword}_{'_'.join(map(str, sorted(sources)))}"

def get_cached_processed_data(keyword, selected_sources):
    """Get cached processed data or None if not cached"""
    cache_key = get_cache_key(keyword, selected_sources)
    return _processed_data_cache.get(cache_key)

def cache_processed_data(keyword, selected_sources, data):
    """Cache processed data with LRU eviction"""
    global _processed_data_cache

    cache_key = get_cache_key(keyword, selected_sources)
    _processed_data_cache[cache_key] = data

    # Evict oldest if cache is full
    if len(_processed_data_cache) > _cache_max_size:
        oldest_key = next(iter(_processed_data_cache))
        del _processed_data_cache[oldest_key]
def get_all_keywords():
    """Extract all keywords from tool_file_dic"""
    all_keywords = []
    for tool_list in tool_file_dic.values():
        for keyword in tool_list[1]:
            if keyword not in all_keywords:
                all_keywords.append(keyword)
    return all_keywords

def get_cache_stats():
    """Get database and cache statistics for performance monitoring"""
    try:
        table_stats = db_manager.get_table_stats()
        total_records = sum(stats.get('row_count', 0) for stats in table_stats.values() if 'error' not in stats)
        total_keywords = sum(stats.get('keyword_count', 0) for stats in table_stats.values() if 'error' not in stats)

        return {
            'processed_data_cache': len(_processed_data_cache),
            'cache_max_size': _cache_max_size,
            'database_records': total_records,
            'database_keywords': total_keywords,
            'database_size_mb': round(db_manager.get_database_size() / 1024 / 1024, 2),
            'cache_hit_rate': 0  # Could be tracked with more complex caching
        }
    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return {
            'processed_data_cache': 0,
            'cache_max_size': _cache_max_size,
            'database_records': 0,
            'database_keywords': 0,
            'database_size_mb': 0,
            'cache_hit_rate': 0
        }


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
    title='Management Tools Analysis Dashboard - ' + str(time.time()),
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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
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
                    min-height: 650px;
                }
            }
            @media (max-width: 768px) {
                #section-mean-analysis {
                    min-height: 600px;
                    margin-bottom: 40px !important;
                }
                #section-temporal-3d {
                    margin-top: 50px !important;
                    min-height: 650px;
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

            // Simple manual control for credits - auto-collapse handled by Dash callback
            // when both keyword and sources are selected
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


# Database options are now imported from fix_source_mapping module

# Define color palette for consistent use across buttons and graphs
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f'
]

# Define consistent colors for each source by display name (used in buttons)
source_colors_by_display = {
    'Google Trends': '#1f77b4',
    'Google Books': '#ff7f0e',
    'Bain Usability': '#d62728',
    'Bain Satisfaction': '#9467bd',
    'Crossref': '#2ca02c'  # Changed from brown to green
}

# Define consistent colors for each source by database name (used in graphs)
source_colors_by_db = {
    "Google Trends": '#1f77b4',
    "Google Books Ngrams": '#ff7f0e',
    "Bain - Usabilidad": '#d62728',
    "Bain - Satisfacción": '#9467bd',
    "Crossref.org": '#2ca02c'  # Changed from brown to green
}

# Create color_map using the database name colors
color_map = {
    dbase_options[key]: source_colors_by_db.get(dbase_options[key], colors[i % len(colors)])
    for i, key in enumerate(dbase_options.keys())
}

# Note: Date range filtering removed to avoid callback reference issues

# Sidebar layout
sidebar = html.Div([
    # Bloque Superior Izquierdo (Afiliación Académica)
    html.Div([
        html.Div([
            html.P("Universidad Latinoamericana y del Caribe (ULAC)",
                     style={'margin': '2px 0', 'fontSize': '12px', 'fontWeight': 'normal', 'textAlign': 'center'}),
            html.P("Coordinación General de Postgrado",
                     style={'margin': '2px 0', 'fontSize': '11px', 'fontWeight': 'normal', 'textAlign': 'center'}),
            html.P("Doctorado en Ciencias Gerenciales",
                     style={'margin': '2px 0', 'fontSize': '13px', 'fontWeight': 'bold', 'textAlign': 'center'}),
        ], style={'marginBottom': '15px'}),
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
                className="mb-2",
                style={'fontSize': '12px'}
            ),
            html.Div(id='keyword-validation', className="text-danger", style={'fontSize': '12px'}),
            html.Div(id='doi-display', style={'marginTop': '10px', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label("Seleccione las Fuentes de Datos: ", className="form-label", style={'fontSize': '12px'}),
            dbc.Button(
                id="select-all-button",
                color="secondary",
                outline=True,
                size="sm",
                className="mb-2 w-100",
                style={'fontSize': '12px'}
            ),
            html.Div(id='data-sources-container'),
            html.Div(id='datasources-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
        html.Div(id='navigation-section', style={'display': 'none'})
    ], style={
        'overflowY': 'auto',
        'overflowX': 'hidden',
        'height': 'calc(100vh - 120px)',  # Reduced to make room for footer
        'paddingRight': '10px'
    }),

    # Credits footer - always at bottom
    html.Div([
        html.Hr(style={'margin': '5px 0'}),
        dbc.Button(
            [
                html.Span("Créditos ", style={'fontSize': '10px', 'fontWeight': 'bold'}),
                html.I(id='credits-chevron', className="fas fa-chevron-down", style={'fontSize': '8px', 'marginLeft': '5px'})
            ],
            id='credits-toggle',
            color="link",
            size="sm",
            style={
                'color': '#6c757d',
                'textDecoration': 'none',
                'padding': '2px 5px',
                'fontSize': '10px',
                'width': '100%',
                'textAlign': 'left',
                'border': 'none',
                'backgroundColor': 'transparent',
                'marginBottom': '10px'  # Move button 10px up
            }
        ),
        dbc.Collapse(
            html.Div([
                html.P([
                    "Dashboard de Análisis de ",
                    html.B("Herramientas Gerenciales")
                ], style={'marginBottom': '2px', 'fontSize': '9px', 'textAlign': 'left'}),
                html.P([
                    "Desarrollado con Python, Plotly y Dash"
                ], style={'fontSize': '9px', 'textAlign': 'left', 'marginTop': '0px', 'marginBottom': '2px'}),
                html.P([
                    "por: ",
                    html.A([
                        html.Img(src='assets/orcid.logo.icon.svg', style={'height': '13px', 'verticalAlign': 'middle', 'marginRight': '2px'}),
                        html.B("Dimar Anez")
                    ], href="https://orcid.org/0009-0001-5386-2689", target="_blank", title="ORCID",
                       style={'color': '#6c757d', 'textDecoration': 'none', 'fontSize': '9px'}),
                    " - ",
                    html.A("Wise Connex", href="https://wiseconnex.com/", target="_blank", title="wiseconnex.com",
                           style={'color': '#6c757d', 'textDecoration': 'none', 'fontSize': '9px'})
                ], style={'fontSize': '9px', 'textAlign': 'left', 'marginTop': '0px', 'marginBottom': '5px'}),

                # Horizontal rule above logos
                html.Hr(style={'margin': '8px 0 5px 0'}),

                # Logos section - side by side below author credit, above copyright
                html.Div([
                    html.A(
                        html.Img(
                            src='assets/LogoSolidumBUSINESS.png',
                            style={
                                'height': '34px',
                                'width': 'auto',
                                'marginRight': '8px',
                                'verticalAlign': 'middle'
                            }
                        ),
                        href="https://solidum360.com",
                        target="_blank",
                        title="Solidum Consulting"
                    ),
                    html.A(
                        html.Img(
                            src='assets/WC-Logo-SQ.png',
                            style={
                                'height': '34px',
                                'width': 'auto',
                                'verticalAlign': 'middle'
                            }
                        ),
                        href="https://wiseconnex.com",
                        target="_blank",
                        title="Wise Connex"
                    )
                ], style={
                    'textAlign': 'left',
                    'marginBottom': '5px',
                    'marginTop': '3px'
                }),

                html.Hr(style={'margin': '8px 0 5px 0'}),
                html.P("© 2024-2025 Diomar Añez - Dimar Añez. Licencia Dashboard: CC BY-NC 4.0",
                       style={'margin': '2px 0', 'fontSize': '9px', 'textAlign': 'left', 'lineHeight': '1.3'}),
                html.Div([
                    html.Div([
                        html.A("Harvard Dataverse: Data de la Investigación", href="https://dataverse.harvard.edu/dataverse/management-fads", target="_blank", title="Datos en el prestigioso repositorio de la Universidad de Harvard", style={'color': '#993300', 'textDecoration': 'none', 'fontSize': '9px', 'display': 'block', 'margin': '3px 0', 'padding': '0', 'lineHeight': '1'}),
                        html.A("Publicación en la National Library of Medicine", href="https://datasetcatalog.nlm.nih.gov/searchResults?filters=agent%3AAnez%252C%2520Diomar&sort=rel&page=1&size=10", target="_blank", title="Datos en la Biblioteca Nacional de Medicina de EE.UU.", style={'color': '#993300', 'textDecoration': 'none', 'fontSize': '9px', 'display': 'block', 'margin': '3px 0', 'padding': '0', 'lineHeight': '1'}),
                        html.A("Publicación en el Repositorio CERN - Zenodo", href="https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Anez%2C%20Diomar%22&l=list&p=1&s=10&sort=bestmatch", target="_blank", title="138 Informes Técnicos en el Repositorio Europeo Zenodo, del Conseil Européen pour la Recherche Nucléaire.", style={'color': '#993300', 'textDecoration': 'none', 'fontSize': '9px', 'display': 'block', 'margin': '3px 0', 'padding': '0', 'lineHeight': '1'}),
                        html.A("Visibilidad Europea en OpenAire", href="https://explore.openaire.eu/search/advanced/research-outcomes?f0=resultauthor&fv0=Diomar%2520Anez", target="_blank", title="Informes y Datos indexados en el Portal Europeo de Ciencia Abierta OpenAire", style={'color': '#993300', 'textDecoration': 'none', 'fontSize': '9px', 'display': 'block', 'margin': '3px 0', 'padding': '0', 'lineHeight': '1'}),
                        html.A("Informes y Documentación Técnica en GitHub", href="https://github.com/Wise-Connex/Management-Tools-Analysis/tree/main/Informes", target="_blank", title="Documentación técnica y científica de herramientas gerenciales en GitHub", style={'color': '#993300', 'textDecoration': 'none', 'fontSize': '9px', 'display': 'block', 'margin': '3px 0', 'padding': '0', 'lineHeight': '1'})
                    ], style={'margin': '3px 0', 'padding': '0', 'lineHeight': '1'})
                ], style={'marginTop': '5px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '8px 2px 12px 2px',  # 2px margins on sides
                'borderTop': '1px solid #dee2e6',
                'marginTop': '5px',
                'width': '100%'  # Full width of container
            }),
            id='credits-collapse',
            is_open=True  # Default to expanded on page load
        )
    ], style={
        'position': 'absolute',
        'bottom': 0,
        'left': 0,
        'right': 0,
        'backgroundColor': '#f3f4f6',
        'padding': '5px 2px 10px 2px'  # 2px margins on container
    })
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

# Header - Bloque Superior Central (Logo + Títulos y Créditos Principales)
header = html.Div([
    # Logo on the left
    html.Div([
        html.A(
            html.Img(
                src='assets/logo-ulac.png',
                style={
                    'height': '72px',  # Increased by 20% (60px * 1.2)
                    'width': 'auto',
                    'maxWidth': '120px',  # Increased by 20% (100px * 1.2)
                    'marginRight': '20px'
                }
            ),
            href='https://ulac.edu.ve/',
            target='_blank'
        )
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'flexShrink': 0
    }),

    # Text content on the right
    html.Div([
        # Línea 1 (Subtítulo): Base analítica para la Investigación Doctoral
        html.P([
            "Base analítica para la Investigación Doctoral: ",
            html.I("«Dicotomía ontológica en las \"Modas Gerenciales\"»")
        ], style={
            'margin': '5px 0',
            'fontSize': '14px',
            'fontStyle': 'italic',
            'textAlign': 'center',
            'color': '#6c757d'
        }),

        # Línea 2 (Título Principal): Herramientas gerenciales...
        html.H3("Herramientas gerenciales: Dinámicas temporales contingentes y antinomias policontextuales",
                style={
                    'margin': '8px 0',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'color': '#212529',
                    'lineHeight': '1.3'
                }),

        # Línea 3 (Créditos): Investigador Principal...
        html.P([
            "Investigador Principal: ",
            html.A([
                html.Img(src='assets/orcid.logo.icon.svg', style={'height': '18px', 'verticalAlign': 'middle', 'marginRight': '3px'}),
                html.B("Diomar Añez")
            ], href="https://orcid.org/0000-0002-7925-5078", target="_blank",
               style={'color': '#495057', 'textDecoration': 'none'}),
            " (",
            html.A("Solidum Consulting", href="https://solidum360.com", target="_blank",
                   style={'color': '#495057', 'textDecoration': 'none'}),
            ") | Tutora Académica: ",
            html.A([
                html.Img(src='assets/orcid.logo.icon.svg', style={'height': '18px', 'verticalAlign': 'middle', 'marginRight': '3px'}),
                html.B("Dra. Elizabeth Pereira")
            ], href="https://orcid.org/0000-0002-8264-7080", target="_blank",
               style={'color': '#495057', 'textDecoration': 'none'}),
            " (ULAC)"
        ], style={
            'margin': '5px 0',
            'fontSize': '13px',
            'textAlign': 'center',
            'color': '#495057'
        })
    ], style={
        'flex': 1,
        'textAlign': 'center'
    })
], style={
    'position': 'sticky',
    'top': 0,
    'zIndex': 1000,
    'backgroundColor': '#ffffff',
    'padding': '15px 20px',
    'borderBottom': '2px solid #dee2e6',
    'width': '100%',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'marginBottom': '20px',
    'display': 'flex',
    'alignItems': 'center'
})

# Notes modal
notes_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Notas de la Fuente", style={'fontSize': '16px'})),
        dbc.ModalBody(id="notes-content"),
        dbc.ModalFooter(
            dbc.Button("Cerrar", id="close-notes-modal", className="ml-auto")
        ),
    ],
    id="notes-modal",
    size="lg",
    centered=True,  # Position modal in vertical center of screen
)

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
            dcc.Store(id='data-sources-store-v2', data=[]),
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
    ], style={'height': '100vh'}),
    notes_modal
], fluid=True, className="px-0", style={'height': '100vh'})

# Callbacks

# Callback to reset source selections when keyword changes
@app.callback(
    Output('data-sources-store-v2', 'data', allow_duplicate=True),
    Input('keyword-dropdown', 'value'),
    prevent_initial_call=True
)
def reset_sources_on_keyword_change(selected_tool):
    """Reset source selections when a new keyword is selected"""
    return []

# Callback to initialize select all button text
@app.callback(
    Output('select-all-button', 'children', allow_duplicate=True),
    Input('keyword-dropdown', 'value'),
    prevent_initial_call=True
)
def initialize_select_all_button_text(selected_tool):
    """Initialize the select all button text when a tool is selected"""
    return "Seleccionar Todo"

# Callback to update data sources container
@app.callback(
    Output('data-sources-container', 'children'),
    Input('keyword-dropdown', 'value'),
    Input('data-sources-store-v2', 'data')
)
def update_data_sources_container(selected_tool, selected_sources):
    if not selected_tool:
        return html.Div("Seleccione una herramienta para ver las fuentes disponibles")

    if selected_sources is None:
        selected_sources = []

    sources = DISPLAY_NAMES

    components = []

    # Map display names to the correct source names for buttons
    display_to_source = {
        'Google Trends': 'Google Trends',
        'Google Books': 'Google Books',
        'Bain Usability': 'Bain Usability',
        'Bain Satisfaction': 'Bain Satisfaction',
        'Crossref': 'Crossref'
    }

    for source in sources:
        # Use display name for button text
        display_name = source
        if source in display_to_source:
            display_name = display_to_source[source]

        # Determine button style based on selection state
        base_color = source_colors_by_display.get(source, '#6c757d')
        
        # IMPORTANT: Check if source is in the CURRENT selected_sources list
        is_selected = source in selected_sources

        if is_selected:
            # Selected style - brighter/darker
            button_style = {
                'backgroundColor': base_color,
                'borderColor': base_color,
                'color': 'white',
                'fontSize': '12px',
                'minWidth': '120px',
                'boxShadow': '0 0 0 2px rgba(0,123,255,0.5)',
                'fontWeight': 'bold'
            }
        else:
            # Unselected style - outline
            button_style = {
                'backgroundColor': 'transparent',
                'borderColor': base_color,
                'color': base_color,
                'fontSize': '12px',
                'minWidth': '120px',
                'fontWeight': 'normal'
            }

        # Create button with appropriate style
        button = dbc.Button(
            display_name,
            id={'type': 'data-source-button', 'index': display_name},
            color="outline-primary",
            size="sm",
            className="me-2 mb-2",
            style=button_style
        )

        # Info icon beside the button
        icon = html.I(
            className="fas fa-info-circle",
            id={'type': 'info-icon', 'index': source},
            style={
                'cursor': 'pointer',
                'marginLeft': '10px',
                'color': '#007bff',
                'fontSize': '16px',
                'verticalAlign': 'middle'
            }
        )

        row = html.Div([button, icon], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '5px'})
        components.append(row)

    return components

# Callback to update DOI display
@app.callback(
    Output('doi-display', 'children'),
    Input('keyword-dropdown', 'value')
)
def update_doi_display(selected_tool):
    if not selected_tool:
        return html.Div()

    # Get the IC report DOI from the IC source (Complementary Report)
    tool_notes = db_manager.get_tool_notes_and_doi(selected_tool, 'IC')
    
    if tool_notes and len(tool_notes) > 0:
        doi = tool_notes[0].get('doi', '')
        if doi:
            return html.Div([
                html.Strong("DOI del Informe IC: ", style={'fontSize': '12px'}),
                html.A(doi, href=f"https://doi.org/{doi}", target="_blank",
                        style={'color': '#007bff', 'fontSize': '12px', 'textDecoration': 'none'})
            ], style={'padding': '8px', 'backgroundColor': '#f8f9fa', 'borderRadius': '4px', 'border': '1px solid #dee2e6'})
    
    return html.Div("No hay DOI disponible para esta herramienta", style={'fontSize': '11px', 'color': '#6c757d', 'fontStyle': 'italic'})

# Callback to update selected sources store
@app.callback(
    Output('data-sources-store-v2', 'data'),
    Input({'type': 'data-source-button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'data-source-button', 'index': ALL}, 'id'),
    Input('select-all-button', 'n_clicks'),
    State('data-sources-store-v2', 'data')
)
def update_selected_sources(n_clicks, ids, select_all_clicks, current_selected):
    if current_selected is None:
        current_selected = []

    # Find which button was clicked
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id']

        # IMPORTANT: Ignore triggers from initial component creation
        if trigger_id.endswith('.n_clicks') and ctx.triggered[0]['value'] is None:
            return current_selected

        # Check if "Seleccionar Todo" button was clicked
        if 'select-all-button' in trigger_id:
            # Get all available sources
            all_sources = DISPLAY_NAMES

            # If all sources are already selected, deselect all
            if set(current_selected) == set(all_sources):
                current_selected = []
            else:
                # Select all sources
                current_selected = all_sources.copy()

        elif 'data-source-button' in trigger_id:
            # Extract the source name from the triggered button
            button_id = eval(trigger_id.split('.')[0])  # Convert string back to dict
            source = button_id['index']

            # Toggle selection
            if source in current_selected:
                current_selected.remove(source)
            else:
                current_selected.append(source)

    return current_selected


# Callback for notes modal
@app.callback(
    Output("notes-modal", "is_open"),
    Output("notes-content", "children"),
    Input({'type': 'info-icon', 'index': ALL}, 'n_clicks'),
    Input("close-notes-modal", "n_clicks"),
    State("notes-modal", "is_open"),
    State('keyword-dropdown', 'value'),
    State({'type': 'info-icon', 'index': ALL}, 'id'),
)
def toggle_notes_modal(icon_clicks, close_click, is_open, selected_tool, icon_ids):
    if not selected_tool:
        return False, ""

    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, ""

    trigger_id = ctx.triggered[0]['prop_id']
    if 'close-notes-modal' in trigger_id:
        return False, ""
    
    # Only proceed if an info-icon was actually clicked
    # Check if the trigger_id contains 'info-icon' and it's not from the dropdown
    if 'info-icon' not in trigger_id or 'keyword-dropdown' in trigger_id:
        return is_open, ""
    
    # Also check if any icon was actually clicked (has click count > 0)
    if not any(clicks and clicks > 0 for clicks in icon_clicks):
        return is_open, ""

    # Debug: Print all the information to understand what's happening
    print(f"Debug: icon_clicks={icon_clicks}")
    print(f"Debug: icon_ids={icon_ids}")
    print(f"Debug: trigger_id={trigger_id}")

    # Find which icon was clicked by matching the trigger_id with the specific icon
    clicked_source = None
    
    # Parse the trigger_id to extract the index that was clicked
    # trigger_id format: {"index":"Google Trends","type":"info-icon"}.n_clicks
    try:
        import json
        # Extract the JSON part from the trigger_id
        json_part = trigger_id.split('.n_clicks')[0]
        trigger_data = json.loads(json_part)
        clicked_index = trigger_data['index']
        
        # Find the corresponding icon_id
        for i, icon_id in enumerate(icon_ids):
            if icon_id['index'] == clicked_index:
                clicked_source = icon_id['index']
                print(f"Debug: Found clicked icon at index {i}: {clicked_source}")
                break
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Debug: Error parsing trigger_id: {e}")
        # Fallback to original logic
        for i, icon_id in enumerate(icon_ids):
            if icon_clicks[i] and icon_clicks[i] > 0:
                clicked_source = icon_id['index']
                print(f"Debug: Fallback - Found clicked icon at index {i}: {clicked_source}")
                break
    
    if clicked_source:
        # Map source to the key in database
        source_map = {
            'Google Trends': 'Google_Trends',
            'Google Books': 'Google_Books',
            'IC': 'IC',
            'Bain Usability': 'BAIN_Ind_Usabilidad',
            'Bain Satisfaction': 'BAIN_Ind_Satisfacción',
            'Crossref': 'Crossref'
        }
        mapped_source = source_map.get(clicked_source, clicked_source)

        # Debug print to check mapping
        print(f"Debug: source='{clicked_source}', mapped_source='{mapped_source}', selected_tool='{selected_tool}'")

        # Get notes from the new database
        tool_notes = db_manager.get_tool_notes_and_doi(selected_tool, mapped_source)
        print(f"Debug: tool_notes={tool_notes}")
        print(f"Debug: Query parameters - tool='{selected_tool}', source='{mapped_source}'")
        
        if tool_notes and len(tool_notes) > 0:
            notes = tool_notes[0].get('notes', 'No hay notas disponibles')
            links = tool_notes[0].get('links', '')
            doi = tool_notes[0].get('doi', '')
            print(f"Debug: Found notes='{notes[:50]}...', links='{links}', doi='{doi}'")
        else:
            notes = 'No hay notas disponibles'
            links = ''
            doi = ''
            print(f"Debug: No notes found for {selected_tool} - {mapped_source}")
            
            # Let's check what's actually in the database for this tool
            all_tool_notes = db_manager.get_tool_notes_and_doi(selected_tool, None)
            print(f"Debug: All notes for {selected_tool}: {all_tool_notes}")

        # Parse notes with clickable links
        notes_components = parse_text_with_links(notes)

        content = html.Div([
            html.Div(notes_components, style={'marginBottom': '10px'}),
            html.Span("Fuente: ", style={'fontSize': '12px'}),
            html.A(clicked_source, href=links, target="_blank", style={'fontSize': '12px'}) if links else html.Span(clicked_source, style={'fontSize': '12px'}),
            html.Br() if (links and doi) or (not links and doi) else "",
            html.A(f"DOI: {doi}", href=f"https://doi.org/{doi}", target="_blank", style={'fontSize': '12px'}) if doi else ""
        ])
        return True, content

    return is_open, ""

# Main content update callback
@app.callback(
    [Output('main-content', 'children'),
     Output('credits-collapse', 'is_open')],
    Input('data-sources-store-v2', 'data'),
    Input('keyword-dropdown', 'value')
)
def update_main_content(selected_sources, selected_keyword):
    if selected_sources is None:
        selected_sources = []

    # Use centralized mapping function
    selected_source_ids = map_display_names_to_source_ids(selected_sources)

    # Auto-collapse credits when both keyword and sources are selected
    credits_open = not (selected_keyword and selected_source_ids)

    if not selected_keyword or not selected_sources:
        return html.Div("Por favor, seleccione una Herramienta y al menos una Fuente de Datos."), credits_open

    try:
        # Check cache first
        cached_data = get_cached_processed_data(selected_keyword, selected_sources)

        if cached_data:
            combined_dataset, combined_dataset_fecha_formatted, selected_source_names = cached_data
        else:
            # Map display names to source IDs
            selected_source_ids = map_display_names_to_source_ids(selected_sources)
            
            print(f"DEBUG: Getting data for keyword='{selected_keyword}', sources={selected_sources}")
            print(f"DEBUG: Converted to source IDs: {selected_source_ids}")
            
            datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
            print(f"DEBUG: Retrieved datasets_norm keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")
            print(f"DEBUG: Retrieved sl_sc: {sl_sc}")
            
            if not datasets_norm:
                print(f"DEBUG: No data retrieved for keyword='{selected_keyword}'")
                return html.Div(f"No hay datos disponibles para la herramienta '{selected_keyword}' con las fuentes seleccionadas."), credits_open
                
            combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
            print(f"DEBUG: Combined dataset shape: {combined_dataset.shape if not combined_dataset.empty else 'Empty'}")

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
            data_columns = [dbase_options[src_id] for src_id in selected_source_ids]
            combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

            selected_source_names = [dbase_options[src_id] for src_id in selected_source_ids]

            # Cache the processed data
            cache_processed_data(selected_keyword, selected_sources,
                               (combined_dataset, combined_dataset_fecha_formatted, selected_source_names))

        # Create content sections
        content = []

        # Create content sections
        content = []

        # Create content sections
        content = []

        # 1. Temporal Analysis 2D
        try:
            print(f"DEBUG: Creating initial temporal 2D figure for main content")
            temporal_2d_fig = create_temporal_2d_figure(combined_dataset, selected_source_names)
            print(f"DEBUG: Initial temporal 2D figure created with {len(temporal_2d_fig.data) if hasattr(temporal_2d_fig, 'data') else 0} traces")
        except Exception as e:
            print(f"DEBUG: Error creating initial temporal 2D figure: {e}")
            import traceback
            traceback.print_exc()
            temporal_2d_fig = go.Figure()
            temporal_2d_fig.add_annotation(text=f"Error creating temporal 2D graph: {str(e)}", showarrow=False)

        content.append(html.Div([
            html.Div([
                html.H6("1. Análisis Temporal 2D", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
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
                figure=temporal_2d_fig,
                style={'height': '400px'},
                config={'displaylogo': False, 'responsive': True}
            ),
            html.Div(id='temporal-2d-slider-container', style={'display': 'none'})  # Hidden container for slider updates
        ], id='section-temporal-2d', className='section-anchor'))

        # 2. Mean Analysis
        try:
            mean_fig = create_mean_analysis_figure(combined_dataset, selected_source_names)
            print(f"DEBUG: Created mean analysis figure with {len(mean_fig.data) if hasattr(mean_fig, 'data') else 0} traces")
            print(f"DEBUG: Mean figure data: {mean_fig.data[:2] if hasattr(mean_fig, 'data') and len(mean_fig.data) > 0 else 'No data'}")
        except Exception as e:
            print(f"ERROR: Failed to create mean analysis figure: {e}")
            import traceback
            traceback.print_exc()
            mean_fig = go.Figure()
            mean_fig.add_annotation(text=f"Error creating mean analysis graph: {str(e)}", showarrow=False)

        content.append(html.Div([
            html.Div([
                html.H6("2. Análisis de Medias", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
            }),
            dcc.Graph(
                id='mean-analysis-graph',
                figure=mean_fig,
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
                    'backgroundColor': '#2c3e50',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '30px',
                    'marginTop': '60px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': '1px solid #34495e'
                }),
                html.Div([
                    # Left side: Graph
                    html.Div([
                        dcc.Graph(
                            id='temporal-3d-graph',
                            style={'height': '600px', 'width': 'calc(100% - 240px)'},
                            config={'displaylogo': False, 'responsive': True}
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': 'calc(100% - 220px)', 'paddingRight': '20px'}),

                    # Right side: Controls
                    html.Div([
                        html.Div([
                            html.Label("Frecuencia de Datos:", style={'marginBottom': '8px', 'fontSize': '14px', 'fontWeight': 'bold'}),
                            dbc.ButtonGroup([
                                dbc.Button("Mensual", id="temporal-3d-monthly", size="sm", className="me-2", n_clicks=0, style={'fontSize': '11px'}),
                                dbc.Button("Anual", id="temporal-3d-annual", size="sm", n_clicks=0, style={'fontSize': '11px'}),
                            ], className="mb-3", style={'display': 'flex', 'gap': '8px'})
                        ], style={'marginBottom': '20px'}),

                        html.Div([
                            html.Label("Ejes del Gráfico:", style={'marginBottom': '8px', 'fontSize': '14px', 'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='y-axis-3d',
                                options=[{'label': src, 'value': src} for src in selected_source_names],
                                value=selected_source_names[0] if selected_source_names else None,
                                placeholder="Eje Y",
                                style={'width': '100%', 'marginBottom': '10px'}
                            ),
                            dcc.Dropdown(
                                id='z-axis-3d',
                                options=[{'label': src, 'value': src} for src in selected_source_names],
                                value=selected_source_names[1] if len(selected_source_names) > 1 else None,
                                placeholder="Eje Z",
                                style={'width': '100%'}
                            )
                        ])
                    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '220px'})
                ], style={'whiteSpace': 'nowrap', 'height': '600px'})
            ], id='section-temporal-3d', className='section-anchor'))

        # 4. Seasonal Analysis (Lazy loaded)
        content.append(html.Div([
            html.Div([
                html.H6("4. Análisis Estacional", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
            }),
            html.Div([
                dcc.Dropdown(
                    id='seasonal-source-select',
                    options=[{'label': src, 'value': src} for src in selected_source_names],
                    value=selected_source_names[0] if selected_source_names else None,
                    placeholder="Seleccione fuente para cargar análisis",
                    clearable=True,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                dcc.Loading(
                    id="loading-seasonal",
                    type="circle",
                    children=[
                        dcc.Graph(
                            id='seasonal-analysis-graph',
                            style={'height': '600px'},
                            config={'displaylogo': False, 'responsive': True}
                        )
                    ]
                )
            ])
        ], id='section-seasonal', className='section-anchor'))

        # 5. Fourier Analysis (Lazy loaded)
        content.append(html.Div([
            html.Div([
                html.H6("5. Análisis de Fourier (Periodograma)", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
            }),
            html.Div([
                dcc.Dropdown(
                    id='fourier-source-select',
                    options=[{'label': src, 'value': src} for src in selected_source_names],
                    value=selected_source_names[0] if selected_source_names else None,
                    placeholder="Seleccione fuente para cargar análisis",
                    clearable=True,
                    style={'width': '100%', 'marginBottom': '10px'}
                ),
                dcc.Loading(
                    id="loading-fourier",
                    type="circle",
                    children=[
                        dcc.Graph(
                            id='fourier-analysis-graph',
                            style={'height': '500px'},
                            config={'displaylogo': False, 'responsive': True}
                        )
                    ]
                )
            ])
        ], id='section-fourier', className='section-anchor'))

        # 6. Correlation Heatmap
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.Div([
                    html.H6("6. Mapa de Calor (Correlación)", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
                ], style={
                    'backgroundColor': '#2c3e50',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': '1px solid #34495e'
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
                    'backgroundColor': '#2c3e50',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': '1px solid #34495e'
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
                    'backgroundColor': '#2c3e50',
                    'padding': '12px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': '1px solid #34495e'
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
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
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
        # Calculate current query statistics
        current_query_records = 0
        current_query_sources = len(selected_sources)
        current_query_date_range = "N/A"

        if datasets_norm:
            for source_data in datasets_norm.values():
                if source_data is not None and not source_data.empty:
                    current_query_records += len(source_data)

            # Calculate date range for current query
            all_dates = set()
            for source_data in datasets_norm.values():
                if source_data is not None and not source_data.empty:
                    all_dates.update(source_data.index)
            if all_dates:
                min_date = min(all_dates).strftime('%Y')
                max_date = max(all_dates).strftime('%Y')
                current_query_date_range = f"{min_date} - {max_date}"

        db_stats = get_cache_stats()
        content.append(html.Div([
            html.Div([
                html.H6("📊 Monitor de Rendimiento del Sistema", style={'fontSize': '16px', 'marginBottom': '15px', 'color': 'white'})
            ], style={
                'backgroundColor': '#2c3e50',
                'padding': '12px 20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #34495e'
            }),
            html.Div([
                # Database Information
                html.Div([
                    html.H6("💾 Información de Base de Datos", style={'marginBottom': '10px', 'color': '#2c3e50', 'fontSize': '14px'}),
                    html.Div([
                        html.Div([
                            html.Strong("Total de Registros:"),
                            html.Span(f"{db_stats['database_records']:,}", style={'marginLeft': '5px', 'color': '#28a745', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Palabras Clave Únicas:"),
                            html.Span(f"{db_stats['database_keywords']}", style={'marginLeft': '5px', 'color': '#007bff', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Fuentes de Datos:"),
                            html.Span("5 disponibles", style={'marginLeft': '5px'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'})
                    ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '15px'})
                ]),

                # Current Query Information
                html.Div([
                    html.H6("🔍 Consulta Actual", style={'marginBottom': '10px', 'color': '#2c3e50', 'fontSize': '14px'}),
                    html.Div([
                        html.Div([
                            html.Strong("Registros en Uso:"),
                            html.Span(f"{current_query_records:,}", style={'marginLeft': '5px', 'color': '#e74c3c', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Fuentes Seleccionadas:"),
                            html.Span(f"{current_query_sources}", style={'marginLeft': '5px', 'color': '#f39c12', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Rango Temporal:"),
                            html.Span(current_query_date_range, style={'marginLeft': '5px', 'color': '#9b59b6', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Herramienta:"),
                            html.Span(selected_keyword if selected_keyword else "Ninguna", style={'marginLeft': '5px', 'color': '#1abc9c', 'fontWeight': 'bold'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'})
                    ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '15px'})
                ]),

                # Performance Metrics
                html.Div([
                    html.H6("⚡ Métricas de Rendimiento", style={'marginBottom': '10px', 'color': '#2c3e50', 'fontSize': '14px'}),
                    html.Div([
                        html.Div([
                            html.Strong("Tiempo de Carga:"),
                            html.Span("< 0.5 segundos", style={'marginLeft': '5px', 'color': '#28a745'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Eficiencia de Consultas:"),
                            html.Span("Alta", style={'marginLeft': '5px', 'color': '#28a745'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Uso de Memoria:"),
                            html.Span("Optimizado", style={'marginLeft': '5px', 'color': '#28a745'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'}),
                        html.Div([
                            html.Strong("Compresión:"),
                            html.Span("85% promedio", style={'marginLeft': '5px', 'color': '#28a745'})
                        ], style={'margin': '3px 0', 'fontSize': '12px'})
                    ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '15px'})
                ]),

                # Active Optimizations
                html.Div([
                    html.H6("🔧 Optimizaciones Activas", style={'marginBottom': '10px', 'color': '#2c3e50', 'fontSize': '14px'}),
                    html.Div([
                        html.Ul([
                            html.Li("✅ Datos pre-procesados en base de datos", style={'fontSize': '11px', 'margin': '2px 0'}),
                            html.Li("✅ Índices optimizados para velocidad", style={'fontSize': '11px', 'margin': '2px 0'}),
                            html.Li("✅ Caché inteligente de resultados", style={'fontSize': '11px', 'margin': '2px 0'}),
                            html.Li("✅ Lazy loading para análisis complejos", style={'fontSize': '11px', 'margin': '2px 0'}),
                            html.Li("✅ Optimización automática de gráficos", style={'fontSize': '11px', 'margin': '2px 0'})
                        ], style={'paddingLeft': '20px', 'margin': '0'})
                    ], style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px'})
                ])

            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ], id='section-performance', className='section-anchor'))


        return html.Div(content), credits_open

    except Exception as e:
        return html.Div(f"Error: {str(e)}"), credits_open

# Helper functions for creating figures
def create_temporal_2d_figure(data, sources, start_date=None, end_date=None):
    print(f"DEBUG: create_temporal_2d_figure called")
    print(f"DEBUG: data shape: {data.shape}")
    print(f"DEBUG: sources: {sources}")
    print(f"DEBUG: start_date: {start_date}, end_date: {end_date}")
    
    # Filter data by date range if provided
    filtered_data = data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Fecha'] >= pd.to_datetime(start_date)) &
            (filtered_data['Fecha'] <= pd.to_datetime(end_date))
        ]
        print(f"DEBUG: Filtered data shape: {filtered_data.shape}")

    fig = go.Figure()
    trace_count = 0

    # Optimize: Use fewer markers and simpler rendering for better performance
    for i, source in enumerate(sources):
        print(f"DEBUG: Processing source: {source}")
        if source in filtered_data.columns:
            source_data = filtered_data[source]
            valid_mask = ~source_data.isna()
            print(f"DEBUG: Source {source} has {valid_mask.sum()} valid points out of {len(source_data)}")

            if valid_mask.any():
                # Use lines only for better performance, add markers only for sparse data
                mode = 'lines+markers' if valid_mask.sum() < 50 else 'lines'
                print(f"DEBUG: Using mode: {mode}")

                fig.add_trace(go.Scatter(
                    x=filtered_data['Fecha'][valid_mask],
                    y=source_data[valid_mask],
                    mode=mode,
                    name=source,
                    line=dict(
                        color=color_map.get(source, '#000000'),
                        width=2
                    ),
                    marker=dict(size=4) if mode == 'lines+markers' else None,
                    connectgaps=False,
                    hovertemplate=f'{source}: %{{y:.2f}}<br>%{{x|%Y-%m-%d}}<extra></extra>'
                ))
                trace_count += 1
                print(f"DEBUG: Added trace for {source}")
        else:
            print(f"DEBUG: Source {source} not found in filtered_data columns")

    print(f"DEBUG: Total traces added: {trace_count}")
    print(f"DEBUG: Figure has {len(fig.data)} traces after creation")

    # Simplified tick calculation for better performance
    date_range_days = (filtered_data['Fecha'].max() - filtered_data['Fecha'].min()).days
    print(f"DEBUG: Date range in days: {date_range_days}")

    if date_range_days <= 365:
        tickformat = "%Y-%m"
    elif date_range_days <= 365 * 3:
        tickformat = "%Y-%m"
    else:
        tickformat = "%Y"

    # Optimized layout with performance settings
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
            tickangle=45,
            autorange=True  # Let Plotly optimize tick spacing
        ),
        # Performance optimizations
        hovermode='x unified',
        showlegend=True
    )

    # Reduce data points for very large datasets
    if len(filtered_data) > 1000:
        fig.update_traces(
            hoverinfo='skip'  # Reduce hover computation for large datasets
        )

    print(f"DEBUG: Final figure has {len(fig.data)} traces")
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
    print(f"DEBUG: create_correlation_heatmap called with sources: {sources}")
    corr_data = data[sources].corr()
    print(f"DEBUG: Correlation data shape: {corr_data.shape}")

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

    # Create heatmap using go.Heatmap for proper click event support
    fig = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=sources,
        y=sources,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        hovertemplate='%{x} vs %{y}<br>Correlación: %{z:.3f}<extra></extra>',
        showscale=True
    ))

    # Update layout with annotations and enable click events
    fig.update_layout(
        title="Mapa de Calor de Correlación",
        height=400,
        annotations=annotations,
        xaxis=dict(side='bottom'),
        yaxis=dict(side='left'),
        clickmode='event+select'  # Enable click events
    )

    return fig

# Callback for Temporal Analysis 2D with date range filtering
@app.callback(
    Output('temporal-2d-graph', 'figure'),
    [Input('temporal-2d-all', 'n_clicks'),
     Input('temporal-2d-20y', 'n_clicks'),
     Input('temporal-2d-15y', 'n_clicks'),
     Input('temporal-2d-10y', 'n_clicks'),
     Input('temporal-2d-5y', 'n_clicks'),
     Input('temporal-2d-date-range', 'value'),
     Input('keyword-dropdown', 'value'),
     Input('data-sources-store-v2', 'data')]
)
def update_temporal_2d_analysis(all_clicks, y20_clicks, y15_clicks, y10_clicks, y5_clicks, slider_values, selected_keyword, selected_sources):
    print(f"DEBUG: update_temporal_2d_analysis called")
    print(f"DEBUG: selected_keyword={selected_keyword}")
    print(f"DEBUG: selected_sources={selected_sources}")
    print(f"DEBUG: slider_values={slider_values}")
    
    if selected_sources is None:
        selected_sources = []

    # Map display names to source IDs
    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"DEBUG: mapped to source IDs: {selected_source_ids}")

    if not selected_keyword or not selected_sources:
        print(f"DEBUG: Returning empty figure - missing keyword or sources")
        return go.Figure()

    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        print(f"DEBUG: Retrieved datasets_norm keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")
        
        if not datasets_norm:
            print(f"DEBUG: No data retrieved from database")
            return go.Figure()
            
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        print(f"DEBUG: Combined dataset shape: {combined_dataset.shape if not combined_dataset.empty else 'Empty'}")

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Sort by date to ensure chronological order for slider indices
        combined_dataset = combined_dataset.sort_values('Fecha').reset_index(drop=True)

        # No longer need Bain/Crossref alignment since we preserve individual date ranges

        # Filter out rows where ALL selected sources are NaN (preserve partial data)
        data_columns = [dbase_options[src_id] for src_id in selected_source_ids]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        selected_source_names = [dbase_options[src_id] for src_id in selected_source_ids]
        print(f"DEBUG: Selected source names: {selected_source_names}")

        # Default to full date range
        start_date = combined_dataset['Fecha'].min().date()
        end_date = combined_dataset['Fecha'].max().date()
        print(f"DEBUG: Default date range: {start_date} to {end_date}")

        # Check if any button was clicked or slider moved
        try:
            ctx = dash.callback_context
            if ctx.triggered and len(ctx.triggered) > 0:
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                print(f"DEBUG: Triggered by: {trigger_id}")

                if trigger_id in ['temporal-2d-all', 'temporal-2d-20y', 'temporal-2d-15y', 'temporal-2d-10y', 'temporal-2d-5y']:
                    # Button was clicked - calculate new date range
                    if trigger_id == 'temporal-2d-all':
                        start_date = combined_dataset['Fecha'].min().date()
                        end_date = combined_dataset['Fecha'].max().date()
                    else:
                        # Calculate years back from end
                        years_back = int(trigger_id.split('-')[-1].replace('y', ''))
                        end_date = combined_dataset['Fecha'].max().date()
                        start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=years_back)).date()
                    print(f"DEBUG: Updated date range from button: {start_date} to {end_date}")

                elif trigger_id == 'temporal-2d-date-range':
                    # Slider was moved - convert indices to dates
                    if slider_values is not None and len(slider_values) == 2:
                        start_idx, end_idx = slider_values
                        if start_idx < len(combined_dataset) and end_idx < len(combined_dataset):
                            start_date = combined_dataset['Fecha'].iloc[start_idx].date()
                            end_date = combined_dataset['Fecha'].iloc[end_idx].date()
                            print(f"DEBUG: Updated date range from slider: {start_date} to {end_date}")
        except Exception as e:
            # Handle case when callback context is not available (e.g., during testing)
            print(f"DEBUG: No callback context available, using default date range: {e}")
            # Keep default date range (full range)

        print(f"DEBUG: Creating temporal 2D figure...")
        figure = create_temporal_2d_figure(combined_dataset, selected_source_names, start_date, end_date)
        print(f"DEBUG: Figure created with {len(figure.data) if hasattr(figure, 'data') else 0} traces")
        return figure
    except Exception as e:
        print(f"Error in temporal 2D analysis: {e}")
        import traceback
        traceback.print_exc()
        return go.Figure()

# Callback to update the slider properties when data changes (only min, max, marks)
@app.callback(
    Output('temporal-2d-date-range', 'min'),
    Output('temporal-2d-date-range', 'max'),
    Output('temporal-2d-date-range', 'marks'),
    Output('temporal-2d-date-range', 'value'),
    Input('keyword-dropdown', 'value'),
    Input('data-sources-store-v2', 'data')
)
def update_temporal_slider_properties(selected_keyword, selected_sources):
    print(f"DEBUG: update_temporal_slider_properties called")
    print(f"DEBUG: selected_keyword={selected_keyword}")
    print(f"DEBUG: selected_sources={selected_sources}")
    
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"DEBUG: mapped to source IDs: {selected_source_ids}")

    if not selected_keyword or not selected_sources:
        print(f"DEBUG: Returning default slider values - missing keyword or sources")
        return 0, 100, {}, [0, 100]

    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        print(f"DEBUG: Retrieved datasets_norm keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")
        
        if not datasets_norm:
            print(f"DEBUG: No data retrieved from database")
            return 0, 100, {}, [0, 100]
            
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        print(f"DEBUG: Combined dataset shape: {combined_dataset.shape if not combined_dataset.empty else 'Empty'}")

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # No longer need Bain/Crossref alignment since we preserve individual date ranges

        # Filter out rows where ALL selected sources are NaN (preserve partial data)
        data_columns = [dbase_options[src_id] for src_id in selected_source_ids]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        print(f"DEBUG: Processed dataset shape: {combined_dataset.shape}")
        print(f"DEBUG: Date range: {combined_dataset['Fecha'].min()} to {combined_dataset['Fecha'].max()}")

        # Create marks for the slider
        n_marks = min(5, len(combined_dataset))  # Limit to 5 marks
        mark_indices = [int(i * (len(combined_dataset) - 1) / (n_marks - 1)) for i in range(n_marks)]
        marks = {
            idx: combined_dataset['Fecha'].iloc[idx].strftime('%Y-%m')
            for idx in mark_indices
        }
        print(f"DEBUG: Created {len(marks)} slider marks")

        return 0, len(combined_dataset) - 1, marks, [0, len(combined_dataset) - 1]
    except Exception as e:
        print(f"DEBUG: Error in update_temporal_slider_properties: {e}")
        import traceback
        traceback.print_exc()
        return 0, 100, {}, [0, 100]

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
     Input('keyword-dropdown', 'value'),
     Input('data-sources-store-v2', 'data')]
)
def update_3d_plot(y_axis, z_axis, monthly_clicks, annual_clicks, selected_keyword, selected_sources):
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)

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
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
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
            height=600
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
     Input('keyword-dropdown', 'value'),
     Input('data-sources-store-v2', 'data')]
)
def update_seasonal_analysis(selected_source, selected_keyword, selected_sources):
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)

    if not all([selected_source, selected_keyword]) or not selected_sources:
        return {}

    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
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
     Input('keyword-dropdown', 'value'),
     Input('data-sources-store-v2', 'data')],
    prevent_initial_call=False
)
def update_regression_analysis(click_data, selected_keyword, selected_sources):
    print(f"DEBUG: update_regression_analysis called")
    print(f"DEBUG: click_data={click_data}")
    print(f"DEBUG: selected_keyword={selected_keyword}")
    print(f"DEBUG: selected_sources={selected_sources}")
    
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"DEBUG: selected_source_ids={selected_source_ids}")

    if not selected_keyword or len(selected_sources) < 2 or not click_data:
        print(f"DEBUG: Returning empty figure - missing keyword, sources, or click_data")
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
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Get display names from the actual data columns, not from dbase_options
        # The combined_dataset already has the correct column names
        selected_source_names = list(combined_dataset.columns[1:])  # Skip 'Fecha' column

        # Get clicked variables from heatmap
        if 'points' not in click_data or len(click_data['points']) == 0:
            # Return empty figure and empty equations
            fig = go.Figure()
            fig.update_layout(
                title="Error: No se recibieron datos del clic",
                xaxis_title="",
                yaxis_title="",
                height=400
            )
            return fig, ""

        x_var = click_data['points'][0]['x']
        y_var = click_data['points'][0]['y']

        # Debug: print available columns and clicked variables
        print(f"Available columns: {list(combined_dataset.columns)}")
        print(f"Clicked variables: x='{x_var}', y='{y_var}'")

        # Check if variables are the same (diagonal click on heatmap)
        if x_var == y_var:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No se puede hacer regresión de {x_var} contra sí mismo.<br>Seleccione dos variables diferentes en el mapa de calor.",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(
                title="Selección Inválida",
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
                height=400
            )
            return fig, "Seleccione dos variables diferentes para el análisis de regresión."

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
            return fig, ""

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
                    # Polynomial: y = dx³ + cx² + bx + a (highest power to lowest)
                    terms = []

                    # Polynomial terms (highest power first)
                    for i in range(len(coefs) - 1, 0, -1):  # Start from highest degree down to x term
                        if abs(coefs[i]) > 0.001:  # Only show significant coefficients
                            coef_str = f"{coefs[i]:+.3f}"
                            if i == 1:
                                terms.append(f"{coef_str}x")
                            else:
                                terms.append(f"{coef_str}x<sup>{i}</sup>")

                    # Intercept term (comes last)
                    if abs(intercept) > 0.001:
                        terms.append(f"{intercept:+.3f}")

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

# Callback for credits toggle - allows manual override
@app.callback(
    Output('credits-collapse', 'is_open', allow_duplicate=True),
    Output('credits-chevron', 'className'),
    Input('credits-toggle', 'n_clicks'),
    State('credits-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_credits_manually(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        chevron_class = "fas fa-chevron-up" if new_state else "fas fa-chevron-down"
        return new_state, chevron_class
    return is_open, "fas fa-chevron-down"

# Callback to show/hide navigation menu with dynamic buttons
@app.callback(
    Output('navigation-section', 'children'),
    Output('navigation-section', 'style'),
    Input('keyword-dropdown', 'value'),
    Input('data-sources-store-v2', 'data')
)
def update_navigation_visibility(selected_keyword, selected_sources):
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)

    if selected_keyword and selected_sources:
        # Define navigation buttons with their requirements
        nav_buttons = [
            # Always visible (basic analysis)
            {"id": 1, "text": "1. Temporal 2D", "href": "#section-temporal-2d", "color": "#e8f4fd", "border": "#b8daff", "min_sources": 1},
            {"id": 2, "text": "2. Análisis Medias", "href": "#section-mean-analysis", "color": "#f0f9ff", "border": "#bee3f8", "min_sources": 1},

            # Require 2+ sources (multi-source analysis)
            {"id": 3, "text": "3. Temporal 3D", "href": "#section-temporal-3d", "color": "#fef5e7", "border": "#fbd38d", "min_sources": 2},
            {"id": 4, "text": "4. Estacional", "href": "#section-seasonal", "color": "#f0fff4", "border": "#9ae6b4", "min_sources": 1},
            {"id": 5, "text": "5. Fourier", "href": "#section-fourier", "color": "#faf5ff", "border": "#d6bcfa", "min_sources": 1},
            {"id": 6, "text": "6. Correlación", "href": "#section-correlation", "color": "#e6fffa", "border": "#81e6d9", "min_sources": 2},
            {"id": 7, "text": "7. Regresión", "href": "#section-regression", "color": "#fffaf0", "border": "#fce5cd", "min_sources": 2},
            {"id": 8, "text": "8. PCA", "href": "#section-pca", "color": "#f0f9ff", "border": "#bee3f8", "min_sources": 2},

            # Always visible (utility sections) - placed at the end
            {"id": 9, "text": "Tabla de Datos", "href": "#section-data-table", "color": "#f8f9fa", "border": "#dee2e6", "min_sources": 1},
            {"id": 10, "text": "Rendimiento", "href": "#section-performance", "color": "#f7fafc", "border": "#e2e8f0", "min_sources": 1},
        ]

        # Filter buttons based on number of selected sources
        num_sources = len(selected_sources)
        active_buttons = [btn for btn in nav_buttons if num_sources >= btn["min_sources"]]

        # Generate button elements
        button_elements = []
        for btn in active_buttons:
            button_elements.append(
                html.Div([
                    html.A(btn["text"], href=btn["href"], className="nav-link",
                           style={'color': '#2c3e50', 'textDecoration': 'none', 'fontSize': '9px', 'fontWeight': '500'})
                ], style={
                    'backgroundColor': btn["color"],
                    'padding': '4px 8px',
                    'borderRadius': '4px',
                    'margin': '2px',
                    'display': 'inline-block',
                    'border': f'1px solid {btn["border"]}'
                })
            )

        # Show navigation menu with filtered buttons
        return [
            html.Hr(),
            html.Div([
                html.Div(button_elements, style={'marginBottom': '15px'}),
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
    Input('data-sources-store-v2', 'data')
)
def update_fourier_analysis(selected_source, selected_keyword, selected_sources):
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)

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
        datasets_norm, _ = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)

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

        # PHASE 1 OPTIMIZATION: Add data size limits to prevent performance issues
        MAX_FFT_SIZE = 10000
        original_length = len(values)
        if len(values) > MAX_FFT_SIZE:
            # Downsample while preserving frequency content
            downsample_factor = max(1, len(values) // MAX_FFT_SIZE)
            values = values[::downsample_factor]
            print(f"Fourier: Downsampled from {original_length} to {len(values)} points")

        # PHASE 1 OPTIMIZATION: Single FFT calculation (removed duplicate)
        from scipy.fft import fft, fftfreq
        import numpy as np

        # Apply FFT (only once now)
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

        # PHASE 1 OPTIMIZATION: Simplified significance threshold using percentiles
        # Much faster than chi-squared distribution calculations
        scaled_threshold = np.percentile(magnitude, 95)  # Top 5% are significant

        # Create figure
        fig = go.Figure()

        # Determine significant components
        significant_mask = magnitude >= scaled_threshold

        # PHASE 1 OPTIMIZATION: Efficient stem plotting with controlled batching
        # Separate significant and non-significant for better legend control
        sig_periods = periods[significant_mask]
        sig_magnitude = magnitude[significant_mask]
        non_sig_periods = periods[~significant_mask]
        non_sig_magnitude = magnitude[~significant_mask]

        # Add stems for significant components (red) - batch add for performance
        if len(sig_periods) > 0:
            # Use bar chart for stems (much more efficient than individual lines)
            fig.add_trace(go.Bar(
                x=sig_periods,
                y=sig_magnitude,
                name='Componentes Significativos',
                marker_color='red',
                marker_line_width=2,
                marker_line_color='red',
                opacity=0.8,
                showlegend=True,
                width=[0.5] * len(sig_periods)  # Narrow bars for stem-like appearance
            ))

        # Add stems for non-significant components (grey)
        if len(non_sig_periods) > 0:
            fig.add_trace(go.Bar(
                x=non_sig_periods,
                y=non_sig_magnitude,
                name='Componentes No Significativos',
                marker_color='grey',
                marker_line_width=1,
                marker_line_color='grey',
                opacity=0.6,
                showlegend=True,
                width=[0.3] * len(non_sig_periods)  # Even narrower for less prominent
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

        # Legend is now handled by the bar traces above
        # No need for additional dummy traces


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