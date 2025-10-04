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

def get_file_data2(selected_keyword, selected_sources):
    """Simplified data loading function without heavy dependencies"""
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

    # Load data for each source
    for source in selected_sources:
        filename = filenames.get(source, 'Archivo no encontrado')
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbase", filename)

        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue

        try:
            # Read CSV file
            df = pd.read_csv(file_path, index_col=0)
            df.index = df.index.str.strip()

            # Convert index to datetime based on source type
            if source == 2:  # Google Books Ngrams
                df.index = pd.to_datetime(df.index.str.split('-').str[0], format='%Y')
            else:  # Other sources
                df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')

            all_raw_datasets[source] = df
        except Exception as e:
            print(f"Error loading data for source {source}: {e}")
            continue

    # Process datasets (simplified - just trim to common date range)
    for source in selected_sources:
        if source in all_raw_datasets:
            df = all_raw_datasets[source]

            # Find common date range across all datasets
            if len(all_raw_datasets) > 1:
                earliest_date = max(df.index.min() for df in all_raw_datasets.values())
                latest_date = min(df.index.max() for df in all_raw_datasets.values())
                df = df.loc[earliest_date:latest_date]

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
    title='Management Tools Analysis Dashboard'
)

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
        html.Img(
            src='assets/Management-Tools-Analysis-logo.png',
            style={
                'width': '80%',
                'marginBottom': '20px',
                'display': 'block',
                'marginLeft': 'auto',
                'marginRight': 'auto'
            }
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
        html.Hr(),
        html.Div([
            html.P([
                "Dashboard de Análisis de ",
                html.B("Herramientas Gerenciales")
            ], style={'marginBottom': '2px', 'fontSize': '10px', 'textAlign': 'center'}),
            html.P([
                "Desarrollado con Python, Plotly y Dash"
            ], style={'fontSize': '10px', 'textAlign': 'center', 'marginTop': '0px'})
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
        "Tesista: ", html.B("Diomar Anez"), " | Python Dev: ", html.B("Dimar Anez")
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
            html.Div(id='main-content', className="w-100", style={
                'height': 'calc(100vh - 200px)',
                'overflowY': 'auto',
                'overflowX': 'hidden',
                'paddingRight': '10px'
            })
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

        # Handle Bain/Crossref alignment
        bain_sources = [3, 5]
        has_bain = any(src_id in selected_sources for src_id in bain_sources)
        has_crossref = 4 in selected_sources

        if has_bain and has_crossref:
            bain_columns = [dbase_options[src_id] for src_id in bain_sources if src_id in selected_sources]
            bain_start_date = combined_dataset[combined_dataset[bain_columns].notna().any(axis=1)]['Fecha'].min()
            combined_dataset = combined_dataset[combined_dataset['Fecha'] >= bain_start_date]

        # Filter NaN values
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns)

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Create content sections
        content = []

        # 1. Temporal Analysis 2D
        content.append(html.Div([
            html.H6("1. Análisis Temporal 2D", style={'fontSize': '16px', 'marginTop': '20px'}),
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
        ]))

        # 2. Mean Analysis
        content.append(html.Div([
            html.H6("2. Análisis de Medias", style={'fontSize': '16px', 'marginTop': '20px'}),
            dcc.Graph(
                id='mean-analysis-graph',
                figure=create_mean_analysis_figure(combined_dataset, selected_source_names),
                style={'height': '300px'},
                config={'displaylogo': False, 'responsive': True}
            )
        ]))

        # 3. Temporal Analysis 3D (if 2+ sources)
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.H6("3. Análisis Temporal 3D", style={'fontSize': '16px', 'marginTop': '20px'}),
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
                    style={'height': '500px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ]))

        # 4. Seasonal Analysis
        content.append(html.Div([
            html.H6("4. Análisis Estacional", style={'fontSize': '16px', 'marginTop': '20px'}),
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
        ]))

        # 5. Fourier Analysis
        content.append(html.Div([
            html.H6("5. Análisis de Fourier (Periodograma)", style={'fontSize': '16px', 'marginTop': '20px'}),
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
                    style={'height': '400px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ])
        ]))

        # 6. PCA Analysis
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.H6("6. Análisis PCA (Cargas y Componentes)", style={'fontSize': '16px', 'marginTop': '20px'}),
                dcc.Graph(
                    id='pca-analysis-graph',
                    figure=create_pca_figure(combined_dataset, selected_source_names),
                    style={'height': '500px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ]))

        # 7. Correlation Heatmap
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.H6("7. Mapa de Calor (Correlación)", style={'fontSize': '16px', 'marginTop': '20px'}),
                dcc.Graph(
                    id='correlation-heatmap',
                    figure=create_correlation_heatmap(combined_dataset, selected_source_names),
                    style={'height': '400px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ]))

        # 8. Regression Analysis (clickable from heatmap)
        if len(selected_sources) >= 2:
            content.append(html.Div([
                html.H6("8. Análisis de Regresión", style={'fontSize': '16px', 'marginTop': '20px'}),
                html.P("Haga clic en el mapa de calor para seleccionar variables para regresión", style={'fontSize': '12px'}),
                dcc.Graph(
                    id='regression-graph',
                    style={'height': '400px'},
                    config={'displaylogo': False, 'responsive': True}
                )
            ]))

        # Data table
        content.append(html.Div([
            html.H6("Tabla de Datos", style={'fontSize': '16px', 'marginTop': '20px'}),
            dbc.Button(
                "Mostrar/Ocultar Tabla",
                id="toggle-table-button",
                color="primary",
                size="sm",
                className="mb-2",
                style={'fontSize': '12px'}
            ),
            dbc.Collapse(
                html.Div([
                    dash_table.DataTable(
                        data=combined_dataset.to_dict('records'),
                        columns=[{"name": str(col), "id": str(col)} for col in combined_dataset.columns],
                        style_table={'overflowX': 'auto', 'overflowY': 'auto', 'height': '400px'},
                        style_cell={'textAlign': 'left', 'padding': '5px', 'minWidth': '100px', 'width': '120px', 'maxWidth': '150px'},
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        page_size=20
                    )
                ]),
                id="collapse-table",
                is_open=False
            )
        ]))

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
    for source in sources:
        if source in filtered_data.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data['Fecha'],
                y=filtered_data[source],
                mode='lines',
                name=source,
                line=dict(color=color_map.get(source, '#000000'))
            ))

    # Update layout with legend at bottom and monthly ticks
    fig.update_layout(
        title="Análisis Temporal 2D",
        xaxis_title="Fecha",
        yaxis_title="Valor",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            tickformat="%Y-%m",  # Show year-month format
            dtick="M1",  # Monthly ticks
            tickangle=45
        )
    )
    return fig

def create_mean_analysis_figure(data, sources):
    means = data[sources].mean()
    fig = go.Figure(data=[
        go.Bar(
            x=list(means.index),
            y=means.values,
            marker_color=[color_map.get(src, '#000000') for src in means.index]
        )
    ])
    fig.update_layout(
        title="Análisis de Medias",
        xaxis_title="Fuente",
        yaxis_title="Media",
        height=300
    )
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

    # Loadings plot
    for i, source in enumerate(sources):
        fig.add_trace(
            go.Scatter(
                x=pca.components_[0],
                y=pca.components_[1],
                mode='markers+text',
                text=[source],
                textposition="top center",
                name=f'PC1-PC2: {source}',
                marker=dict(color=color_map.get(source, '#000000'))
            ),
            row=1, col=1
        )

    # Explained variance
    explained_var = pca.explained_variance_ratio_ * 100
    fig.add_trace(
        go.Bar(
            x=[f'PC{i+1}' for i in range(len(explained_var))],
            y=explained_var,
            name='Varianza Explicada (%)'
        ),
        row=1, col=2
    )

    fig.update_layout(height=500, showlegend=False)
    return fig

def create_correlation_heatmap(data, sources):
    corr_data = data[sources].corr()
    fig = ff.create_annotated_heatmap(
        z=corr_data.values,
        x=sources,
        y=sources,
        colorscale='RdBu',
        zmin=-1, zmax=1
    )
    fig.update_layout(
        title="Mapa de Calor de Correlación",
        height=400
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

        # Handle Bain/Crossref alignment
        bain_sources = [3, 5]
        has_bain = any(src_id in selected_sources for src_id in bain_sources)
        has_crossref = 4 in selected_sources

        if has_bain and has_crossref:
            bain_columns = [dbase_options[src_id] for src_id in bain_sources if src_id in selected_sources]
            bain_start_date = combined_dataset[combined_dataset[bain_columns].notna().any(axis=1)]['Fecha'].min()
            combined_dataset = combined_dataset[combined_dataset['Fecha'] >= bain_start_date]

        # Filter NaN values
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns)

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Determine date range based on button clicks or slider values
        ctx = dash.callback_context
        start_date = None
        end_date = None
        slider_value = slider_values  # Default to current slider value

        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'temporal-2d-all':
                start_date = combined_dataset['Fecha'].min().date()
                end_date = combined_dataset['Fecha'].max().date()
                # Update slider to full range
                slider_value = [0, len(combined_dataset) - 1]
            elif trigger_id == 'temporal-2d-20y':
                end_date = combined_dataset['Fecha'].max().date()
                start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=20)).date()
                # Find indices for the date range
                start_idx = combined_dataset[combined_dataset['Fecha'].dt.date >= start_date].index[0]
                end_idx = len(combined_dataset) - 1
                slider_value = [start_idx, end_idx]
            elif trigger_id == 'temporal-2d-15y':
                end_date = combined_dataset['Fecha'].max().date()
                start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=15)).date()
                start_idx = combined_dataset[combined_dataset['Fecha'].dt.date >= start_date].index[0]
                end_idx = len(combined_dataset) - 1
                slider_value = [start_idx, end_idx]
            elif trigger_id == 'temporal-2d-10y':
                end_date = combined_dataset['Fecha'].max().date()
                start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=10)).date()
                start_idx = combined_dataset[combined_dataset['Fecha'].dt.date >= start_date].index[0]
                end_idx = len(combined_dataset) - 1
                slider_value = [start_idx, end_idx]
            elif trigger_id == 'temporal-2d-5y':
                end_date = combined_dataset['Fecha'].max().date()
                start_date = (pd.to_datetime(end_date) - pd.DateOffset(years=5)).date()
                start_idx = combined_dataset[combined_dataset['Fecha'].dt.date >= start_date].index[0]
                end_idx = len(combined_dataset) - 1
                slider_value = [start_idx, end_idx]
            elif trigger_id == 'temporal-2d-date-range':
                # Slider values are indices, convert to dates
                start_idx, end_idx = slider_values
                start_date = combined_dataset['Fecha'].iloc[start_idx].date()
                end_date = combined_dataset['Fecha'].iloc[end_idx].date()
                slider_value = slider_values  # Keep the slider value as is

        # If no specific trigger, use slider values
        if start_date is None and end_date is None and slider_values:
            start_idx, end_idx = slider_values
            start_date = combined_dataset['Fecha'].iloc[start_idx].date()
            end_date = combined_dataset['Fecha'].iloc[end_idx].date()
            slider_value = slider_values

        return create_temporal_2d_figure(combined_dataset, selected_source_names, start_date, end_date), slider_value
    except Exception as e:
        return {}

# Callback to update the slider when data changes
@app.callback(
    Output('temporal-2d-date-range', 'min'),
    Output('temporal-2d-date-range', 'max'),
    Output('temporal-2d-date-range', 'value'),
    Output('temporal-2d-date-range', 'marks'),
    [Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_temporal_slider(selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or not selected_sources:
        return 0, 100, [0, 100], {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Handle Bain/Crossref alignment
        bain_sources = [3, 5]
        has_bain = any(src_id in selected_sources for src_id in bain_sources)
        has_crossref = 4 in selected_sources

        if has_bain and has_crossref:
            bain_columns = [dbase_options[src_id] for src_id in bain_sources if src_id in selected_sources]
            bain_start_date = combined_dataset[combined_dataset[bain_columns].notna().any(axis=1)]['Fecha'].min()
            combined_dataset = combined_dataset[combined_dataset['Fecha'] >= bain_start_date]

        # Filter NaN values
        data_columns = [dbase_options[src_id] for src_id in selected_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns)

        # Create marks for the slider
        n_marks = min(5, len(combined_dataset))  # Limit to 5 marks
        mark_indices = [int(i * (len(combined_dataset) - 1) / (n_marks - 1)) for i in range(n_marks)]
        marks = {
            idx: combined_dataset['Fecha'].iloc[idx].strftime('%Y-%m')
            for idx in mark_indices
        }

        return 0, len(combined_dataset) - 1, [0, len(combined_dataset) - 1], marks
    except Exception as e:
        return 0, 100, [0, 100], {}

# Additional callbacks for specific analyses
@app.callback(
    Output('temporal-3d-graph', 'figure'),
    [Input('y-axis-3d', 'value'),
     Input('z-axis-3d', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_3d_plot(y_axis, z_axis, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not all([y_axis, z_axis, selected_keyword]) or len(selected_sources) < 2:
        return {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        fig = go.Figure(data=[
            go.Scatter3d(
                x=combined_dataset['Fecha'],
                y=combined_dataset[y_axis],
                z=combined_dataset[z_axis],
                mode='lines',
                line=dict(color=color_map.get(y_axis, '#000000'), width=2),
                name=f'{y_axis} vs {z_axis}'
            )
        ])

        fig.update_layout(
            title=f'Análisis Temporal 3D: {y_axis} vs {z_axis}',
            scene=dict(
                xaxis_title='Fecha',
                yaxis_title=y_axis,
                zaxis_title=z_axis
            ),
            height=500
        )
        return fig
    except Exception as e:
        return {}

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
    Output('fourier-analysis-graph', 'figure'),
    [Input('fourier-source-select', 'value'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_fourier_analysis(selected_source, selected_keyword, *button_states):
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

        yf = fft(ts_data.values)
        N = len(ts_data)
        xf = fftfreq(N)[:N//2]
        power = 2.0/N * np.abs(yf[1:N//2])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=xf[1:],
            y=power,
            name='Espectro de Potencia',
            marker_color=color_map.get(selected_source, '#000000')
        ))

        fig.update_layout(
            title=f'Análisis de Fourier: {selected_source}',
            xaxis_title='Frecuencia',
            yaxis_title='Potencia',
            height=400
        )
        return fig
    except Exception as e:
        return {}

@app.callback(
    Output('regression-graph', 'figure'),
    [Input('correlation-heatmap', 'clickData'),
     Input('keyword-dropdown', 'value')] +
    [Input(f"toggle-source-{id}", "outline") for id in dbase_options.keys()]
)
def update_regression_analysis(click_data, selected_keyword, *button_states):
    selected_sources = [id for id, outline in zip(dbase_options.keys(), button_states) if not outline]

    if not selected_keyword or len(selected_sources) < 2 or not click_data:
        return {}

    try:
        datasets_norm, sl_sc = get_file_data2(selected_keyword=selected_keyword, selected_sources=selected_sources)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        selected_source_names = [dbase_options[src_id] for src_id in selected_sources]

        # Get clicked variables from heatmap
        x_var = click_data['points'][0]['x']
        y_var = click_data['points'][0]['y']

        if x_var not in combined_dataset.columns or y_var not in combined_dataset.columns:
            return {}

        # Perform regression
        valid_data = combined_dataset[[x_var, y_var]].dropna()
        if len(valid_data) < 2:
            return {}

        X = valid_data[[x_var]]
        y = valid_data[y_var]

        model = LinearRegression()
        model.fit(X, y)

        y_pred = model.predict(X)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=valid_data[x_var],
            y=valid_data[y_var],
            mode='markers',
            name='Datos',
            marker=dict(color=color_map.get(x_var, '#000000'))
        ))

        fig.add_trace(go.Scatter(
            x=valid_data[x_var],
            y=y_pred,
            mode='lines',
            name='Regresión',
            line=dict(color='red', width=2)
        ))

        fig.update_layout(
            title=f'Regresión: {y_var} vs {x_var}',
            xaxis_title=x_var,
            yaxis_title=y_var,
            height=400
        )
        return fig
    except Exception as e:
        return {}

@app.callback(
    Output('collapse-table', 'is_open'),
    [Input('toggle-table-button', 'n_clicks')],
    [State('collapse-table', 'is_open')]
)
def toggle_table(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
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


# Note: Time range filtering buttons are displayed but their callbacks are disabled
# to avoid Dash callback reference errors. The full date range is used by default.

if __name__ == '__main__':
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050
    )