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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
# Define database options as a global variable
dbase_options = {
    1: "Google Trends",
    2: "Google Books Ngrams", 
    3: "Bain - Usabilidad",
    4: "Crossref.org",
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
        
        #html.H4("Menú", className="display-6 mb-4 fs-4"),
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
            dcc.Dropdown(
                id='datasources-dropdown',
                options=[
                    {'label': source, 'value': id} 
                    for id, source in dbase_options.items()
                ],
                value=[1],  # Default to Google Trends selected
                multi=True,
                placeholder="Seleccione una o más fuentes de datos",
                className="mb-4",
                style={'fontSize': '12px'}
            ),
            # Add Select All button
            dbc.Button(
                "Seleccionar Todo",
                id="select-all-button",
                color="primary",
                size="sm",
                className="mb-2",
                style={'fontSize': '12px'}
            ),
            # Add validation message div
            html.Div(id='datasources-validation', className="text-danger", style={'fontSize': '12px'})
        ]),
    ],
    style={
        'background-color': '#f8f9fa',
        'padding': '20px',
        'height': '100vh',
    }
)

# Define the main layout
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar column - changed from width=3 to width=2 (20% of 12 columns)
        dbc.Col(sidebar, width=2, className="bg-light"),
        
        # Main content column - changed from width=9 to width=10
        dbc.Col([
            html.Div(id='main-title', style={'fontSize': '30px', 'marginBottom': '15px'}),
            # Add the time range buttons to the main layout
            html.Div([
                html.Label("Rango de tiempo:  ", style={'marginRight': '10px'}),
                dbc.ButtonGroup([
                    dbc.Button("5 años", id="btn-5y", size="sm", className="me-1", n_clicks=0),
                    dbc.Button("10 años", id="btn-10y", size="sm", className="me-1", n_clicks=0),
                    dbc.Button("15 años", id="btn-15y", size="sm", className="me-1", n_clicks=0),
                    dbc.Button("20 años", id="btn-20y", size="sm", className="me-1", n_clicks=0),
                    dbc.Button("Todo", id="btn-all", size="sm", n_clicks=0),
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
    [Input('keyword-dropdown', 'value'),
     Input('datasources-dropdown', 'value')]  # Remove line-graph relayoutData
)
def update_main_content(selected_keyword, selected_sources):
    if not selected_keyword or not selected_sources:
        return html.Div("Por favor, selecciones una Herrmienta y al menos una Fuente de Datos.")
    
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

    # Add 3D graph controls when more than 2 sources are selected
    html.Div([
        html.H6("Gráfico 3D", style={'fontSize': '12px', 'marginTop': '10px'}),
        html.Div([
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                        for src_id in selected_sources],
                placeholder="Seleccione eje Y",
                style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'fontSize': '12px'}
            ),
            dcc.Dropdown(
                id='z-axis-dropdown',
                options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                        for src_id in selected_sources],
                placeholder="Seleccione eje Z",
                style={'width': '48%', 'display': 'inline-block', 'fontSize': '12px'}
            ),
        ], style={'marginBottom': '10px'}),
        dcc.Graph(id='3d-graph', style={'height': '400px'}),
    ]),
    
    # Remove the nested callback and return the initial graphs
    return html.Div([
        # First row: Line and Bar charts
        html.Div([
            # Line chart container
            html.Div([
                dcc.Graph(
                    id='line-graph',
                    figure=fig,
                    style={'height': '520px'}
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
                    style={'height': '520px'}
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
        
        # Third row: 3D Graph (only shown when more than 2 sources selected)
        html.Div([
            html.H6("Gráfico 3D", style={'fontSize': '12px', 'marginTop': '10px'}),
            html.Div([
                dcc.Dropdown(
                    id='y-axis-dropdown',
                    options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                            for src_id in selected_sources],
                    placeholder="Seleccione eje Y",
                    style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'fontSize': '12px'}
                ),
                dcc.Dropdown(
                    id='z-axis-dropdown',
                    options=[{'label': dbase_options[src_id], 'value': dbase_options[src_id]} 
                            for src_id in selected_sources],
                    placeholder="Seleccione eje Z",
                    style={'width': '48%', 'display': 'inline-block', 'fontSize': '12px'}
                ),
            ], style={'marginBottom': '10px'}),
            dcc.Graph(
                id='3d-graph',
                style={'height': '600px'}  # Increased height for better visibility
            )
        ], className="w-100") if len(selected_sources) > 2 else html.Div()
    ])

# Move the graph update callback outside of update_main_content
@app.callback(
    [Output('line-graph', 'figure'), 
     Output('bar-graph', 'figure')],
    [Input('btn-5y', 'n_clicks'),
     Input('btn-10y', 'n_clicks'),
     Input('btn-15y', 'n_clicks'),
     Input('btn-20y', 'n_clicks'),
     Input('btn-all', 'n_clicks'),
     Input('line-graph', 'relayoutData'),
     Input('keyword-dropdown', 'value'),
     Input('datasources-dropdown', 'value')]
)
def update_graphs(n5, n10, n15, n20, nall, relayoutData, selected_keyword, selected_sources):
    global global_date_range
    
    if not selected_keyword or not selected_sources:
        return dash.no_update, dash.no_update

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

    return line_fig, bar_fig

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
    Input('datasources-dropdown', 'value')
)
def validate_datasources(selected_sources):
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

# Add new callback for 3D graph
@app.callback(
    Output('3d-graph', 'figure'),
    [Input('y-axis-dropdown', 'value'),
     Input('z-axis-dropdown', 'value'),
     Input('keyword-dropdown', 'value'),
     Input('datasources-dropdown', 'value')]
)
def update_3d_graph(y_axis, z_axis, selected_keyword, selected_sources):
    if not all([y_axis, z_axis, selected_keyword, selected_sources]):
        return {}
    
    # Get the data
    datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
    combined_dataset = create_combined_dataset(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
    
    # Reset index and format date
    combined_dataset = combined_dataset.reset_index()
    date_column = combined_dataset.columns[0]
    combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
    
    # Convert dates to numeric values for interpolation
    dates = combined_dataset[date_column].astype(np.int64) // 10**9
    
    # Create more points for smoother interpolation using cubic spline
    t = np.arange(len(combined_dataset))
    t_smooth = np.linspace(0, len(combined_dataset) - 1, num=len(combined_dataset) * 100)
    
    # Create cubic spline interpolations
    cs_dates = CubicSpline(t, dates)
    cs_y = CubicSpline(t, combined_dataset[y_axis])
    cs_z = CubicSpline(t, combined_dataset[z_axis])
    
    # Generate smooth data points
    dates_smooth = cs_dates(t_smooth)
    y_smooth = cs_y(t_smooth)
    z_smooth = cs_z(t_smooth)
    
    # Convert smooth dates back to datetime
    dates_dt_smooth = pd.to_datetime(dates_smooth * 10**9)

    # Create frames for animation
    n_frames = 50  # Number of frames for animation
    frames = []
    
    for i in range(n_frames + 1):
        # Calculate how many points to show in this frame
        points_to_show = int((i / n_frames) * len(dates_dt_smooth))
        
        frame = go.Frame(
            data=[
                # Smoothed line (animated)
                go.Scatter3d(
                    x=dates_dt_smooth[:points_to_show],
                    y=y_smooth[:points_to_show],
                    z=z_smooth[:points_to_show],
                    mode='lines',
                    line=dict(
                        width=4,
                        color=dates_smooth[:points_to_show],
                        colorscale='Viridis'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ),
                # Points (animated)
                go.Scatter3d(
                    x=combined_dataset[date_column][:points_to_show//100],
                    y=combined_dataset[y_axis][:points_to_show//100],
                    z=combined_dataset[z_axis][:points_to_show//100],
                    mode='markers',
                    marker=dict(
                        size=3,
                        color=dates[:points_to_show//100],
                        colorscale='Viridis',
                        opacity=0.8
                    ),
                    hovertemplate=
                    f'Fecha: %{{x|%Y-%m-%d}}<br>' +
                    f'{y_axis}: %{{y:.2f}}<br>' +
                    f'{z_axis}: %{{z:.2f}}<extra></extra>'
                )
            ],
            name=f'frame{i}'
        )
        frames.append(frame)

    # Determine fixed axis ranges
    x_range = [dates_dt_smooth.min(), dates_dt_smooth.max()]
    y_range = [combined_dataset[y_axis].min(), combined_dataset[y_axis].max()]
    z_range = [combined_dataset[z_axis].min(), combined_dataset[z_axis].max()]

    # Create the initial figure
    fig = go.Figure(
        data=[
            # Initial empty line
            go.Scatter3d(
                x=[dates_dt_smooth[0]],
                y=[y_smooth[0]],
                z=[z_smooth[0]],
                mode='lines',
                line=dict(
                    width=4,
                    color=[dates_smooth[0]],
                    colorscale='Viridis'
                ),
                showlegend=False,
                hoverinfo='skip'
            ),
            # Initial point
            go.Scatter3d(
                x=[combined_dataset[date_column].iloc[0]],
                y=[combined_dataset[y_axis].iloc[0]],
                z=[combined_dataset[z_axis].iloc[0]],
                mode='markers',
                marker=dict(
                    size=3,
                    color=[dates[0]],
                    colorscale='Viridis',
                    opacity=0.8
                ),
                hovertemplate=
                f'Fecha: %{{x|%Y-%m-%d}}<br>' +
                f'{y_axis}: %{{y:.2f}}<br>' +
                f'{z_axis}: %{{z:.2f}}<extra></extra>'
            )
        ],
        frames=frames
    )

    # Update layout with fixed axis ranges and animation settings
    fig.update_layout(
        title=dict(
            text='Visualización 3D de las Fuentes de Datos',
            font=dict(size=12)
        ),
        scene=dict(
            xaxis_title='Fecha',
            yaxis_title=y_axis,
            zaxis_title=z_axis,
            xaxis=dict(
                type='date',
                tickformat='%Y-%m-%d',
                range=x_range,
                autorange=False  # Disable auto-scaling
            ),
            yaxis=dict(
                range=y_range,
                autorange=False  # Disable auto-scaling
            ),
            zaxis=dict(
                range=z_range,
                autorange=False  # Disable auto-scaling
            ),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False,
        updatemenus=[
            {
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': '▶️ Play',
                        'method': 'animate',
                        'args': [
                            None,
                            {
                                'frame': {'duration': 50, 'redraw': True},
                                'fromcurrent': True,
                                'transition': {'duration': 0}
                            }
                        ]
                    },
                    {
                        'label': '⏸️ Pause',
                        'method': 'animate',
                        'args': [
                            [None],
                            {
                                'frame': {'duration': 0, 'redraw': False},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }
                        ]
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'x': 0.1,
                'y': 0,
                'xanchor': 'right'
            }
        ],
        sliders=[{
            'currentvalue': {'prefix': 'Frame: '},
            'pad': {'t': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': [
                {
                    'args': [
                        [f'frame{k}'],
                        {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }
                    ],
                    'label': str(k),
                    'method': 'animate'
                }
                for k in range(n_frames + 1)
            ]
        }]
    )

    return fig

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

if __name__ == '__main__':
    app.run_server(debug=True)
