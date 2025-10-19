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
        heatmap_data = data.get('heatmap_analysis', {})

        # Build prompt sections
        sections = []

        # Context section
        sections.append(self._build_context_section(tool_name, sources, data))

        # Heatmap analysis section
        sections.append(self._build_heatmap_section(heatmap_data))

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
        
        # Check for data quality issues
        sources_count = len(components[0].get('loadings', {})) if components else 0
        has_quality_issues = variance_explained < 10 or sources_count < 2

        # Build detailed PCA analysis with specific numerical insights
        detailed_pca_analysis = self._build_detailed_pca_narrative(components, tool_name, variance_explained)

        if self.language == 'es':
            section = f"""
### ANÁLISIS DE COMPONENTES PRINCIPALES (PCA) - NARRATIVA UNIFICADA

**Datos PCA Adjuntos:**
- Herramienta de Gestión Analizada: {tool_name}
- Varianza Total Explicada: {variance_explained:.1f}%
- Componentes Principales Identificados: {len(components)}
- Fuentes de Datos Disponibles: {sources_count}

{detailed_pca_analysis}

**INSTRUCCIONES ESPECÍFICAS PARA ANÁLISIS PCA DETALLADO:**

Basado en los datos numéricos anteriores, genera una narrativa unificada que:

1. **Interprete las cargas específicas**: Usa los valores numéricos exactos (ej: "Google Trends con carga de +0.45")
2. **Explique las relaciones de oposición**: Cuando una fuente tiene carga positiva y otra negativa, explica esta tensión
3. **Conecte con la teoría de gestión**: Relaciona los patrones con conceptos académicos como "brecha teoría-práctica"
4. **Use el porcentaje de varianza**: Menciona específicamente "los primeros dos componentes explican el XX.X% de la varianza"
5. **Genere insights ejecutivos**: Traduce los hallazgos técnicos implicaciones prácticas para negocios

**Ejemplo del Formato Esperado:**
"Este PCA es particularmente poderoso porque sus primeros dos componentes (los ejes horizontal y vertical) capturan y explican un XX.X% combinado de la varianza total en los datos. Esto proporciona una narrativa clara y unificada sobre el viaje peligroso que una metodología de gestión como {tool_name} toma desde la teoría académica hasta la práctica industrial, destacando la brecha crítica entre teoría y práctica.

El análisis primero revela una 'dinámica de adopción'. El interés público en {tool_name} (Google Trends) y la facilidad de uso percibida de sus herramientas (Bain - Usabilidad) están estrechamente correlacionados, ambos mostrando fuerte influencia positiva a lo largo de los ejes de componentes principales. Por ejemplo, Google Trends tiene una carga positiva fuerte de aproximadamente +0.XX en el eje horizontal principal (PC1). Esto confirma numéricamente que a medida que {tool_name} se empaqueta en marcos accesibles, gana tracción en el mundo empresarial, un patrón clásico descrito en modelos académicos de difusión de innovación.

Sin embargo, esta popularidad crea una trampa. El PCA revela una relación inversa poderosa: Bain - Satisfacción aparece en oposición directa a esta tendencia de crecimiento, con una carga negativa fuerte de aproximadamente -0.XX en PC1. Este contraste numérico stark visualiza un modo de falla crítico. A medida que el impulso por herramientas simplificadas y populares impulsa la dinámica en una dirección (positiva en PC1), la satisfacción se jala en la dirección completamente opuesta. Desde una perspectiva académica, esto es un fracaso de fidelidad de implementación; para líderes industriales, es una advertencia respaldada por datos de que adoptar los aspectos superficiales de {tool_name} lleva a un fracaso predecible.

Finalmente, el análisis muestra que el discurso académico riguroso sobre {tool_name} (Crossref.org) opera en un eje de influencia completamente diferente. Tiene la carga individual más alta en el eje vertical (+0.XX en PC2) mientras está negativamente asociado con el eje de tendencia principal (-0.XX en PC1). Esta posición perpendicular confirma numéricamente que la conversación académica está desconectada del ciclo de hype de practicantes. El verdadero éxito, sugiere el gráfico, radica en conectar estos mundos—usando principios rigurosos para informar la práctica en lugar de simplemente seguir una tendencia popular que lleva a la insatisfacción."

"""
        else:
            section = f"""
### PRINCIPAL COMPONENT ANALYSIS (PCA) - UNIFIED NARRATIVE

**Attached PCA Data:**
- Management Tool Analyzed: {tool_name}
- Total Variance Explained: {variance_explained:.1f}%
- Principal Components Identified: {len(components)}
- Data Sources Available: {sources_count}

"""
            
            # Add specific guidance for low-quality data scenarios
            if has_quality_issues:
                section += f"""
**⚠️ IMPORTANT NOTE: LIMITED DATA QUALITY**

The current analysis shows significant limitations:
- Very low variance explained ({variance_explained:.1f}%)
- {sources_count} data source(s) available

**Specific Instructions for This Scenario:**
1. **Focus on identifying data problems** rather than patterns
2. **Suggest specific improvements** for data quality
3. **Recommend additional sources** that could enrich the analysis
4. **Provide strategic insights** based on current limitations
5. **Be honest about limitations** but provide executive value

**Example of Expected Analysis:**
"The current PCA analysis is limited by {sources_count} data source(s), explaining only {variance_explained:.1f}% of variance. This suggests the need to incorporate additional sources like [suggest specific sources] for a more comprehensive view. Meanwhile, available data indicates [extract any possible insight]..."

"""
            
            # Build detailed PCA analysis with specific numerical insights
            detailed_pca_analysis = self._build_detailed_pca_narrative(components, tool_name, variance_explained)
            
            # Continue with regular PCA instructions
            section += f"""
{detailed_pca_analysis}

**SPECIFIC INSTRUCTIONS FOR DETAILED PCA ANALYSIS:**

Based on the numerical data above, generate a unified narrative that:

1. **Interprets specific loadings**: Use exact numerical values (e.g., "Google Trends with loading of +0.45")
2. **Explains opposition relationships**: When one source has positive and another negative loading, explain this tension
3. **Connects with management theory**: Relate patterns to academic concepts like "theory-practice gap"
4. **Uses variance percentage**: Specifically mention "the first two components explain XX.X% of variance"
5. **Generates executive insights**: Translate technical findings into practical business implications

**Expected Format Example:**
"This PCA is particularly powerful because its first two components (the horizontal and vertical axes) capture and explain a combined XX.X% of the total variance in the data. This provides a clear, unified narrative about the perilous journey a management methodology like {tool_name} takes from academic theory to industry practice, highlighting the critical theory-practice gap.

The analysis first reveals an 'adoption dynamic.' The public interest in {tool_name} (Google Trends) and the perceived ease-of-use of its tools (Bain - Usabilidad) are closely correlated, both showing strong positive influence along the principal component axes. For instance, Google Trends has a strong positive loading of approximately +0.XX on the main horizontal axis (PC1). This numerically confirms that as {tool_name} is packaged into accessible frameworks, it gains traction in the business world, a classic pattern described in academic models of innovation diffusion.

However, this popularity creates a trap. The PCA reveals a powerful inverse relationship: Bain - Satisfacción appears in direct opposition to this growth trend, with a strong negative loading of approximately -0.XX on PC1. This stark numerical contrast visualizes a critical failure mode. As the push for simplified, popular tools drives the dynamic in one direction (positive on PC1), satisfaction is pulled in the complete opposite direction. From an academic view, this is a failure of implementation fidelity; for industry leaders, it's a data-backed warning that adopting the superficial aspects of {tool_name} leads to predictable failure.

Finally, the analysis shows that the rigorous academic discourse on {tool_name} (Crossref.org) operates on an entirely different axis of influence. It has the single highest loading on the vertical axis (+0.XX on PC2) while being negatively associated with the main trend axis (-0.XX on PC1). This perpendicular position numerically confirms that the academic conversation is disconnected from the practitioner hype cycle. True success, the chart suggests, lies in bridging these worlds—using rigorous principles to inform practice rather than simply following a popular trend that leads to dissatisfaction."

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
        """Build trends and patterns section with emphasis on integration."""
        if not trends:
            return ""
        
        trend_data = trends.get('trends', {})
        anomalies = trends.get('anomalies', {})
        patterns = trends.get('overall_patterns', [])
        
        if self.language == 'es':
            section = """
### ANÁLISIS TEMPORAL INTEGRADO PARA HALLAZGOS PRINCIPALES

**Datos Temporales para Integrar en Hallazgos Principales:**

**INSTRUCCIÓN ESPECÍFICA:** Estos datos temporales DEBEN ser integrados en la sección "Hallazgos Principales" como narrativa fluida, NO como viñetas. Conecte los patrones temporales con los hallazgos de PCA.

**Tendencias Temporales Clave:**
"""
        else:
            section = """
### INTEGRATED TEMPORAL ANALYSIS FOR PRINCIPAL FINDINGS

**Temporal Data to Integrate into Principal Findings:**

**SPECIFIC INSTRUCTION:** This temporal data MUST be integrated into the "Principal Findings" section as fluid narrative, NOT as bullet points. Connect temporal patterns with PCA findings.

**Key Temporal Trends:**
"""
        
        # Add trend information with integration guidance
        for source, trend_info in trend_data.items():
            direction = trend_info.get('trend_direction', 'stable')
            momentum = trend_info.get('momentum', 0)
            volatility = trend_info.get('volatility', 0)
            
            if self.language == 'es':
                section += f"""
**{source}:** tendencia {direction} con momento de {momentum:.3f} y volatilidad de {volatility:.3f}
"""
                # Add integration guidance
                if direction in ['strong_upward', 'moderate_upward']:
                    section += f"→ Integrar este crecimiento con cargas PCA positivas de {source}\n"
                elif direction in ['strong_downward', 'moderate_downward']:
                    section += f"→ Conectar esta disminución con posibles cargas PCA negativas\n"
                else:
                    section += f"→ Analizar estabilidad de {source} en contexto multivariado\n"
            else:
                section += f"""
**{source}:** {direction} trend with momentum of {momentum:.3f} and volatility of {volatility:.3f}
"""
                # Add integration guidance
                if direction in ['strong_upward', 'moderate_upward']:
                    section += f"→ Integrate this growth with positive PCA loadings of {source}\n"
                elif direction in ['strong_downward', 'moderate_downward']:
                    section += f"→ Connect this decline with possible negative PCA loadings\n"
                else:
                    section += f"→ Analyze stability of {source} in multivariate context\n"
        
        # Add anomalies with integration guidance
        if anomalies:
            if self.language == 'es':
                section += "\n**Anomalías Temporales para Análisis:**\n"
                section += "**INSTRUCCIÓN:** Conecte estas anomalías con patrones PCA inesperados\n\n"
            else:
                section += "\n**Temporal Anomalies for Analysis:**\n"
                section += "**INSTRUCTION:** Connect these anomalies with unexpected PCA patterns\n\n"
            
            for source, anomaly_info in anomalies.items():
                count = anomaly_info.get('count', 0)
                percentage = anomaly_info.get('percentage', 0)
                max_z = anomaly_info.get('max_z_score', 0)
                
                if self.language == 'es':
                    section += f"- {source}: {count} anomalías ({percentage:.1f}%), Z-score máximo: {max_z:.2f}\n"
                    section += f"  → Analizar cómo estas anomalías afectan las relaciones PCA\n"
                else:
                    section += f"- {source}: {count} anomalies ({percentage:.1f}%), Max Z-score: {max_z:.2f}\n"
                    section += f"  → Analyze how these anomalies affect PCA relationships\n"
        
        # Add overall patterns with integration guidance
        if patterns:
            if self.language == 'es':
                section += "\n**Patrones Temporales Generales para Integración:**\n"
                section += "**INSTRUCCIÓN:** Use estos patrones para enriquecer la narrativa de Hallazgos Principales\n\n"
            else:
                section += "\n**Overall Temporal Patterns for Integration:**\n"
                section += "**INSTRUCTION:** Use these patterns to enrich the Principal Findings narrative\n\n"
            
            for pattern in patterns:
                section += f"- {pattern}\n"
                if self.language == 'es':
                    section += f"  → Conectar este patrón con la dinámica de componentes principales\n"
                else:
                    section += f"  → Connect this pattern with principal component dynamics\n"
        
        return section

    def _build_heatmap_section(self, heatmap_data: Dict[str, Any]) -> str:
        """Build heatmap analysis section."""
        if not heatmap_data:
            return ""

        # Extract heatmap metrics
        value_ranges = heatmap_data.get('value_ranges', {})
        dense_regions = heatmap_data.get('most_dense_regions', [])
        sparse_regions = heatmap_data.get('least_dense_regions', [])
        clusters = heatmap_data.get('detected_clusters', [])
        outliers = heatmap_data.get('detected_outliers', [])
        gradients = heatmap_data.get('gradients', {})

        if self.language == 'es':
            section = """
### ANÁLISIS DEL MAPA DE CALOR

**Datos del Mapa de Calor Proporcionados:**
"""
        else:
            section = """
### HEATMAP ANALYSIS

**Provided Heatmap Data:**
"""

        # Add value ranges
        if value_ranges:
            if self.language == 'es':
                section += "\n**Rangos de Valores del Mapa de Calor:**\n"
            else:
                section += "\n**Heatmap Value Ranges:**\n"

            for source, ranges in value_ranges.items():
                min_val = ranges.get('min', 'N/A')
                max_val = ranges.get('max', 'N/A')
                if self.language == 'es':
                    section += f"- {source}: mínimo {min_val}, máximo {max_val}\n"
                else:
                    section += f"- {source}: min {min_val}, max {max_val}\n"

        # Add dense regions
        if dense_regions:
            if self.language == 'es':
                section += "\n**Regiones Más Densas:**\n"
            else:
                section += "\n**Most Dense Regions:**\n"

            for region in dense_regions:
                section += f"- {region}\n"

        # Add sparse regions
        if sparse_regions:
            if self.language == 'es':
                section += "\n**Regiones Menos Densas:**\n"
            else:
                section += "\n**Least Dense Regions:**\n"

            for region in sparse_regions:
                section += f"- {region}\n"

        # Add detected clusters
        if clusters:
            if self.language == 'es':
                section += "\n**Agrupamientos Detectados:**\n"
            else:
                section += "\n**Detected Clusters:**\n"

            for cluster in clusters:
                section += f"- {cluster}\n"

        # Add detected outliers
        if outliers:
            if self.language == 'es':
                section += "\n**Valores Atípicos Detectados:**\n"
            else:
                section += "\n**Detected Outliers:**\n"

            for outlier in outliers:
                section += f"- {outlier}\n"

        # Add gradients
        if gradients:
            if self.language == 'es':
                section += "\n**Gradientes Observados:**\n"
            else:
                section += "\n**Observed Gradients:**\n"

            for gradient_type, description in gradients.items():
                section += f"- {gradient_type}: {description}\n"

        # Add analysis instructions
        if self.language == 'es':
            section += """

**INSTRUCCIONES OBLIGATORIAS PARA ANÁLISIS DEL MAPA DE CALOR:**

Basado en los datos proporcionados arriba, analiza el mapa de calor y discute:

1. **Patrones Visuales Clave**: Identifica los patrones más prominentes en la visualización
2. **Agrupamientos**: Describe cualquier cluster o agrupamiento visible y sus características
3. **Anomalías**: Identifica valores atípicos o anomalías y explica su significado
4. **Gradientes**: Analiza los gradientes de color y qué representan en términos de intensidad de datos
5. **Implicaciones para el Conjunto de Datos**: Explica cómo estos patrones afectan la interpretación general de los datos

**Enfoque del Análisis:**
- Conecta los patrones del mapa de calor con las tendencias temporales
- Relaciona los clusters con los hallazgos de PCA cuando sea relevante
- Identifica áreas de alta densidad que puedan indicar períodos de interés significativo
- Explica anomalías en el contexto del comportamiento general de la herramienta de gestión

**REQUISITO OBLIGATORIO PARA EL FORMATO DE SALIDA:**
- Esta sección proporciona los datos y instrucciones para que generes el contenido de la sección "heatmap_analysis" en el JSON de salida
- **DEBES generar el campo "heatmap_analysis" en tu respuesta JSON**
- **DEBES crear un análisis de EXACTAMENTE 3 párrafos separados por \n\n**
- **Si no hay datos de heatmap disponibles, crea un análisis basado en correlaciones generales**
- **El campo heatmap_analysis es OBLIGATORIO - no lo omitas bajo ninguna circunstancia**
"""
        else:
            section += """

**MANDATORY HEATMAP ANALYSIS INSTRUCTIONS:**

Based on the data provided above, analyze the heatmap and discuss:

1. **Key Visual Patterns**: Identify the most prominent patterns in the visualization
2. **Clusters**: Describe any visible clusters or groupings and their characteristics
3. **Anomalies**: Identify outliers or anomalies and explain their significance
4. **Gradients**: Analyze color gradients and what they represent in terms of data intensity
5. **Implications for the Dataset**: Explain how these patterns affect the overall interpretation of the data

**Analysis Focus:**
- Connect heatmap patterns with temporal trends
- Relate clusters with PCA findings when relevant
- Identify high-density areas that may indicate periods of significant interest
- Explain anomalies in the context of the management tool's general behavior

**MANDATORY OUTPUT REQUIREMENT:**
- This section provides the data and instructions for you to generate the content of the "heatmap_analysis" field in the output JSON
- **YOU MUST generate the "heatmap_analysis" field in your JSON response**
- **YOU MUST create an analysis of EXACTLY 3 paragraphs separated by \n\n**
- **If no heatmap data is available, create an analysis based on general correlations**
- **The heatmap_analysis field is MANDATORY - do not omit it under any circumstances**
"""

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

1. **Sintetice Información Multi-fuente**: Integre insights de todas las fuentes de datos incluyendo análisis temporal, de heatmap y PCA
2. **Énfasis en Análisis de Mapa de Calor**: Destaque patrones visuales clave, clusters, anomalías y gradientes del heatmap con explicaciones claras integradas en la narrativa
2. **Énfasis en PCA**: Destaque insights de componentes principales con explicaciones claras integradas en una narrativa fluida
3. **Identifique Patrones Temporales**: Detecte tendencias, ciclos y anomalías significativas e integrelas en los hallazgos principales
4. **Genere Conclusiones Ejecutivas**: Proporcione insights accionables para tomadores de decisiones
5. **Mantenga Rigor Académico**: Use terminología apropiada y metodología sistemática
6. **Mencione la Herramienta Específica**: Incluya el nombre de la herramienta de gestión analizada en todos los hallazgos para personalizar el análisis

**ESTRUCTURA REQUERIDA DEL ANÁLISIS:**

Genera un análisis doctoral con las siguientes cuatro secciones principales:

**1. Resumen Ejecutivo:**
- **REQUISITO MEJORADO**: Un párrafo conciso pero completo que capture los insights más críticos
- **CONTENIDO ESENCIAL**: Debe incluir (1) el gap teoría-práctica, (2) implicaciones estratégicas, (3) tendencias temporales clave, (4) insights de heatmap, (5) patrones visuales del mapa de calor
- **DATOS CUANTITATIVOS**: Mencione específicamente el porcentaje de varianza explicada por los primeros dos componentes y al menos 2 valores numéricos exactos
- **CONTEXTO ESPECÍFICO**: Conecte los hallazgos con la herramienta de gestión específica analizada
- **EJEMPLO DE CALIDAD**: "El análisis de 'Herramienta X' revela una brecha crítica entre teoría y práctica, con los primeros dos componentes explicando el XX.X% de la varianza. La tendencia temporal muestra [patrón específico] mientras que el análisis de correlación indica [insight específico], sugiriendo [implicación estratégica]."

**2. Hallazgos Principales:**
- **REQUISITO ABSOLUTO**: MÚLTIPLES viñetas concisas y accionables (3-5 viñetas diferentes)
- **FORMATO OBLIGATORIO**: Cada viñeta debe comenzar con "•" o "-" y ser una línea separada
- Cada viñeta debe ser un hallazgo específico y diferente con datos cuantitativos
- **REQUISITO DE CONTENIDO ESPECÍFICO**: Debe incluir al menos una viñeta con análisis temporal, una viñeta con insights de heatmap, y una viñeta con patrones visuales del mapa de calor
- Integre insights de PCA, análisis temporal, y heatmap en cada viñeta
- Conecte los patrones temporales con los hallazgos de PCA en diferentes viñetas
- Mencione fuentes específicas y valores numéricos exactos en cada viñeta
- **ADVERTENCIA CRÍTICA**: NO genere un solo párrafo grande, genere varias viñetas distintas separadas por saltos de línea
- **EJEMPLO DE FORMATO CORRECTO**:
  • Hallazgo 1 con datos cuantitativos específicos
  • Hallazgo 2 con análisis temporal integrado (tendencias, ciclos, anomalías)
  • Hallazgo 3 con insights de PCA
  • Hallazgo 4 con patrón de correlación/heatmap
  • Hallazgo 5 con conclusión estratégica

**3. Análisis de Mapa de Calor:**
- **REQUISITO ABSOLUTO**: Un ensayo analítico de EXACTAMENTE 3 párrafos separados por DOS líneas en blanco
- **ADVERTENCIA CRÍTICA**: Si no genera exactamente 3 párrafos distintos, el análisis será rechazado
- **Párrafo 1** (termina con la primera línea en blanco): Analice los patrones visuales clave, clusters y gradientes observados en el mapa de calor
- **Párrafo 2** (termina con la segunda línea en blanco): Interprete las anomalías y valores atípicos detectados, explicando su significado en el contexto de los datos
- **Párrafo 3** (no necesita línea en blanco al final): Discuta las implicaciones de estos patrones para el conjunto de datos y su relación con las tendencias temporales
- **ESTRUCTURA FORZADA**: Párrafo 1 + \n\n + Párrafo 2 + \n\n + Párrafo 3
- **VERIFICACIÓN AUTOMÁTICA**: El sistema contará los párrafos - debe haber exactamente 3
- Use los rangos de valores, regiones densas/espresas y clusters proporcionados
- Conecte con los hallazgos de PCA cuando sea relevante

**4. Análisis PCA:**
- **REQUISITO ABSOLUTO E INNEGOCIABLE**: Un ensayo analítico de EXACTAMENTE 3 párrafos separados por DOS líneas en blanco (NO datos estadísticos)
- **ADVERTENCIA CRÍTICA**: Si no genera exactamente 3 párrafos distintos, el análisis será rechazado
- **Párrafo 1** (termina con la primera línea en blanco): Interprete las cargas específicas con valores numéricos exactos y explique las relaciones de oposición entre fuentes
- **Párrafo 2** (termina con la segunda línea en blanco): Analice las RELACIONES entre las diferentes fuentes de datos, enfocándose en cómo interactúan y qué patrones revelan estas interacciones
- **Párrafo 3** (no necesita línea en blanco al final): Discuta las IMPLICACIONES estratégicas y prácticas de estos patrones para la implementación y adopción de la herramienta de gestión
- **ESTRUCTURA FORZADA**: Párrafo 1 + \n\n + Párrafo 2 + \n\n + Párrafo 3
- **VERIFICACIÓN AUTOMÁTICA**: El sistema contará los párrafos - debe haber exactamente 3
- Conecte con conceptos académicos como "brecha teoría-práctica"
- Use el porcentaje de varianza explicada

**EJEMPLO ESTRUCTURAL OBLIGATORIO para heatmap_analysis:**
"Contenido del Párrafo 1 sobre patrones visuales, clusters y gradientes.\n\nContenido del Párrafo 2 sobre anomalías y valores atípicos.\n\nContenido del Párrafo 3 sobre implicaciones para el conjunto de datos."

**EJEMPLO ESTRUCTURAL OBLIGATORIO para pca_analysis:**
"Contenido del Párrafo 1 sobre interpretación técnica con cargas específicas.\n\nContenido del Párrafo 2 sobre relaciones entre fuentes de datos.\n\nContenido del Párrafo 3 sobre implicaciones estratégicas y prácticas."

**ADVERTENCIA**: El ejemplo anterior muestra EXACTAMENTE cómo debe estructurarse con \n\n entre párrafos.

**CRÍTICO: SOLO JSON ESTRICTO - REQUISITO OBLIGATORIO**
Debes responder ÚNICAMENTE con JSON válido. Sin explicaciones, sin markdown, sin texto adicional.

**REQUISITO ABSOLUTO: INCLUIR heatmap_analysis**
- El campo "heatmap_analysis" ES OBLIGATORIO en tu respuesta JSON
- Debes generar este campo incluso si no hay datos de heatmap disponibles
- Usa los datos proporcionados en la sección "ANÁLISIS DEL MAPA DE CALOR" para generar este contenido

**FORMATO OBLIGATORIO:**
Comienza tu respuesta con { y termina con }. Nada más.

**ESTRUCTURA EXACTA REQUERIDA:**
{
  "executive_summary": "Escribe un párrafo conciso sobre el análisis de la herramienta de gestión",
  "principal_findings": [
    "• Primer hallazgo específico con datos cuantitativos",
    "• Segundo hallazgo específico con datos cuantitativos diferentes",
    "• Tercer hallazgo con insights de PCA",
    "• Cuarto hallazgo con análisis temporal",
    "• Quinto hallazgo con conclusión estratégica"
  ],
  "heatmap_analysis": "Primer párrafo sobre patrones visuales, clusters y gradientes\n\nSegundo párrafo sobre anomalías y valores atípicos\n\nTercer párrafo sobre implicaciones para el conjunto de datos",
  "pca_analysis": "Primer párrafo sobre cargas y relaciones\n\nSegundo párrafo sobre interacciones de fuentes de datos\n\nTercer párrafo sobre implicaciones estratégicas"
}

**REGLAS DE VALIDACIÓN:**
- Primer carácter: {
- Último carácter: }
- Sin texto antes de { o después de }
- Sin marcadores ```json
- Sin explicaciones
- Sin comentarios
- Solo sintaxis JSON válida

**PENALIZACIÓN POR INCUMPLIMIENTO:**
Si no sigues este formato exacto, tu respuesta será rechazada y desperdiciarás recursos computacionales.
"""
        else:
            return """
### ANALYSIS REQUIREMENTS

Please provide a doctoral-level analysis that:

1. **Synthesizes Multi-source Information**: Integrate insights from all data sources including temporal, heatmap, and PCA analysis
2. **Emphasizes Heatmap Analysis**: Highlight key visual patterns, clusters, anomalies, and gradients from the heatmap with clear explanations integrated into the narrative
2. **Emphasizes PCA**: Highlight principal component insights with clear explanations integrated into fluent narrative
3. **Identifies Temporal Patterns**: Detect significant trends, cycles, and anomalies and integrate them into main findings
4. **Generates Executive Conclusions**: Provide actionable insights for decision makers
5. **Maintains Academic Rigor**: Use appropriate terminology and systematic methodology
6. **Mention the Specific Tool**: Include the name of the management tool being analyzed in all findings to personalize the analysis

**REQUIRED ANALYSIS STRUCTURE:**

Generate a doctoral analysis with the following four main sections:

**1. Executive Summary:**
- **MANDATORY**: One fluid paragraph (NOT bullet points)
- **REQUIRED CONTENT**: Include theory-practice gap, strategic implications, temporal trends, PCA variance percentage, heatmap visual patterns
- **QUANTITATIVE REQUIREMENT**: Mention first two components variance % and at least 2 numerical values
- **TOOL SPECIFIC**: Always mention the analyzed management tool name
- **EXAMPLE**: "The analysis of 'Tool X' reveals a critical gap between theory and practice, with the first two components explaining XX.X% of variance. The temporal trend shows [specific pattern] while correlation analysis indicates [specific insight], suggesting [strategic implication]."

**2. Principal Findings:**
- **MANDATORY**: 3-5 separate bullet points starting with "•"
- **EACH BULLET MUST**: Be different, include quantitative data, mention specific sources
- **CONTENT REQUIREMENTS**: At least one temporal analysis bullet, one PCA insights bullet, one heatmap analysis bullet
- **FORMAT**: Each bullet on separate line, no paragraphs
- **EXAMPLE FORMAT**:
  • Finding 1 with specific quantitative data
  • Finding 2 with integrated temporal analysis
  • Finding 3 with PCA insights
  • Finding 4 with heatmap visual patterns
  • Finding 5 with strategic conclusion

**3. Heatmap Analysis:**
- **MANDATORY**: EXACTLY 3 paragraphs separated by \n\n
- **Paragraph 1**: Analysis of key visual patterns, clusters, and gradients observed in the heatmap
- **Paragraph 2**: Interpretation of detected anomalies and outliers, explaining their significance
- **Paragraph 3**: Discussion of implications for the dataset and relationship to temporal trends
- **STRICT FORMAT**: "Paragraph 1 content\n\nParagraph 2 content\n\nParagraph 3 content"
- **VERIFICATION**: System counts paragraphs - must be exactly 3
- Use provided value ranges, dense/sparse regions, and detected clusters
- Connect with PCA findings when relevant

**4. PCA Analysis:**
- **MANDATORY**: EXACTLY 3 paragraphs separated by \n\n
- **Paragraph 1**: Technical interpretation with specific loadings and relationships
- **Paragraph 2**: Analysis of relationships between data sources
- **Paragraph 3**: Strategic and practical implications
- **STRICT FORMAT**: "Paragraph 1 content\n\nParagraph 2 content\n\nParagraph 3 content"
- **VERIFICATION**: System counts paragraphs - must be exactly 3

**CRITICAL: STRICT JSON OUTPUT ONLY**
You MUST respond with VALID JSON only. No explanations, no markdown, no additional text.

**MANDATORY REQUIREMENT: INCLUDE heatmap_analysis**
- The "heatmap_analysis" field IS MANDATORY in your JSON response
- You must generate this field even if no heatmap data is available
- Use the data provided in the "HEATMAP ANALYSIS" section to generate this content

**MANDATORY FORMAT:**
Start your response with { and end with }. Nothing else.

**EXACT STRUCTURE REQUIRED:**
{
  "executive_summary": "Write a concise paragraph about the management tool analysis",
  "principal_findings": [
    "• First specific finding with quantitative data",
    "• Second specific finding with different quantitative data",
    "• Third finding with PCA insights",
    "• Fourth finding with temporal analysis",
    "• Fifth finding with strategic conclusion"
  ],
  "heatmap_analysis": "First paragraph about visual patterns, clusters, and gradients\n\nSecond paragraph about anomalies and outliers\n\nThird paragraph about implications for the dataset",
  "pca_analysis": "First paragraph about loadings and relationships\n\nSecond paragraph about data source interactions\n\nThird paragraph about strategic implications"
}

**VALIDATION RULES:**
- First character: {
- Last character: }
- No text before { or after }
- No ```json markers
- No explanations
- No comments
- Valid JSON syntax only

**PENALTY FOR NON-COMPLIANCE:**
If you don't follow this exact format, your response will be rejected and you'll waste computational resources.
"""

    def _build_output_format_section(self) -> str:
        """Build output format section."""
        if self.language == 'es':
            return """
### FORMATO DE SALIDA

**IMPORTANTE**: Responde ÚNICAMENTE con el objeto JSON. No incluyas explicaciones,
introducciones, o texto fuera del JSON.

El JSON debe contener exactamente:
- `executive_summary`: Párrafo fluido con resumen ejecutivo
- `principal_findings`: Ensayo doctoral narrativo integrando todos los análisis
- `heatmap_analysis`: Ensayo analítico detallado de EXACTAMENTE 3 párrafos sobre patrones del mapa de calor
- `pca_analysis`: Ensayo analítico detallado de EXACTAMENTE 3 párrafos sobre componentes principales

**Instrucciones Específicas:**
1. **PRINCIPAL FINDINGS SÍ USE viñetas MÚLTIPLES** - genere lista de 3-5 hallazgos específicos y diferentes
2. **Resumen Ejecutivo, Heatmap Analysis y PCA NO USE viñetas** - genere texto narrativo fluido
3. **Heatmap Analysis DEBE tener EXACTAMENTE 3 párrafos** - Párrafo 1: patrones visuales, Párrafo 2: anomalías, Párrafo 3: implicaciones
4. **PCA Analysis DEBE tener EXACTAMENTE 3 párrafos** - Párrafo 1: interpretación técnica, Párrafo 2: relaciones, Párrafo 3: implicaciones
5. **Cada viñeta debe ser diferente** - no repita el mismo contenido en viñetas múltiples
6. **Integre análisis temporal** en los hallazgos principales
7. **Mencione datos cuantitativos específicos** (ej: "Google Trends con carga de +0.387")
8. **Conecte los patrones temporales con los hallazgos PCA**
9. **Use lenguaje académico pero accesible**
10. **Mencione el nombre de la herramienta** - incluya "Alianzas y Capital de Riesgo" (o la herramienta específica) en su análisis

**Ejemplo del estilo esperado para Heatmap Analysis de 3 párrafos:**
"El mapa de calor revela patrones visuales distintos con clusters de alta densidad concentrados en regiones temporales específicas, indicando períodos de interés máximo en la herramienta de gestión. Los gradientes de color muestran una clara progresión de valores bajos a altos, con Google Trends mostrando las señales más fuertes en los períodos más recientes. Varios clusters emergen, sugiriendo interés coordinado entre múltiples fuentes de datos durante períodos clave.

Las anomalías detectadas aparecen como picos de alta intensidad aislados que se desvían significativamente de los patrones circundantes, indicando potencialmente eventos virales o anuncios importantes relacionados con la herramienta. Estos valores atípicos, particularmente visibles en los datos de Google Trends, representan desviaciones estadísticas que justifican una investigación adicional sobre factores externos que influyen en los niveles de interés. Las regiones dispersas, por el contrario, destacan períodos de relativo desinterés que pueden corresponder a saturación del mercado o emergencia de herramientas competidoras.

Estos patrones del mapa de calor tienen implicaciones significativas para comprender el ciclo de vida de adopción de la herramienta. Los clusters densos se correlacionan con períodos de implementación activa y cambio organizacional, mientras que las regiones dispersas pueden indicar madurez del mercado o la necesidad de evolución de la herramienta. Esta distribución temporal sugiere tiempos estratégicos para actualizaciones de herramientas y esfuerzos de marketing para maximizar la adopción durante períodos de alto interés."

**Ejemplo del estilo esperado para PCA Analysis de 3 párrafos:**
"El análisis de componentes principales revela que el primer componente (PC1) explica el 49.3% de la varianza total en los datos, mostrando una fuerte correlación positiva entre Google Trends (+0.387) y Bain Usability (+0.421), lo que sugiere una dinámica de adopción popular. Por otro lado, Bain Satisfaction muestra una carga negativa (-0.311), lo que indica una tensión entre la popularidad y la satisfacción real.

El segundo componente (PC2) explica el 19.4% de la varianza y muestra una carga positiva moderada para Google Books (+0.356) y una carga negativa moderada para Crossref (-0.222), lo que sugiere una interacción compleja entre las fuentes de datos académicas y comerciales. Esto implica que la conversación académica está operando en un eje diferente al de la adopción popular.

Las implicaciones estratégicas de estos patrones sugieren que la implementación exitosa de la herramienta requiere una alineación entre la teoría académica y la práctica industrial. La brecha entre la adopción popular y la satisfacción real implica una necesidad de adaptación y ajuste continuo para asegurar la efectividad de la herramienta en diferentes contextos."

**NOTA**: Observe que hay DOS líneas en blanco entre cada párrafo para crear 3 párrafos distintos.
"""
        else:
            return """
### OUTPUT FORMAT

**IMPORTANT**: Respond ONLY with the JSON object. Do not include explanations,
introductions, or text outside the JSON.

The JSON must contain exactly:
- `executive_summary`: Fluid paragraph with executive summary
- `principal_findings`: Narrative doctoral essay integrating all analyses
- `heatmap_analysis`: Detailed analytical essay of EXACTLY 3 paragraphs about heatmap patterns
- `pca_analysis`: Detailed analytical essay of EXACTLY 3 paragraphs about principal components

**Specific Instructions:**
1. **PRINCIPAL FINDINGS YES USE MULTIPLE bullet points** - generate list of 3-5 specific and different findings
2. **Executive Summary, Heatmap Analysis and PCA DO NOT USE bullet points** - generate fluid narrative text
3. **Heatmap Analysis MUST have EXACTLY 3 paragraphs** - Paragraph 1: visual patterns, Paragraph 2: anomalies, Paragraph 3: implications
4. **PCA Analysis MUST have EXACTLY 3 paragraphs** - Paragraph 1: technical interpretation, Paragraph 2: relationships, Paragraph 3: implications
5. **Each bullet must be different** - do not repeat the same content in multiple bullets
6. **Integrate temporal analysis** into principal findings
7. **Mention specific quantitative data** (e.g., "Google Trends with loading of +0.387")
8. **Connect temporal patterns with PCA findings**
9. **Use academic but accessible language**
10. **Mention the tool name** - include the specific management tool name in your analysis

**Example of expected style for 3-paragraph Heatmap Analysis:**
"The heatmap reveals distinct visual patterns with high-density clusters concentrated in specific temporal regions, indicating periods of peak interest in the management tool. The color gradients show a clear progression from low to high intensity values, with Google Trends displaying the strongest signals in the most recent periods. Several clusters emerge, suggesting coordinated interest across multiple data sources during key time periods.

Detected anomalies appear as isolated high-intensity spikes that deviate significantly from surrounding patterns, potentially indicating viral events or major announcements related to the tool. These outliers, particularly visible in the Google Trends data, represent statistical deviations that warrant further investigation into external factors influencing interest levels. The sparse regions, conversely, highlight periods of relative disinterest that may correspond to market saturation or competing tool emergence.

These heatmap patterns have significant implications for understanding the tool's adoption lifecycle. The dense clusters correlate with periods of active implementation and organizational change, while sparse regions may indicate market maturity or the need for tool evolution. This temporal distribution suggests strategic timing for tool updates and marketing efforts to maximize adoption during high-interest periods."

**Example of expected style for 3-paragraph PCA Analysis:**
"The principal component analysis reveals that the first component (PC1) explains 49.3% of the total variance in the data, showing a strong positive correlation between Google Trends (+0.387) and Bain Usability (+0.421), suggesting a popular adoption dynamic. Conversely, Bain Satisfaction shows a negative loading (-0.311), indicating tension between popularity and real satisfaction.

The second component (PC2) explains 19.4% of the variance and shows a moderate positive loading for Google Books (+0.356) and a moderate negative loading for Crossref (-0.222), suggesting complex interactions between academic and commercial data sources. This implies that academic conversation operates on a different axis than popular adoption.

The strategic implications of these patterns suggest that successful tool implementation requires alignment between academic theory and industrial practice. The gap between popular adoption and real satisfaction implies a need for continuous adaptation and adjustment to ensure tool effectiveness in different contexts."

**NOTE**: Observe the TWO blank lines between each paragraph to create 3 distinct paragraphs.
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

    def _build_detailed_pca_narrative(self, components: List[Dict[str, Any]], tool_name: str, variance_explained: float) -> str:
        """Build detailed PCA narrative with specific numerical insights."""
        if not components:
            return ""
        
        narrative = f"""
**ANÁLISIS NUMÉRICO DETALLADO DE COMPONENTES:**

"""
        
        # Analyze first two components in detail
        for i, component in enumerate(components[:2]):
            comp_num = i + 1
            variance = component.get('variance_explained', 0)
            interpretation = component.get('interpretation', '')
            loadings = component.get('loadings', {})
            
            narrative += f"""
**Componente {comp_num} ({variance:.1f}% varianza explicada):**
{interpretation}

**Cargas Específicas:**
"""
            
            # Sort loadings by absolute value for emphasis
            sorted_loadings = sorted(loadings.items(), key=lambda x: abs(x[1]), reverse=True)
            
            for source, loading in sorted_loadings:
                direction = "positiva" if loading > 0 else "negativa" if loading < 0 else "neutral"
                strength = "fuerte" if abs(loading) >= 0.4 else "moderada" if abs(loading) >= 0.2 else "débil"
                narrative += f"- {source}: carga {direction} {strength} de {loading:.3f}\n"
            
            # Add specific insights for this component
            if i == 0:  # PC1
                positive_sources = [src for src, loading in loadings.items() if loading > 0.2]
                negative_sources = [src for src, loading in loadings.items() if loading < -0.2]
                
                if positive_sources and negative_sources:
                    narrative += f"""
**Relación de Oposición en PC1:**
- Fuentes con influencia positiva: {', '.join(positive_sources)}
- Fuentes con influencia negativa: {', '.join(negative_sources)}
- Esto sugiere una tensión entre popularidad/acceso y satisfacción/efectividad
"""
                elif len(positive_sources) >= 2:
                    narrative += f"""
**Patrón de Alineación en PC1:**
- Fuentes trabajando en sinergia: {', '.join(positive_sources)}
- Indica un patrón coherente de adopción o interés
"""
            
            elif i == 1:  # PC2
                # Identify perpendicular/independent factors
                independent_sources = [src for src, loading in loadings.items() if abs(loading) >= 0.2]
                if independent_sources:
                    narrative += f"""
**Factores Independientes en PC2:**
- Fuentes con influencia única: {', '.join(independent_sources)}
- Representa dimensiones ortogonales al patrón principal
"""
        
        # Add combined variance analysis
        if len(components) >= 2:
            combined_variance = components[0].get('variance_explained', 0) + components[1].get('variance_explained', 0)
            narrative += f"""
**ANÁLISIS COMBINADO DE PRIMEROS DOS COMPONENTES:**
- Varianza combinada explicada: {combined_variance:.1f}%
- """
            
            if combined_variance >= 70:
                narrative += "Poder explicativo excelente para análisis robusto"
            elif combined_variance >= 50:
                narrative += "Poder explicativo bueno para insights significativos"
            else:
                narrative += "Poder explicativo moderado, requiere interpretación cuidadosa"
        
        # Add specific guidance for narrative construction
        narrative += f"""

**GUÍA PARA CONSTRUIR LA NARRATIVA:**
1. Usa los valores numéricos exactos de cargas (ej: +0.387, -0.380)
2. Explica la tensión entre fuentes con cargas opuestas
3. Conecta PC1 con "dinámicas de adopción popular" vs "satisfacción real"
4. Conecta PC2 con "factores académicos/independientes" vs "factores comerciales"
5. Menciona específicamente el {combined_variance if len(components) >= 2 else variance_explained:.1f}% de varianza explicada
6. Relaciona con la brecha teoría-práctica en gestión organizacional
"""
        
        return narrative

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