import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from correlation import get_all_keywords, get_file_data2, create_combined_dataset  # Update import
import pandas as pd
import plotly.graph_objects as go  # Add this import
import numpy as np  # Add this import
from scipy.interpolate import CubicSpline

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    title='Management Tools Analysis'
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
        
        # Keyword dropdown (single selection)
        html.Div([
            html.Label("Seleccione una Herramienta:", style={'fontSize': '12px'}),
            dcc.Dropdown(
                id='keyword-dropdown',
                options=[
                    {'label': keyword, 'value': keyword} 
                    for keyword in get_all_keywords()
                ],
                value=get_all_keywords()[0] if get_all_keywords() else None,
                placeholder="Seleccione una Herramienta Gerencial",
                className="mb-4",
                style={'fontSize': '12px'}
            ),
            # Add validation message div for keywords
            html.Div(id='keyword-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
        
        # Update the dropdown component
        html.Div([
            html.Label("Seleccione las Fuentes de Datos: ", className="form-label", style={'fontSize': '12px'}),
            # Replace dropdown with button group
            html.Div([
                dbc.Button(
                    source,
                    id=f"toggle-source-{id}",
                    color="primary",
                    outline=True,  # Start with outline style
                    size="sm",
                    className="me-2 mb-2",
                    style={'fontSize': '12px'}
                ) for id, source in dbase_options.items()
            ], id='source-buttons-container'),
            # Add validation message div
            html.Div(id='datasources-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
    ],
    style={
        'background-color': '#f8f9fa',
        'padding': '20px',
        'height': '100vh',
        'position': 'fixed',  # Make sidebar fixed
        'width': 'inherit',   # Inherit width from parent
        'overflow-y': 'auto', # Add scroll if content is too long
        'top': 0,            # Align to top
        'left': 0,           # Align to left
        'bottom': 0,         # Extend to bottom
    }
)

# Add the membrete div before the main layout
membrete = html.Div(
    [
        html.Div([
            html.H3("Análisis Estadístico Correlacional: Técnicas y Herramientas Gerenciales", className="mb-0"),
            html.H5("Enfoque Central de la Investigación Doctoral: Dicotomía Ontológica en las 'Modas Gerenciales'", className="mb-0"),
            html.P([
                "Autor de la Tesis: ", html.B("Diomar Anez"), " | Desarrollador en Python: ", html.B("Dimar Anez")
            ], className="mb-0"),
            html.P([
                "Equipo de desarrollo: ",
                html.A("Wise Connex", href="http://wiseconnex.com", target="_blank"),
                " - (c)2024 | Code: ",
                html.A("https://github.com/Wise-Connex/Management-Tools-Analysis.git", 
                      href="https://github.com/Wise-Connex/Management-Tools-Analysis.git",
                      target="_blank")
            ], className="mb-0"),
        ])
    ],
    style={
        'position': 'sticky',  # Make it sticky
        'top': 0,             # Stick to top
        'zIndex': 1000,       # Ensure it stays on top of other content
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
            html.Div(id='main-title', style={'fontSize': '30px', 'marginBottom': '15px'}),
            # Add the time range buttons to the main layout
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
            # Main content div
            html.Div(id='main-content', className="w-100")
        ], width=10, className="px-4")
    ], style={'height': '100vh'})
], fluid=True, className="px-0")

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
            dcc.Graph(id='3d-graph-view-1', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False}),
            dcc.Graph(id='3d-graph-view-2', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False}),
            dcc.Graph(id='3d-graph-view-3', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ], className="w-100") if len(selected_sources) >= 2 else html.Div()
    
    # Remove the nested callback and return the initial graphs
    return html.Div([
        # First row: Line and Bar charts
        html.Div([
            # Line chart container
            html.Div([
                dcc.Graph(
                    id='line-graph',
                    figure=fig,
                    style={'height': '520px'},
                    config={'displaylogo': False}
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
                    style={'height': '520px'},
                    config={'displaylogo': False}
                ),
            ], style={
                'width': '20%',
                'display': 'inline-block',
                'vertical-align': 'top'
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '20px'
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
                            'height': '200px',
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
                        page_size=5
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
                        value=dbase_options[selected_sources[0]] if len(selected_sources) > 0 else None,  # Prepopulate with first source
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
                        value=dbase_options[selected_sources[1]] if len(selected_sources) > 1 else None,  # Prepopulate with second source
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
                dcc.Graph(id='3d-graph-view-1', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False}),
                dcc.Graph(id='3d-graph-view-2', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False}),
                dcc.Graph(id='3d-graph-view-3', style={'height': '600px', 'width': '33%'}, config={'displaylogo': False})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
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
        'Últimos 20 años': 20,
        'Últimos 15 años': 15,
        'Últimos 10 años': 10,
        'Últimos 5 años': 5,
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
        'Últimos 20 años': 20,
        'Últimos 15 años': 15,
        'Últimos 10 años': 10,
        'Últimos 5 años': 5,
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
            'name': source,
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
                'ticktext': list(periods.keys()),
                'tickvals': [x_positions[period] for period in periods.keys()],
                'type': 'linear'  # Changed to linear for custom positioning
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
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()],
    [State('frequency-label', 'children')]
)
def update_3d_graph(y_axis, z_axis, selected_keyword, n_clicks, *args):
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
    date_column = combined_dataset.columns[0]  # Get the date column name
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
        # Group by year with different aggregations for different columns
        combined_dataset = combined_dataset.set_index(date_column)
        
        # Create aggregation dictionary
        agg_dict = {}
        for column in combined_dataset.columns:
            # Check if the column name contains 'Crossref'
            if 'Crossref' in column:
                agg_dict[column] = 'sum'  # Sum for Crossref data
            else:
                # Mean for all other sources (Google Trends, Google Books, Bain)
                agg_dict[column] = 'mean'
        
        print("Aggregation methods:", agg_dict)  # Debug print to verify aggregation methods
        
        # Apply different aggregations for different columns
        combined_dataset = combined_dataset.groupby(pd.Grouper(freq='Y')).agg(agg_dict)
        
        # Print sample of results to verify
        print("\nSample of aggregated data:")
        print(combined_dataset.head())
        
        combined_dataset = combined_dataset.reset_index()
        
        # Ensure we have data for the first day of each year
        combined_dataset[date_column] = combined_dataset[date_column].apply(
            lambda x: pd.Timestamp(year=x.year, month=1, day=1)
        )
    
    # Special handling for Crossref data
    if 'Crossref' in y_column or 'Crossref' in z_column:
        # Fill any missing values with 0 for Crossref data
        combined_dataset = combined_dataset.fillna(0)
        
        # Ensure data is properly normalized between 0 and 100
        for col in [y_column, z_column]:
            if 'Crossref' in col:
                max_val = combined_dataset[col].max()
                if max_val > 0:  # Avoid division by zero
                    combined_dataset[col] = (combined_dataset[col] / max_val) * 100

    # Convert dates to numeric values for interpolation
    dates = combined_dataset[date_column].astype(np.int64) // 10**9
    
    # Create more points for smoother interpolation
    if not is_annual:
        # More points for monthly data
        num_points = len(combined_dataset) * 100
    else:
        # Fewer points for annual data to avoid over-smoothing
        num_points = len(combined_dataset) * 12
    
    t = np.arange(len(combined_dataset))
    t_smooth = np.linspace(0, len(combined_dataset) - 1, num=num_points)
    
    # Create cubic spline interpolations with appropriate boundary conditions
    cs_dates = CubicSpline(t, dates, bc_type='natural')
    cs_y = CubicSpline(t, combined_dataset[y_column], bc_type='natural')
    cs_z = CubicSpline(t, combined_dataset[z_column], bc_type='natural')
    
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
            # Set fixed ranges for axes
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
            )
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
                            eye=dict(x=0, y=0, z=2),
                            up=dict(x=0, y=1, z=0)
                        )}]
                    )
                ],
                x=0.1,  # Changed from 0.9 to 0.1
                y=1.1,
                xanchor='left',  # Changed from 'right' to 'left'
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
            eye=dict(x=0, y=0, z=2),  # Camera looking straight at X-Y plane
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
            eye=dict(x=1.5, y=1.5, z=1.5),  # Isometric view
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
                            eye=dict(x=1.5, y=1.5, z=1.5),
                            up=dict(x=0, y=0, z=1)
                        )}]
                    )
                ],
                x=0.1,  # Changed from 0.9 to 0.1
                y=1.1,
                xanchor='left',  # Changed from 'right' to 'left'
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
            eye=dict(x=0, y=-2, z=0),  # Camera looking straight at X-Z plane
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
                            eye=dict(x=0, y=-2, z=0),
                            up=dict(x=0, y=0, z=1)
                        )}]
                    )
                ],
                x=0.1,  # Changed from 0.9 to 0.1
                y=1.1,
                xanchor='left',  # Changed from 'right' to 'left'
                yanchor='top',
                font=dict(size=8)
            )
        ],
        **{k:v for k,v in common_layout.items() if k != 'updatemenus'}
    )

    return fig1, fig2, fig3, new_frequency

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
    [Output(f"toggle-source-{id}", "outline") for id in dbase_options.keys()],
    [Input(f"toggle-source-{id}", "n_clicks") for id in dbase_options.keys()],
    [State(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def toggle_sources(*args):
    n_clicks = args[:len(dbase_options)]
    current_states = args[len(dbase_options):]
    
    # Get the button that triggered the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        # Initial load - default to Google Trends selected
        return [id != 1 for id in dbase_options.keys()]
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # Extract the ID directly from the button_id
    source_id = int(button_id.split('-')[-1])
    
    # Find the index in dbase_options that matches this ID
    clicked_index = list(dbase_options.keys()).index(source_id)
    
    # Update the states list
    new_states = list(current_states)
    new_states[clicked_index] = not new_states[clicked_index]
    
    # Ensure at least one source is selected
    if all(new_states):
        new_states[clicked_index] = False
    
    return new_states

if __name__ == '__main__':
    app.run_server(debug=True)
