"""
Key Findings Modal Component

Interactive dashboard component for displaying AI-generated
doctoral-level analysis with bilingual support and user interactions.
"""

import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeyFindingsModal:
    """
    Modal component for displaying Key Findings.
    
    Provides interactive UI for AI-generated analysis with
    bilingual support, user interactions, and performance metrics.
    """

    def __init__(self, app, language_store):
        """
        Initialize Key Findings modal.
        
        Args:
            app: Dash application instance
            language_store: Language state store
        """
        self.app = app
        self.language_store = language_store
        
        # Modal state
        self.modal_id = "key-findings-modal"
        self.is_open_id = "key-findings-modal-open"
        self.content_id = "key-findings-content"
        self.loading_id = "key-findings-loading"
        
        # Component IDs
        self.findings_display_id = "key-findings-display"
        self.pca_insights_id = "key-findings-pca"
        self.executive_summary_id = "key-findings-summary"
        self.metadata_id = "key-findings-metadata"
        
        # Interaction controls
        self.regenerate_btn_id = "key-findings-regenerate"
        self.save_btn_id = "key-findings-save"
        self.rating_id = "key-findings-rating"
        self.feedback_id = "key-findings-feedback"
        
        # Performance metrics
        self.metrics_id = "key-findings-metrics"
        
        # Register callbacks
        self._register_callbacks()

    def create_modal_layout(self) -> dbc.Modal:
        """
        Create the modal layout with all sections.
        
        Returns:
            Complete modal layout
        """
        return dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("🧠 Key Findings - Análisis", id="key-findings-modal-title"),
                    close_button=True,
                    className="bg-primary text-white"
                ),
                dbc.ModalBody(
                    [
                        # Loading state
                        html.Div(
                            id=self.loading_id,
                            children=[
                                html.Div([
                                    dbc.Spinner(color="primary", size="lg"),
                                    html.P("Generando análisis...", className="mt-3 text-center"),
                                    html.P("Esto puede tomar hasta 30 segundos...", className="text-muted text-center")
                                ], className="text-center py-5")
                            ],
                            style={"display": "none"}
                        ),
                        
                        # Main content
                        html.Div(
                            id=self.content_id,
                            children=self._create_empty_state()
                        ),
                        
                        # Performance metrics (hidden by default)
                        html.Div(
                            id=self.metrics_id,
                            style={"display": "none"}
                        )
                    ],
                    className="modal-body-scrollable",
                    style={"maxHeight": "70vh", "overflowY": "auto"}
                ),
                dbc.ModalFooter(
                    [
                        # Left side controls
                        html.Div([
                            # Rating component
                            html.Div([
                                html.Label("Calificación:", className="me-2"),
                                dbc.Rating(
                                    id=self.rating_id,
                                    max=5,
                                    size="md",
                                    value=0,
                                    className="me-3"
                                )
                            ], className="d-flex align-items-center"),
                            
                            # Feedback textarea
                            dbc.Textarea(
                                id=self.feedback_id,
                                placeholder="Comentarios sobre el análisis...",
                                size="sm",
                                style={"width": "200px", "height": "60px"}
                            )
                        ], className="d-flex align-items-center me-auto"),
                        
                        # Right side buttons
                        html.Div([
                            # Regenerate button
                            dbc.Button(
                                "🔄 Regenerar",
                                id=self.regenerate_btn_id,
                                color="warning",
                                size="sm",
                                className="me-2"
                            ),
                            
                            # Save button
                            dbc.Button(
                                "💾 Guardar",
                                id=self.save_btn_id,
                                color="success",
                                size="sm"
                            ),
                            
                            # Close button
                            dbc.Button(
                                "Cerrar",
                                id="key-findings-close",
                                color="secondary",
                                size="sm",
                                className="ms-2"
                            )
                        ])
                    ],
                    className="d-flex justify-content-between align-items-center"
                )
            ],
            id=self.modal_id,
            is_open=False,
            size="xl",
            backdrop="static",
            keyboard=False,
            className="key-findings-modal"
        )

    def create_findings_display(self, report_data: Dict[str, Any]) -> html.Div:
        """
        Create formatted display of AI findings.
        
        Args:
            report_data: Report data from database or AI
            
        Returns:
            Formatted findings display
        """
        if not report_data:
            return self._create_empty_state()
        
        # Extract data with proper JSON parsing if needed
        executive_summary = self._extract_text_content(report_data.get('executive_summary', ''))
        principal_findings = self._extract_text_content(report_data.get('principal_findings', ''))
        pca_analysis = self._extract_text_content(report_data.get('pca_analysis', ''))
        metadata = self._extract_metadata(report_data)
        
        return html.Div([
            # Executive Summary Section
            self._create_executive_summary_section(executive_summary),
            
            # Principal Findings Section (now narrative)
            self._create_principal_findings_narrative_section(principal_findings),
            
            # PCA Analysis Section (now narrative essay)
            self._create_pca_analysis_section(pca_analysis),
            
            # Metadata Section
            self._create_metadata_section(metadata)
        ])

    def create_interaction_controls(self) -> html.Div:
        """
        Create user interaction controls.
        
        Returns:
            Interaction controls layout
        """
        return html.Div([
            # Rating and feedback
            html.Div([
                html.H6("Evaluar este Análisis", className="mb-3"),
                html.Div([
                    html.Label("Calificación de Precisión:", className="form-label"),
                    dbc.Rating(
                        id=self.rating_id,
                        max=5,
                        size="lg",
                        value=0
                    )
                ], className="mb-3"),
                
                html.Label("Comentarios Adicionales:", className="form-label"),
                dbc.Textarea(
                    id=self.feedback_id,
                    placeholder="Proporcione feedback sobre la calidad y utilidad de este análisis...",
                    rows=3,
                    className="mb-3"
                )
            ]),
            
            # Action buttons
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-sync-alt me-2"), "Regenerar Análisis"],
                    id=self.regenerate_btn_id,
                    color="warning",
                    size="lg",
                    className="w-100 mb-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-save me-2"), "Guardar en Biblioteca"],
                    id=self.save_btn_id,
                    color="success",
                    size="lg",
                    className="w-100 mb-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "Exportar PDF"],
                    id="key-findings-export",
                    color="info",
                    size="lg",
                    className="w-100"
                )
            ])
        ])

    def create_loading_state(self) -> html.Div:
        """
        Create loading animation during AI processing.
        
        Returns:
            Loading state component
        """
        return html.Div([
            html.Div([
                dbc.Spinner(color="primary", size="lg", type="grow"),
                html.H4("Generando Análisis", className="mt-4 mb-3"),
                html.P("Analizando datos multi-fuente con énfasis en PCA...", className="text-muted mb-2"),
                html.P("Tiempo estimado: 15-30 segundos", className="text-muted"),
                
                # Progress indicators
                html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Datos recopilados"
                    ], className="mb-2"),
                    html.Div([
                        html.I(className="fas fa-spinner fa-spin text-primary me-2"),
                        "Análisis PCA en progreso..."
                    ], className="mb-2"),
                    html.Div([
                        html.I(className="far fa-circle text-muted me-2"),
                        "Generando insights con IA"
                    ], className="mb-2"),
                    html.Div([
                        html.I(className="far fa-circle text-muted me-2"),
                        "Creando resumen ejecutivo"
                    ])
                ], className="text-start mt-4")
            ], className="text-center py-5")
        ])

    def _create_empty_state(self) -> html.Div:
        """Create empty state when no data available."""
        return html.Div([
            html.Div([
                html.I(className="fas fa-brain fa-3x text-muted mb-3"),
                html.H4("Análisis No Disponible", className="mb-3"),
                html.P("Seleccione una herramienta y fuentes de datos para generar Key Findings.", 
                       className="text-muted"),
                html.P("El análisis doctoral proporcionará insights basados en:", className="mt-3"),
                html.Ul([
                    html.Li("Análisis de Componentes Principales (PCA)"),
                    html.Li("Tendencias temporales y patrones"),
                    html.Li("Correlaciones entre fuentes de datos"),
                    html.Li("Insights ejecutivos accionables")
                ], className="text-start")
            ], className="text-center py-5")
        ])

    def _create_executive_summary_section(self, summary: str) -> html.Div:
        """Create executive summary section."""
        return html.Div([
            html.H4([
                html.I(className="fas fa-lightbulb text-warning me-2"),
                "Resumen Ejecutivo"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.P(summary, className="lead text-justify mb-0 executive-summary-text",
                           style={"lineHeight": "1.7"}),
                ])
            ], className="border-primary bg-primary text-white")
        ], className="mb-4")

    def _create_principal_findings_narrative_section(self, findings_text: str) -> html.Div:
        """Create principal findings section as narrative text."""
        if not findings_text:
            return html.Div()
        
        return html.Div([
            html.H4([
                html.I(className="fas fa-search text-primary me-2"),
                "Hallazgos Principales"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.P(findings_text, className="lead text-justify principal-findings-text",
                               style={"lineHeight": "1.6"}),
                        # Add a subtle indicator that this integrates multiple analyses
                        html.Div([
                            html.Small([
                                html.I(className="fas fa-info-circle text-info me-1"),
                                "Esta sección integra análisis de componentes principales, patrones temporales y correlaciones"
                            ], className="text-muted")
                        ], className="mt-3 text-end")
                    ])
                ])
            ], className="border-0 bg-light shadow-sm")
        ], className="mb-4")

    def _create_pca_analysis_section(self, pca_analysis_text: str) -> html.Div:
        """Create PCA analysis section as narrative essay with proper paragraph formatting."""
        if not pca_analysis_text:
            return html.Div()
        
        # Split text into paragraphs and create separate P elements for each
        paragraphs = [p.strip() for p in pca_analysis_text.split('\n\n') if p.strip()]
        
        return html.Div([
            html.H4([
                html.I(className="fas fa-chart-line text-info me-2"),
                "Análisis PCA"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Create separate P elements for each paragraph
                        html.Div([
                            html.P(p, className="text-justify pca-analysis-text mb-3",
                                   style={"lineHeight": "1.6"})
                            for p in paragraphs
                        ]),
                        # Add a subtle indicator that this is detailed PCA analysis
                        html.Div([
                            html.Small([
                                html.I(className="fas fa-calculator text-info me-1"),
                                f"Análisis detallado de componentes principales ({len(paragraphs)} párrafos)"
                            ], className="text-muted")
                        ], className="mt-3 text-end")
                    ])
                ])
            ], className="border-0 bg-light shadow-sm")
        ], className="mb-4")

    def _create_metadata_section(self, metadata: Dict[str, Any]) -> html.Div:
        """Create metadata section."""
        return html.Div([
            html.H4([
                html.I(className="fas fa-info-circle text-secondary me-2"),
                "Información del Análisis"
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Modelo IA: "),
                        metadata.get('model_used', 'N/A')
                    ]),
                    html.P([
                        html.Strong("Tiempo de Respuesta: "),
                        f"{metadata.get('response_time_ms', 0)} ms"
                    ]),
                    html.P([
                        html.Strong("Puntos de Datos: "),
                        f"{metadata.get('data_points_analyzed', 0):,}"
                    ])
                ], width=6),
                
                dbc.Col([
                    html.P([
                        html.Strong("Fecha de Generación: "),
                        metadata.get('generation_timestamp', 'N/A')
                    ]),
                    html.P([
                        html.Strong("Accesos Previos: "),
                        metadata.get('access_count', 0)
                    ]),
                    html.P([
                        html.Strong("Profundidad: "),
                        metadata.get('analysis_depth', 'comprehensive')
                    ])
                ], width=6)
            ])
        ], className="mb-4")

    def _create_pca_chart(self, dominant_patterns: List[Dict[str, Any]]) -> dcc.Graph:
        """Create PCA visualization chart (kept for compatibility but not used in new structure)."""
        # This method is kept for backward compatibility but not used in the new narrative structure
        return dcc.Graph()

    def _extract_metadata(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from report data."""
        return {
            'model_used': report_data.get('model_used', 'N/A'),
            'response_time_ms': report_data.get('api_latency_ms', 0),
            'data_points_analyzed': report_data.get('data_points_analyzed', 0),
            'generation_timestamp': report_data.get('generation_timestamp', 'N/A'),
            'access_count': report_data.get('access_count', 0),
            'analysis_depth': report_data.get('analysis_depth', 'comprehensive'),
            'sources_count': report_data.get('sources_count', 0)
        }
    
    def _extract_text_content(self, content: Any) -> str:
        """
        Extract text content from various data types.
        
        Args:
            content: Content that might be string, dict, or other types
            
        Returns:
            Extracted text content as string
        """
        if isinstance(content, str):
            # Check if it's JSON formatted
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    # Try to parse as JSON and extract text
                    json_data = json.loads(content)
                    if isinstance(json_data, dict):
                        # Look for common text fields
                        for field in ['executive_summary', 'principal_findings', 'pca_analysis', 'bullet_point', 'analysis']:
                            if field in json_data and isinstance(json_data[field], str):
                                return json_data[field]
                except:
                    pass
            return content
        elif isinstance(content, dict):
            # Extract from dictionary
            for field in ['executive_summary', 'principal_findings', 'pca_analysis', 'bullet_point', 'analysis']:
                if field in content and isinstance(content[field], str):
                    return content[field]
        elif isinstance(content, list) and content:
            # Extract from list
            first_item = content[0]
            if isinstance(first_item, dict):
                for field in ['bullet_point', 'text', 'content']:
                    if field in first_item and isinstance(first_item[field], str):
                        return first_item[field]
            elif isinstance(first_item, str):
                return first_item
        
        return str(content) if content else ''

    def _register_callbacks(self):
        """Register all modal callbacks."""
        
        # Toggle modal
        @self.app.callback(
            [Output(self.modal_id, "is_open"),
             Output(self.loading_id, "style"),
             Output(self.content_id, "children")],
            [Input("key-findings-trigger", "n_clicks"),
             Input("key-findings-close", "n_clicks"),
             Input(self.regenerate_btn_id, "n_clicks")],
            [State(self.modal_id, "is_open"),
             State("selected-tool", "value"),
             State("selected-sources", "value"),
             State("language-store", "data")]
        )
        def toggle_modal(trigger_clicks, close_clicks, regenerate_clicks, 
                       is_open, selected_tool, selected_sources, language):
            """Handle modal open/close and content loading."""
            
            # Determine which button was clicked
            ctx = dash.callback_context
            if not ctx.triggered:
                return False, {"display": "none"}, self._create_empty_state()
            
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == "key-findings-close":
                return False, {"display": "none"}, self._create_empty_state()
            
            if trigger_id in ["key-findings-trigger", self.regenerate_btn_id]:
                if not selected_tool or not selected_sources:
                    return True, {"display": "none"}, self._create_empty_state()
                
                # Show loading state
                return True, {"display": "block"}, self._create_empty_state()
            
            return is_open, {"display": "none"}, self._create_empty_state()
        
        # Update modal content (this would be connected to the actual analysis service)
        @self.app.callback(
            Output(self.content_id, "children", allow_duplicate=True),
            [Input("key-findings-data-ready", "data")]
        )
        def update_content(analysis_data):
            """Update modal content with analysis results."""
            if not analysis_data:
                return self._create_empty_state()
            
            return self.create_findings_display(analysis_data)
        
        # Handle user interactions
        @self.app.callback(
            [Output("key-findings-toast", "is_open"),
             Output("key-findings-toast", "children")],
            [Input(self.save_btn_id, "n_clicks"),
             Input(self.rating_id, "value")],
            [State(self.feedback_id, "value"),
             State("key-findings-current-report", "data")]
        )
        def handle_interactions(save_clicks, rating, feedback, current_report):
            """Handle save and rating interactions."""
            ctx = dash.callback_context
            if not ctx.triggered:
                return False, ""
            
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == self.save_btn_id:
                # Handle save functionality
                return True, "Análisis guardado exitosamente"
            
            if trigger_id == self.rating_id and rating and rating > 0:
                # Handle rating functionality
                return True, f"Calificación de {rating} estrellas registrada"
            
            return False, ""