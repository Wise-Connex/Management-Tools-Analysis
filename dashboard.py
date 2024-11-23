import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from correlation import get_all_keywords, get_file_data2, create_combined_dataset  # Update import
import pandas as pd

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Define database options as a global variable
dbase_options = {
    1: "Google Trends",
    2: "Google Books Ngrams", 
    3: "Bain - Usabilidad",
    4: "Crossref.org",
    5: "Bain - Satisfacción"
}

# Define the sidebar layout
sidebar = html.Div(
    [
        # Logo
        html.Img(
            src='assets/Management-Tools-Analysis-logo.png',
            style={
                'width': '40%',
                'margin-bottom': '20px',
                'display': 'block',
                'margin-left': 'auto',
                'margin-right': 'auto'
            }
        ),
        
        html.H4("Menú", className="display-6 mb-4"),
        html.Hr(),
        
        # Keyword dropdown (single selection)
        html.Div([
            html.Label("Seleccione una Herramienta:"),
            dcc.Dropdown(
                id='keyword-dropdown',
                options=[
                    {'label': keyword, 'value': keyword} 
                    for keyword in get_all_keywords()
                ],
                value=get_all_keywords()[0] if get_all_keywords() else None,
                placeholder="Seleccione una Herramienta Gerencial",
                className="mb-4"
            ),
            # Add validation message div for keywords
            html.Div(id='keyword-validation', className="text-danger")
        ]),
        
        # Update the dropdown component
        html.Div([
            html.Label("Seleccione las Fuentes de Datos: ", className="form-label"),
            dcc.Dropdown(
                id='datasources-dropdown',
                options=[
                    {'label': source, 'value': id} 
                    for id, source in dbase_options.items()
                ],
                value=[1],  # Default to Google Trends selected
                multi=True,
                placeholder="Seleccione una o más fuentes de datos",
                className="mb-4"
            ),
            # Add Select All button
            dbc.Button(
                "Seleccionar Todo",
                id="select-all-button",
                color="primary",
                size="sm",
                className="mb-2"
            ),
            # Add validation message div
            html.Div(id='datasources-validation', className="text-danger")
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
        # Sidebar column
        dbc.Col(sidebar, width=3, className="bg-light"),
        
        # Main content column
        dbc.Col([
            html.H1("Análisis de Herramientas Gerenciales bajo diferentes variables"),
            # Add your main content/plots here
            html.Div(id='main-content')
        ], width=9)
    ], style={'height': '100vh'})
], fluid=True)

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
     Input('datasources-dropdown', 'value')]
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
                'title': 'Fecha',
                'title_standoff': 25,
                'tickangle': 45,
                'dtick': 'M1',
                'tickformat': '%b',
                'showgrid': True,
                'gridcolor': 'lightgray',
                'tickmode': 'array',
                'ticktext': years_data['Fecha'].dt.strftime('%Y'),
                'tickvals': years_data['Fecha'].dt.strftime('%Y-%m-%d'),
                'tickfont': {'size': 10},
                'rangeslider': {'visible': True},
                'domain': [0, 1],
            },
            'yaxis': {
                'title': 'Valor Normalizado',
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

    # Update the callback for bar graph to use same colors
    @app.callback(
        Output('bar-graph', 'figure'),
        [Input('line-graph', 'relayoutData'),
         Input('keyword-dropdown', 'value'),
         Input('datasources-dropdown', 'value')]
    )
    def update_bar_graph(relayoutData, selected_keyword, selected_sources):
        # Filter data based on selected date range
        df_filtered = combined_dataset.copy()
        
        if relayoutData and ('xaxis.range' in relayoutData or 'xaxis.range[0]' in relayoutData):
            start_date = relayoutData.get('xaxis.range[0]') or relayoutData.get('xaxis.range')[0]
            end_date = relayoutData.get('xaxis.range[1]') or relayoutData.get('xaxis.range')[1]
            
            df_filtered = df_filtered[
                (df_filtered['Fecha'] >= start_date) &
                (df_filtered['Fecha'] <= end_date)
            ]

        # Calculate means for the filtered period
        means = df_filtered.drop('Fecha', axis=1).mean()

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
                'title': 'Promedios del Período Seleccionado',
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
        
        return bar_fig

    # Create buttons for time range selection
    time_range_buttons = html.Div([
        html.Label("Rango de tiempo:  ", style={'marginRight': '10px'}),
        dbc.ButtonGroup([
            dbc.Button("5 años", id="btn-5y", size="sm", className="me-1", n_clicks=0),
            dbc.Button("10 años", id="btn-10y", size="sm", className="me-1", n_clicks=0),
            dbc.Button("15 años", id="btn-15y", size="sm", className="me-1", n_clicks=0),
            dbc.Button("20 años", id="btn-20y", size="sm", className="me-1", n_clicks=0),
            dbc.Button("Todo", id="btn-all", size="sm", n_clicks=0),
        ], className="mb-3")
    ], style={'marginBottom': '10px'})

    # Add callback for time range buttons
    @app.callback(
        Output('line-graph', 'figure'),
        [Input('btn-5y', 'n_clicks'),
         Input('btn-10y', 'n_clicks'),
         Input('btn-15y', 'n_clicks'),
         Input('btn-20y', 'n_clicks'),
         Input('btn-all', 'n_clicks')]
    )
    def update_time_range(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Convert to pandas datetime
        df_dates = pd.to_datetime(combined_dataset['Fecha'])
        end_date = df_dates.max()
        
        if button_id == 'btn-all':
            start_date = df_dates.min()
        else:
            years = int(button_id.split('-')[1][:-1])
            start_date = end_date - pd.DateOffset(years=years)
        
        # Filter the data
        mask = (df_dates >= start_date) & (df_dates <= end_date)
        filtered_data = combined_dataset[mask]
        
        # Create new figure
        new_fig = {
            'data': [
                {
                    'x': filtered_data['Fecha'],
                    'y': filtered_data[col],
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
                } for col in filtered_data.columns if col != 'Fecha'
            ],
            'layout': {
                'title': f'Tendencia de {selected_keyword} a través del tiempo',
                'xaxis': {
                    'title': 'Fecha',
                    'title_standoff': 25,
                    'tickangle': 45,
                    'dtick': 'M1',
                    'tickformat': '%b',
                    'showgrid': True,
                    'gridcolor': 'lightgray',
                    'tickmode': 'array',
                    'ticktext': filtered_data['Fecha'].dt.strftime('%Y'),
                    'tickvals': filtered_data['Fecha'],
                    'tickfont': {'size': 10},
                    'range': [start_date, end_date],
                    'rangeslider': {
                        'visible': True,
                        'range': [start_date, end_date]
                    }
                },
                'yaxis': {
                    'title': 'Valor Normalizado',
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
        
        return new_fig

    # Create the layout
    return html.Div([
        # Header information
        html.P([
            html.Strong("Herramienta Seleccionada: "),
            f"{selected_keyword}"
        ]),
        html.P([
            html.Strong("Fuentes de datos Seleccionadas: "),
            f"{', '.join(selected_source_names)}"
        ]),
        # Add time range buttons
        time_range_buttons,
        # Container for both graphs side by side
        html.Div([
            # Line chart container
            html.Div([
                dcc.Graph(
                    id='line-graph',
                    figure=fig,
                    style={'height': '520px'}  # Match the height we set before
                ),
            ], style={
                'width': '80%',  # 4/5 of the width
                'display': 'inline-block',
                'vertical-align': 'top'
            }),
            # Bar chart container
            html.Div([
                dcc.Graph(
                    id='bar-graph',
                    figure=initial_bar_fig,
                    style={'height': '520px'}  # Match the height of line chart
                ),
            ], style={
                'width': '20%',  # 1/5 of the width
                'display': 'inline-block',
                'vertical-align': 'top'
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '20px'
        }),
        html.Div([
            dash_table.DataTable(
                data=combined_dataset.to_dict('records'),
                columns=[{"name": str(i), "id": str(i)} for i in combined_dataset.columns],
                style_table={
                    'overflowX': 'auto',
                    'overflowY': 'auto',
                    'height': '240px',
                    'minWidth': '100%'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px',
                    'width': '150px',
                    'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'position': 'sticky',
                    'top': 0,
                    'zIndex': 1000
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_filter={
                    'display': 'none'
                },
                fixed_rows={'headers': True},
                sort_action='native',
                filter_action='native',
                page_size=5,
                page_action='native',
                page_current=0
            ),
            html.Div(
                f"Total de registros: {total_records}",
                style={
                    'position': 'relative',
                    'marginTop': '-48px',
                    'marginLeft': '10px',
                    'color': '#666',
                    'zIndex': 1000
                }
            )
        ])
    ])

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

if __name__ == '__main__':
    app.run_server(debug=True)
