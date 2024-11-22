import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the sidebar layout
sidebar = html.Div(
    [
        # Logo
        html.Img(
            src='/assets/Management-Tools-Analysis-logo.png',
            style={
                'width': '100%',
                'margin-bottom': '20px'
            }
        ),
        
        html.H4("Menú", className="display-6 mb-4"),
        html.Hr(),
        
        # Keyword dropdown (single selection)
        html.Label("Select Keyword:"),
        dcc.Dropdown(
            id='keyword-dropdown',
            options=[
                # Add your keyword options here
                {'label': 'Keyword 1', 'value': 'keyword1'},
                {'label': 'Keyword 2', 'value': 'keyword2'},
                # ... more keywords
            ],
            value='keyword1',  # default value
            className="mb-4"
        ),
        
        # Data sources dropdown (multiple selection)
        html.Label("Select Data Sources:"),
        dcc.Dropdown(
            id='datasources-dropdown',
            options=[
                # Add your data source options here
                {'label': 'Source 1', 'value': 'source1'},
                {'label': 'Source 2', 'value': 'source2'},
                # ... more sources
            ],
            value=['source1'],  # default value
            multi=True,
            className="mb-4"
        ),
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
            html.H1("Dashboard Title"),
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
    # Add your logic here to update the content based on selections
    return html.Div([
        html.P(f"Selected Keyword: {selected_keyword}"),
        html.P(f"Selected Sources: {', '.join(selected_sources)}")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
