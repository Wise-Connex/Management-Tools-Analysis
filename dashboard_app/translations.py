# Bilingual Translation System for Management Tools Analysis Dashboard
# Supports Spanish (es) and English (en) languages

TRANSLATIONS = {
    'es': {
        # UI Labels and Buttons
        'select_tool': 'Seleccione una Herramienta:',
        'select_sources': 'Seleccione las Fuentes de Datos:',
        'select_all': 'Seleccionar Todo',
        'show_table': 'Mostrar Tabla',
        'hide_table': 'Ocultar Tabla',
        'credits': 'Créditos',
        'data_table': 'Tabla de Datos',
        'performance_monitor': 'Monitor de Rendimiento del Sistema',

        # Placeholders
        'select_management_tool': 'Seleccione una Herramienta Gerencial',

        # Section Headers
        'temporal_analysis_2d': '1. Análisis Temporal 2D',
        'mean_analysis': '2. Análisis de Medias',
        'temporal_analysis_3d': '3. Análisis Temporal 3D',
        'seasonal_analysis': '4. Análisis Estacional',
        'fourier_analysis': '5. Análisis de Fourier (Periodograma)',
        'correlation_heatmap': '6. Mapa de Calor (Correlación)',
        'regression_analysis': '7. Análisis de Regresión',
        'pca_analysis': '8. Análisis PCA (Cargas y Componentes)',

        # Time Range Buttons
        'all': 'Todo',
        '20_years': '20 años',
        '15_years': '15 años',
        '10_years': '10 años',
        '5_years': '5 años',

        # Date Range Labels
        'date_range': 'Rango de Fechas:',
        'custom_range': 'Rango Personalizado:',

        # 3D Analysis
        'data_frequency': 'Frecuencia de Datos:',
        'monthly': 'Mensual',
        'annual': 'Anual',
        'chart_axes': 'Ejes del Gráfico:',
        'y_axis': 'Eje Y',
        'z_axis': 'Eje Z',

        # Seasonal Analysis
        'original_series': 'Serie Original',
        'trend': 'Tendencia',
        'seasonal': 'Estacional',
        'residuals': 'Residuos',

        # Fourier Analysis
        'fourier_analysis_periodogram': 'Análisis de Fourier - Periodograma',
        'magnitude': 'Magnitud',
        'period_months': 'Período (meses)',
        'significance_threshold': 'Umbral Significancia (95%)',
        'significant_components': 'Componentes Significativos',
        'non_significant_components': 'Componentes No Significativos',
        'quarterly': 'Trimestral (3m)',
        'semiannual': 'Semestral (6m)',
        'annual': 'Anual (12m)',

        # Dropdown Placeholders
        'select_source_for_analysis': 'Seleccione fuente para cargar análisis',
        'select_y_axis': 'Eje Y',
        'select_z_axis': 'Eje Z',

        # Data Frequency
        'data_frequency': 'Frecuencia de Datos:',
        'monthly': 'Mensual',
        'annual': 'Anual',

        # Chart Elements
        'date': 'Fecha',
        'value': 'Valor',
        'contribution_relative': 'Contribución Relativa (%)',
        'absolute_value': 'Valor Absoluto',
        'relative_absolute': 'Relativo (100% = {max_value:.2f}) + Absoluto',
        'data_sources': 'Fuentes de Datos',
        'correlation': 'Correlación',
        'regression_equations': 'Haga clic en el mapa de calor para ver las ecuaciones de regresión',
        'click_heatmap': 'Haga clic en el mapa de calor para seleccionar variables para regresión',
        'invalid_selection': 'Seleccione dos variables diferentes para el análisis de regresión',
        'cannot_regress_same': 'No se puede hacer regresión de {var} contra sí mismo.',
        'select_different_vars': 'Seleccione dos variables diferentes en el mapa de calor.',
        'correlation_heatmap_title': 'Mapa de Calor de Correlación',
        'temporal_3d_title': 'Análisis Temporal 3D: {y_axis} vs {z_axis} ({frequency})',
        'seasonal_title': 'Análisis Estacional: {source}',
        'fourier_title': 'Análisis de Fourier - Periodograma: {source}',
        'regression_title': 'Análisis de Regresión Polinomial: {y_var} vs {x_var}',
        'regression_error': 'Error en el análisis de regresión',
        'variables_not_found': 'Variables no encontradas: {x_var} vs {y_var}',
        'pca_title': 'Análisis PCA (Cargas y Componentes)',

        # Performance Monitor
        'database_info': 'Información de Base de Datos',
        'total_records': 'Total de Registros:',
        'unique_keywords': 'Palabras Clave Únicas:',
        'data_sources_count': 'Fuentes de Datos:',
        'current_query': 'Consulta Actual',
        'records_in_use': 'Registros en Uso:',
        'selected_sources': 'Fuentes Seleccionadas:',
        'temporal_range': 'Rango Temporal:',
        'tool': 'Herramienta:',
        'performance_metrics': 'Métricas de Rendimiento',
        'load_time': 'Tiempo de Carga:',
        'query_efficiency': 'Eficiencia de Consultas:',
        'memory_usage': 'Uso de Memoria:',
        'compression': 'Compresión:',
        'active_optimizations': 'Optimizaciones Activas',
        'preprocessed_data': '✅ Datos pre-procesados en base de datos',
        'optimized_indexes': '✅ Índices optimizados para velocidad',
        'smart_cache': '✅ Caché inteligente de resultados',
        'lazy_loading': '✅ Lazy loading para análisis complejos',
        'auto_graph_optimization': '✅ Optimización automática de gráficos',

        # Modal
        'source_notes': 'Notas de la Fuente',
        'close': 'Cerrar',
        'no_notes': 'No hay notas disponibles',

        # Error Messages
        'no_data_available': 'No hay datos disponibles para la herramienta \'{keyword}\' con las fuentes seleccionadas.',
        'please_select_tool_and_sources': 'Por favor, seleccione una Herramienta y al menos una Fuente de Datos.',
        'no_sources_selected': 'Seleccione una herramienta para ver las fuentes disponibles',
        'no_doi_available': 'No hay DOI disponible para esta herramienta',

        # Chart Labels
        'period_months': 'Período (meses)',
        'magnitude': 'Magnitud',
        'significance_threshold': 'Umbral Significancia (95%)',
        'significant_components': 'Componentes Significativos',
        'non_significant_components': 'Componentes No Significativos',
        'quarterly': 'Trimestral (3m)',
        'semiannual': 'Semestral (6m)',
        'annual': 'Anual (12m)',

        # Navigation
        'temporal_2d_nav': '1. Temporal 2D',
        'mean_analysis_nav': '2. Análisis Medias',
        'temporal_3d_nav': '3. Temporal 3D',
        'seasonal_nav': '4. Estacional',
        'fourier_nav': '5. Fourier',
        'correlation_nav': '6. Correlación',
        'regression_nav': '7. Regresión',
        'pca_nav': '8. PCA',
        'data_table_nav': 'Tabla de Datos',
        'performance_nav': 'Rendimiento',

        # Header
        'doctoral_research_focus': 'Base analítica para la Investigación Doctoral:',
        'ontological_dichotomy': '«Dicotomía ontológica en las "Modas Gerenciales"»',
        'management_tools': 'Herramientas gerenciales: Dinámicas temporales contingentes y antinomias policontextuales',
        'principal_investigator': 'Investigador Principal:',
        'academic_tutor': 'Tutora Académica:',
        'solidum_consulting': 'Solidum Consulting',
        'ulac': 'ULAC',

        # Credits
        'dashboard_analysis': 'Dashboard de Análisis de',
        'management_tools_lower': 'Herramientas Gerenciales',
        'developed_with': 'Desarrollado con Python, Plotly y Dash',
        'by': 'por:',
        'tutor': 'Tutora Académica:',
        'license': 'Licencia Dashboard: CC BY-NC 4.0',
        'harvard_dataverse': 'Harvard Dataverse: Data de la Investigación',
        'harvard_title': 'Datos en el prestigioso repositorio de la Universidad de Harvard',
        'nlm_publication': 'Publicación en la National Library of Medicine',
        'nlm_title': 'Datos en la Biblioteca Nacional de Medicina de EE.UU.',
        'zenodo_publication': 'Publicación en el Repositorio CERN - Zenodo',
        'zenodo_title': '138 Informes Técnicos en el Repositorio Europeo Zenodo, del Conseil Européen pour la Recherche Nucléaire.',
        'openaire_visibility': 'Visibilidad Europea en OpenAire',
        'openaire_title': 'Informes y Datos indexados en el Portal Europeo de Ciencia Abierta OpenAire',
        'github_reports': 'Informes y Documentación Técnica en GitHub',
        'github_title': 'Documentación técnica y científica de herramientas gerenciales en GitHub',

        # Sidebar affiliations
        'university': 'Universidad Latinoamericana y del Caribe (ULAC)',
        'postgraduate_coordination': 'Coordinación General de Postgrado',
        'doctoral_program': 'Doctorado en Ciencias Gerenciales',

        # Source Notes Modal
        'source': 'Fuente:',
        'doi': 'DOI:',

        # DOI and Links
        'ic_report_doi': 'DOI del Informe IC:',

        # Regression
        'linear': 'Lineal',
        'quadratic': 'Cuadrática',
        'cubic': 'Cúbica',
        'quartic': 'Cuártica',
        'r_squared': 'R²',
        'data_points': 'Puntos de Datos',

        # Source names for display
        'bain_satisfaction': 'Bain - Satisfacción',
        'bain_usability': 'Bain - Usabilidad',
        'bain_satisfaction_db': 'Bain - Satisfacción',
        'bain_usability_db': 'Bain - Usabilidad',

        # PCA
        'loadings': 'Cargas de Componentes',
        'explained_variance': 'Varianza Explicada',
        'cumulative_variance': 'Varianza Acumulativa (%)',
        'inverse_relationship': 'Relación Inversa',

        # Fourier
        'select_source_fourier': 'Seleccione una fuente de datos para ver el análisis de Fourier',

        # General
        'available': 'disponibles',
        'none': 'Ninguna',
        'healthy': 'saludable',
        'unhealthy': 'no saludable',
        'connected': 'conectado',
        'unavailable': 'no disponible',
        'version': 'Versión',
        'service': 'Servicio',
        'database': 'Base de Datos',
        'less_than_half_second': '< 0.5 segundos',
        'high': 'Alta',
        'optimized': 'Optimizado',
        'average_compression': '85% promedio',
    },
    'en': {
        # UI Labels and Buttons
        'select_tool': 'Select a Tool:',
        'select_sources': 'Select Data Sources:',
        'select_all': 'Select All',
        'show_table': 'Show Table',
        'hide_table': 'Hide Table',
        'credits': 'Credits',
        'data_table': 'Data Table',
        'performance_monitor': 'System Performance Monitor',

        # Placeholders
        'select_management_tool': 'Select a Management Tool',

        # Section Headers
        'temporal_analysis_2d': '1. Temporal Analysis 2D',
        'mean_analysis': '2. Mean Analysis',
        'temporal_analysis_3d': '3. Temporal Analysis 3D',
        'seasonal_analysis': '4. Seasonal Analysis',
        'fourier_analysis': '5. Fourier Analysis (Periodogram)',
        'correlation_heatmap': '6. Correlation Heatmap',
        'regression_analysis': '7. Regression Analysis',
        'pca_analysis': '8. PCA Analysis (Loadings and Components)',

        # Time Range Buttons
        'all': 'All',
        '20_years': '20 years',
        '15_years': '15 years',
        '10_years': '10 years',
        '5_years': '5 years',

        # Date Range Labels
        'date_range': 'Date Range:',
        'custom_range': 'Custom Range:',

        # 3D Analysis
        'data_frequency': 'Data Frequency:',
        'monthly': 'Monthly',
        'annual': 'Annual',
        'chart_axes': 'Chart Axes:',
        'y_axis': 'Y Axis',
        'z_axis': 'Z Axis',

        # Seasonal Analysis
        'original_series': 'Original Series',
        'trend': 'Trend',
        'seasonal': 'Seasonal',
        'residuals': 'Residuals',

        # Fourier Analysis
        'fourier_analysis_periodogram': 'Fourier Analysis - Periodogram',
        'magnitude': 'Magnitude',
        'period_months': 'Period (months)',
        'significance_threshold': 'Significance Threshold (95%)',
        'significant_components': 'Significant Components',
        'non_significant_components': 'Non-Significant Components',
        'quarterly': 'Quarterly (3m)',
        'semiannual': 'Semiannual (6m)',
        'annual': 'Annual (12m)',

        # Dropdown Placeholders
        'select_source_for_analysis': 'Select source to load analysis',
        'select_y_axis': 'Y Axis',
        'select_z_axis': 'Z Axis',

        # Data Frequency
        'data_frequency': 'Data Frequency:',
        'monthly': 'Monthly',
        'annual': 'Annual',

        # Chart Elements
        'date': 'Date',
        'value': 'Value',
        'contribution_relative': 'Relative Contribution (%)',
        'absolute_value': 'Absolute Value',
        'relative_absolute': 'Relative (100% = {max_value:.2f}) + Absolute',
        'data_sources': 'Data Sources',
        'correlation': 'Correlation',
        'regression_equations': 'Click on the heatmap to see regression equations',
        'click_heatmap': 'Click on the heatmap to select variables for regression',
        'invalid_selection': 'Select two different variables for regression analysis',
        'cannot_regress_same': 'Cannot regress {var} against itself.',
        'select_different_vars': 'Select two different variables on the heatmap.',
        'correlation_heatmap_title': 'Correlation Heatmap',
        'temporal_3d_title': 'Temporal 3D Analysis: {y_axis} vs {z_axis} ({frequency})',
        'seasonal_title': 'Seasonal Analysis: {source}',
        'fourier_title': 'Fourier Analysis - Periodogram: {source}',
        'regression_title': 'Polynomial Regression Analysis: {y_var} vs {x_var}',
        'regression_error': 'Error in regression analysis',
        'variables_not_found': 'Variables not found: {x_var} vs {y_var}',
        'pca_title': 'PCA Analysis (Loadings and Components)',

        # Performance Monitor
        'database_info': 'Database Information',
        'total_records': 'Total Records:',
        'unique_keywords': 'Unique Keywords:',
        'data_sources_count': 'Data Sources:',
        'current_query': 'Current Query',
        'records_in_use': 'Records in Use:',
        'selected_sources': 'Selected Sources:',
        'temporal_range': 'Temporal Range:',
        'tool': 'Tool:',
        'performance_metrics': 'Performance Metrics',
        'load_time': 'Load Time:',
        'query_efficiency': 'Query Efficiency:',
        'memory_usage': 'Memory Usage:',
        'compression': 'Compression:',
        'active_optimizations': 'Active Optimizations',
        'preprocessed_data': '✅ Pre-processed data in database',
        'optimized_indexes': '✅ Optimized indexes for speed',
        'smart_cache': '✅ Smart result caching',
        'lazy_loading': '✅ Lazy loading for complex analyses',
        'auto_graph_optimization': '✅ Automatic graph optimization',

        # Modal
        'source_notes': 'Source Notes',
        'close': 'Close',
        'no_notes': 'No notes available',

        # Error Messages
        'no_data_available': 'No data available for tool \'{keyword}\' with selected sources.',
        'please_select_tool_and_sources': 'Please select a Tool and at least one Data Source.',
        'no_sources_selected': 'Select a tool to view available sources',
        'no_doi_available': 'No DOI available for this tool',

        # Chart Labels
        'period_months': 'Period (months)',
        'magnitude': 'Magnitude',
        'significance_threshold': 'Significance Threshold (95%)',
        'significant_components': 'Significant Components',
        'non_significant_components': 'Non-Significant Components',
        'quarterly': 'Quarterly (3m)',
        'semiannual': 'Semiannual (6m)',
        'annual': 'Annual (12m)',

        # Navigation
        'temporal_2d_nav': '1. Temporal 2D',
        'mean_analysis_nav': '2. Mean Analysis',
        'temporal_3d_nav': '3. Temporal 3D',
        'seasonal_nav': '4. Seasonal',
        'fourier_nav': '5. Fourier',
        'correlation_nav': '6. Correlation',
        'regression_nav': '7. Regression',
        'pca_nav': '8. PCA',
        'data_table_nav': 'Data Table',
        'performance_nav': 'Performance',

        # Header
        'doctoral_research_focus': 'Analytical basis for Doctoral Research:',
        'ontological_dichotomy': '«Ontological dichotomy in "Management Fads"»',
        'management_tools': 'Management tools: Contingent temporal dynamics and policontextual antinomies',
        'principal_investigator': 'Doctoral Candidate:',
        'academic_tutor': 'Academic Tutor:',
        'solidum_consulting': 'Solidum Consulting',
        'ulac': 'ULAC',

        # Credits
        'dashboard_analysis': 'Analysis Dashboard of',
        'management_tools_lower': 'Management Tools',
        'developed_with': 'Developed with Python, Plotly and Dash',
        'by': 'by:',
        'tutor': 'Academic Tutor:',
        'license': 'Dashboard License: CC BY-NC 4.0',
        'harvard_dataverse': 'Harvard Dataverse: Research Data',
        'harvard_title': 'Data in Harvard University\'s prestigious repository',
        'nlm_publication': 'Publication in the National Library of Medicine',
        'nlm_title': 'Data in the U.S. National Library of Medicine',
        'zenodo_publication': 'Publication in the CERN Zenodo Repository',
        'zenodo_title': '138 Technical Reports in the European Zenodo Repository, from the Conseil Européen pour la Recherche Nucléaire.',
        'openaire_visibility': 'European Visibility in OpenAire',
        'openaire_title': 'Reports and Data indexed in the European Open Science Portal OpenAire',
        'github_reports': 'Reports and Technical Documentation on GitHub',
        'github_title': 'Technical and scientific documentation of management tools on GitHub',

        # Sidebar affiliations
        'university': 'Latin American and Caribbean University (ULAC)',
        'postgraduate_coordination': 'General Postgraduate Coordination',
        'doctoral_program': 'Doctorate in Management Sciences',

        # Source Notes Modal
        'source': 'Source:',
        'doi': 'DOI:',

        # DOI and Links
        'ic_report_doi': 'IC Report DOI:',

        # Regression
        'linear': 'Linear',
        'quadratic': 'Quadratic',
        'cubic': 'Cubic',
        'quartic': 'Quartic',
        'r_squared': 'R²',
        'data_points': 'Data Points',

        # PCA
        'loadings': 'Component Loadings',
        'explained_variance': 'Explained Variance',
        'cumulative_variance': 'Cumulative Variance (%)',
        'inverse_relationship': 'Inverse Relationship',

        # Fourier
        'select_source_fourier': 'Select a data source to view the Fourier analysis',

        # General
        'available': 'available',
        'none': 'None',
        'healthy': 'healthy',
        'unhealthy': 'unhealthy',
        'connected': 'connected',
        'unavailable': 'unavailable',
        'version': 'Version',
        'service': 'Service',
        'database': 'Database',
        'less_than_half_second': '< 0.5 seconds',
        'high': 'High',
        'optimized': 'Optimized',
        'average_compression': '85% average',
    }
}

# Tool name translations (Spanish to English)
TOOL_TRANSLATIONS = {
    'es': {
        'Alianzas y Capital de Riesgo': 'Alianzas y Capital de Riesgo',
        'Benchmarking': 'Benchmarking',
        'Calidad Total': 'Calidad Total',
        'Competencias Centrales': 'Competencias Centrales',
        'Cuadro de Mando Integral': 'Cuadro de Mando Integral',
        'Estrategias de Crecimiento': 'Estrategias de Crecimiento',
        'Experiencia del Cliente': 'Experiencia del Cliente',
        'Fusiones y Adquisiciones': 'Fusiones y Adquisiciones',
        'Gestión de Costos': 'Gestión de Costos',
        'Gestión de la Cadena de Suministro': 'Gestión de la Cadena de Suministro',
        'Gestión del Cambio': 'Gestión del Cambio',
        'Gestión del Conocimiento': 'Gestión del Conocimiento',
        'Innovación Colaborativa': 'Innovación Colaborativa',
        'Lealtad del Cliente': 'Lealtad del Cliente',
        'Optimización de Precios': 'Optimización de Precios',
        'Outsourcing': 'Outsourcing',
        'Planificación Estratégica': 'Planificación Estratégica',
        'Planificación de Escenarios': 'Planificación de Escenarios',
        'Presupuesto Base Cero': 'Presupuesto Base Cero',
        'Propósito y Visión': 'Propósito y Visión',
        'Reingeniería de Procesos': 'Reingeniería de Procesos',
        'Segmentación de Clientes': 'Segmentación de Clientes',
        'Talento y Compromiso': 'Talento y Compromiso',
    },
    'en': {
        'Alianzas y Capital de Riesgo': 'Alliances and Venture Capital',
        'Benchmarking': 'Benchmarking',
        'Calidad Total': 'Total Quality',
        'Competencias Centrales': 'Core Competencies',
        'Cuadro de Mando Integral': 'Balanced Scorecard',
        'Estrategias de Crecimiento': 'Growth Strategies',
        'Experiencia del Cliente': 'Customer Experience',
        'Fusiones y Adquisiciones': 'Mergers and Acquisitions',
        'Gestión de Costos': 'Cost Management',
        'Gestión de la Cadena de Suministro': 'Supply Chain Management',
        'Gestión del Cambio': 'Change Management',
        'Gestión del Conocimiento': 'Knowledge Management',
        'Innovación Colaborativa': 'Collaborative Innovation',
        'Lealtad del Cliente': 'Customer Loyalty',
        'Optimización de Precios': 'Price Optimization',
        'Outsourcing': 'Outsourcing',
        'Planificación Estratégica': 'Strategic Planning',
        'Planificación de Escenarios': 'Scenario Planning',
        'Presupuesto Base Cero': 'Zero-Based Budgeting',
        'Propósito y Visión': 'Purpose and Vision',
        'Reingeniería de Procesos': 'Business Process Reengineering',
        'Segmentación de Clientes': 'Customer Segmentation',
        'Talento y Compromiso': 'Talent and Commitment',
    }
}

def get_text(key, language='es', **kwargs):
    """
    Get translated text for a given key and language.

    Args:
        key (str): Translation key
        language (str): Language code ('es' or 'en')
        **kwargs: Format string arguments

    Returns:
        str: Translated text
    """
    if language not in TRANSLATIONS:
        language = 'es'  # Fallback to Spanish

    translation = TRANSLATIONS[language].get(key, key)  # Fallback to key if not found

    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Return unformatted if formatting fails

    return translation

def get_tool_name(tool_key, language='es'):
    """
    Get translated tool name.

    Args:
        tool_key (str): Original tool name key
        language (str): Language code ('es' or 'en')

    Returns:
        str: Translated tool name
    """
    if language not in TOOL_TRANSLATIONS:
        language = 'es'

    return TOOL_TRANSLATIONS[language].get(tool_key, tool_key)

def get_available_languages():
    """Get list of available language codes."""
    return list(TRANSLATIONS.keys())

def get_language_name(language_code):
    """Get human-readable language name."""
    names = {
        'es': 'Español',
        'en': 'English'
    }
    return names.get(language_code, language_code)

def translate_database_content(text, language='es'):
    """
    Translate database content that contains Spanish text.
    This handles common patterns found in the database notes.

    Args:
        text (str): The text from database to translate
        language (str): Target language code

    Returns:
        str: Translated text
    """
    if not text or language == 'es':
        return text

    # Common translation patterns for database content
    translations = {
        # Source notes patterns
        'Descriptores lógicos:': 'Logical Descriptors:',
        'Parámetros de búsqueda:': 'Search Parameters:',
        'cobertura global': 'global coverage',
        'marco temporal': 'temporal framework',
        'categorización amplia': 'broad categorization',
        'tipo de búsqueda': 'search type',
        'Índice Relativo:': 'Relative Index:',
        'Los datos se normalizan en un índice relativo': 'Data is normalized into a relative index',
        'mediante la fórmula:': 'using the formula:',
        'Índice relativo = (Volumen de búsqueda del término / Volumen total de búsquedas) x 100': 'Relative Index = (Search volume of the term / Total search volume) x 100',
        'mitigando sesgos por heterogeneidad en volúmenes de búsqueda entre regiones y periodos.': 'mitigating biases due to heterogeneity in search volumes between regions and periods.',
        'Metodología:': 'Methodology:',
        'La métrica es comparativa, no absoluta,': 'The metric is comparative, not absolute,',
        'basada en muestreo probabilístico,': 'based on probabilistic sampling,',
        'lo que introduce variabilidad estadística.': 'which introduces statistical variability.',
        'La interpretación se centra en tendencias de interés relativo,': 'The interpretation focuses on relative interest trends,',
        'no en recuentos absolutos.': 'not on absolute counts.',
        'Disponibilidad de datos (desde 2004)': 'Data availability (since 2004)',
        'permite análisis diacrónico contextualizado en evolución digital': 'allows contextualized diachronic analysis in digital evolution',
        'y patrones de búsqueda.': 'and search patterns.',
        'Perfil de Usuarios:': 'User Profile:',
        'Refleja interés público,': 'Reflects public interest,',
        'popularidad de búsqueda': 'search popularity',
        'y tendencias emergentes en tiempo real': 'and emerging trends in real time',
        'en un perfil de usuarios heterogéneos:': 'in a heterogeneous user profile:',
        'investigadores,': 'researchers,',
        'periodistas,': 'journalists,',
        'profesionales del marketing,': 'marketing professionals,',
        'empresarios': 'entrepreneurs',
        'y usuarios generales.': 'and general users.',
        'Limitaciones:': 'Limitations:',
        'No hay correlación directa entre interés en búsquedas': 'There is no direct correlation between search interest',
        'e implementación efectiva en organizaciones.': 'and effective implementation in organizations.',
        'La evolución terminológica puede afectar': 'Terminological evolution may affect',
        'la coherencia longitudinal': 'longitudinal coherence',

        # General patterns
        'benchmarking': 'benchmarking',
        '+': '+',
        'web': 'web',
        '01/2004-01/2025': '01/2004-01/2025',
        '2004': '2004',
        '2025': '2025',
        '95%': '95%',
        'N/A': 'N/A',

        # Database source names (translated)
        'bain_usabilidad_translated': 'Bain - Usability',
        'bain_satisfacción_translated': 'Bain - Satisfaction'
    }

    translated_text = text
    for spanish, english in translations.items():
        translated_text = translated_text.replace(spanish, english)

    return translated_text

def translate_source_name(source_name, language='es'):
    """Translate source names for display in charts and tables"""
    if language == 'es':
        return source_name

    # Translation mapping for source names
    source_translations = {
        'Bain - Usabilidad': 'Bain - Usability',
        'Bain Usabilidad': 'Bain Usability',
        'Bain - Satisfacción': 'Bain - Satisfaction',
        'Bain Satisfacción': 'Bain Satisfaction',
        'BAIN_Ind_Usabilidad': 'Bain - Usability',
        'BAIN_Ind_Satisfacción': 'Bain - Satisfaction'
    }

    return source_translations.get(source_name, source_name)

# DOCKER_FIX: Enhanced translation for Docker environment
def enhanced_translate_source_name(source_name, language='es'):
    """
    Enhanced translation function that handles more variations and provides fallbacks.
    This addresses Docker-specific issues with source name translation.
    
    Args:
        source_name: Source name to translate
        language: Target language ('es' or 'en')
        
    Returns:
        Translated source name
    """
    # Try the standard translation first
    try:
        return translate_source_name(source_name, language)
    except:
        pass
    
    # Fallback translations for Docker environment
    if language == 'es':
        # English to Spanish
        fallback_translations = {
            'Bain - Usability': 'Bain - Usabilidad',
            'Bain Usability': 'Bain - Usabilidad',
            'Bain - Satisfaction': 'Bain - Satisfacción',
            'Bain Satisfaction': 'Bain - Satisfacción',
            'Google Books': 'Google Books Ngrams',
            'Crossref': 'Crossref.org'
        }
    else:
        # Spanish to English
        fallback_translations = {
            'Bain - Usabilidad': 'Bain - Usability',
            'Bain - Satisfacción': 'Bain - Satisfaction',
            'Google Books Ngrams': 'Google Books',
            'Crossref.org': 'Crossref'
        }
    
    return fallback_translations.get(source_name, source_name)

