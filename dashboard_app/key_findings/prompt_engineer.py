"""
Prompt Engineering System

Creates sophisticated prompts for doctoral-level analysis of
management tools data with emphasis on PCA insights and bilingual support.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class PromptEngineer:
    """
    Creates sophisticated prompts for doctoral-level analysis.
    
    Generates context-aware prompts with PCA emphasis, bilingual support,
    and structured output requirements for AI analysis.
    """

    def __init__(self, language: str = 'es'):
        """
        Initialize prompt engineer.
        
        Args:
            language: Analysis language ('es' or 'en')
        """
        self.language = language
        self.prompt_templates = self._load_templates()

    def create_analysis_prompt(self, data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Create comprehensive analysis prompt.

        Args:
            data: Aggregated analysis data
            context: Additional context for analysis

        Returns:
            Complete analysis prompt string
        """
        import time
        start_time = time.time()
        logging.info(f"📝 Starting prompt generation for tool '{data.get('tool_name', 'Unknown')}' in {self.language}")

        template = self.prompt_templates['comprehensive_analysis'][self.language]
        
        # Extract key information
        tool_name = data.get('tool_name', 'Unknown Tool')
        sources = data.get('selected_sources', [])
        pca_insights = data.get('pca_insights', {})
        stats_summary = data.get('statistical_summary', {})
        trends = data.get('trends_analysis', {})
        data_quality = data.get('data_quality', {})
        
        # Build prompt sections
        sections = []
        
        # Context section
        sections.append(self._build_context_section(tool_name, sources, data))
        
        # PCA emphasis section
        sections.append(self._build_pca_section(pca_insights))
        
        # Statistical analysis section
        sections.append(self._build_statistics_section(stats_summary))
        
        # Trends and patterns section
        sections.append(self._build_trends_section(trends))
        
        # Data quality section
        sections.append(self._build_data_quality_section(data_quality))
        
        # Analysis requirements
        sections.append(self._build_requirements_section())
        
        # Output format
        sections.append(self._build_output_format_section())
        
        prompt = template.format(
            analysis_date=datetime.now().strftime('%Y-%m-%d'),
            context='\n\n'.join(sections)
        )

        generation_time = time.time() - start_time
        logging.info(f"✅ Prompt generation completed in {generation_time:.2f}s - prompt length: {len(prompt)} characters")
        logging.info(f"📊 Prompt sections created: {len(sections)} sections")

        return prompt

    def create_pca_focused_prompt(self, pca_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Create PCA-focused analysis prompt.
        
        Args:
            pca_data: PCA analysis data
            context: Additional context for analysis
            
        Returns:
            PCA-focused analysis prompt string
        """
        template = self.prompt_templates['pca_focused'][self.language]
        
        tool_name = context.get('tool_name', 'Unknown Tool')
        components = pca_data.get('dominant_patterns', [])
        variance_explained = pca_data.get('total_variance_explained', 0)
        
        sections = []
        
        # PCA context
        sections.append(f"## Herramienta de Gestión Analizada: {tool_name}" if self.language == 'es' 
                      else f"## Management Tool Analyzed: {tool_name}")
        
        # Component analysis
        for i, component in enumerate(components[:3]):  # Top 3 components
            sections.append(self._build_component_analysis(component, i+1))
        
        # Variance explanation
        sections.append(self._build_variance_analysis(variance_explained))
        
        # Interpretation requirements
        sections.append(self._build_pca_requirements())
        
        return template.format(
            analysis_date=datetime.now().strftime('%Y-%m-%d'),
            pca_analysis='\n\n'.join(sections)
        )

    def create_executive_summary_prompt(self, findings: Dict[str, Any]) -> str:
        """
        Create prompt for executive summary generation.
        
        Args:
            findings: Analysis findings to summarize
            
        Returns:
            Executive summary prompt string
        """
        template = self.prompt_templates['executive_summary'][self.language]
        
        tool_name = findings.get('tool_name', 'Unknown Tool')
        principal_findings = findings.get('principal_findings', [])
        
        sections = []
        
        # Executive context
        sections.append(f"## Herramienta: {tool_name}" if self.language == 'es' 
                      else f"## Tool: {tool_name}")
        
        # Key findings synthesis
        sections.append(self._build_findings_synthesis(principal_findings))
        
        # Strategic implications
        sections.append(self._build_strategic_implications(findings))
        
        # Recommendations
        sections.append(self._build_recommendations(findings))
        
        return template.format(
            executive_date=datetime.now().strftime('%Y-%m-%d'),
            executive_content='\n\n'.join(sections)
        )

    def _build_context_section(self, tool_name: str, sources: List[str], data: Dict[str, Any]) -> str:
        """Build context section of prompt."""
        date_range = f"del {data.get('date_range_start', 'N/A')} al {data.get('date_range_end', 'N/A')}"
        data_points = data.get('data_points_analyzed', 0)
        
        if self.language == 'es':
            return f"""
### CONTEXTO DEL ANÁLISIS

**Herramienta de Gestión:** {tool_name}
**Fuentes de Datos Seleccionadas:** {', '.join(sources)}
**Rango Temporal:** {date_range}
**Puntos de Datos Analizados:** {data_points:,}

Este análisis se basa en datos multi-fuente recopilados de diversas bases de datos académicas y empresariales,
proporcionando una visión integral del comportamiento de la herramienta de gestión a lo largo del tiempo.
"""
        else:
            return f"""
### ANALYSIS CONTEXT

**Management Tool:** {tool_name}
**Selected Data Sources:** {', '.join(sources)}
**Time Range:** {date_range}
**Data Points Analyzed:** {data_points:,}

This analysis is based on multi-source data collected from various academic and business databases,
providing a comprehensive view of the management tool's behavior over time.
"""

    def _build_pca_section(self, pca_insights: Dict[str, Any]) -> str:
        """Build PCA emphasis section with unified narrative prompt."""
        if not pca_insights or pca_insights.get('error'):
            return ""

        components = pca_insights.get('dominant_patterns', [])
        variance_explained = pca_insights.get('total_variance_explained', 0)
        tool_name = pca_insights.get('tool_name', 'Unknown Tool')

        # Extract variable relationships for narrative
        variable_relationships = self._extract_variable_relationships(pca_insights)

        if self.language == 'es':
            section = f"""
### ANÁLISIS DE COMPONENTES PRINCIPALES (PCA) - NARRATIVA UNIFICADA

**Datos PCA Adjuntos:**
- Herramienta de Gestión Analizada: {tool_name}
- Varianza Total Explicada: {variance_explained:.1f}%
- Componentes Principales Identificados: {len(components)}

**INSTRUCCIONES PARA ANÁLISIS PCA:**

Proporciona una sola narrativa unificada que fusione insights desde una perspectiva [estratégica empresarial] con una perspectiva [académica/organizacional].

Tu análisis debe enfocarse en la historia central que los datos cuentan, especialmente las relaciones clave y tensiones entre factores como {variable_relationships}.

Asegúrate de fundamentar todas las conclusiones incorporando datos numéricos específicos de las gráficas, tales como cargas de componentes y el porcentaje de varianza explicada.

**Ejemplo de Estructura Narrativa:**
- Comienza con el poder del PCA (componentes que capturan X% de varianza)
- Identifica dinámicas clave (ej: "dinámica de adopción" con correlaciones específicas)
- Muestra relaciones inversas que crean "trampas" (cargas negativas específicas)
- Revela cómo diferentes discursos operan en ejes distintos
- Conecta con brechas teoría-práctica usando datos numéricos

**Patrones Dominantes Identificados:**
"""
        else:
            section = f"""
### PRINCIPAL COMPONENT ANALYSIS (PCA) - UNIFIED NARRATIVE

**Attached PCA Data:**
- Management Tool Analyzed: {tool_name}
- Total Variance Explained: {variance_explained:.1f}%
- Principal Components Identified: {len(components)}

**PCA ANALYSIS INSTRUCTIONS:**

Provide a single, unified narrative that fuses insights from a [strategic business] viewpoint with a [academic/organizational culture] viewpoint.

Your analysis should focus on the core story the data tells, especially the key relationships and tensions between factors like {variable_relationships}.

Be sure to ground all conclusions by incorporating specific numerical data from the graphs, such as component loadings and the percentage of variance explained.

**Narrative Structure Example:**
- Start with PCA power (components capturing X% of variance)
- Identify key dynamics (e.g., "adoption dynamic" with specific correlations)
- Show inverse relationships creating "traps" (specific negative loadings)
- Reveal how different discourses operate on different axes
- Connect to theory-practice gaps using numerical data

**Dominant Patterns Identified:**
"""

        for i, component in enumerate(components[:3]):
            comp_num = i + 1
            interpretation = component.get('interpretation', f'Component {comp_num}')
            variance = component.get('variance_explained', 0)
            loadings = component.get('loadings', {})

            if self.language == 'es':
                section += f"""
**Componente {comp_num}** ({variance:.1f}% varianza explicada):
{interpretation}
"""
                if loadings:
                    section += "**Cargas principales:**\n"
                    for var, loading in loadings.items():
                        section += f"- {var}: {loading:.3f}\n"
            else:
                section += f"""
**Component {comp_num}** ({variance:.1f}% variance explained):
{interpretation}
"""
                if loadings:
                    section += "**Principal loadings:**\n"
                    for var, loading in loadings.items():
                        section += f"- {var}: {loading:.3f}\n"

        return section

    def _build_statistics_section(self, stats_summary: Dict[str, Any]) -> str:
        """Build statistical analysis section."""
        if not stats_summary:
            return ""
        
        source_stats = stats_summary.get('source_statistics', {})
        correlations = stats_summary.get('correlations', {})
        
        if self.language == 'es':
            section = """
### ANÁLISIS ESTADÍSTICO COMPRENSIVO

**Estadísticas por Fuente de Datos:**
"""
        else:
            section = """
### COMPREHENSIVE STATISTICAL ANALYSIS

**Statistics by Data Source:**
"""
        
        # Add source statistics
        for source, stats in source_stats.items():
            if self.language == 'es':
                section += f"""
**{source}:**
- Media: {stats.get('mean', 'N/A'):.2f}
- Desviación Estándar: {stats.get('std', 'N/A'):.2f}
- Tendencia: {stats.get('trend', {}).get('trend_direction', 'N/A')}
- Significancia: {stats.get('trend', {}).get('significance', 'N/A')}
"""
            else:
                section += f"""
**{source}:**
- Mean: {stats.get('mean', 'N/A'):.2f}
- Standard Deviation: {stats.get('std', 'N/A'):.2f}
- Trend: {stats.get('trend', {}).get('trend_direction', 'N/A')}
- Significance: {stats.get('trend', {}).get('significance', 'N/A')}
"""
        
        # Add correlations
        if correlations:
            if self.language == 'es':
                section += "\n**Correlaciones Significativas Entre Fuentes:**\n"
            else:
                section += "\n**Significant Correlations Between Sources:**\n"
            
            for corr_pair, corr_data in correlations.items():
                if corr_data.get('significance') == 'significant':
                    strength = corr_data.get('strength', 'unknown')
                    if self.language == 'es':
                        section += f"- {corr_pair}: Correlación {strength} ({corr_data.get('correlation', 0):.3f})\n"
                    else:
                        section += f"- {corr_pair}: {strength} correlation ({corr_data.get('correlation', 0):.3f})\n"
        
        return section

    def _build_trends_section(self, trends: Dict[str, Any]) -> str:
        """Build trends and patterns section."""
        if not trends:
            return ""
        
        trend_data = trends.get('trends', {})
        anomalies = trends.get('anomalies', {})
        patterns = trends.get('overall_patterns', [])
        
        if self.language == 'es':
            section = """
### ANÁLISIS DE TENDENCIAS Y PATRONES TEMPORALES

**Tendencias Identificadas:**
"""
        else:
            section = """
### TEMPORAL TRENDS AND PATTERNS ANALYSIS

**Identified Trends:**
"""
        
        # Add trend information
        for source, trend_info in trend_data.items():
            direction = trend_info.get('trend_direction', 'stable')
            momentum = trend_info.get('momentum', 0)
            
            if self.language == 'es':
                section += f"""
**{source}:**
- Dirección de Tendencia: {direction}
- Momento Reciente: {momentum:.3f}
- Volatilidad: {trend_info.get('volatility', 0):.3f}
"""
            else:
                section += f"""
**{source}:**
- Trend Direction: {direction}
- Recent Momentum: {momentum:.3f}
- Volatility: {trend_info.get('volatility', 0):.3f}
"""
        
        # Add anomalies
        if anomalies:
            if self.language == 'es':
                section += "\n**Anomalías Detectadas:**\n"
            else:
                section += "\n**Detected Anomalies:**\n"
            
            for source, anomaly_info in anomalies.items():
                count = anomaly_info.get('count', 0)
                percentage = anomaly_info.get('percentage', 0)
                
                if self.language == 'es':
                    section += f"- {source}: {count} anomalías ({percentage:.1f}% de los datos)\n"
                else:
                    section += f"- {source}: {count} anomalies ({percentage:.1f}% of data)\n"
        
        # Add overall patterns
        if patterns:
            if self.language == 'es':
                section += "\n**Patrones Generales:**\n"
            else:
                section += "\n**Overall Patterns:**\n"
            
            for pattern in patterns:
                section += f"- {pattern}\n"
        
        return section

    def _build_data_quality_section(self, data_quality: Dict[str, Any]) -> str:
        """Build data quality assessment section."""
        if not data_quality:
            return ""
        
        overall_score = data_quality.get('overall_score', 0)
        completeness = data_quality.get('completeness', {})
        timeliness = data_quality.get('timeliness', {})
        
        if self.language == 'es':
            section = f"""
### EVALUACIÓN DE CALIDAD DE DATOS

**Puntuación General de Calidad:** {overall_score:.1f}/100

**Completitud por Fuente:**
"""
        else:
            section = f"""
### DATA QUALITY ASSESSMENT

**Overall Quality Score:** {overall_score:.1f}/100

**Completeness by Source:**
"""
        
        # Add completeness information
        for source, comp_data in completeness.items():
            comp_pct = comp_data.get('completeness_percentage', 0)
            missing_pct = comp_data.get('missing_percentage', 0)
            
            if self.language == 'es':
                section += f"- {source}: {comp_pct:.1f}% completo, {missing_pct:.1f}% faltante\n"
            else:
                section += f"- {source}: {comp_pct:.1f}% complete, {missing_pct:.1f}% missing\n"
        
        # Add timeliness
        if timeliness:
            latest_date = timeliness.get('latest_date', 'N/A')
            days_since = timeliness.get('days_since_latest', 0)
            timeliness_score = timeliness.get('timeliness_score', 0)
            
            if self.language == 'es':
                section += f"""
**Actualidad de los Datos:**
- Fecha más reciente: {latest_date}
- Días desde actualización: {days_since}
- Puntuación de actualidad: {timeliness_score:.1f}/100
"""
            else:
                section += f"""
**Data Timeliness:**
- Most Recent Date: {latest_date}
- Days Since Update: {days_since}
- Timeliness Score: {timeliness_score:.1f}/100
"""
        
        return section

    def _build_requirements_section(self) -> str:
        """Build analysis requirements section."""
        if self.language == 'es':
            return """
### REQUISITOS DEL ANÁLISIS

Por favor, proporciona un análisis doctoral-level que:

1. **Sintetice Información Multi-fuente**: Integre insights de todas las fuentes de datos
2. **Énfasis en PCA**: Destaque insights de componentes principales con explicaciones claras
3. **Identifique Patrones Temporales**: Detecte tendencias, ciclos y anomalías significativas
4. **Genere Conclusiones Ejecutivas**: Proporcione insights accionables para tomadores de decisiones
5. **Mantenga Rigor Académico**: Use terminología apropiada y metodología sistemática

**Formato de Salida Requerido:**
Responde únicamente en formato JSON con la siguiente estructura:
```json
{
  "principal_findings": [
    {
      "bullet_point": "Insight principal con datos específicos",
      "reasoning": "Explicación detallada del porqué este insight es importante",
      "data_source": ["Fuentes que soportan este finding"],
      "confidence": "high|medium|low"
    }
  ],
  "pca_insights": {
    "dominant_components": "Descripción de componentes principales",
    "variance_explained": "Porcentaje de varianza explicada",
    "key_patterns": ["Patrones clave identificados"]
  },
  "executive_summary": "Resumen ejecutivo conciso y accionable (2-3 frases)"
}
```
"""
        else:
            return """
### ANALYSIS REQUIREMENTS

Please provide a doctoral-level analysis that:

1. **Synthesizes Multi-source Information**: Integrate insights from all data sources
2. **Emphasizes PCA**: Highlight principal component insights with clear explanations
3. **Identifies Temporal Patterns**: Detect significant trends, cycles, and anomalies
4. **Generates Executive Conclusions**: Provide actionable insights for decision makers
5. **Maintains Academic Rigor**: Use appropriate terminology and systematic methodology

**Required Output Format:**
Respond only in JSON format with the following structure:
```json
{
  "principal_findings": [
    {
      "bullet_point": "Principal insight with specific data",
      "reasoning": "Detailed explanation of why this insight is important",
      "data_source": ["Sources supporting this finding"],
      "confidence": "high|medium|low"
    }
  ],
  "pca_insights": {
    "dominant_components": "Description of principal components",
    "variance_explained": "Percentage of variance explained",
    "key_patterns": ["Key patterns identified"]
  },
  "executive_summary": "Concise, actionable executive summary (2-3 sentences)"
}
```
"""

    def _build_output_format_section(self) -> str:
        """Build output format section."""
        if self.language == 'es':
            return """
### FORMATO DE SALIDA

**IMPORTANTE**: Responde ÚNICAMENTE con el objeto JSON. No incluyas explicaciones, 
introducciones, o texto fuera del JSON.

El JSON debe contener exactamente:
- `principal_findings`: Array de objetos con insights principales
- `pca_insights`: Objeto con análisis de componentes principales
- `executive_summary`: Resumen ejecutivo conciso

Cada finding debe incluir:
- `bullet_point`: Insight específico y medible
- `reasoning`: Justificación basada en datos
- `data_source`: Fuentes que validan el finding
- `confidence`: Nivel de confianza (high/medium/low)
"""
        else:
            return """
### OUTPUT FORMAT

**IMPORTANT**: Respond ONLY with the JSON object. Do not include explanations, 
introductions, or text outside the JSON.

The JSON must contain exactly:
- `principal_findings`: Array of objects with principal insights
- `pca_insights`: Object with principal component analysis
- `executive_summary`: Concise executive summary

Each finding must include:
- `bullet_point`: Specific, measurable insight
- `reasoning`: Data-based justification
- `data_source`: Sources validating the finding
- `confidence`: Confidence level (high/medium/low)
"""

    def _build_component_analysis(self, component: Dict[str, Any], comp_num: int) -> str:
        """Build individual component analysis."""
        variance = component.get('variance_explained', 0)
        interpretation = component.get('interpretation', '')
        dominant_sources = component.get('dominant_sources', [])
        
        if self.language == 'es':
            return f"""
**Análisis del Componente {comp_num}:**
- Varianza Explicada: {variance:.1f}%
- Interpretación: {interpretation}
- Fuentes Dominantes: {', '.join(dominant_sources)}
"""
        else:
            return f"""
**Component {comp_num} Analysis:**
- Variance Explained: {variance:.1f}%
- Interpretation: {interpretation}
- Dominant Sources: {', '.join(dominant_sources)}
"""

    def _build_variance_analysis(self, variance_explained: float) -> str:
        """Build variance analysis section."""
        if self.language == 'es':
            if variance_explained >= 80:
                quality = "Excelente"
                explanation = "Los componentes principales capturan la mayoría de la variabilidad en los datos"
            elif variance_explained >= 60:
                quality = "Bueno"
                explanation = "Los componentes principales capturan una porción significativa de la variabilidad"
            elif variance_explained >= 40:
                quality = "Aceptable"
                explanation = "Los componentes principales capturan una porción moderada de la variabilidad"
            else:
                quality = "Limitado"
                explanation = "Los componentes principales capturan una porción limitada de la variabilidad"
            
            return f"""
**Evaluación de Varianza Explicada:**
- Porcentaje Total: {variance_explained:.1f}%
- Calidad del Análisis: {quality}
- Interpretación: {explanation}
"""
        else:
            if variance_explained >= 80:
                quality = "Excellent"
                explanation = "Principal components capture most of the data variability"
            elif variance_explained >= 60:
                quality = "Good"
                explanation = "Principal components capture a significant portion of variability"
            elif variance_explained >= 40:
                quality = "Acceptable"
                explanation = "Principal components capture a moderate portion of variability"
            else:
                quality = "Limited"
                explanation = "Principal components capture a limited portion of variability"
            
            return f"""
**Explained Variance Assessment:**
- Total Percentage: {variance_explained:.1f}%
- Analysis Quality: {quality}
- Interpretation: {explanation}
"""

    def _build_findings_synthesis(self, principal_findings: List[Dict[str, Any]]) -> str:
        """Build findings synthesis section."""
        if not principal_findings:
            return ""
        
        if self.language == 'es':
            section = "### SÍNTESIS DE HALLAZGOS PRINCIPALES\n\n"
        else:
            section = "### PRINCIPAL FINDINGS SYNTHESIS\n\n"
        
        # Group findings by confidence
        high_confidence = [f for f in principal_findings if f.get('confidence') == 'high']
        medium_confidence = [f for f in principal_findings if f.get('confidence') == 'medium']
        low_confidence = [f for f in principal_findings if f.get('confidence') == 'low']
        
        if high_confidence:
            if self.language == 'es':
                section += "**Hallazgos de Alta Confianza:**\n"
            else:
                section += "**High Confidence Findings:**\n"
            
            for finding in high_confidence:
                bullet = finding.get('bullet_point', '')[:100] + "..." if len(finding.get('bullet_point', '')) > 100 else finding.get('bullet_point', '')
                section += f"- {bullet}\n"
        
        if medium_confidence:
            if self.language == 'es':
                section += "\n**Hallazgos de Confianza Media:**\n"
            else:
                section += "\n**Medium Confidence Findings:**\n"
            
            for finding in medium_confidence:
                bullet = finding.get('bullet_point', '')[:100] + "..." if len(finding.get('bullet_point', '')) > 100 else finding.get('bullet_point', '')
                section += f"- {bullet}\n"
        
        return section

    def _build_strategic_implications(self, findings: Dict[str, Any]) -> str:
        """Build strategic implications section."""
        if self.language == 'es':
            return """
### IMPLICACIONES ESTRATÉGICAS

Basado en el análisis multi-fuente y PCA, identifica:

1. **Implicaciones para la Adopción**: ¿Qué sugieren los datos sobre la adopción de esta herramienta?
2. **Impacto Organizacional**: ¿Cómo afecta la implementación a diferentes áreas de la organización?
3. **Ventajas Competitivas**: ¿Qué ventajas ofrece esta herramienta sobre alternativas?
4. **Riesgos Potenciales**: ¿Qué riesgos deben considerarse?

Proporciona insights estratégicos accionables para líderes empresariales.
"""
        else:
            return """
### STRATEGIC IMPLICATIONS

Based on multi-source analysis and PCA, identify:

1. **Adoption Implications**: What does the data suggest about this tool's adoption?
2. **Organizational Impact**: How does implementation affect different organizational areas?
3. **Competitive Advantages**: What advantages does this tool offer over alternatives?
4. **Potential Risks**: What risks should be considered?

Provide actionable strategic insights for business leaders.
"""

    def _build_recommendations(self, findings: Dict[str, Any]) -> str:
        """Build recommendations section."""
        if self.language == 'es':
            return """
### RECOMENDACIONES EJECUTIVAS

Proporciona 3-5 recomendaciones específicas y accionables:

1. **Para la Implementación**: Recomendaciones prácticas para adoptar esta herramienta
2. **Para la Optimización**: Cómo maximizar el valor y efectividad
3. **Para la Medición**: Qué métricas monitorear para evaluar el éxito
4. **Para la Evolución**: Próximos pasos y consideraciones futuras

Cada recomendación debe ser:
- Específica y medible
- Basada en evidencia de los datos
- Alineada con objetivos empresariales
- Practicable de implementar
"""
        else:
            return """
### EXECUTIVE RECOMMENDATIONS

Provide 3-5 specific, actionable recommendations:

1. **For Implementation**: Practical recommendations for adopting this tool
2. **For Optimization**: How to maximize value and effectiveness
3. **For Measurement**: What metrics to monitor for success evaluation
4. **For Evolution**: Next steps and future considerations

Each recommendation should be:
- Specific and measurable
- Evidence-based from the data
- Aligned with business objectives
- Practical to implement
"""

    def _build_pca_requirements(self) -> str:
        """Build PCA-specific requirements with emphasis on loadings."""
        if self.language == 'es':
            return """
### REQUISITOS ESPECÍFICOS DE PCA - ANÁLISIS DE CARGAS Y COMPONENTES

Para el análisis de componentes principales, enfócate ESPECÍFICAMENTE en:

1. **Análisis de Cargas (Loadings)**: Examine las cargas de cada fuente en cada componente para entender su contribución
2. **Interpretación de Componentes**: Cada componente representa una combinación única de fuentes - explica qué patrones subyacentes revela
3. **Diferencias entre Fuentes**: Usa las cargas para identificar cómo se diferencian las fuentes y qué información única aporta cada una
4. **Relaciones Ocultas**: Identifica correlaciones y relaciones no obvias entre fuentes reveladas por las cargas
5. **Patrones de Contribución**: Clasifica las fuentes según su peso en cada componente (alta, media, baja contribución)

**Análisis Detallado de Cargas:**
- **Cargas Altas (>0.6)**: Fuentes que dominan el componente
- **Cargas Moderadas (0.3-0.6)**: Fuentes con influencia significativa
- **Cargas Bajas (<0.3)**: Fuentes con contribución mínima
- **Signos de Cargas**: Interpretar si las relaciones son positivas o negativas

**Insights Específicos:**
- ¿Qué componente representa el "patrón institucional" vs "patrón de innovación"?
- ¿Cómo se diferencian las fuentes académicas (Crossref) de las comerciales (Bain)?
- ¿Qué fuentes están más correlacionadas entre sí según las cargas?
- ¿Qué información única aporta cada fuente al análisis general?

Conecta estos hallazgos con las tendencias temporales para explicar la evolución de estos patrones.
"""
        else:
            return """
### PCA-SPECIFIC REQUIREMENTS - LOADINGS AND COMPONENTS ANALYSIS

For principal component analysis, focus SPECIFICALLY on:

1. **Loadings Analysis**: Examine each source's loading on each component to understand its contribution
2. **Component Interpretation**: Each component represents a unique combination of sources - explain what underlying patterns it reveals
3. **Source Differences**: Use loadings to identify how sources differ and what unique information each provides
4. **Hidden Relationships**: Identify correlations and non-obvious relationships between sources revealed by loadings
5. **Contribution Patterns**: Classify sources by their weight in each component (high, medium, low contribution)

**Detailed Loadings Analysis:**
- **High Loadings (>0.6)**: Sources that dominate the component
- **Moderate Loadings (0.3-0.6)**: Sources with significant influence
- **Low Loadings (<0.3)**: Sources with minimal contribution
- **Loading Signs**: Interpret whether relationships are positive or negative

**Specific Insights:**
- Which component represents "institutional pattern" vs "innovation pattern"?
- How do academic sources (Crossref) differ from commercial sources (Bain)?
- Which sources are most correlated according to loadings?
- What unique information does each source contribute to the overall analysis?

Connect these findings with temporal trends to explain the evolution of these patterns.
"""

    def _extract_variable_relationships(self, pca_insights: Dict[str, Any]) -> str:
        """Extract key variable relationships for narrative prompt."""
        components = pca_insights.get('dominant_patterns', [])
        tool_name = pca_insights.get('tool_name', 'Unknown Tool')

        # Default relationships based on common management tools analysis
        default_vars = {
            'es': "'popularidad pública', 'complejidad de implementación', 'efectividad reportada'",
            'en': "'public popularity', 'implementation complexity', 'reported effectiveness'"
        }

        # Try to extract from actual PCA data
        variables = []
        for component in components[:2]:  # Focus on first two components
            loadings = component.get('loadings', {})
            if loadings:
                # Get variables with highest absolute loadings
                sorted_vars = sorted(loadings.items(), key=lambda x: abs(x[1]), reverse=True)
                variables.extend([var for var, _ in sorted_vars[:2]])  # Top 2 per component

        if variables:
            unique_vars = list(set(variables))[:3]  # Limit to 3 unique variables
            if self.language == 'es':
                return ', '.join([f"'{var}'" for var in unique_vars])
            else:
                return ', '.join([f"'{var}'" for var in unique_vars])

        return default_vars[self.language]

    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load bilingual prompt templates."""
        return {
            'comprehensive_analysis': {
                'es': """
ANÁLISIS DOCTORAL DE HERRAMIENTAS DE GESTIÓN
Fecha: {analysis_date}

{context}

Por favor, genera un análisis doctoral-level que integre todos los elementos anteriores.
""",
                'en': """
DOCTORAL-LEVEL MANAGEMENT TOOLS ANALYSIS
Date: {analysis_date}

{context}

Please generate a doctoral-level analysis that integrates all the above elements.
"""
            },
            'pca_focused': {
                'es': """
ANÁLISIS ENFOCADO EN PCA DE HERRAMIENTAS DE GESTIÓN
Fecha: {analysis_date}

{pca_analysis}

Genera insights profundos basados en el análisis de componentes principales.
""",
                'en': """
PCA-FOCUSED MANAGEMENT TOOLS ANALYSIS
Date: {analysis_date}

{pca_analysis}

Generate deep insights based on principal component analysis.
"""
            },
            'executive_summary': {
                'es': """
RESUMEN EJECUTIVO DE HERRAMIENTAS DE GESTIÓN
Fecha: {executive_date}

{executive_content}

Genera un resumen conciso y accionable para líderes empresariales.
""",
                'en': """
EXECUTIVE SUMMARY OF MANAGEMENT TOOLS
Date: {executive_date}

{executive_content}

Generate a concise, actionable summary for business leaders.
"""
            }
        }