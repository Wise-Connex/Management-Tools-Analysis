# Key Findings Module - Implementation Plan

## Development Roadmap

### Phase 1: Foundation Infrastructure (Week 1-2)

1. **Database Setup & Schema Creation**
2. **Persistent Storage Configuration** ⚠️ **CRITICAL FOR DOCKER/DEKPLOY**
3. **Configuration Management**
4. **Basic OpenRouter.ai Integration**
5. **Core Data Structures**

### Phase 2: Core Functionality (Week 3-4)

1. **Data Aggregation Pipeline**
2. **AI Prompt Engineering System**
3. **Caching Logic Implementation**
4. **Error Handling Framework**

### Phase 3: User Interface (Week 5-6)

1. **Modal Component Development**
2. **Dashboard Integration**
3. **Bilingual Support**
4. **User Interaction Controls**

### Phase 4: Advanced Features (Week 7-8)

1. **Performance Optimization**
2. **Security Hardening**
3. **Monitoring & Analytics**
4. **Testing & Documentation**

## Detailed Implementation Specifications

### ⚠️ CRITICAL: Persistent Storage Configuration

**IMPORTANT**: For Docker/Dokploy deployments, persistent storage MUST be configured to prevent cache loss during updates.

#### Docker Configuration

**Update `docker-compose.yml`:**

```yaml
version: "3.8"

services:
  dashboard-app:
    build: .
    ports:
      - "8050:8050"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
    volumes:
      - key_findings_data:/app/data
      - ./dashboard_app:/app
    restart: unless-stopped

volumes:
  key_findings_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/key_findings_data
```

**Update `Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Create data directory for persistent storage
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# ... rest of Dockerfile ...

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
```

**Environment Variables for Persistence:**

```env
# Persistent Database Configuration
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_BACKUP_INTERVAL=3600  # Backup every hour

# Docker-specific Configuration
KEY_FINDINGS_DATA_DIR=/app/data
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data
```

#### Server Setup for Dokploy

**Create persistent directory on server:**

```bash
# SSH into your Dokploy server
ssh your-server

# Create persistent directory
sudo mkdir -p /var/lib/key_findings_data
sudo chmod 755 /var/lib/key_findings_data
sudo chown 1000:1000 /var/lib/key_findings_data  # Match container user
```

### 1. Database Schema Implementation

#### File: `key_findings/database_manager.py`

```python
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

class KeyFindingsDBManager:
    """Database manager for Key Findings caching system"""

    def __init__(self, db_path: str = "key_findings.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._ensure_database_exists()
        self._create_schema()

    def _ensure_database_exists(self):
        """Ensure database directory and file exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _create_schema(self):
        """Create database schema if not exists"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Reports table for storing AI-generated findings
                CREATE TABLE IF NOT EXISTS key_findings_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_hash TEXT UNIQUE NOT NULL,
                    tool_name TEXT NOT NULL,
                    selected_sources TEXT NOT NULL,
                    date_range_start TEXT,
                    date_range_end TEXT,
                    language TEXT DEFAULT 'es',

                    -- AI Analysis Results
                    principal_findings TEXT NOT NULL,
                    pca_insights TEXT,
                    executive_summary TEXT NOT NULL,

                    -- Metadata
                    model_used TEXT NOT NULL,
                    api_latency_ms INTEGER,
                    confidence_score REAL,
                    generation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cache_version TEXT DEFAULT '1.0',

                    -- User Interaction
                    user_rating INTEGER,
                    user_feedback TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed DATETIME,

                    -- Performance Metrics
                    data_points_analyzed INTEGER,
                    sources_count INTEGER,
                    analysis_depth TEXT DEFAULT 'comprehensive'
                );

                -- Analysis history for tracking changes over time
                CREATE TABLE IF NOT EXISTS key_findings_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_hash TEXT NOT NULL,
                    report_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    previous_version_id INTEGER,
                    change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    change_reason TEXT,
                    FOREIGN KEY (report_id) REFERENCES key_findings_reports(id)
                );

                -- Model performance tracking
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER,
                    token_count INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    user_satisfaction INTEGER
                );

                -- Cache statistics for optimization
                CREATE TABLE IF NOT EXISTS cache_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_requests INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    cache_misses INTEGER DEFAULT 0,
                    avg_response_time_ms REAL,
                    unique_scenarios INTEGER DEFAULT 0
                );

                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_reports_scenario_hash ON key_findings_reports(scenario_hash);
                CREATE INDEX IF NOT EXISTS idx_reports_tool_name ON key_findings_reports(tool_name);
                CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON key_findings_reports(generation_timestamp);
                CREATE INDEX IF NOT EXISTS idx_history_scenario_hash ON key_findings_history(scenario_hash);
                CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON model_performance(request_timestamp);
            """)

    def generate_scenario_hash(self, tool_name: str, selected_sources: List[str],
                             date_range: tuple = None, language: str = 'es') -> str:
        """Generate unique hash for scenario identification"""
        scenario_data = {
            'tool': tool_name,
            'sources': sorted(selected_sources),
            'date_range': date_range,
            'language': language,
            'version': '1.0'
        }
        scenario_json = json.dumps(scenario_data, sort_keys=True)
        return hashlib.sha256(scenario_json.encode()).hexdigest()

    def store_report(self, scenario_hash: str, report_data: Dict[str, Any]) -> int:
        """Store a new report in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO key_findings_reports
                (scenario_hash, tool_name, selected_sources, date_range_start, date_range_end,
                 language, principal_findings, pca_insights, executive_summary,
                 model_used, api_latency_ms, confidence_score, data_points_analyzed,
                 sources_count, analysis_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario_hash,
                report_data['tool_name'],
                json.dumps(report_data['selected_sources']),
                report_data.get('date_range_start'),
                report_data.get('date_range_end'),
                report_data.get('language', 'es'),
                json.dumps(report_data['principal_findings']),
                json.dumps(report_data.get('pca_insights', {})),
                report_data['executive_summary'],
                report_data['model_used'],
                report_data.get('api_latency_ms'),
                report_data.get('confidence_score'),
                report_data.get('data_points_analyzed'),
                report_data.get('sources_count'),
                report_data.get('analysis_depth', 'comprehensive')
            ))
            return cursor.lastrowid

    def get_report(self, scenario_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve a report by scenario hash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM key_findings_reports
                WHERE scenario_hash = ?
            """, (scenario_hash,))
            row = cursor.fetchone()

            if row:
                # Update access count and last accessed
                conn.execute("""
                    UPDATE key_findings_reports
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (row['id'],))

                return {
                    'id': row['id'],
                    'scenario_hash': row['scenario_hash'],
                    'tool_name': row['tool_name'],
                    'selected_sources': json.loads(row['selected_sources']),
                    'date_range_start': row['date_range_start'],
                    'date_range_end': row['date_range_end'],
                    'language': row['language'],
                    'principal_findings': json.loads(row['principal_findings']),
                    'pca_insights': json.loads(row['pca_insights'] or '{}'),
                    'executive_summary': row['executive_summary'],
                    'model_used': row['model_used'],
                    'api_latency_ms': row['api_latency_ms'],
                    'confidence_score': row['confidence_score'],
                    'generation_timestamp': row['generation_timestamp'],
                    'cache_version': row['cache_version'],
                    'user_rating': row['user_rating'],
                    'user_feedback': row['user_feedback'],
                    'access_count': row['access_count'],
                    'last_accessed': row['last_accessed'],
                    'data_points_analyzed': row['data_points_analyzed'],
                    'sources_count': row['sources_count'],
                    'analysis_depth': row['analysis_depth']
                }
            return None
```

### 2. OpenRouter.ai Integration Service

#### File: `key_findings/ai_service.py`

```python
import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import os

@dataclass
class AIResponse:
    """Response structure for AI analysis"""
    success: bool
    content: str
    model_used: str
    response_time_ms: int
    token_count: int
    error_message: Optional[str] = None
    confidence_score: Optional[float] = None

class OpenRouterService:
    """Service for interacting with OpenRouter.ai API"""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key') or os.getenv('OPENROUTER_API_KEY')
        self.base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)

        # Model configuration
        self.primary_model = config.get('primary_model', 'openai/gpt-4o-mini')
        self.fallback_models = config.get('fallback_models', [
            'nvidia/llama-3.1-nemotron-70b-instruct',
            'meta-llama/llama-3.1-8b-instruct:free'
        ])
        self.all_models = [self.primary_model] + self.fallback_models

        self.logger = logging.getLogger(__name__)
        self._session = None

    async def generate_analysis(self, prompt: str, language: str = 'es') -> AIResponse:
        """Generate AI analysis with fallback models"""
        start_time = time.time()

        # Try models in order of preference
        for model in self.all_models:
            for attempt in range(self.max_retries):
                try:
                    result = await self._call_model(prompt, model, language)
                    response_time = int((time.time() - start_time) * 1000)

                    if result.success:
                        return AIResponse(
                            success=True,
                            content=result.content,
                            model_used=model,
                            response_time_ms=response_time,
                            token_count=result.token_count,
                            confidence_score=self._calculate_confidence(result.content)
                        )
                    else:
                        self.logger.warning(f"Model {model} attempt {attempt + 1} failed: {result.error_message}")

                except Exception as e:
                    self.logger.error(f"Model {model} attempt {attempt + 1} error: {e}")
                    if attempt == self.max_retries - 1:
                        break  # Try next model
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        # All models failed
        response_time = int((time.time() - start_time) * 1000)
        return AIResponse(
            success=False,
            content="",
            model_used="none",
            response_time_ms=response_time,
            token_count=0,
            error_message="All models failed to generate analysis"
        )

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on language"""
        if language == 'es':
            return """
            Eres un analista de investigación doctoral especializado en herramientas de gestión y análisis de datos temporales.
            Tu tarea es generar análisis de nivel ejecutivo con rigor académico doctoral.

            Directrices:
            1. Usa terminología académica precisa y conceptos de nivel doctoral
            2. Enfócate en insights de PCA (Análisis de Componentes Principales) como prioridad
            3. Genera abstracciones de alto nivel que identifiquen los insights más relevantes
            4. Estructura tus respuestas en puntos concisos con razonamiento profundo
            5. Mantén un tono académico adecuado para discurso académico
            6. Prioriza la coherencia lógica y el flujo del razonamiento
            7. Sé conciso pero sin sacrificar la profundidad analítica
            """
        else:
            return """
            You are a doctoral research analyst specializing in management tools and temporal data analysis.
            Your task is to generate executive-level analysis with doctoral academic rigor.

            Guidelines:
            1. Use precise academic terminology and doctoral-level concepts
            2. Focus on PCA (Principal Component Analysis) insights as priority
            3. Generate high-level abstractions identifying most relevant insights
            4. Structure responses in concise bullet points with deep reasoning
            5. Maintain academic tone suitable for scholarly discourse
            6. Prioritize logical coherence and reasoning flow
            7. Be concise without sacrificing analytical depth
            """
```

### 3. Data Aggregation Pipeline

#### File: `key_findings/data_aggregator.py`

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
import logging
from datetime import datetime

class DataAggregator:
    """Aggregates and synthesizes data from multiple dashboard sources"""

    def __init__(self, db_manager, cache_manager):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)

    def collect_analysis_data(self, tool_name: str, selected_sources: List[str],
                            language: str = 'es') -> Dict[str, Any]:
        """Collect all relevant data for AI analysis"""
        try:
            # Get raw data from database
            source_ids = self._map_sources_to_ids(selected_sources)
            datasets_norm, valid_sources = self.db_manager.get_data_for_keyword(tool_name, source_ids)

            if not datasets_norm:
                return {'error': 'No data available for selected sources'}

            # Create combined dataset
            combined_data = self._create_combined_dataset(datasets_norm, valid_sources)

            # Extract various analytical components
            analysis_data = {
                'tool_name': tool_name,
                'selected_sources': selected_sources,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'data_points': len(combined_data),
                'sources_count': len(valid_sources),
                'date_range': {
                    'start': combined_data.index.min().strftime('%Y-%m-%d'),
                    'end': combined_data.index.max().strftime('%Y-%m-%d')
                }
            }

            # Add statistical summaries
            analysis_data['statistical_summary'] = self._calculate_statistical_summaries(combined_data)

            # Add PCA insights (emphasized as per requirements)
            analysis_data['pca_insights'] = self._extract_pca_insights(combined_data)

            # Add trend analysis
            analysis_data['trend_analysis'] = self._identify_trends_and_anomalies(combined_data)

            # Add correlation analysis
            analysis_data['correlation_analysis'] = self._calculate_correlations(combined_data)

            # Anonymize sensitive data
            analysis_data = self._anonymize_sensitive_data(analysis_data)

            return analysis_data

        except Exception as e:
            self.logger.error(f"Error collecting analysis data: {e}")
            return {'error': f'Data collection failed: {str(e)}'}

    def _extract_pca_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extract PCA-specific insights for emphasis"""
        if len(data.columns) < 2:
            return {'error': 'PCA requires at least 2 variables'}

        try:
            # Standardize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data.dropna())

            # Perform PCA
            pca = PCA()
            pca_result = pca.fit_transform(scaled_data)

            # Extract insights
            insights = {
                'n_components': len(pca.components_),
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
                'dominant_components': [],
                'component_loadings': {},
                'variance_explained_summary': {}
            }

            # Identify dominant components (those explaining > 20% variance)
            for i, var_ratio in enumerate(pca.explained_variance_ratio_):
                if var_ratio > 0.2:
                    insights['dominant_components'].append({
                        'component': f'PC{i+1}',
                        'variance_explained': float(var_ratio),
                        'cumulative_variance': float(np.cumsum(pca.explained_variance_ratio_)[i])
                    })

            return insights

        except Exception as e:
            self.logger.error(f"Error extracting PCA insights: {e}")
            return {'error': f'PCA analysis failed: {str(e)}'}

    def _anonymize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or anonymize sensitive information before LLM processing"""
        # Remove any potentially sensitive identifiers
        if 'raw_data' in data:
            del data['raw_data']

        # Round numerical values to reduce precision
        if 'statistical_summary' in data:
            for source, stats in data['statistical_summary'].items():
                for key, value in stats.items():
                    if isinstance(value, float):
                        stats[key] = round(value, 4)

        return data
```

### 4. Prompt Engineering System

#### File: `key_findings/prompt_engineer.py`

```python
import json
from typing import Dict, Any, List
import logging

class PromptEngineer:
    """Creates sophisticated prompts for doctoral-level analysis"""

    def __init__(self, language: str = 'es'):
        self.language = language
        self.prompt_templates = self._load_templates()
        self.logger = logging.getLogger(__name__)

    def create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt"""
        if self.language == 'es':
            return self._create_spanish_prompt(data)
        else:
            return self._create_english_prompt(data)

    def _create_spanish_prompt(self, data: Dict[str, Any]) -> str:
        """Create Spanish analysis prompt"""
        prompt = f"""
ANÁLISIS DOCTORAL DE HERRAMIENTAS DE GESTIÓN

Herramienta: {data['tool_name']}
Fuentes de datos: {', '.join(data['selected_sources'])}
Período: {data['date_range']['start']} a {data['date_range']['end']}
Puntos de datos: {data['data_points']}

CONTEXTO ESTADÍSTICO:
{self._format_statistical_summary(data.get('statistical_summary', {}))}

INSIGHTS DE PCA (PRIORIDAD MÁXIMA):
{self._format_pca_insights(data.get('pca_insights', {}))}

ANÁLISIS DE TENDENCIAS:
{self._format_trend_analysis(data.get('trend_analysis', {}))}

ANÁLISIS DE CORRELACIÓN:
{self._format_correlation_analysis(data.get('correlation_analysis', {}))}

INSTRUCCIONES:
Genera un análisis ejecutivo de nivel doctoral con las siguientes secciones:

1. HALLAZGOS PRINCIPALES (máximo 5 puntos):
   • Cada punto debe ser una abstracción de alto nivel
   • Incluir razonamiento doctoral de 3-5 frases
   • Priorizar insights de PCA
   • Usar terminología académica precisa

2. INSIGHTS DE PCA:
   • Interpretación académica de componentes principales
   • Significado de la varianza explicada
   • Implicaciones para la gestión

3. RESUMEN EJECUTIVO (2-3 párrafos):
   • Síntesis doctoral de los hallazgos más relevantes
   • Implicaciones estratégicas de nivel ejecutivo
   • Conclusiones académicas significativas

REQUISITOS DE CALIDAD:
• Rigor académico doctoral
• Coherencia lógica y flujo
• Terminología precisa
• Abstracciones de alto nivel
• Enfoque en insights de PCA
"""
        return prompt

    def _create_english_prompt(self, data: Dict[str, Any]) -> str:
        """Create English analysis prompt"""
        prompt = f"""
DOCTORAL ANALYSIS OF MANAGEMENT TOOLS

Tool: {data['tool_name']}
Data Sources: {', '.join(data['selected_sources'])}
Period: {data['date_range']['start']} to {data['date_range']['end']}
Data Points: {data['data_points']}

STATISTICAL CONTEXT:
{self._format_statistical_summary(data.get('statistical_summary', {}))}

PCA INSIGHTS (HIGHEST PRIORITY):
{self._format_pca_insights(data.get('pca_insights', {}))}

TREND ANALYSIS:
{self._format_trend_analysis(data.get('trend_analysis', {}))}

CORRELATION ANALYSIS:
{self._format_correlation_analysis(data.get('correlation_analysis', {}))}

INSTRUCTIONS:
Generate an executive-level doctoral analysis with the following sections:

1. PRINCIPAL FINDINGS (maximum 5 points):
   • Each point should be a high-level abstraction
   • Include doctoral reasoning of 3-5 sentences
   • Prioritize PCA insights
   • Use precise academic terminology

2. PCA INSIGHTS:
   • Academic interpretation of principal components
   • Meaning of explained variance
   • Management implications

3. EXECUTIVE SUMMARY (2-3 paragraphs):
   • Doctoral synthesis of most relevant findings
   • Strategic executive-level implications
   • Significant academic conclusions

QUALITY REQUIREMENTS:
• Doctoral academic rigor
• Logical coherence and flow
• Precise terminology
• High-level abstractions
• Focus on PCA insights
"""
        return prompt

    def _format_statistical_summary(self, stats: Dict[str, Any]) -> str:
        """Format statistical summary for prompt"""
        if not stats:
            return "No statistical summary available"

        formatted = []
        for source, data in stats.items():
            formatted.append(f"{source}:")
            formatted.append(f"  Media: {data.get('mean', 'N/A')}")
            formatted.append(f"  Desviación: {data.get('std', 'N/A')}")
            formatted.append(f"  Tendencia: {data.get('trend_direction', 'N/A')}")
            formatted.append(f"  Volatilidad: {data.get('volatility', 'N/A')}")

        return '\n'.join(formatted)

    def _format_pca_insights(self, pca_data: Dict[str, Any]) -> str:
        """Format PCA insights for prompt"""
        if 'error' in pca_data:
            return "PCA analysis not available"

        formatted = []
        if 'dominant_components' in pca_data:
            formatted.append("Componentes Dominantes:")
            for comp in pca_data['dominant_components']:
                formatted.append(f"  {comp['component']}: {comp['variance_explained']:.1%} varianza explicada")

        if 'variance_explained_summary' in pca_data:
            summary = pca_data['variance_explained_summary']
            formatted.append(f"Varianza total en 2 componentes: {summary.get('total_variance_2pc', 'N/A'):.1%}")
            formatted.append(f"Componentes para 80% varianza: {summary.get('components_for_80pct', 'N/A')}")

        return '\n'.join(formatted)
```

### 5. Modal UI Component

#### File: `key_findings/modal_component.py`

```python
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional
import logging

class KeyFindingsModal:
    """Modal component for displaying Key Findings"""

    def __init__(self, app, language_store):
        self.app = app
        self.language_store = language_store
        self.logger = logging.getLogger(__name__)

    def create_modal_layout(self) -> dbc.Modal:
        """Create the modal layout with all sections"""
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("🧠 Key Findings - Análisis Doctoral",
                                              style={'fontSize': '18px', 'color': '#2c3e50'})),
                dbc.ModalBody(
                    dcc.Loading(
                        id="key-findings-loading",
                        type="circle",
                        children=[
                            html.Div(id="key-findings-content")
                        ],
                        style={'height': '400px'}
                    )
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button(
                            "🔄 Regenerar",
                            id="key-findings-rerun-btn",
                            color="warning",
                            size="sm",
                            className="me-2"
                        ),
                        dbc.Button(
                            "💾 Guardar",
                            id="key-findings-save-btn",
                            color="success",
                            size="sm",
                            className="me-2"
                        ),
                        dbc.Button(
                            "⭐ Calificar",
                            id="key-findings-rate-btn",
                            color="info",
                            size="sm",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Cerrar",
                            id="key-findings-close-btn",
                            color="secondary",
                            size="sm"
                        )
                    ], style={'display': 'flex', 'justifyContent': 'space-between'})
                )
            ],
            id="key-findings-modal",
            size="lg",
            centered=True,
            backdrop="static"
        )

    def create_findings_display(self, report_data: Dict[str, Any]) -> html.Div:
        """Create formatted display of AI findings"""
        if not report_data:
            return html.Div("No findings available", style={'textAlign': 'center', 'padding': '20px'})

        return html.Div([
            # Header with metadata
            html.Div([
                html.H5(f"📊 Análisis: {report_data.get('tool_name', 'Unknown Tool')}",
                       style={'color': '#2c3e50', 'marginBottom': '10px'}),
                html.P([
                    f"Fuentes: {', '.join(report_data.get('selected_sources', []))} | ",
                    f"Modelo: {report_data.get('model_used', 'Unknown')} | ",
                    f"Confianza: {report_data.get('confidence_score', 0):.1%} | ",
                    f"Generado: {report_data.get('generation_timestamp', 'Unknown')}"
                ], style={'fontSize': '12px', 'color': '#6c757d', 'marginBottom': '20px'})
            ]),

            # Principal Findings
            html.Div([
                html.H6("🎯 Hallazgos Principales", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("•", style={'color': '#007bff', 'fontWeight': 'bold', 'marginRight': '8px'}),
                            html.Span(finding['bullet_point'], style={'fontWeight': 'bold'}),
                            html.P(finding['reasoning'], style={'margin': '5px 0 0 20px', 'fontSize': '14px', 'color': '#495057'})
                        ], style={'marginBottom': '15px'})
                    ]) for finding in report_data.get('principal_findings', [])
                ])
            ], style={'marginBottom': '25px'}),

            # PCA Insights
            if report_data.get('pca_insights'):
                html.Div([
                    html.H6("📈 Insights de PCA", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    html.P(report_data.get('pca_insights', {}).get('dominant_components', 'No PCA insights available'),
                          style={'fontSize': '14px', 'color': '#495057'})
                ], style={'marginBottom': '25px'}),

            # Executive Summary
            html.Div([
                html.H6("📋 Resumen Ejecutivo", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                html.P(report_data.get('executive_summary', 'No executive summary available'),
                      style={'fontSize': '14px', 'lineHeight': '1.6', 'color': '#495057'})
            ])
        ])

    def create_loading_state(self) -> html.Div:
        """Create loading animation during AI processing"""
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("🤖 Generando Análisis Doctoral", style={'color': '#2c3e50'}),
                    html.P("Analizando datos con IA para generar insights de nivel ejecutivo...",
                          style={'color': '#6c757d'}),
                    html.Div([
                        html.Div(style={'width': '100%', 'height': '4px', 'backgroundColor': '#e9ecef', 'borderRadius': '2px'}),
                        html.Div(style={'width': '60%', 'height': '4px', 'backgroundColor': '#007bff', 'borderRadius': '2px',
                                       'animation': 'pulse 2s infinite'})
                    ], style={'margin': '20px 0'})
                ], style={'textAlign': 'center', 'padding': '40px'})
            ])
        ])
```

### 6. Interactive Workflow Integration

#### File: `key_findings/interactive_workflow.py`

```python
import dash
from dash import Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from typing import Dict, Any
import asyncio
import logging
import threading
import time

class AnalysisState:
    """Manages the state of interactive analysis workflow"""

    def __init__(self):
        self.current_config = None
        self.analysis_active = False
        self.analysis_interrupted = False
        self.countdown_active = False
        self.progress_percentage = 0
        self.current_step = ""
        self.current_analysis_task = None

    def update_config(self, tool, sources):
        """Update configuration and check if changed"""
        new_config = {'tool': tool, 'sources': sorted(sources)}

        if self.current_config != new_config:
            self.current_config = new_config
            self.reset_analysis()
            return True  # Configuration changed
        return False

    def reset_analysis(self):
        """Reset analysis state"""
        self.analysis_active = False
        self.analysis_interrupted = False
        self.progress_percentage = 0
        self.current_step = ""
        if self.current_analysis_task:
            self.current_analysis_task = None

    def start_countdown(self):
        """Start configuration review countdown"""
        self.countdown_active = True
        self.reset_analysis()

    def start_analysis(self):
        """Start the AI analysis"""
        self.analysis_active = True
        self.countdown_active = False
        self.analysis_interrupted = False

    def interrupt_analysis(self):
        """Interrupt the current analysis"""
        self.analysis_interrupted = True
        self.analysis_active = False

class KeyFindingsInteractiveIntegration:
    """Enhanced integration with interactive workflow and interruption support"""

    def __init__(self, app, db_manager, config):
        self.app = app
        self.db_manager = db_manager
        self.config = config
        self.state = AnalysisState()
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.modal_component = KeyFindingsModal(app, None)
        self.ai_service = OpenRouterService(config)
        self.cache_manager = KeyFindingsDBManager()
        self.data_aggregator = DataAggregator(db_manager, self.cache_manager)
        self.prompt_engineer = PromptEngineer()

        self._setup_interactive_callbacks()

    def _setup_interactive_callbacks(self):
        """Setup interactive callbacks with countdown and interruption support"""

        # Main orchestration callback
        @self.app.callback(
            [Output("config-review-modal", "is_open"),
             Output("progress-modal", "is_open"),
             Output("results-modal", "is_open"),
             Output("countdown-display", "children"),
             Output("config-changed-flag", "data")],
            [Input('keyword-dropdown', 'value'),
             Input('data-sources-store-v2', 'data'),
             Input("key-findings-trigger-btn", "n_clicks"),
             Input("start-now-btn", "n_clicks"),
             Input("interrupt-analysis", "n_clicks")],
            [State('language-store', 'data'),
             State('config-changed-flag', 'data')],
            prevent_initial_call=True
        )
        def orchestrate_interactive_analysis(tool, sources, trigger_click, start_click,
                                          interrupt_click, language, current_config_flag):
            ctx = dash.callback_context
            trigger_id = ctx.triggered[0]['prop_id'] if ctx.triggered else ""

            # Handle configuration changes
            if 'keyword-dropdown' in trigger_id or 'data-sources-store' in trigger_id:
                if self.state.update_config(tool, sources):
                    # Configuration changed - restart countdown
                    return True, False, False, "3", {'changed': True, 'config': self.state.current_config}

            # Handle initial trigger
            elif 'key-findings-trigger-btn' in trigger_id and trigger_click:
                if tool and sources:
                    self.state.start_countdown()
                    return True, False, False, "3", {'changed': False, 'config': self.state.current_config}

            # Handle manual start
            elif 'start-now-btn' in trigger_id and start_click:
                self.state.start_analysis()
                self._start_background_analysis(tool, sources, language)
                return False, True, False, "", {'changed': False, 'config': self.state.current_config}

            # Handle interruption
            elif 'interrupt-analysis' in trigger_id and interrupt_click:
                self.state.interrupt_analysis()
                self._cancel_current_analysis()
                return True, False, False, "3", {'changed': False, 'config': self.state.current_config}

            # Keep current state
            return False, False, False, "", current_config_flag or {'changed': False, 'config': None}

        # Countdown timer callback
        @self.app.callback(
            Output("countdown-timer", "children"),
            Output("countdown-timer", "style"),
            [Input("config-review-modal", "is_open")],
            [State('keyword-dropdown', 'value'),
             State('data-sources-store-v2', 'data')],
            interval=1000
        )
        def countdown_timer(modal_open, selected_tool, selected_sources):
            if not modal_open or not selected_tool or not selected_sources:
                return "", {}

            # This would be implemented with actual countdown logic
            # For now, return static display
            return "3", {'fontSize': '2rem', 'fontWeight': 'bold', 'color': '#ffc107'}

        # Progress monitoring callback
        @self.app.callback(
            Output("analysis-progress-bar", "style"),
            Output("analysis-status", "children"),
            Output("current-step", "children"),
            [Input("progress-modal", "is_open")],
            interval=500
        )
        def monitor_analysis_progress(modal_open):
            if not modal_open or not self.state.analysis_active:
                return {'width': '0%'}, "", ""

            # Return current progress
            width_style = {'width': f'{self.state.progress_percentage}%',
                          'height': '20px', 'backgroundColor': '#007bff',
                          'transition': 'width 0.3s ease', 'borderRadius': '10px'}

            return width_style, self.state.current_step, f"Step: {self.state.current_step}"

    def _start_background_analysis(self, tool, sources, language):
        """Start analysis that can be interrupted"""
        def analysis_worker():
            try:
                self.state.analysis_interrupted = False

                # Step 1: Data collection
                self.state.progress_percentage = 20
                self.state.current_step = "📊 Collecting data sources..."
                time.sleep(1)
                if self.state.analysis_interrupted:
                    return

                # Step 2: Data aggregation
                self.state.progress_percentage = 40
                self.state.current_step = "🔄 Processing and aggregating data..."
                time.sleep(2)
                if self.state.analysis_interrupted:
                    return

                # Step 3: PCA analysis
                self.state.progress_percentage = 60
                self.state.current_step = "📈 Performing PCA analysis..."
                time.sleep(1.5)
                if self.state.analysis_interrupted:
                    return

                # Step 4: AI prompt generation
                self.state.progress_percentage = 80
                self.state.current_step = "🤝 Generating AI prompts..."
                time.sleep(1)
                if self.state.analysis_interrupted:
                    return

                # Step 5: AI analysis
                self.state.progress_percentage = 90
                self.state.current_step = "🧠 Running AI analysis..."
                # Actual AI call here
                time.sleep(2)
                if self.state.analysis_interrupted:
                    return

                # Complete
                self.state.progress_percentage = 100
                self.state.current_step = "✅ Analysis complete!"
                time.sleep(1)
                self._show_results()

            except Exception as e:
                self._handle_analysis_error(e)

        # Start background thread
        self.state.current_analysis_task = threading.Thread(target=analysis_worker)
        self.state.current_analysis_task.daemon = True
        self.state.current_analysis_task.start()

    def _cancel_current_analysis(self):
        """Cancel the current analysis"""
        self.state.analysis_interrupted = True
        self.state.current_analysis_task = None

        # Update UI to show cancellation
        self.state.progress_percentage = 0
        self.state.current_step = "🛑 Analysis interrupted"

        # Reset for new analysis
        time.sleep(1)
        self.state.reset_analysis()

    def _show_results(self):
        """Show analysis results"""
        # This would trigger the results modal
        pass

    def _handle_analysis_error(self, error):
        """Handle analysis errors"""
        self.logger.error(f"Analysis error: {error}")
        self.state.current_step = f"❌ Error: {str(error)}"

    def _setup_callbacks(self):
        """Setup all Dash callbacks for Key Findings functionality"""

        # Trigger button callback
        @self.app.callback(
            Output("key-findings-modal", "is_open"),
            Input("key-findings-trigger-btn", "n_clicks"),
            State('keyword-dropdown', 'value'),
            State('data-sources-store-v2', 'data'),
            State('language-store', 'data'),
            prevent_initial_call=True
        )
        def toggle_key_findings_modal(n_clicks, selected_tool, selected_sources, language):
            if n_clicks and selected_tool and selected_sources:
                return True
            return False

        # Generate findings callback
        @self.app.callback(
            Output("key-findings-content", "children"),
            Input("key-findings-modal", "is_open"),
            State('keyword-dropdown', 'value'),
            State('data-sources-store-v2', 'data'),
            State('language-store', 'data'),
            prevent_initial_call=True
        )
        def generate_key_findings(is_open, selected_tool, selected_sources, language):
            if not is_open or not selected_tool or not selected_sources:
                return ""

            try:
                # Generate scenario hash
                scenario_hash = self.cache_manager.generate_scenario_hash(
                    selected_tool, selected_sources, language=language
                )

                # Check cache first
                cached_report = self.cache_manager.get_report(scenario_hash)
                if cached_report:
                    self.cache_manager.update_cache_statistics(
                        datetime.now(), cache_hit=True, response_time_ms=0
                    )
                    return self.modal_component.create_findings_display(cached_report)

                # Generate new analysis
                return self._generate_new_analysis(selected_tool, selected_sources, language, scenario_hash)

            except Exception as e:
                self.logger.error(f"Error generating key findings: {e}")
                return html.Div(f"Error generating analysis: {str(e)}",
                              style={'textAlign': 'center', 'padding': '20px', 'color': 'red'})

        # Rerun analysis callback
        @self.app.callback(
            Output("key-findings-content", "children", allow_duplicate=True),
            Input("key-findings-rerun-btn", "n_clicks"),
            State('keyword-dropdown', 'value'),
            State('data-sources-store-v2', 'data'),
            State('language-store', 'data'),
            prevent_initial_call=True
        )
        def rerun_analysis(n_clicks, selected_tool, selected_sources, language):
            if n_clicks and selected_tool and selected_sources:
                # Force new analysis by bypassing cache
                return self._generate_new_analysis(selected_tool, selected_sources, language, force_new=True)
            return ""

    def _generate_new_analysis(self, selected_tool: str, selected_sources: List[str],
                             language: str, scenario_hash: str = None, force_new: bool = False) -> html.Div:
        """Generate new AI analysis"""
        try:
            # Collect analysis data
            analysis_data = self.data_aggregator.collect_analysis_data(selected_tool, selected_sources, language)

            if 'error' in analysis_data:
                return html.Div(f"Data collection error: {analysis_data['error']}",
                              style={'textAlign': 'center', 'padding': '20px', 'color': 'red'})

            # Generate prompt
            prompt = self.prompt_engineer.create_analysis_prompt(analysis_data)

            # Generate AI analysis (synchronous for Dash)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            ai_response = loop.run_until_complete(self.ai_service.generate_analysis(prompt, language))

            if not ai_response.success:
                return html.Div(f"AI analysis failed: {ai_response.error_message}",
                              style={'textAlign': 'center', 'padding': '20px', 'color': 'red'})

            # Parse AI response
            parsed_findings = self._parse_ai_response(ai_response.content, analysis_data)

            # Store in cache
            if scenario_hash and not force_new:
                report_data = {
                    'tool_name': selected_tool,
                    'selected_sources': selected_sources,
                    'language': language,
                    'principal_findings': parsed_findings['principal_findings'],
                    'pca_insights': parsed_findings.get('pca_insights', {}),
                    'executive_summary': parsed_findings['executive_summary'],
                    'model_used': ai_response.model_used,
                    'api_latency_ms': ai_response.response_time_ms,
                    'confidence_score': ai_response.confidence_score,
                    'data_points_analyzed': analysis_data['data_points'],
                    'sources_count': len(selected_sources)
                }

                self.cache_manager.store_report(scenario_hash, report_data)
                self.cache_manager.update_cache_statistics(
                    datetime.now(), cache_hit=False, response_time_ms=ai_response.response_time_ms
                )

            # Log performance
            self.cache_manager.log_model_performance(
                ai_response.model_used, ai_response.response_time_ms,
                ai_response.token_count, True
            )

            return self.modal_component.create_findings_display(parsed_findings)

        except Exception as e:
            self.logger.error(f"Error in _generate_new_analysis: {e}")
            return html.Div(f"Analysis generation error: {str(e)}",
                          style={'textAlign': 'center', 'padding': '20px', 'color': 'red'})

    def _parse_ai_response(self, ai_content: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        lines = ai_content.split('\n')

        principal_findings = []
        pca_insights = ""
        executive_summary = ""

        current_section = None
        current_finding = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            if 'HALLAZGOS PRINCIPALES' in line.upper() or 'PRINCIPAL FINDINGS' in line.upper():
                current_section = 'findings'
            elif 'INSIGHTS DE PCA' in line.upper() or 'PCA INSIGHTS' in line.upper():
                current_section = 'pca'
            elif 'RESUMEN EJECUTIVO' in line.upper() or 'EXECUTIVE SUMMARY' in line.upper():
                current_section = 'summary'
            elif line.startswith('•') or line.startswith('-'):
                if current_section == 'findings':
                    # Extract bullet point and reasoning
                    parts = line.split('•', 1)[1].strip() if '•' in line else line[1:].strip()
                    if ':' in parts:
                        bullet_point, reasoning = parts.split(':', 1)
                        principal_findings.append({
                            'bullet_point': bullet_point.strip(),
                            'reasoning': reasoning.strip(),
                            'data_source': analysis_data.get('selected_sources', []),
                            'confidence': 'high'
                        })
            elif current_section == 'pca':
                pca_insights += line + ' '
            elif current_section == 'summary':
                executive_summary += line + ' '

        return {
            'principal_findings': principal_findings,
            'pca_insights': {'dominant_components': pca_insights.strip()},
            'executive_summary': executive_summary.strip()
        }
```

### 7. Configuration Management

#### File: `key_findings/config.py`

```python
import os
from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class KeyFindingsConfig:
    """Configuration for Key Findings module"""

    # API Configuration
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 30
    max_retries: int = 3

    # Model Configuration
    primary_model: str = "openai/gpt-4o-mini"
    fallback_models: List[str] = None

    # Cache Configuration
    cache_ttl: int = 86400  # 24 hours
    max_history: int = 100
    auto_generate: bool = True

    # Analysis Configuration
    max_data_points: int = 10000
    pca_emphasis_weight: float = 0.3
    confidence_threshold: float = 0.7

    # Security Configuration
    anonymize_data: bool = True
    max_token_limit: int = 4000

    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = [
                "nvidia/llama-3.1-nemotron-70b-instruct",
                "meta-llama/llama-3.1-8b-instruct:free"
            ]

    @classmethod
    def from_env(cls) -> 'KeyFindingsConfig':
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv('OPENROUTER_API_KEY', ''),
            base_url=os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
            timeout=int(os.getenv('OPENROUTER_TIMEOUT', '30')),
            max_retries=int(os.getenv('OPENROUTER_MAX_RETRIES', '3')),
            primary_model=os.getenv('PRIMARY_MODEL', 'openai/gpt-4o-mini'),
            fallback_models=os.getenv('FALLBACK_MODELS', '').split(',') if os.getenv('FALLBACK_MODELS') else None,
            cache_ttl=int(os.getenv('KEY_FINDINGS_CACHE_TTL', '86400')),
            max_history=int(os.getenv('KEY_FINDINGS_MAX_HISTORY', '100')),
            auto_generate=os.getenv('KEY_FINDINGS_AUTO_GENERATE', 'true').lower() == 'true',
            max_data_points=int(os.getenv('KEY_FINDINGS_MAX_DATA_POINTS', '10000')),
            pca_emphasis_weight=float(os.getenv('KEY_FINDINGS_PCA_WEIGHT', '0.3')),
            confidence_threshold=float(os.getenv('KEY_FINDINGS_CONFIDENCE_THRESHOLD', '0.7')),
            anonymize_data=os.getenv('KEY_FINDINGS_ANONYMIZE_DATA', 'true').lower() == 'true',
            max_token_limit=int(os.getenv('KEY_FINDINGS_MAX_TOKENS', '4000'))
        )

    @classmethod
    def from_file(cls, config_path: str) -> 'KeyFindingsConfig':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'primary_model': self.primary_model,
            'fallback_models': self.fallback_models,
            'cache_ttl': self.cache_ttl,
            'max_history': self.max_history,
            'auto_generate': self.auto_generate,
            'max_data_points': self.max_data_points,
            'pca_emphasis_weight': self.pca_emphasis_weight,
            'confidence_threshold': self.confidence_threshold,
            'anonymize_data': self.anonymize_data,
            'max_token_limit': self.max_token_limit
        }
```

## Integration Steps

### 1. Add to Main Dashboard

#### Modify `dashboard_app/app.py`:

```python
# Add imports at the top
from key_findings.dashboard_integration import KeyFindingsIntegration
from key_findings.config import KeyFindingsConfig

# Initialize Key Findings after app creation
key_findings_config = KeyFindingsConfig.from_env()
key_findings_integration = KeyFindingsIntegration(app, db_manager, key_findings_config.to_dict())

# Add Key Findings button to navigation
def update_navigation_visibility(selected_keyword, selected_sources, language):
    # ... existing code ...

    if selected_keyword and selected_sources:
        # ... existing navigation buttons ...

        # Add Key Findings button
        nav_buttons.append({
            "id": 11,
            "text": "🧠 Key Findings",
            "href": "#key-findings-modal",
            "color": "#e8f5e8",
            "border": "#28a745",
            "min_sources": 1
        })

    # ... rest of existing code ...

# Add Key Findings modal to layout
app.layout.children.append(key_findings_integration.modal_component.create_modal_layout())

# Add Key Findings trigger button to main content
def update_main_content(selected_sources, selected_keyword, language):
    # ... existing code ...

    if selected_keyword and selected_sources:
        # Add Key Findings trigger button
        content.append(html.Div([
            dbc.Button(
                "🧠 Generar Key Findings",
                id="key-findings-trigger-btn",
                color="success",
                size="lg",
                className="mb-3",
                style={'fontSize': '14px', 'fontWeight': 'bold'}
            )
        ], style={'textAlign': 'center', 'margin': '20px 0'}))

    # ... rest of existing code ...
```

### 2. Update Requirements

#### Add to `dashboard_app/requirements.txt`:

```
aiohttp>=3.8.0
asyncio-throttle>=1.0.2
```

### 3. Environment Configuration

#### Add to `.env`:

```env
# OpenRouter.ai Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TIMEOUT=30
OPENROUTER_MAX_RETRIES=3

# ⚠️ CRITICAL: Persistent Database Configuration (Required for Docker/Dokploy)
KEY_FINDINGS_DB_PATH=/app/data/key_findings.db
KEY_FINDINGS_BACKUP_PATH=/app/data/backups/
KEY_FINDINGS_BACKUP_INTERVAL=3600  # Backup every hour
KEY_FINDINGS_DATA_DIR=/app/data
KEY_FINDINGS_VOLUME_MOUNT=/var/lib/key_findings_data

# Key Findings Configuration
KEY_FINDINGS_CACHE_TTL=86400
KEY_FINDINGS_MAX_HISTORY=100
KEY_FINDINGS_AUTO_GENERATE=true
KEY_FINDINGS_MAX_DATA_POINTS=10000
KEY_FINDINGS_PCA_WEIGHT=0.3
KEY_FINDINGS_CONFIDENCE_THRESHOLD=0.7
KEY_FINDINGS_ANONYMIZE_DATA=true
KEY_FINDINGS_MAX_TOKENS=4000

# Model Configuration
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODELS=nvidia/llama-3.1-nemotron-70b-instruct,meta-llama/llama-3.1-8b-instruct:free
```

## Testing Strategy

### 1. Unit Tests

#### File: `tests/test_key_findings.py`

```python
import pytest
import unittest
from unittest.mock import Mock, patch
from key_findings.database_manager import KeyFindingsDBManager
from key_findings.ai_service import OpenRouterService
from key_findings.data_aggregator import DataAggregator
from key_findings.prompt_engineer import PromptEngineer

class TestKeyFindingsDBManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = KeyFindingsDBManager(":memory:")

    def test_generate_scenario_hash(self):
        hash1 = self.db_manager.generate_scenario_hash("Tool1", ["Source1", "Source2"])
        hash2 = self.db_manager.generate_scenario_hash("Tool1", ["Source1", "Source2"])
        hash3 = self.db_manager.generate_scenario_hash("Tool2", ["Source1", "Source2"])

        self.assertEqual(hash1, hash2)  # Same inputs should produce same hash
        self.assertNotEqual(hash1, hash3)  # Different inputs should produce different hash

    def test_store_and_retrieve_report(self):
        scenario_hash = "test_hash"
        report_data = {
            'tool_name': 'Test Tool',
            'selected_sources': ['Source1'],
            'principal_findings': [{'bullet_point': 'Test', 'reasoning': 'Test reasoning'}],
            'executive_summary': 'Test summary',
            'model_used': 'test-model'
        }

        report_id = self.db_manager.store_report(scenario_hash, report_data)
        self.assertIsNotNone(report_id)

        retrieved = self.db_manager.get_report(scenario_hash)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['tool_name'], 'Test Tool')
        self.assertEqual(retrieved['model_used'], 'test-model')

class TestPromptEngineer(unittest.TestCase):

    def setUp(self):
        self.prompt_engineer_es = PromptEngineer('es')
        self.prompt_engineer_en = PromptEngineer('en')

    def test_create_spanish_prompt(self):
        data = {
            'tool_name': 'Test Tool',
            'selected_sources': ['Source1'],
            'date_range': {'start': '2020-01-01', 'end': '2023-12-31'},
            'data_points': 100
        }

        prompt = self.prompt_engineer_es.create_analysis_prompt(data)
        self.assertIn('ANÁLISIS DOCTORAL', prompt)
        self.assertIn('Test Tool', prompt)
        self.assertIn('Source1', prompt)

    def test_create_english_prompt(self):
        data = {
            'tool_name': 'Test Tool',
            'selected_sources': ['Source1'],
            'date_range': {'start': '2020-01-01', 'end': '2023-12-31'},
            'data_points': 100
        }

        prompt = self.prompt_engineer_en.create_analysis_prompt(data)
        self.assertIn('DOCTORAL ANALYSIS', prompt)
        self.assertIn('Test Tool', prompt)
        self.assertIn('Source1', prompt)

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Tests

#### File: `tests/test_integration.py`

```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from key_findings.dashboard_integration import KeyFindingsIntegration

class TestKeyFindingsIntegration(unittest.TestCase):

    def setUp(self):
        self.mock_app = Mock()
        self.mock_db_manager = Mock()
        self.config = {
            'api_key': 'test_key',
            'primary_model': 'test-model'
        }

    @patch('key_findings.dashboard_integration.OpenRouterService')
    @patch('key_findings.dashboard_integration.KeyFindingsDBManager')
    @patch('key_findings.dashboard_integration.DataAggregator')
    def test_initialization(self, mock_aggregator, mock_db, mock_ai):
        integration = KeyFindingsIntegration(self.mock_app, self.mock_db_manager, self.config)

        self.assertIsNotNone(integration.ai_service)
        self.assertIsNotNone(integration.cache_manager)
        self.assertIsNotNone(integration.data_aggregator)
        self.assertIsNotNone(integration.prompt_engineer)

    def test_generate_scenario_hash_consistency(self):
        # Test that same inputs generate same hash
        integration = KeyFindingsIntegration(self.mock_app, self.mock_db_manager, self.config)

        hash1 = integration.cache_manager.generate_scenario_hash("Tool1", ["Source1", "Source2"])
        hash2 = integration.cache_manager.generate_scenario_hash("Tool1", ["Source1", "Source2"])

        self.assertEqual(hash1, hash2)

if __name__ == '__main__':
    unittest.main()
```

## Deployment Checklist

### 1. Pre-deployment

- [ ] API key configured and tested
- [ ] Database schema created
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Performance benchmarks completed
- [ ] Security review completed

### 2. Deployment Steps

- [ ] Update requirements.txt
- [ ] Add environment variables
- [ ] Run database migrations
- [ ] Deploy code changes
- [ ] Verify functionality
- [ ] Monitor performance

### 3. Post-deployment

- [ ] Monitor API usage and costs
- [ ] Track cache hit rates
- [ ] Collect user feedback
- [ ] Optimize based on metrics
- [ ] Plan enhancements

This comprehensive implementation plan provides all the necessary components to successfully integrate the Key Findings module into the existing dashboard with AI-powered doctoral-level analysis capabilities.
