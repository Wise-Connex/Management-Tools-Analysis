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
            src='/assets/Management-Tools-Analysis-logo.png',
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
    combined_dataset = combined_dataset.reset_index()
    selected_source_names = [dbase_options[src_id] for src_id in selected_sources]
    
    total_records = len(combined_dataset)
    
    return html.Div([
        html.P(f"Herramienta Seleccionada: {selected_keyword}"),
        html.P(f"Fuentes de datos Seleccionadas: {', '.join(selected_source_names)}"),
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
