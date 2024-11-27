import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from correlation import get_all_keywords, get_file_data2, create_combined_dataset  # Update import
import pandas as pd
import plotly.graph_objects as go  # Add this import
import numpy as np  # Add this import
from scipy.interpolate import CubicSpline
import plotly.figure_factory as ff
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import warnings
from pmdarima import auto_arima
from plotly.subplots import make_subplots
import plotly.subplots as make_subplots
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.fft import fft, fftfreq

warnings.filterwarnings('ignore')

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    title='Análisis de Herramientas Gerenciales'
)

# Define custom HTML index string with additional favicon tags
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16x16.png">
        <link rel="manifest" href="/assets/site.webmanifest">
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

# Define database options as a global variable
dbase_options = {
    1: "Google Trends",
    4: "Crossref.org",
    2: "Google Books Ngrams",
    3: "Bain - Usabilidad",
    5: "Bain - Satisfacción"
}

# Define a color palette for the available options
colors = [
    '#1f77b4',    # blue
    '#ff7f0e',    # orange
    '#2ca02c',    # green
    '#d62728',    # red
    '#9467bd',    # purple
    '#8c564b',    # brown
    '#e377c2',    # pink
    '#7f7f7f'     # gray
]

# Create color map using dbase_options
color_map = {
    dbase_options[key]: colors[i % len(colors)]  # Use modulo to cycle through colors if more sources than colors
    for i, key in enumerate(dbase_options.keys())
}

# Add a new global variable to store the current date range
global_date_range = {'start': None, 'end': None}

# Define the sidebar layout
sidebar = html.Div(
    [
        # Logo
        html.Img(
            src='assets/Management-Tools-Analysis-logo.png',
            style={
                'width': '80%',
                'margin-bottom': '20px',
                'display': 'block',
                'margin-left': 'auto',
                'margin-right': 'auto'
            }
        ),
        
        html.Hr(),
        
        # Keyword dropdown (single selection) - removed default value
        html.Div([
            html.Label("Seleccione una Herramienta:", style={'fontSize': '12px'}),
            dcc.Dropdown(
                id='keyword-dropdown',
                options=[
                    {'label': keyword, 'value': keyword} 
                    for keyword in get_all_keywords()
                ],
                value=None,  # Changed from default value to None
                placeholder="Seleccione una Herramienta Gerencial",
                className="mb-4",
                style={'fontSize': '12px'}
            ),
            html.Div(id='keyword-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
        
        # Update the source buttons to start with all unselected
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
                    outline=True,  # All buttons start as outlined (unselected)
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

        # Add footer div that sticks to bottom
        html.Div([
            html.Hr(),
            html.P([
                "Equipo de desarrollo: ",
                html.A("Wise Connex", href="http://wiseconnex.com", target="_blank"),
                " - (c)2024"
            ], style={'marginBottom': '2px', 'fontSize': '10px', 'textAlign': 'center'}),
            html.P([
                "Código: ",
                html.A(
                    "github.com/Wise-Connex/Management-Tools-Analysis.git",
                    href="https://github.com/Wise-Connex/Management-Tools-Analysis.git",
                    target="_blank"
                )
            ], style={'fontSize': '10px', 'textAlign': 'center', 'marginTop': '0px'})
        ], style={
            'position': 'absolute',
            'bottom': '20px',
            'left': '0',
            'right': '0',
            'padding': '5px'
        })
    ],
    style={
        'background-color': '#f3f4f6',  # Changed to a slightly darker shade than '#f8f9fa'
        'padding': '20px',
        'height': '100vh',
        'position': 'fixed',
        'width': 'inherit',
        'overflow-y': 'auto',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'boxShadow': '2px 0 5px rgba(0,0,0,0.1)'  # Keeping the subtle shadow
    }
)

# Update membrete to remove the moved content
membrete = html.Div(
    [
        html.Div([
            html.H5("Enfoque Central de la Investigación Doctoral: Dicotomía Ontológica en las 'Modas Gerenciales'", className="mb-0"),
            html.H3("Análisis Estadístico Correlacional: Técnicas y Herramientas Gerenciales", className="mb-0"),
            html.P([
                "Tesista: ", html.B("Diomar Anez"), " | Desarrollador en Python: ", html.B("Dimar Anez")
            ], className="mb-0"),
        ])
    ],
    style={
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
    }
)

# Update the main layout container
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar column - width=2 (20% of 12 columns)
        dbc.Col([
            # Wrapper div to maintain space
            html.Div(style={'width': '100%', 'height': '100vh'}),
            # Sidebar
            sidebar
        ], width=2, className="bg-light"),
        
        # Main content column - width=10
        dbc.Col([
            membrete,
            html.Div(id='main-title', style={
                'fontSize': '24px',  # Changed from '30px' to '20px'
                'marginBottom': '10px'  # Changed from '15px' to '10px' to reduce spacing
            }),
            # Main content div with scroll - now includes time range buttons
            html.Div(id='main-content', className="w-100", style={
                'height': 'calc(100vh - 200px)',
                'overflowY': 'auto',
                'overflowX': 'hidden',
                'paddingRight': '10px'  # Add padding for scrollbar
            })
        ], width=10, className="px-4", style={
            'height': '100vh',
            'overflow': 'hidden'  # Prevent column from scrolling
        })
    ], style={'height': '100vh'})
], fluid=True, className="px-0", style={'height': '100vh'})

# Add callback to update main content based on selections
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
    
    datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
    combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
    
    # Reset index and format date
    combined_dataset = combined_dataset.reset_index()
    date_column = combined_dataset.columns[0]
    combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
    combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})
    
    # Check if Bain and Crossref are both selected
    bain_sources = [3, 5]  # IDs for Bain sources
    has_bain = any(src_id in selected_sources for src_id in bain_sources)
    has_crossref = 4 in selected_sources
    
    if has_bain and has_crossref:
        # Get the earliest date from Bain data
        bain_columns = [dbase_options[src_id] for src_id in bain_sources if src_id in selected_sources]
        bain_start_date = combined_dataset[combined_dataset[bain_columns].notna().any(axis=1)]['Fecha'].min()
        
        # Truncate all data to start from Bain's start date
        combined_dataset = combined_dataset[combined_dataset['Fecha'] >= bain_start_date]

    # Filter out rows where any selected source has NaN values
    data_columns = [dbase_options[src_id] for src_id in selected_sources]
    combined_dataset = combined_dataset.dropna(subset=data_columns)
    
    # Filter the dataset based on the current date range
    if global_date_range['start'] and global_date_range['end']:
        combined_dataset = combined_dataset[
            (combined_dataset['Fecha'] >= global_date_range['start']) &
            (combined_dataset['Fecha'] <= global_date_range['end'])
        ]

    selected_source_names = [dbase_options[src_id] for src_id in selected_sources]
    total_records = len(combined_dataset)
    
    # Create year ticks for January 1st of each year
    years_data = combined_dataset[combined_dataset['Fecha'].dt.month == 1]
    if len(years_data) == 0:  # If no January dates, get unique years and create ticks
        unique_years = combined_dataset['Fecha'].dt.year.unique()
        years_data = pd.DataFrame({
            'Fecha': [pd.Timestamp(year=year, month=1, day=1) for year in unique_years]
        })

    # Create the line chart
    fig = {
        'data': [
            {
                'x': combined_dataset['Fecha'].dt.strftime('%Y-%m-%d'),
                'y': combined_dataset[col],
                'name': col,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'shape': 'spline',
                    'smoothing': 1.3,
                    'width': 2,
                    'color': color_map.get(col, '#000000')
                },
                'hovertemplate': '%{y:.2f} - ' + col + '<extra></extra>'
            } for col in combined_dataset.columns if col != 'Fecha'
        ],
        'layout': {
            'title': f'Tendencia de {selected_keyword} a través del tiempo',
            'xaxis': {
                'title': {
                    'text': 'Fecha',
                    'font': {'size': 12}
                },
                'title_standoff': 25,
                'tickangle': 45,
                'dtick': 'M1',
                'tickformat': '%b',
                'showgrid': True,
                'gridcolor': 'lightgray',
                'tickmode': 'array',
                'ticktext': years_data['Fecha'].dt.strftime('%Y'),
                'tickvals': years_data['Fecha'].dt.strftime('%Y-%m-%d'),
                'tickfont': {'size': 8},
                'rangeslider': {'visible': True},
                'domain': [0, 1],
            },
            'yaxis': {
                'title': {
                    'text': 'Valor Normalizado',
                    'font': {'size': 12}
                },
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'height': 520,
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 150},
            'hovermode': 'x unified',
            'legend': {
                'orientation': 'h',
                'yanchor': 'top',
                'y': -0.55,
                'xanchor': 'center',
                'x': 0.5
            }
        }
    }
    
    # Create the bar chart initial state
    bar_data = combined_dataset.drop('Fecha', axis=1).mean()
    initial_bar_fig = {
        'data': [{
            'x': list(bar_data.index),
            'y': bar_data.values,
            'type': 'bar',
            'text': [f'{val:.2f}' for val in bar_data.values],
            'textposition': 'auto',
            'marker': {
                'color': [color_map.get(col, '#000000') for col in bar_data.index]
            }
        }],
        'layout': {
            'title': 'Promedios',
            'yaxis': {
                'title': 'Valor Promedio',
                'range': [0, max(bar_data.values) * 1.1]
            },
            'showlegend': False,
            'height': 520,
            'margin': {
                'l': 40,
                'r': 20,
                't': 40,
                'b': 80
            },
            'bargap': 0.2,
            'xaxis': {
                'tickangle': 45,
                'tickfont': {'size': 10}
            }
        }
    }

    # Add 3D graph controls when more than 1 sources are selected
    html.Div([
        html.H6("Evolución Temporal", style={'fontSize': '20px', 'marginTop': '10px'}),
        html.Div([
            # Add toggle button for data frequency
            dbc.Button(
                "Cambiar Frecuencia",
                id="toggle-frequency-button",
                color="primary",
                size="sm",
                className="me-2",
                style={'fontSize': '12px'}
            ),
            html.Span(
                "Mensual",
                id="frequency-label",
                style={'fontSize': '12px', 'marginRight': '20px'}
            ),
            # Existing dropdowns
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                        for src_id in selected_sources],
                value=dbase_options[selected_sources[0]] if len(selected_sources) > 0 else None,  # Prepopulate with first source
                placeholder="Seleccione eje Y",
                style={'fontSize': '12px'}
            ),
            dcc.Dropdown(
                id='z-axis-dropdown',
                options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                        for src_id in selected_sources],
                value=dbase_options[selected_sources[1]] if len(selected_sources) > 1 else None,  # Prepopulate with second source
                placeholder="Seleccione eje Z",
                style={'fontSize': '12px'}
            ),
        ], style={'marginBottom': '10px'}),
        # Update this section to include all three graph views
        html.Div([
            dcc.Graph(
                id='3d-graph-view-1',
                style={'height': '600px', 'width': '33%'},
                config={'displaylogo': False, 'responsive': True, 'autosizable': True}
            ),
            dcc.Graph(
                id='3d-graph-view-2',
                style={'height': '600px', 'width': '33%'},
                config={'displaylogo': False, 'responsive': True, 'autosizable': True}
            ),
            dcc.Graph(
                id='3d-graph-view-3',
                style={'height': '600px', 'width': '33%'},
                config={'displaylogo': False, 'responsive': True, 'autosizable': True}
            )
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'width': '100%',
            'flexWrap': 'wrap'  # Added to handle smaller screens
        }),
            
            # Add horizontal divider with shadow at the end
            html.Hr(style={
                'border': 'none',
                'height': '3px',  # Made thicker
                'backgroundColor': '#dee2e6',
                'margin': '30px 0',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'width': '100%',  # Ensure full width
                'display': 'block',  # Ensure it's displayed as a block element
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            
    ], className="w-100") if len(selected_sources) >= 2 else html.Div()
    
    # Remove the nested callback and return the initial graphs
    return html.Div([
        # Time range buttons section
        html.Div([
            html.Label("Rango de tiempo:  ", style={'marginRight': '12px', 'fontSize': '14px'}),
            dbc.ButtonGroup([
                dbc.Button("5 años", id="btn-5y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                dbc.Button("10 años", id="btn-10y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                dbc.Button("15 años", id="btn-15y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                dbc.Button("20 años", id="btn-20y", size="sm", className="me-1", n_clicks=0, style={'fontSize': '11px'}),
                dbc.Button("Todo", id="btn-all", size="sm", n_clicks=0, style={'fontSize': '11px'}),
            ], className="mb-3")
        ], style={'marginBottom': '10px'}),
        
        # First row: Line and Bar charts
        html.Div([
            # Line chart container
            html.Div([
                dcc.Graph(
                    id='line-graph',
                    figure=fig,
                    style={'height': '520px', 'width': '100%'},  # Changed: Set width to 100%
                    config={'displaylogo': False, 'responsive': True}  # Added: responsive config
                ),
            ], style={
                'width': '80%',
                'display': 'inline-block',
                'vertical-align': 'top'
            }),
            # Bar chart container
            html.Div([
                dcc.Graph(
                    id='bar-graph',
                    figure=initial_bar_fig,
                    style={'height': '520px', 'width': '100%'},  # Changed: Set width to 100%
                    config={'displaylogo': False, 'responsive': True}  # Added: responsive config
                ),
            ], style={
                'width': '20%',
                'display': 'inline-block',
                'vertical-align': 'top'
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '20px',
            'width': '100%'  # Added: ensure container takes full width
        }),
        
        # Add new row for periods bar graph
        html.Div([
            dcc.Graph(
                id='periods-bar-graph',
                style={'height': '400px'},
                config={'displaylogo': False}
            ),
        ], style={'marginBottom': '20px'}),
        
        # Second row: Table with toggle button
        html.Div([
            # Add toggle button
            dbc.Button(
                "Mostrar/Ocultar Tabla de Datos",
                id="toggle-table-button",
                color="primary",
                size="sm",
                className="mb-2",
                style={'fontSize': '12px'}
            ),
            # Wrap table in a collapsible div
            dbc.Collapse(
                html.Div([
                    dash_table.DataTable(
                        # Format the date in the data before passing to table
                        data=[
                            {
                                **{
                                    'Fecha': row['Fecha'].strftime('%Y-%m-%d') if isinstance(row['Fecha'], pd.Timestamp) else row['Fecha'],
                                    **{col: row[col] for col in combined_dataset.columns if col != 'Fecha'}
                                }
                            }
                            for row in combined_dataset.to_dict('records')
                        ],
                        columns=[{"name": str(i), "id": str(i)} for i in combined_dataset.columns],
                        style_table={
                            'overflowX': 'auto',
                            'overflowY': 'auto',
                            'height': '500px',
                            'width': '100%',  # Ensure table uses full width of its column
                        },
                        style_cell={
                            'textAlign': 'left',
                            'padding': '5px',
                            'minWidth': '100px',
                            'width': '150px',
                            'maxWidth': '180px',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': '10px'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold',
                            'position': 'sticky',
                            'top': 0,
                            'zIndex': 1000,
                            'fontSize': '10px'
                        },
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': '10px'
                        },
                        page_size=15
                    ),
                    html.P(
                        f"TOTAL REGISTROS: {len(combined_dataset)}",
                        style={
                            'fontSize': '12px',
                            'marginTop': '5px',
                            'fontWeight': 'bold'
                        }
                    )
                ]),
                id="collapse-table",
                is_open=False  # Initially collapsed
            )
        ], style={'marginBottom': '20px'}),
        
        # Add horizontal divider with shadow
        html.Hr(style={
            'border': 'none',
            'height': '3px',  # Made thicker
            'backgroundColor': '#dee2e6',
            'margin': '30px 0',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'width': '100%',  # Ensure full width
            'display': 'block',  # Ensure it's displayed as a block element
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),
        
        # Third row: 3D Graph (only shown when 2 or more sources selected)
        html.Div([
            html.H6("Evolución Temporal", style={'fontSize': '20px', 'marginTop': '10px'}),
            html.Div([
                # Left section: Toggle button and frequency label
                html.Div([
                    dbc.Button(
                        "Cambiar Frecuencia",
                        id="toggle-frequency-button",
                        color="primary",
                        size="sm",
                        className="me-2",
                        style={'fontSize': '12px'}
                    ),
                    html.Span(
                        "Mensual",
                        id="frequency-label",
                        style={'fontSize': '12px'}
                    ),
                ], style={
                    'display': 'inline-block',
                    'width': '20%',
                    'verticalAlign': 'middle'
                }),
                
                # Right section: Axis dropdowns
                html.Div([
                    dcc.Dropdown(
                        id='y-axis-dropdown',
                        options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                                for src_id in selected_sources],
                        value=dbase_options[selected_sources[0]] if len(selected_sources) > 0 else None,
                        placeholder="Seleccione eje Y",
                        style={'fontSize': '12px'}
                    ),
                ], style={
                    'display': 'inline-block',
                    'width': '38%',
                    'paddingLeft': '1%',
                    'paddingRight': '1%',
                    'verticalAlign': 'middle'
                }),
                
                html.Div([
                    dcc.Dropdown(
                        id='z-axis-dropdown',
                        options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                                for src_id in selected_sources],
                        value=dbase_options[selected_sources[1]] if len(selected_sources) > 1 else None,
                        placeholder="Seleccione eje Z",
                        style={'fontSize': '12px'}
                    ),
                ], style={
                    'display': 'inline-block',
                    'width': '38%',
                    'paddingLeft': '1%',
                    'verticalAlign': 'middle'
                }),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'width': '100%',
                'marginBottom': '10px'
            }),
            # Update this section to include all three graph views
            html.Div([
                dcc.Graph(
                    id='3d-graph-view-1',
                    style={'height': '600px', 'width': '33%'},
                    config={'displaylogo': False, 'responsive': True, 'autosizable': True}
                ),
                dcc.Graph(
                    id='3d-graph-view-2',
                    style={'height': '600px', 'width': '33%'},
                    config={'displaylogo': False, 'responsive': True, 'autosizable': True}
                ),
                dcc.Graph(
                    id='3d-graph-view-3',
                    style={'height': '600px', 'width': '33%'},
                    config={'displaylogo': False, 'responsive': True, 'autosizable': True}
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'width': '100%',
                'flexWrap': 'wrap'  # Added to handle smaller screens
            }),
            
            # Add horizontal divider with shadow at the end
            html.Hr(style={
                'border': 'none',
                'height': '3px',  # Made thicker
                'backgroundColor': '#dee2e6',
                'margin': '30px 0',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'width': '100%',  # Ensure full width
                'display': 'block',  # Ensure it's displayed as a block element
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            
            # Update the Statistical Analysis section spacing
            html.Div([
                html.H6("Análisis Estadístico", style={
                    'fontSize': '20px', 
                    'marginTop': '10px',
                    'marginBottom': '20px'  # Add consistent bottom margin
                }),
                
                # Container for correlation and regression (2 sections side by side)
                html.Div([
                    # Section 1: Correlación
                    html.Div([
                        html.H6("Correlación", style={'fontSize': '16px', 'textAlign': 'center'}),
                        dcc.Graph(
                            id='correlation-graph',
                            style={'height': '300px', 'width': '100%'},
                            config={'displaylogo': False, 'responsive': True}
                        ),
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    
                    # Section 2: Regresión
                    html.Div([
                        html.H6("Regresión", style={'fontSize': '16px', 'textAlign': 'center'}),
                        dcc.Graph(
                            id='regression-graph',
                            style={'height': '300px', 'width': '100%'},
                            config={'displaylogo': False, 'responsive': True}
                        ),
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'marginBottom': '150px',  # Consistent bottom margin
                    'width': '100%'
                }),

                # Add horizontal divider with consistent spacing
                html.Hr(style={
                    'border': 'none',
                    'height': '3px',
                    'backgroundColor': '#dee2e6',
                    'margin': '50px 0',  # Consistent vertical margins
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'width': '100%'
                }),

                # Section 3: Seasonal Analysis with consistent spacing
                html.Div([
                    html.H6("Análisis Estacional", style={
                        'fontSize': '20px', 
                        'textAlign': 'center',
                        'marginTop': '20px',
                        'marginBottom': '20px'  # Consistent bottom margin
                    }),
                    # Container for two seasonal decomposition graphs side by side
                    html.Div([
                        # Left seasonal graph
                        html.Div([
                            dcc.Loading(
                                id="loading-seasonal-1",
                                type="default",
                                children=dcc.Graph(
                                    id='seasonal-graph-1', 
                                    style={'height': '1200px', 'width': '100%'},  # Reduced from 600px to 400px
                                    config={'displaylogo': False, 'responsive': True}
                                ),
                            ),
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        # Right seasonal graph
                        html.Div([
                            dcc.Loading(
                                id="loading-seasonal-2",
                                type="default",
                                children=dcc.Graph(
                                    id='seasonal-graph-2', 
                                    style={'height': '1200px', 'width': '100%'},  # Reduced from 600px to 400px
                                    config={'displaylogo': False, 'responsive': True}
                                ),
                            ),
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'width': '100%',
                        'marginBottom': '50px'  # Consistent bottom margin
                    }),
                ]),

                # Add horizontal divider with consistent spacing
                html.Hr(style={
                    'border': 'none',
                    'height': '3px',
                    'backgroundColor': '#dee2e6',
                    'margin': '50px 0',  # Consistent vertical margins
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'width': '100%'
                }),

                # Section 4: Pronóstico with consistent spacing
                html.Div([
                    html.H6("Pronóstico", style={
                        'fontSize': '20px', 
                        'textAlign': 'center',
                        'marginTop': '10px',
                        'marginBottom': '20px'  # Consistent bottom margin
                    }),
                    # Container for two ARIMA graphs side by side
                    html.Div([
                        # Left ARIMA graph
                        html.Div([
                            dcc.Loading(
                                id="loading-forecast-1",
                                type="default",
                                children=dcc.Graph(
                                    id='forecast-graph-1', 
                                    style={'height': '400px', 'width': '100%'},  # Increased from 300px to 400px
                                    config={'displaylogo': False, 'responsive': True}
                                ),
                            ),
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        # Right ARIMA graph
                        html.Div([
                            dcc.Loading(
                                id="loading-forecast-2",
                                type="default",
                                children=dcc.Graph(
                                    id='forecast-graph-2', 
                                    style={'height': '400px', 'width': '100%'},  # Increased from 300px to 400px
                                    config={'displaylogo': False, 'responsive': True}
                                ),
                            ),
                        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'space-between',
                        'width': '100%',
                        'marginBottom': '50px'  # Consistent bottom margin
                    }),
                ]),

                # Final horizontal divider
                html.Hr(style={
                    'border': 'none',
                    'height': '3px',
                    'backgroundColor': '#dee2e6',
                    'margin': '50px 0',  # Consistent vertical margins
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'width': '100%'
                }),
            ], className="w-100")
        ], className="w-100") if len(selected_sources) >= 2 else html.Div()
    ])

# Update the graph callback to use button states instead of dropdown
@app.callback(
    [Output('line-graph', 'figure'), 
     Output('bar-graph', 'figure'),
     Output('periods-bar-graph', 'figure')],
    [Input('btn-5y', 'n_clicks'),
     Input('btn-10y', 'n_clicks'),
     Input('btn-15y', 'n_clicks'),
     Input('btn-20y', 'n_clicks'),
     Input('btn-all', 'n_clicks'),
     Input('line-graph', 'relayoutData'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_graphs(n5, n10, n15, n20, nall, relayoutData, selected_keyword, *button_states):
    global global_date_range
    
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not selected_keyword or not selected_sources:
        return dash.no_update, dash.no_update, dash.no_update

    # Get the data
    datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
    combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
    
    # Reset index and format date
    combined_dataset = combined_dataset.reset_index()
    date_column = combined_dataset.columns[0]  # Get the original date column name
    combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
    combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})  # Rename to 'Fecha'
    
    # Get the full date range
    end_date = combined_dataset['Fecha'].max()
    start_date = combined_dataset['Fecha'].min()
    
    # Determine which button was clicked and set the visible range accordingly
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'btn-all'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id not in ['btn-5y', 'btn-10y', 'btn-15y', 'btn-20y', 'btn-all']:
            button_id = 'btn-all'

    # Determine visible range based on button clicks or slider
    visible_end = end_date
    if button_id == 'btn-all':
        visible_start = start_date
    else:
        years = int(button_id.split('-')[1][:-1])
        visible_start = end_date - pd.DateOffset(years=years)

    # Update range based on slider if it's been changed
    if relayoutData and ('xaxis.range' in relayoutData or 'xaxis.range[0]' in relayoutData):
        visible_start = pd.to_datetime(relayoutData.get('xaxis.range[0]') or relayoutData.get('xaxis.range')[0])
        visible_end = pd.to_datetime(relayoutData.get('xaxis.range[1]') or relayoutData.get('xaxis.range')[1])

    # Update the global date range
    global_date_range['start'] = visible_start
    global_date_range['end'] = visible_end

    # Filter data based on either button selection or slider range
    df_filtered = combined_dataset.copy()
    if relayoutData and ('xaxis.range' in relayoutData or 'xaxis.range[0]' in relayoutData):
        # Use slider range if it's been changed
        visible_start = relayoutData.get('xaxis.range[0]') or relayoutData.get('xaxis.range')[0]
        visible_end = relayoutData.get('xaxis.range[1]') or relayoutData.get('xaxis.range')[1]

    # Apply the filtering using the determined range
    df_filtered = df_filtered[
        (df_filtered['Fecha'] >= visible_start) &
        (df_filtered['Fecha'] <= visible_end)
    ]

    # Calculate means for the filtered period
    means = df_filtered.drop('Fecha', axis=1).mean()
    
    # Update bar chart with filtered means
    bar_fig = {
        'data': [{
            'x': list(means.index),
            'y': means.values,
            'type': 'bar',
            'text': [f'{val:.2f}' for val in means.values],
            'textposition': 'auto',
            'marker': {
                'color': [color_map.get(col, '#000000') for col in means.index]
            }
        }],
        'layout': {
            'title': {
                'text': 'Promedios',
                'font': {'size': 12}
            },
            'yaxis': {
                'title': 'Valor Promedio',
                'range': [0, max(means.values) * 1.1]
            },
            'showlegend': False,
            'height': 520,
            'margin': {
                'l': 40,
                'r': 20,
                't': 40,
                'b': 80
            },
            'bargap': 0.2,
            'xaxis': {
                'tickangle': 45,
                'tickfont': {'size': 10}
            }
        }
    }
    
    # Create year ticks for January 1st of each year
    years_data = combined_dataset[combined_dataset['Fecha'].dt.month == 1]
    if len(years_data) == 0:  # If no January dates, get unique years and create ticks
        unique_years = combined_dataset['Fecha'].dt.year.unique()
        years_data = pd.DataFrame({
            'Fecha': [pd.Timestamp(year=year, month=1, day=1) for year in unique_years]
        })

    year_ticks = years_data['Fecha'].dt.strftime('%Y-%m-%d').tolist()
    year_labels = years_data['Fecha'].dt.strftime('%Y').tolist()
    
    # Create the line chart figure
    line_fig = {
        'data': [
            {
                'x': combined_dataset['Fecha'],
                'y': combined_dataset[col],
                'name': col,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'shape': 'spline',
                    'smoothing': 1.3,
                    'width': 2,
                    'color': color_map.get(col, '#000000')
                },
                'hovertemplate': '%{y:.2f} - ' + col + '<extra></extra>'
            } for col in combined_dataset.columns if col != 'Fecha'
        ],
        'layout': {
            'title': {
                'text': f'Tendencia de {selected_keyword} a través del tiempo',
                'font': {'size': 12}
            },
            'xaxis': {
                'title': {
                    'text': 'Fecha',
                    'font': {'size': 12}
                },
                'title_standoff': 25,
                'tickangle': 45,
                'showgrid': True,
                'gridcolor': 'lightgray',
                'tickmode': 'array',
                'ticktext': year_labels,
                'tickvals': year_ticks,
                'tickfont': {'size': 8},
                'tickposition': 'outside',
                'tickoffset': 5,
                'ticks': 'outside',
                'ticklen': 8,
                'dtick': 'M12',  # Show ticks every 12 months
                'rangeslider': {
                    'visible': True,
                    'range': [start_date, end_date]
                },
                'domain': [0, 1],
            },
            'yaxis': {
                'title': {
                    'text': 'Valor Normalizado',
                    'font': {'size': 12}
                },
                'showgrid': True,
                'gridcolor': 'lightgray'
            },
            'height': 520,
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 150},
            'hovermode': 'x unified',
            'legend': {
                'orientation': 'h',
                'yanchor': 'top',
                'y': -0.55,
                'xanchor': 'center',
                'x': 0.5
            }
        }
    }

    # Update the layout to include both the visible range and the full range
    layout_updates = {
        'xaxis': {
            'range': [visible_start, visible_end],  # Set the visible range
            'rangeslider': {
                'visible': True,
                'range': [start_date, end_date]  # Keep the full range in the slider
            }
        }
    }
    
    # Update your figure layout with these new settings
    line_fig['layout'].update(layout_updates)

    # Calculate means for different time periods with reversed order
    periods = {
        'Todo': None,
        'Hace 20 años': 20,
        'Hace 15 años': 15,
        'Hace 10 años': 10,
        'Hace 5 años': 5,
        'Último año': 1
    }
    
    period_means = {}
    for period_name, years in periods.items():
        if years is None:
            # For 'Todo', use all data
            period_data = combined_dataset
        else:
            start_date = end_date - pd.DateOffset(years=years)
            period_data = combined_dataset[combined_dataset['Fecha'] >= start_date]
        
        if not period_data.empty:
            period_means[period_name] = period_data.drop('Fecha', axis=1).mean()

    # Calculate percentages for each period
    period_percentages = {}
    for period in periods.keys():
        if period in period_means:
            total = sum([period_means[period][source] for source in means.index])
            period_percentages[period] = {
                source: (period_means[period][source] / total * 100) 
                for source in means.index
            }

    # Calculate period lengths (in years)
    period_lengths = {
        'Todo': max(20, (combined_dataset['Fecha'].max() - combined_dataset['Fecha'].min()).days / 365),
        'Hace 20 años': 20,
        'Hace 15 años': 15,
        'Hace 10 años': 10,
        'Hace 5 años': 5,
        'Último año': 1
    }
    
    # Calculate relative widths and center positions
    max_period = max(period_lengths.values())
    relative_widths = {
        period: length / max_period 
        for period, length in period_lengths.items()
    }
    
    # Calculate x positions for back-to-back placement
    x_positions = {}
    current_pos = 0
    for period in periods.keys():
        width = relative_widths[period]
        x_positions[period] = current_pos + (width / 2)  # Center of each bar
        current_pos += width

    # Create traces with variable widths and specific positions
    period_traces = []
    
    # First add all bar traces (percentage based)
    for idx, source in enumerate(means.index):
        y_values = [period_percentages[period][source] for period in periods.keys() if period in period_percentages]
        x_values = [x_positions[period] for period in periods.keys()]  # Use calculated positions
        
        period_traces.append({
            'name': f"{source} (valor relativo %)",  # Updated legend label
            'type': 'bar',
            'x': x_values,
            'y': y_values,
            'marker': {
                'color': color_map.get(source, '#000000'),
                'opacity': 0.2
            },
            'width': [relative_widths[period] for period in periods.keys()],
            'showlegend': True
        })

    # Modify line traces to use same x positions
    for idx, source in enumerate(means.index):
        y_values = [period_means[period][source] for period in periods.keys() if period in period_means]
        x_values = [x_positions[period] for period in periods.keys()]
        
        period_traces.append({
            'name': f'{source} (valor absoluto)',
            'type': 'scatter',
            'x': x_values,
            'y': y_values,
            'mode': 'lines',
            'line': {
                'color': color_map.get(source, '#000000'),
                'width': 3,
                'shape': 'spline',
                'smoothing': 1.3
            },
            'yaxis': 'y2',
            'showlegend': True
        })

    periods_bar_fig = {
        'data': period_traces,
        'layout': {
            'title': {
                'text': 'Promedios por Período (% y valores absolutos)',
                'font': {'size': 12}
            },
            'barmode': 'stack',
            'bargap': 0,
            'bargroupgap': 0,
            'xaxis': {
                'title': 'Período',
                'tickangle': 45,
                'tickfont': {'size': 10},
                'ticktext': ['Todo', 'Últimos 20 años', 'Últimos 15 años', 
                           'Últimos 10 años', 'Últimos 5 años', 'Último año'],
                'tickvals': list(x_positions.values())
            },
            'yaxis': {
                'title': 'Porcentaje (%)',
                'range': [0, 100],
                'tickformat': '.0f',
                'ticksuffix': '%'
            },
            'yaxis2': {
                'title': 'Valor Absoluto',
                'overlaying': 'y',
                'side': 'right',
                'range': [0, 100]
            },
            'legend': {
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.65,
                'xanchor': 'center',
                'x': 0.5
            },
            'height': 400,
            'margin': {
                'l': 50,
                'r': 50,
                't': 40,
                'b': 150
            },
            'showlegend': True,
            'hovermode': 'x unified'
        }
    }

    return line_fig, bar_fig, periods_bar_fig

# Add new callback for keyword validation
@app.callback(
    Output('keyword-validation', 'children'),
    Input('keyword-dropdown', 'value')
)
def validate_keyword(selected_keyword):
    if not selected_keyword:
        return "Por favor, seleccione una herramienta."
    return ""

# Add callback to validate selection
@app.callback(
    Output('datasources-validation', 'children'),
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def validate_datasources(*button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    if not selected_sources:
        return "Por favor, seleccione al menos una fuente de datos."
    return ""

# Add new callback for Select All button
@app.callback(
    Output('datasources-dropdown', 'value'),
    Input('select-all-button', 'n_clicks'),
    State('datasources-dropdown', 'value'),
    prevent_initial_call=True
)
def toggle_select_all(n_clicks, current_values):
    if not current_values or len(current_values) < len(dbase_options):
        return list(dbase_options.keys())
    return [1]  # Return to default selection if all were selected

# Add a new callback to update the main title
@app.callback(
    Output('main-title', 'children'),
    Input('keyword-dropdown', 'value')
)
def update_title(selected_keyword):
    if not selected_keyword:
        return "Análisis de Herramientas Gerenciales"
    return f"Análisis de: {selected_keyword}"

# Update the 3D graph callback
@app.callback(
    [Output('3d-graph-view-1', 'figure'),
     Output('3d-graph-view-2', 'figure'),
     Output('3d-graph-view-3', 'figure'),
     Output('frequency-label', 'children')],
    [Input('y-axis-dropdown', 'value'),
     Input('z-axis-dropdown', 'value'),
     Input('keyword-dropdown', 'value'),
     Input('toggle-frequency-button', 'n_clicks')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()] +
    [State('frequency-label', 'children')]
)
def update_3d_graph(y_axis, z_axis, selected_keyword, n_clicks, *args):
    try:
        # Split args into button_states and current_frequency
        button_states = args[:-1]
        current_frequency = args[-1]
        
        # Convert button states to selected sources
        selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
        
        if not all([y_axis, z_axis, selected_keyword, selected_sources]):
            return {}, {}, {}, current_frequency

        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        # Reset index and format date
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        
        # Get the actual column names from the dataset
        available_columns = combined_dataset.columns.tolist()
        if date_column in available_columns:
            available_columns.remove(date_column)
        
        # Find the matching column names
        y_column = next((col for col in available_columns if y_axis in col), None)
        z_column = next((col for col in available_columns if z_axis in col), None)
        
        if not y_column or not z_column:
            return {}, {}, {}, current_frequency

        # Toggle frequency based on button clicks
        is_annual = current_frequency == "Anual"
        new_frequency = "Mensual" if is_annual else "Anual"
        
        if not is_annual:  # If switching to annual
            # Group by year with different aggregations
            combined_dataset = combined_dataset.set_index(date_column)
            
            agg_dict = {}
            for column in combined_dataset.columns:
                if 'Crossref' in column:
                    agg_dict[column] = 'sum'
                else:
                    agg_dict[column] = 'mean'
            
            combined_dataset = combined_dataset.groupby(pd.Grouper(freq='Y')).agg(agg_dict)
            
            # Add normalization for Crossref data after aggregation
            for column in combined_dataset.columns:
                if 'Crossref' in column:
                    # Normalize Crossref data to 0-100 scale
                    min_val = combined_dataset[column].min()
                    max_val = combined_dataset[column].max()
                    if max_val > min_val:  # Avoid division by zero
                        combined_dataset[column] = ((combined_dataset[column] - min_val) / 
                                                 (max_val - min_val)) * 100
            
            combined_dataset = combined_dataset.reset_index()
            
            combined_dataset[date_column] = combined_dataset[date_column].apply(
                lambda x: pd.Timestamp(year=x.year, month=1, day=1)
            )

        # Handle NaN values and ensure data is finite
        combined_dataset = combined_dataset.dropna(subset=[y_column, z_column])
        
        # Convert dates to numeric values for interpolation
        dates = combined_dataset[date_column].astype(np.int64) // 10**9
        
        # Create more points for smoother interpolation
        if not is_annual:
            num_points = len(combined_dataset) * 100
        else:
            num_points = len(combined_dataset) * 12
        
        # Ensure we have enough data points
        if len(combined_dataset) < 2:
            raise ValueError("Insuficientes datos para interpolación")

        t = np.arange(len(combined_dataset))
        t_smooth = np.linspace(0, len(combined_dataset) - 1, num=num_points)
        
        # Ensure data is finite before creating splines
        y_data = combined_dataset[y_column].replace([np.inf, -np.inf], np.nan).dropna()
        z_data = combined_dataset[z_column].replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(y_data) < 2 or len(z_data) < 2:
            raise ValueError("Insuficientes datos validos después de la limpieza")

        # Create cubic spline interpolations
        cs_dates = CubicSpline(t, dates, bc_type='natural')
        cs_y = CubicSpline(t, y_data, bc_type='natural')
        cs_z = CubicSpline(t, z_data, bc_type='natural')
        
        # Generate smooth data points
        dates_smooth = cs_dates(t_smooth)
        y_smooth = cs_y(t_smooth)
        z_smooth = cs_z(t_smooth)
        
        # Ensure interpolated values stay within bounds
        y_smooth = np.clip(y_smooth, 0, 100)
        z_smooth = np.clip(z_smooth, 0, 100)

        # Convert smooth dates back to datetime
        dates_dt_smooth = pd.to_datetime(dates_smooth * 10**9)

        # Calculate years for x-axis ticks
        years = combined_dataset[date_column].dt.year.unique()
        year_ticks = [pd.Timestamp(year=year, month=1, day=1) for year in years]
        
        # Get date range for x-axis
        date_min = combined_dataset[date_column].min()
        date_max = combined_dataset[date_column].max()

        # Update the base trace with hover information
        base_trace = go.Scatter3d(
            x=dates_dt_smooth,
            y=y_smooth,
            z=z_smooth,
            mode='lines',
            line=dict(width=4, color=dates_smooth, colorscale='Viridis'),
            showlegend=False,
            hovertemplate=(
                "<b>Fecha:</b> %{x|%Y-%m-%d}<br>" +
                f"<b>{y_axis}:</b> %{{y:.2f}}<br>" +
                f"<b>{z_axis}:</b> %{{z:.2f}}<extra></extra>"
            )
        )

        # Update common_layout with left-aligned button
        common_layout = dict(
            scene=dict(
                xaxis_title="Fecha",
                yaxis_title=y_axis,
                zaxis_title=z_axis,
                # Set fixed and equal ranges for axes
                xaxis=dict(
                    range=[date_min, date_max],
                    ticktext=years,
                    tickvals=year_ticks,
                    tickformat='%Y',
                    dtick="M12",
                    tickmode='array',
                    tickangle=45,
                    tickfont=dict(size=8)
                ),
                yaxis=dict(
                    range=[0, 100],
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    tickfont=dict(size=8)
                ),
                zaxis=dict(
                    range=[0, 100],
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    tickfont=dict(size=8)
                ),
                # Add aspectratio to ensure equal scaling
                aspectratio=dict(x=1, y=1, z=1),
                # Add aspectmode to force the ratio
                aspectmode='cube'
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    buttons=[
                        dict(
                            label='Restablecer Vista',
                            method='relayout',
                            args=[{'scene.camera': dict(
                                eye=dict(x=0, y=0, z=3),
                                up=dict(x=0, y=1, z=0)
                            )}]
                        )
                    ],
                    x=0.1,
                    y=1.1,
                    xanchor='left',
                    yanchor='top',
                    font=dict(size=8)
                )
            ]
        )

        # Left viewport (X-Y frontal view)
        fig1 = go.Figure(data=[base_trace])
        fig1.update_layout(
            title=dict(
                text=f"Vista {y_axis}",
                font=dict(size=12),
                x=0.5,
                xanchor='center'
            ),
            scene_camera=dict(
                eye=dict(x=0, y=0, z=3),  # Changed from 12 to 3
                up=dict(x=0, y=1, z=0)
            ),
            **common_layout
        )
        
        # Middle viewport (Isometric view)
        fig2 = go.Figure(data=[base_trace])
        fig2.update_layout(
            title=dict(
                text="Vista isométrica",
                font=dict(size=12),
                x=0.5,
                xanchor='center'
            ),
            scene_camera=dict(
                eye=dict(x=2.25, y=2.25, z=2.25),  # Changed from 9 to 2.25
                up=dict(x=0, y=0, z=1)
            ),
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    buttons=[
                        dict(
                            label='Restablecer Vista',
                            method='relayout',
                            args=[{'scene.camera': dict(
                                eye=dict(x=2.25, y=2.25, z=2.25),  # Match the new camera position
                                up=dict(x=0, y=0, z=1)
                            )}]
                        )
                    ],
                    x=0.1,
                    y=1.1,
                    xanchor='left',
                    yanchor='top',
                    font=dict(size=8)
                )
            ],
            **{k:v for k,v in common_layout.items() if k != 'updatemenus'}
        )
        
        # Right viewport (X-Z frontal view)
        fig3 = go.Figure(data=[base_trace])
        fig3.update_layout(
            title=dict(
                text=f"Vista {z_axis}",
                font=dict(size=12),
                x=0.5,
                xanchor='center'
            ),
            scene_camera=dict(
                eye=dict(x=0, y=-3, z=0),  # Changed from -12 to -3
                up=dict(x=0, y=0, z=1)
            ),
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    buttons=[
                        dict(
                            label='Restablecer Vista',
                            method='relayout',
                            args=[{'scene.camera': dict(
                                eye=dict(x=0, y=-3, z=0),  # Match the new camera position
                                up=dict(x=0, y=0, z=1)
                            )}]
                        )
                    ],
                    x=0.1,
                    y=1.1,
                    xanchor='left',
                    yanchor='top',
                    font=dict(size=8)
                )
            ],
            **{k:v for k,v in common_layout.items() if k != 'updatemenus'}
        )

        return fig1, fig2, fig3, new_frequency

    except Exception as e:
        print(f"Error in 3D graph update: {str(e)}")  # For debugging
        # Return empty figures with error message
        empty_fig = {
            'data': [],
            'layout': {
                'title': {
                    'text': f'Error: {str(e)}',
                    'font': {'size': 12}
                },
                'height': 600
            }
        }    
        return empty_fig, empty_fig, empty_fig, current_frequency

# Add new callback for toggle button (add this near your other callbacks)
@app.callback(
    Output("collapse-table", "is_open"),
    [Input("toggle-table-button", "n_clicks")],
    [State("collapse-table", "is_open")],
)
def toggle_table(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Update the callback for button toggles
@app.callback(
    [Output(f"toggle-source-{id}", "outline") for id in dbase_options.keys()] +
    [Output(f"toggle-source-{id}", "style") for id in dbase_options.keys()] +
    [Output("select-all-button", "outline")],
    [Input(f"toggle-source-{id}", "n_clicks") for id in dbase_options.keys()] +
    [Input("select-all-button", "n_clicks")],
    [State(f"toggle-source-{id}", "outline") for id in dbase_options.keys()] +
    [State("select-all-button", "outline")]
)
def toggle_sources(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Initial load - all sources unselected
        new_states = [True] * len(dbase_options)  # All buttons start as outlined
        styles = [
            {
                'fontSize': '12px',
                'borderColor': color_map[source],
                'color': color_map[source],
                'backgroundColor': 'transparent'
            }
            for source in dbase_options.values()
        ]
        return new_states + styles + [True]
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Get current states from the State inputs
    current_states = list(args[len(dbase_options)+1:-1])  # Extract current states from args
    
    if button_id == "select-all-button":
        # Toggle all sources based on current select-all state
        select_all_state = args[-1]  # Get current select-all button state
        new_states = [not select_all_state] * len(dbase_options)  # Invert the state for all buttons
    else:
        # Individual button toggle
        source_id = int(button_id.split('-')[-1])
        clicked_index = list(dbase_options.keys()).index(source_id)
        new_states = list(current_states)
        new_states[clicked_index] = not new_states[clicked_index]
    
    # Ensure at least one source is selected
    if all(new_states):
        if button_id != "select-all-button":
            clicked_index = list(dbase_options.keys()).index(int(button_id.split('-')[-1]))
            new_states[clicked_index] = False
    
    # Update button styles based on new states
    styles = []
    for i, source in enumerate(dbase_options.values()):
        if new_states[i]:  # Button is unselected (outlined)
            style = {
                'fontSize': '12px',
                'borderColor': color_map[source],
                'color': color_map[source],
                'backgroundColor': 'transparent'
            }
        else:  # Button is selected (filled)
            style = {
                'fontSize': '12px',
                'borderColor': color_map[source],
                'color': 'white',
                'backgroundColor': color_map[source]
            }
        styles.append(style)
    
    # Update select-all button state
    new_select_all_state = all(new_states)  # True if all buttons are unselected
    
    return new_states + styles + [new_select_all_state]

# Add these new Outputs to store the selected sources
@app.callback(
    [Output('correlation-graph', 'figure'),
     Output('y-axis-dropdown', 'value'),  # Add this to update the dropdown
     Output('z-axis-dropdown', 'value')], # Add this to update the dropdown
    [Input('keyword-dropdown', 'value'),
     Input('correlation-graph', 'clickData')] +  # Add clickData input
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_correlation_heatmap(selected_keyword, click_data, *button_states):
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not selected_keyword or len(selected_sources) < 2:
        return {}, dash.no_update, dash.no_update

    # Get the data
    datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
    combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
    
    # Reset index and format date
    combined_dataset = combined_dataset.reset_index()
    date_column = combined_dataset.columns[0]
    combined_dataset = combined_dataset.drop(columns=[date_column])
    
    # Calculate correlation matrix
    corr_matrix = combined_dataset.corr().round(2)  # Round to 2 decimals
    
    # Create custom colorscale with diverging colors
    colorscale = [
        [0.0, 'rgb(49,54,149)'],      # dark blue for -1
        [0.125, 'rgb(69,117,180)'],   # blue
        [0.25, 'rgb(116,173,209)'],   # light blue
        [0.375, 'rgb(171,217,233)'],  # very light blue
        [0.5, 'rgb(255,255,255)'],    # white for 0
        [0.625, 'rgb(253,174,97)'],   # light orange
        [0.75, 'rgb(244,109,67)'],    # orange
        [0.875, 'rgb(215,48,39)'],    # red-orange
        [1.0, 'rgb(165,0,38)']        # dark red for 1
    ]
    
    # Create heatmap
    heatmap = go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale=colorscale,
        zmin=-1,     # Set minimum to -1
        zmax=1,      # Set maximum to 1
        zmid=0,      # Set middle point to 0
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='%{x}<br>%{y}<br>Correlación: %{z:.2f}<extra></extra>'
    )

    # Create layout
    layout = go.Layout(
        title=dict(
            text='Matriz de Correlación',
            x=0.5,
            font=dict(size=12)
        ),
        # Remove fixed width
        height=400,
        autosize=True,  # Add this
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=8),
            title=None
        ),
        yaxis=dict(
            tickfont=dict(size=8),
            title=None
        ),
        margin=dict(l=50, r=50, t=50, b=80)
    )

    fig = go.Figure(data=[heatmap], layout=layout)
    
    # Add color bar title
    fig.update_traces(
        colorbar=dict(
            title=dict(
                text="Correlación",
                font=dict(size=10)
            ),
            tickfont=dict(size=8),
            tickformat='.2f',
            # Add ticks for better readability of the scale
            ticks="outside",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.00", "-0.50", "0.00", "0.50", "1.00"]
        )
    )

    # Get selected sources from click data
    new_y_axis = dash.no_update
    new_z_axis = dash.no_update
    
    if click_data:
        x_source = click_data['points'][0]['x']
        y_source = click_data['points'][0]['y']
        if x_source != y_source:  # Only update if different sources are selected
            new_y_axis = x_source
            new_z_axis = y_source

    return fig, new_y_axis, new_z_axis

@app.callback(
    Output('regression-graph', 'figure'),
    [Input('y-axis-dropdown', 'value'),
     Input('z-axis-dropdown', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_regression_plot(y_axis, z_axis, selected_keyword, *button_states):
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}

    try:
        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        # Reset index and format date
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset = combined_dataset.drop(columns=[date_column])
        
        # Get data for the selected sources and handle NaN values
        x_data = combined_dataset[y_axis].dropna()
        y_data = combined_dataset[z_axis].dropna()
        
        # Ensure both series have the same index after dropping NaN values
        common_index = x_data.index.intersection(y_data.index)
        x_data = x_data[common_index]
        y_data = y_data[common_index]
        
        if len(x_data) < 2 or len(y_data) < 2:
            raise ValueError("Insuficientes datos después de la limpieza")

        # Calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
        line_x = np.array([min(x_data), max(x_data)])
        line_y = slope * line_x + intercept
        r_squared_linear = r_value ** 2
        equation_linear = f'y = {slope:.2f}x + {intercept:.2f}'
        
        # Calculate polynomial regression (degree 2)
        X = x_data.values.reshape(-1, 1)
        poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
        poly_model.fit(X, y_data)
        
        # Generate points for smooth polynomial curve
        X_smooth = np.linspace(min(x_data), max(x_data), 100).reshape(-1, 1)
        y_smooth = poly_model.predict(X_smooth)
        
        # Calculate R² for polynomial regression
        y_pred_poly = poly_model.predict(X)
        r_squared_poly = np.corrcoef(y_data, y_pred_poly)[0,1]**2
        
        # Get polynomial coefficients
        coeffs = poly_model.named_steps['linearregression'].coef_
        intercept_poly = poly_model.named_steps['linearregression'].intercept_
        equation_poly = f'y = {coeffs[2]:.2f}x² + {coeffs[1]:.2f}x + {intercept_poly:.2f}'
        
        # Create scatter plot with both regression lines
        fig = go.Figure()
        
        # Add scatter points
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            name='Datos',
            marker=dict(
                size=8,
                color='rgba(230,85,13,0.5)',
                line=dict(
                    color='rgba(230,85,13,1)',
                    width=1
                )
            ),
            hovertemplate=(
                f"{y_axis}: %{{x:.2f}}<br>" +
                f"{z_axis}: %{{y:.2f}}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Add linear regression line
        fig.add_trace(go.Scatter(
            x=line_x,
            y=line_y,
            mode='lines',
            name='Regresión Lineal',
            line=dict(
                color='rgba(166,54,3,1)',
                width=2,
                dash='solid'
            ),
            hovertemplate=(
                "Regresión Lineal<br>" +
                f"{equation_linear}<br>" +
                f"R² = {r_squared_linear:.3f}" +
                "<extra></extra>"
            )
        ))
        
        # Add polynomial regression line
        fig.add_trace(go.Scatter(
            x=X_smooth.flatten(),
            y=y_smooth,
            mode='lines',
            name='Regresión Polinomial',
            line=dict(
                color='rgba(0,100,80,1)',
                width=2,
                dash='dash'
            ),
            hovertemplate=(
                "Regresión Polinomial<br>" +
                f"{equation_poly}<br>" +
                f"R² = {r_squared_poly:.3f}" +
                "<extra></extra>"
            )
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Análisis de Regresión<br>' +
                     f'<sup>R² Lineal = {r_squared_linear:.3f}, ' +
                     f'R² Polinomial = {r_squared_poly:.3f}</sup>',
                x=0.5,
                font=dict(size=12)
            ),
            autosize=True,  # Add this
            height=400,
            margin=dict(l=50, r=50, t=50, b=100),
            # Remove fixed width
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.35,
                xanchor="center",
                x=0.5
            ),
            hovermode='closest',
            plot_bgcolor='white'
        )

        return fig

    except Exception as e:
        # Return an error message figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error en el análisis de regresión: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        fig.update_layout(
            height=400,  # Increased from 300
            width=500,  # Increased from 450
            title=dict(
                text='Error en el Análisis de Regresión',
                x=0.5,
                font=dict(size=12)
            )
        )
        return fig

@app.callback(
    [Output('forecast-graph-1', 'figure'),
     Output('forecast-graph-2', 'figure')],
    [Input('y-axis-dropdown', 'value'),
     Input('z-axis-dropdown', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_forecast_plots(y_axis, z_axis, selected_keyword, *button_states):
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}, {}

    try:
        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        # Reset index and format date
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Create ARIMA forecast for first source (y_axis)
        fig1 = create_arima_forecast(y_axis, selected_keyword, selected_sources, combined_dataset)
        
        # Create ARIMA forecast for second source (z_axis)
        fig2 = create_arima_forecast(z_axis, selected_keyword, selected_sources, combined_dataset)
        
        return fig1, fig2
        
    except Exception as e:
        print(f"Error in forecast plots: {str(e)}")
        # Return empty figures with error message
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en el pronóstico: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=400,
            width=500,
            title=dict(
                text='Error en el Pronóstico',
                x=0.5,
                font=dict(size=12)
            )
        )    
        return error_fig, error_fig

def create_arima_forecast(source_column, selected_keyword, selected_sources, combined_dataset):
    try:
        # Get the original color for the source from color_map
        source_color = color_map.get(source_column, 'blue')
        
        # Define contrasting colors for predictions and forecasts
        # Using colors from the existing color palette
        prediction_color = '#8c564b'  # brown
        forecast_color = '#e377c2'    # pink
        
        ts_data = combined_dataset[source_column].dropna()
        dates = combined_dataset['Fecha'].loc[ts_data.index]
        
        if len(ts_data) < 24:
            raise ValueError(f"Insuficientes datos para pronosticar {source_column}")

        display_start_idx = int(len(ts_data) * 0.75)
        train_size = len(ts_data) - 12  # Use last 12 months for testing
        train = ts_data[:train_size]
        test = ts_data[train_size:]
        train_dates = dates[:train_size]
        test_dates = dates[train_size:]

        # Find best ARIMA parameters using training data
        auto_model = auto_arima(
            train,
            start_p=0, start_q=0,
            max_p=3, max_q=3,
            m=12,
            seasonal=False,
            d=None,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )

        p, d, q = auto_model.order
        model = ARIMA(train, order=(p, d, q))
        model_fit = model.fit()
        
        # Make predictions for test period
        predictions = model_fit.forecast(steps=len(test))
        
        # Calculate RMSE using test data
        mse = mean_squared_error(test, predictions)
        rmse = np.sqrt(mse)
        
        # Fit model on full dataset for future predictions
        full_model = ARIMA(ts_data, order=(p, d, q))
        full_model_fit = full_model.fit()
        
        # Make future predictions
        future_steps = 12
        future_forecast = full_model_fit.forecast(steps=future_steps)
        
        # Generate future dates
        last_date = dates.iloc[-1]
        future_dates = pd.date_range(start=last_date, periods=future_steps + 1, freq='M')[1:]
        
        # Create figure with new colors
        fig = go.Figure()
        
        # Actual data with original source color
        fig.add_trace(go.Scatter(
            x=dates[display_start_idx:],
            y=ts_data[display_start_idx:],
            mode='lines',
            name='Datos Actuales',
            line=dict(color=source_color, width=1)
        ))
        
        # Test predictions with prediction color
        fig.add_trace(go.Scatter(
            x=test_dates,
            y=predictions,
            mode='lines',
            name='Predicción',
            line=dict(color=prediction_color, width=3)  # Changed from width=1 to width=3
        ))
        
        # Future forecast with forecast color
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_forecast,
            mode='lines',
            name='Pronóstico',
            line=dict(color=forecast_color, width=3)  # Changed from width=1 to width=3
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Pronóstico ARIMA ({p},{d},{q}) para {source_column}<br>' +
                     f'<sup>RMSE: {rmse:.2f}</sup>',
                x=0.5,
                font=dict(size=12)
            ),
            autosize=True,  # Add this
            height=400,
            margin=dict(l=50, r=50, t=50, b=100),
            # Remove fixed width
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.35,
                xanchor="center",
                x=0.5
            ),
            hovermode='x unified',
            plot_bgcolor='white'
        )
        
        return fig

    except Exception as e:
        print(f"Error in create_arima_forecast: {str(e)}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en el pronóstico: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=400,
            width=500,
            title=dict(
                text='Error en el Pronóstico',
                x=0.5,
                font=dict(size=12)
            )
        )
        return error_fig

@app.callback(
    Output('time-series-graph', 'figure'),
    [Input('y-axis-dropdown', 'value'),
    Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_time_series(y_axis, selected_keyword, *button_states):
    try:
        # Convert button states to selected sources
        selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
        
        if not all([y_axis, selected_keyword]) or not selected_sources:
            return {}

        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        
        # Create figure
        fig = go.Figure()
        
        # Process each source separately instead of using combined dataset
        for source in selected_sources:
            if source in datasets_norm and not datasets_norm[source].empty:
                df = datasets_norm[source].copy()
                df.index = pd.to_datetime(df.index)
                
                # Find the column that matches y_axis for this source
                matching_cols = [col for col in df.columns if y_axis in col]
                if matching_cols:
                    col_name = matching_cols[0]
                    
                    # Add trace for this source
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[col_name],
                        name=f"{source}",
                        mode='lines',
                        line=dict(width=2)
                    ))

        # Update layout
        fig.update_layout(
            height=300,
            autosize=True,  # Add this for responsiveness
            title=dict(
                text='Tendencia a través del tiempo',
                x=0.5,
                font=dict(size=12)
            ),
            xaxis=dict(
                title='Fecha',
                tickfont=dict(size=10),
                titlefont=dict(size=10)
            ),
            yaxis=dict(
                title='Frecuencia normalizada',
                tickfont=dict(size=10),
                titlefont=dict(size=10)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=8)
            ),
            margin=dict(l=50, r=20, t=60, b=50)
        )
        
        return fig

    except Exception as e:
        print(f"Error in time series update: {str(e)}")  # For debugging
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        fig.update_layout(
            height=300,
            autosize=True,  # Add this for responsiveness
            title=dict(
                text='Error en la Serie de Tiempo',
                x=0.5,
                font=dict(size=12)
            )
        )
        return fig

# Add new callback for seasonal analysis graphs
@app.callback(
    [Output('seasonal-graph-1', 'figure'),
     Output('seasonal-graph-2', 'figure')],
    [Input('y-axis-dropdown', 'value'),
     Input('z-axis-dropdown', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_seasonal_graphs(y_axis, z_axis, selected_keyword, *button_states):
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}, {}

    try:
        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        # Reset index and format date
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Create seasonal decomposition for both sources
        fig1 = create_seasonal_decomposition(y_axis, combined_dataset)
        fig2 = create_seasonal_decomposition(z_axis, combined_dataset)
        
        return fig1, fig2
        
    except Exception as e:
        print(f"Error in seasonal graphs: {str(e)}")
        # Return empty figures with error message
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en el Análisis estacional: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=600,
            width=500,
            title=dict(
                text='Error en el Análisis Estacional',
                x=0.5,
                font=dict(size=12)
            )
        )
        return error_fig, error_fig

def create_seasonal_decomposition(source_column, data):
    try:
        # Get the data for the selected source
        ts_data = data[source_column].dropna()
        dates = data['Fecha'].loc[ts_data.index]
        
        # Get the color for this source from the color_map
        line_color = color_map.get(source_column, 'blue')  # Use the source's color from color_map
        
        # Create a pandas Series with datetime index for the full dataset
        ts_series_full = pd.Series(ts_data.values, index=pd.DatetimeIndex(dates))
        
        if len(ts_series_full) < 24:
            raise ValueError(f"Insuficientes datos para descompocision estacional {source_column}")

        # Use the imported seasonal_decompose function on the full dataset
        decomposition_full = seasonal_decompose(ts_series_full, period=12, model='additive')
        
        # Filter the data to include only the last 4 years for the seasonal component
        last_4_years = dates.max() - pd.DateOffset(years=4)
        ts_data_4_years = ts_data[dates >= last_4_years]
        dates_4_years = dates[dates >= last_4_years]
        
        # Create a pandas Series with datetime index for the last 4 years
        ts_series_4_years = pd.Series(ts_data_4_years.values, index=pd.DatetimeIndex(dates_4_years))
        
        # Use the imported seasonal_decompose function on the last 4 years
        decomposition_4_years = seasonal_decompose(ts_series_4_years, period=12, model='additive')
        
        # Create subplots with reduced vertical spacing
        fig = make_subplots(
            rows=4, 
            cols=1,
            subplot_titles=(
                'Serie Original', 
                'Tendencia', 
                'Patrón Estacional', 
                'Residuos'
            ),
            vertical_spacing=0.067
        )
        
        # Add traces for each component using the full dataset and the source color
        fig.add_trace(
            go.Scatter(
                x=dates, 
                y=ts_series_full.values,
                mode='lines',
                name='Original',
                line=dict(color=line_color, width=1)  # Use source color
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=decomposition_full.trend,
                mode='lines',
                name='Tendencia',
                line=dict(color=line_color, width=1)  # Use source color
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates_4_years,
                y=decomposition_4_years.seasonal,
                mode='lines',
                name='Estacional',
                line=dict(color=line_color, width=1)  # Use source color
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=decomposition_full.resid,
                mode='lines',
                name='Residuos',
                line=dict(color=line_color, width=1)  # Use source color
            ),
            row=4, col=1
        )
        
        # Rest of the function remains the same...
        
        # Update layout with adjusted margins and height
        fig.update_layout(
            height=1200,
            autosize=True,  # Add this
            # Remove fixed width
            title=dict(
                text=f'Descomposición Estacional de {source_column}',
                x=0.5,
                font=dict(size=12)
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=75, b=25)
        )
        
        # Update y-axes titles
        fig.update_yaxes(title_text="Original", row=1, col=1, titlefont=dict(size=10))
        fig.update_yaxes(title_text="Tendencia", row=2, col=1, titlefont=dict(size=10))
        fig.update_yaxes(title_text="Estacional", row=3, col=1, titlefont=dict(size=10))
        fig.update_yaxes(title_text="Residuos", row=4, col=1, titlefont=dict(size=10))
        
        # Update x-axes
        for i in range(1, 5):
            fig.update_xaxes(
                tickformat='%Y',
                dtick='M12',
                tickangle=45,
                tickfont=dict(size=8),
                row=i,
                col=1
            )
        
        # Specifically update the x-axis for the seasonal component to include month labels every 3 months
        # and year labels only in January
        start_date = dates_4_years.min()
        if start_date.month != 1:
            start_date = pd.Timestamp(year=start_date.year + 1, month=1, day=1)
        
        tickvals = pd.date_range(start=start_date, end=dates_4_years.max(), freq='3MS')
        ticktext = [date.strftime('%b %Y') if date.month == 1 else date.strftime('%b') for date in tickvals]
        
        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=45,
            tickfont=dict(size=8),
            row=3,
            col=1
        )
        
        return fig

    except Exception as e:
        print(f"Error in create_seasonal_decomposition: {str(e)}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en la descomposición estacional: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=600,
            width=500,
            title=dict(
                text='Error en la Descomposición Estacional',
                x=0.5,
                font=dict(size=12)
            )
        )
        return error_fig

# Add these imports at the top with the other imports
from scipy.fft import fft, fftfreq
import numpy as np

# Add this callback before the forecast callback
@app.callback(
    [Output('fourier-graph-1', 'figure'),
     Output('fourier-graph-2', 'figure')],
    [Input('y-axis-dropdown', 'value'),
    Input('z-axis-dropdown', 'value'),
    Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_fourier_plots(y_axis, z_axis, selected_keyword, *button_states):
    # Convert button states to selected sources
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]
    
    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}, {}

    try:
        # Get the data
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
        
        # Reset index and format date
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Create Fourier analysis for both sources
        fig1 = create_fourier_analysis(y_axis, combined_dataset)
        fig2 = create_fourier_analysis(z_axis, combined_dataset)
        
        return fig1, fig2
        
    except Exception as e:
        print(f"Error in Fourier analysis: {str(e)}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en el análisis de Fourier: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=300,
            width=500,
            title=dict(
                text='Error en el Análisis de Fourier',
                x=0.5,
                font=dict(size=12)
            )
        )
        return error_fig, error_fig

def create_fourier_analysis(source_column, data):
    try:
        # Get the data for the selected source
        ts_data = data[source_column].dropna()
        
        if len(ts_data) < 24:  # Need at least 2 years of data
            raise ValueError(f"Insuficientes datos para análisis de Fourier {source_column}")

        # Perform FFT
        yf = fft(ts_data.values)
        N = len(ts_data)
        T = 1.0 / 12.0  # assuming monthly data
        xf = fftfreq(N, T)[:N//2]
        
        # Convert frequency to periods (in months)
        periods = 12 / xf[1:]  # Skip the first frequency (0)
        power = 2.0/N * np.abs(yf[1:N//2])  # Skip the first frequency
        
        # Filter out noise by keeping only significant periods
        # Calculate threshold as a percentage of maximum power
        threshold = np.max(power) * 0.05  # Keep components with >5% of max power
        significant_mask = power > threshold
        
        # Keep only significant periods and their corresponding power
        significant_periods = periods[significant_mask]
        significant_power = power[significant_mask]
        
        # Sort by period for better visualization
        sort_idx = np.argsort(significant_periods)
        significant_periods = significant_periods[sort_idx]
        significant_power = significant_power[sort_idx]
        
        # Filter out very close periods to reduce clutter
        MIN_PERIOD_DIFF = 2  # minimum difference in months between displayed periods
        filtered_indices = []
        last_period = 0
        for i, period in enumerate(significant_periods):
            if i == 0 or period - last_period >= MIN_PERIOD_DIFF:
                filtered_indices.append(i)
                last_period = period
        
        # Apply filtering
        significant_periods = significant_periods[filtered_indices]
        significant_power = significant_power[filtered_indices]

        # Helper function to convert months to year-month format (simplified)
        def months_to_text(months):
            years = int(months) // 12
            remaining_months = int(months) % 12
            if years > 0 and remaining_months > 0:
                if remaining_months >= 6:
                    return f"{years+1}a"
                return f"{years}a"
            elif years > 0:
                return f"{years}a"
            else:
                return f"{remaining_months}m"

        # Create the figure
        fig = go.Figure()
        
        # Add the power spectrum as bars
        fig.add_trace(go.Bar(
            x=significant_periods,
            y=significant_power,
            name='Espectro de Potencia',
            marker_color=color_map.get(source_column, 'blue'),
            hovertemplate=(
                "Período: %{x:.1f} meses<br>" +
                "(%{customdata[1]})<br>" +
                "Potencia: %{y:.2f}<br>" +
                "Frecuencia: %{customdata[0]:.3f} ciclos/mes<extra></extra>"
            ),
            customdata=list(zip(1/significant_periods, 
                              [months_to_text(p) for p in significant_periods]))
        ))
        
        # Add markers only for top peaks to reduce clutter
        peak_threshold = np.max(significant_power) * 0.5  # Increased threshold to 50%
        peak_mask = significant_power > peak_threshold
        
        # Ensure minimum distance between peaks
        peak_indices = np.where(peak_mask)[0]
        filtered_peak_indices = []
        last_peak_period = 0
        for idx in peak_indices:
            if idx == peak_indices[0] or significant_periods[idx] - last_peak_period >= MIN_PERIOD_DIFF * 2:
                filtered_peak_indices.append(idx)
                last_peak_period = significant_periods[idx]
        
        peak_mask = np.zeros_like(peak_mask)
        peak_mask[filtered_peak_indices] = True
        
        fig.add_trace(go.Scatter(
            x=significant_periods[peak_mask],
            y=significant_power[peak_mask],
            mode='markers+text',
            marker=dict(
                symbol='star',
                size=12,
                color='red',
                line=dict(color='black', width=1)
            ),
            text=[months_to_text(p) for p in significant_periods[peak_mask]],
            textposition="top center",
            showlegend=False,
            hovertemplate=(
                "Período Principal: %{x:.1f} meses<br>" +
                "(%{text})<br>" +
                "Potencia: %{y:.2f}<extra></extra>"
            )
        ))
        
        # Update layout with improved aesthetics and reduced clutter
        fig.update_layout(
            title=dict(
                text=f'Análisis de Fourier - {source_column}',
                x=0.5,
                font=dict(size=12)
            ),
            autosize=True,  # Keep this for responsiveness
            height=400,
            xaxis=dict(
                title=dict(
                    text='Período (meses)',
                    font=dict(size=10)
                ),
                tickfont=dict(size=8),
                type='log',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                range=[np.log10(min(significant_periods)), np.log10(max(significant_periods))],
                dtick=0.301,
                # Show fewer tick labels
                ticktext=[months_to_text(p) for p in significant_periods[::2]],  # Show every other label
                tickvals=significant_periods[::2],
                tickmode='array',
                tickangle=45
            ),
            yaxis=dict(
                title=dict(
                    text='Potencia Espectral',
                    font=dict(size=10)
                ),
                tickfont=dict(size=8),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                rangemode='tozero'  # Start y-axis from 0
            ),
            showlegend=False,
            margin=dict(
                l=50,
                r=50,
                t=50,
                b=100         # Increased bottom margin for rotated labels
            ),
            plot_bgcolor='white',
            bargap=0.2
        )
        
        # Add annotations only for top peaks
        top_n = min(3, sum(peak_mask))  # Limit to 3 or fewer annotations
        top_indices = np.argsort(significant_power[peak_mask])[-top_n:]
        peak_periods = significant_periods[peak_mask]
        peak_powers = significant_power[peak_mask]
        
        for i, idx in enumerate(top_indices):
            period = peak_periods[idx]
            power = peak_powers[idx]
            fig.add_annotation(
                x=period,
                y=power,
                text=months_to_text(period),
                yshift=10 + (i * 20),
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor=color_map.get(source_column, 'blue'),
                font=dict(size=8)
            )
        
        return fig

    except Exception as e:
        print(f"Error in create_fourier_analysis: {str(e)}")
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Error en el análisis de Fourier: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=12, color="red")
        )
        error_fig.update_layout(
            height=300,
            width=500,
            title=dict(
                text='Error en el Análisis de Fourier',
                x=0.5,
                font=dict(size=12)
            )
        )
        return error_fig

# Add this section before the Pronóstico section
html.Div([
    html.H6("Análisis de Fourier", style={
        'fontSize': '16px', 
        'textAlign': 'center',
        'width': '100%',
        'margin': '20px auto'  # Changed from 50px to 200px for top margin
    }),
    # Container for Fourier graphs side by side
    html.Div([
        # Left Fourier graph
        html.Div([
            dcc.Loading(
                id="loading-fourier-1",
                type="default",
                children=dcc.Graph(
                    id='fourier-graph-1', 
                    style={
                        'height': '400px',
                        'width': '100%'
                    }, 
                    config={'displaylogo': False}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        # Right Fourier graph
        html.Div([
            dcc.Loading(
                id="loading-fourier-2",
                type="default",
                children=dcc.Graph(
                    id='fourier-graph-2', 
                    style={
                        'height': '400px',
                        'width': '100%'
                    }, 
                    config={'displaylogo': False}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={
        'width': '100%',
        'display': 'flex',
        'flexDirection': 'row'  # Changed from 'column' to 'row'
    }),
], style={
    'width': '100%', 
    'marginBottom': '50px',
    'marginTop': '50px'  # Changed from 150px to 50px to move section up
}),

# Add divider between sections
html.Hr(style={
    'border': 'none',
    'height': '2px',
    'backgroundColor': '#dee2e6',
    'margin': '30px 0',
    'width': '100%',
}),

# Section 3: Seasonal Analysis with consistent spacing
html.Div([
    html.H6("Análisis Estacional", style={
        'fontSize': '20px', 
        'textAlign': 'center',
        'marginTop': '10px',
        'marginBottom': '20px'  # Consistent bottom margin
    }),
    # Container for two seasonal decomposition graphs side by side
    html.Div([
        # Left seasonal graph
        html.Div([
            dcc.Loading(
                id="loading-seasonal-1",
                type="default",
                children=dcc.Graph(
                    id='seasonal-graph-1', 
                    style={'height': '400px', 'width': '100%'},  # Reduced from 600px to 400px
                    config={'displaylogo': False, 'responsive': True}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right seasonal graph
        html.Div([
            dcc.Loading(
                id="loading-seasonal-2",
                type="default",
                children=dcc.Graph(
                    id='seasonal-graph-2', 
                    style={'height': '400px', 'width': '100%'},  # Reduced from 600px to 400px
                    config={'displaylogo': False, 'responsive': True}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'width': '100%',
        'marginBottom': '50px'  # Consistent bottom margin
    }),
]),

# Add horizontal divider with consistent spacing
html.Hr(style={
    'border': 'none',
    'height': '3px',
    'backgroundColor': '#dee2e6',
    'margin': '50px 0',  # Consistent vertical margins
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'width': '100%'
}),

# Section 4: Pronóstico with consistent spacing
html.Div([
    html.H6("Pronóstico", style={
        'fontSize': '20px', 
        'textAlign': 'center',
        'marginTop': '10px',
        'marginBottom': '20px'  # Consistent bottom margin
    }),
    # Container for two ARIMA graphs side by side
    html.Div([
        # Left ARIMA graph
        html.Div([
            dcc.Loading(
                id="loading-forecast-1",
                type="default",
                children=dcc.Graph(
                    id='forecast-graph-1', 
                    style={'height': '400px', 'width': '100%'},  # Increased from 300px to 400px
                    config={'displaylogo': False, 'responsive': True}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right ARIMA graph
        html.Div([
            dcc.Loading(
                id="loading-forecast-2",
                type="default",
                children=dcc.Graph(
                    id='forecast-graph-2', 
                    style={'height': '400px', 'width': '100%'},  # Increased from 300px to 400px
                    config={'displaylogo': False, 'responsive': True}
                ),
            ),
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'width': '100%',
        'marginBottom': '50px'  # Consistent bottom margin
    }),
])

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',  # Makes the server externally visible
        port=8050,        # You can change this port if needed
        use_reloader=True
    )

# if __name__ == '__main__':
#     app.run_server(
#         debug=False,          # Disable debug mode for security
#         host='0.0.0.0',      # Makes the server externally visible
#         port=8050,           # Port number
#         use_reloader=False   # Disable auto-reloader for stability
#     )