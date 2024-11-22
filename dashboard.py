import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from correlation import get_all_keywords, get_file_data2  # Update import

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
                'width': '50%',
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
    
    # Pass both selected_keyword and selected_sources to get_file_data2
    datasets_norm, sl_sc = get_file_data2([selected_keyword], selected_sources)
    
    # Convert source IDs to their names using dbase_options
    selected_source_names = [dbase_options[src_id] for src_id in selected_sources]
    
    return html.Div([
        html.P(f"Herramienta Seleccionada: {selected_keyword}"),
        html.P(f"Fuentes de datos Seleccionadas: {', '.join(selected_source_names)}"),
        html.P(f"Valores normalizados: {datasets_norm}")
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
