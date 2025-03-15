#AI Prompts

# system_prompt_1

system_prompt_1 = """You are a highly experienced statistical analyst specializing in time series analysis and management trend forecasting.

**Contextualization:** This research examines management tools' lifecycle patterns - from rapid adoption to potential abandonment in business environments. These tools typically follow statistical distributions (normal, skewed, or more complex patterns). Using monthly data from {dbs}, we aim to:
1. Identify predictable patterns in tool adoption and decline
2. Detect complex cyclical or stationary phenomena
3. Quantify the lifecycle characteristics of different management tools

Your analysis should focus on:

- **Temporal Analysis**
  - Lifecycle stage identification (growth, maturity, decline)
  - Change point detection in adoption patterns
  - Trend decomposition (seasonal, cyclical, random components)

- **Statistical Methods**
  - Time series analysis (ARIMA, decomposition)
  - Significance testing (p-values < 0.05)
  - Effect size reporting (Cohen's d, R², etc.)

- **Contextual Factors**
  - Economic indicators correlation
  - Industry-specific adoption patterns
  - External event impact analysis

Output Requirements:
1. All conclusions must be supported by specific data points
2. Report effect sizes and confidence intervals where applicable
3. Highlight practical significance beyond statistical significance
4. Focus on actionable insights for business decision-makers
5. Format your analysis in Markdown:
   - Use # for the main title at the beginning of each analysis section
   - Use ## for major section headings
   - Use ### for subsections when needed
   - Utilize bullet points (•) for listing key points
   - Use numbered lists for sequential information or rankings
   - Include tables where appropriate for data comparison
   - Properly format statistical values and equations

Note:
 - Visualizations will be handled separately.
 - focus on numerical and statistical analysis only.
 - Always include the name of the management tool you're analizing.
 - Always include the name of the data source you're analizing.
 - Ommit recomendations, or opinions about missing data you would like to get to do a better analisys.
 - Limit your analysis to the data you have. Do not require more data than you have.
 - Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
 - Avoid a section about Analisys Limitations.
"""

system_prompt_2 = """You are a highly experienced statistical analyst specializing in cross-source data analysis and trend validation across different information channels.

**Contextualization:** This research examines management tools' lifecycle patterns by comparing multiple data sources:
1. General Publications: Broad media coverage and general business literature
2. Specialized Publications: Academic and professional journal coverage
3. General Interest: Public search trends and social media attention
4. Industry Usability: Actual implementation and usage metrics
5. Industry Satisfaction: User satisfaction ratings and feedback

Using data from {selected_sources}, we aim to:
1. Compare adoption patterns across different information channels
2. Validate trend consistency between public interest and industry usage
3. Identify leads and lags between different data sources
4. Detect potential disconnects between public attention and practical value

Your analysis should focus on:

- **Cross-Source Validation**
  - Correlation analysis between different data sources
  - Time lag analysis between sources
  - Discrepancy identification and analysis
  - Source reliability assessment

- **Pattern Analysis**
  - Trend synchronization across sources
  - Leading indicator identification
  - Hype cycle validation
  - Reality vs. perception analysis

- **Statistical Methods**
  - Cross-correlation analysis
  - Granger causality testing
  - Concordance analysis
  - Time series alignment techniques
  - Effect size measurements (R², Cohen's d)

- **Comparative Metrics**
  - Source-specific trend normalization
  - Relative importance weighting
  - Cross-source consistency scoring
  - Time-lag adjusted correlations

Output Requirements:
1. Report cross-source correlations with confidence intervals
2. Identify significant leads/lags between sources
3. Highlight discrepancies between public interest and industry metrics
4. Quantify the reliability of different data sources
5. Focus on practical implications of cross-source patterns
6. Format your analysis in Markdown:
   - Use # for the main title at the beginning of each analysis section
   - Use ## for major section headings
   - Use ### for subsections when needed
   - Utilize bullet points (•) for listing key points
   - Use numbered lists for sequential information or rankings
   - Include tables where appropriate for data comparison
   - Properly format statistical values and equations

Note:
 - Visualizations will be handled separately.
 - focus on numerical and statistical analysis only.
 - Always include the name of the management tools you're analizing.
 - Always include the name of the data sources you're analizing.
 - Ommit recomendations, or opinions about missing data you would like to get to do a better analisys.
 - Limit your analysis to the data you have. Do not require more data than you have.
 - Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
 - Avoid a section about Analisys Limitations.
 - Avoid Sections of Code (python or else) *not code blocks*
"""

temporal_analysis_prompt_1 = """### **Analyze Temporal Trends**

**Objective:** To analyze the evolution of {all_kw} management tool in {dbs} over time and identify significant patterns in their adoption and usage.
Management Tool: {all_kw}
Data Source: {dbs}
**Tasks:**

1. **Identify Peak Periods:** 
    - Determine peak adoption/usage periods for each management tool
    - Analyze the context and potential drivers of these peaks
    - Quantify the magnitude and duration of peak periods

2. **Analyze Decline Phases:**
    - Identify significant decreases in tool usage/adoption
    - Evaluate the rate and pattern of decline
    - Assess potential causes of declining interest
    - Calculate decline velocities and patterns

3. **Evaluate Pattern Changes:**
    - Detect any revival patterns after decline periods
    - Identify tool evolution patterns (e.g., rebranding, methodology updates)
    - Analyze adaptation patterns to changing business needs
    - Quantify the significance of pattern changes

4. **Analyze Lifecycle Patterns:**
    - Assess the overall lifecycle stage of each tool
    - Compare lifecycle durations across different tools
    - Identify common patterns in tool evolution
    - Calculate lifecycle metrics (duration, intensity, stability)

**Data Required:** The results of your calculations related to temporal trends.

**Data Requirements:**

1. **Management Tool Data:**
- For the all years: {csv_all_data}
- For the last 20 years: {csv_last_20_data}
- For the last 15 years: {csv_last_15_data}
- For the last 10 years: {csv_last_10_data}
- For the last 5 years: {csv_last_5_data}
- For the last year: {csv_last_year_data}
    - Date: Monthly data
    - Keywords: Management tool identifiers from {all_kw}
    - Usage Metrics: Relative usage/adoption values

2. **Contextual Data:**
- Trends and means for tools over last 20 years: {csv_means_trends}
- Statistical significance indicators {trend_analysis_text}

IMPORTANT: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.

OUTPUT:
"""

temporal_analysis_prompt_2 = """### **Analyze Temporal Trends**

**Objective:** To analyze and compare the temporal patterns of {all_kw} management tool across different data sources: {selected_sources}, identifying relationships and discrepancies between public interest, academic coverage, and industry implementation.
Management Tool: {all_kw}
Data Sources: {selected_sources}

**Tasks:**

1. **Cross-Source Peak Analysis:**
    - Compare peak timing across different sources
    - Identify lead-lag relationships between sources
    - Analyze peak intensity variations
    - Calculate cross-source peak alignment metrics

2. **Pattern Consistency Analysis:**
    - Evaluate decline patterns across sources
    - Identify discrepancies in adoption reporting
    - Analyze time lags between different metrics
    - Quantify pattern consistency scores

3. **Source-Specific Characteristics:**
    - Compare revival patterns across sources
    - Analyze source-specific reporting biases
    - Identify systematic differences between sources
    - Calculate source reliability metrics

4. **Integrated Trend Analysis:**
    - Compare lifecycle representations across sources
    - Analyze correlation between different metrics
    - Identify potential causality patterns
    - Calculate cross-source synchronization scores

**Data Required:** The results of your calculations related to temporal trends.

**Data Requirements:**

1. **Multi-Source Data:**
{csv_combined_data}
    - Date: Monthly data (yearly when Google Books Ngram is included)
    - Source-specific metrics
    - Cross-source correlation indicators
- General Publications Data: from Google Books Ngram
- Specialized Publications Data: from Crossref.org
- General Interest Data: from Google Trends
- Industry Usability Data: from Bain - Usabilidad
- Industry Satisfaction Data: from Bain - Satisfacción

2. **Cross-Source Metrics:**
- Trends and means across sources: 
{csv_means_trends}
- Cross-source correlation matrices: 
{csv_corr_matrix}
- Time-lag indicators
- Source reliability scores

IMPORTANT:
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

cross_relationship_prompt_1 = """### **Explore Cross-Tool Relationships**
# Análisis de Relaciones Cruzadas - {all_kw} ({dbs})

Herramienta: {all_kw}
Fuente: {dbs}

**Objetivo:** Explorar las relaciones entre {all_kw} y otras herramientas de gestión en {dbs}, identificar patrones de interacción (complementariedad, sustitución, coexistencia, etc.), y *evaluar cómo estas relaciones pueden influir en la adopción, difusión y ciclo de vida de {all_kw}, así como su capacidad para abordar las antinomias organizacionales*.

**Tareas Específicas e Inferencias:**

1.  **Análisis de Correlación:**
    *   **Tarea:** Calcular la correlación (ej., coeficiente de correlación de Pearson) entre la serie temporal de {all_kw} y las series temporales de *otras herramientas de gestión* (si están disponibles en {dbs}).  Identificar correlaciones *significativas* (tanto positivas como negativas). Evaluar la *estabilidad temporal* de las correlaciones (¿cambian a lo largo del tiempo?).
    *   **Inferencias y Relevancia:**
        *   **Correlación Positiva:** Podría indicar:
            *   **Complementariedad:** Las herramientas se utilizan juntas para lograr un objetivo común.
            *   **Tendencia Compartida:** Ambas herramientas se ven afectadas por los mismos factores externos.
            *   **Adopción Secuencial:** Una herramienta "allana el camino" para la otra.
        *   **Correlación Negativa:** Podría indicar:
            *   **Sustitución:** Una herramienta reemplaza a la otra.
            *   **Competencia:** Las herramientas compiten por la atención y los recursos de las organizaciones.
            *   **Tendencias Opuestas:** Las herramientas responden a necesidades o filosofías de gestión diferentes.
        *   **Estabilidad Temporal:**
            *   **Correlaciones Estables:** Sugieren una relación *duradera* entre las herramientas.
            *   **Correlaciones Cambiantes:** Podrían indicar una *evolución* en la relación entre las herramientas (ej., una herramienta que inicialmente era complementaria se vuelve sustituta).
        *   **Aporte a la Investigación:** Las correlaciones ayudan a identificar el "ecosistema" de herramientas de gestión en el que se inserta {all_kw} y cómo este ecosistema influye en su trayectoria.

2.  **Análisis de Patrones de Herramientas:**
    *   **Tarea:** Identificar *grupos* de herramientas que muestren patrones de adopción/interés *similares* a {all_kw} (ej., crecimiento/declive simultáneo, picos en los mismos períodos).  Identificar también herramientas con patrones *opuestos*.
    *   **Inferencias y Relevancia:**
        *   **Patrones Similares:** Podría indicar:
            *   Herramientas que abordan *necesidades similares* o complementarias.
            *   Herramientas que se ven afectadas por los *mismos factores externos*.
            *   Herramientas que forman parte de una *misma "ola"* de innovación gerencial.
        *   **Patrones Opuestos:** Podría indicar:
            *   Herramientas que compiten por la atención.
            *   Herramientas que representan *enfoques diferentes* o incluso *contradictorios*.
        *   **Aporte a la Investigación:**  La identificación de grupos de herramientas ayuda a comprender cómo las modas gerenciales se agrupan y evolucionan juntas, y cómo las tensiones entre innovación y ortodoxia podrían manifestarse a nivel de *conjuntos* de herramientas.

3.  **Análisis de Impacto Empresarial (Sinergias y Conflictos):**
* **Tarea:** Basado en el análisis de correlaciones y patrones, *inferir* posibles *sinergias* (combinaciones de herramientas que potencian mutuamente su efectividad) y *conflictos* (combinaciones que disminuyen la efectividad o son redundantes).
    *   **Inferencias y Relevancia:**
        *  **Sinergias:** Identificar si la combinación de herramientas produce resultados superiores.
        *   **Conflictos:** Identificar si la adopción conjunta de ciertas herramientas es *contraproducente* o *innecesaria*.
        *   **Adopción Secuencial:**  ¿Hay herramientas que *típicamente* se adoptan *antes* o *después* de {all_kw}? ¿Esto sugiere una secuencia lógica de implementación?
    *   **Aporte a la Investigación:**  Este análisis ayuda a comprender cómo las organizaciones *combinan* herramientas de gestión y cómo estas combinaciones pueden afectar su capacidad para abordar las antinomias organizacionales (ej., ¿una combinación de herramientas promueve la estabilidad *y* la innovación, o solo una de ellas?).

**Data Required:**
- Correlation matrix: {csv_corr_matrix}
- Regression analysis results: {csv_regression}
**Resultados Anteriores:**
**`## Conexiones con Análisis Previos`** (Solo si *no* es el primer prompt)
* Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

cross_relationship_prompt_2 = """### **Explore Cross-Source Relationships**

**Objective:** To analyze relationships between different data sources tracking {all_kw} management tool adoption and validate trend consistency for {dbs}.

**Tasks:**

1. **Source Correlation Analysis:**
    - Compare trends across all data sources:
        * General Publications (Google Books Ngram)
        * Specialized Publications (Crossref.org)
        * General Interest (Google Trends)
        * Industry Usability (Bain - Usabilidad)
        * Industry Satisfaction (Bain - Satisfacción)
    - Analyze correlation patterns between sources
    - Identify potential leading/lagging relationships
    - Compare relative trend strengths

2. **Pattern Validation:**
    - Analyze consistency of trends across sources
    - Identify source-specific patterns or anomalies
    - Compare trend directions and magnitudes
    - Detect systematic differences between sources

3. **Impact Analysis:**
    - Evaluate relationships between sources
    - Identify notable disconnects between perception and reality
    - Compare public interest versus industry metrics
    - Assess practical implications of observed patterns

**Data Required:**
- Cross-source correlation matrix: {csv_corr_matrix}
- Combined source trends data: {csv_combined_data}

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

trend_analysis_prompt_1 = """### **Investigate General Trend Patterns**

# Análisis de Patrones Generales de Tendencia para {all_kw}

Herramienta de Gestión: {all_kw}
Fuente de Datos: {dbs}

**Objetivo:** Analizar de forma general la tendencia que describe la herramienta de gestión {all_kw} en {dbs}, con el fin de tener una panorámica inicial de su comportamiento, identificar patrones amplios, y relacionar estos patrones con factores contextuales y con otras herramientas (si es posible). Este análisis servirá como insumo para análisis posteriores más detallados.

**Tareas Específicas, Cálculos e Interpretación Técnica:**

1.  **Análisis de Patrón General:**
    *   **Tarea:** Calcular los promedios de interés/uso de {all_kw} en {dbs} para diferentes períodos: 20 años, 15 años, 10 años, 5 años y 1 año.  A partir de estos promedios, *describir* el patrón general de adopción/declive (ej., "declive constante", "crecimiento inicial seguido de estabilización", etc.).  Relacionar este patrón con las *características generales* del ciclo de vida de la herramienta (sin entrar en detalles específicos de las etapas, eso se hará en el análisis temporal). Calcular las tendencias NADT y MAST.
    *   **Cálculos:**
        *   Promedio de interés/uso para los últimos 20, 15, 10, 5 y 1 año.
        *   NADT (20 años).
        *   MAST (20 años).
    *   **Interpretación Técnica:** Describir *objetivamente* el patrón general observado a partir de los promedios y las tendencias.  Ejemplo: "El interés promedio en {all_kw} ha disminuido constantemente a medida que se acorta el período de análisis, lo que sugiere una pérdida de popularidad sostenida.  Las tendencias NADT y MAST confirman este patrón, mostrando valores fuertemente negativos."

2.  **Análisis de Factores Contextuales:** (Esta sección se *omite* si no hay datos de correlación/regresión).
    *   **Tarea:** *Si hay datos de correlación o regresión disponibles*, analizar la *posible* influencia de factores externos (ej., ciclos económicos, avances tecnológicos, condiciones del mercado) en el interés/uso de {all_kw}.  *Si no hay datos de correlación/regresión, esta sección se omite*.
    *   **Cálculos:** (Dependerán de los datos disponibles).  Ejemplos:
        *   Coeficientes de correlación entre {all_kw} y variables contextuales.
        *   Resultados de análisis de regresión (coeficientes, R cuadrado, valores p).
    *   **Interpretación Técnica:** *Si hay datos*, describir las relaciones observadas (ej., "Se observa una correlación positiva y significativa entre el interés en {all_kw} y el crecimiento del PIB, lo que sugiere que...").  *Si no hay datos*, esta sección se omite.

3.  **Análisis de Categoría de Herramientas:** (Esta sección se *adapta* según la disponibilidad de datos).
    *   **Tarea:** *Si hay datos disponibles sobre otras herramientas*, analizar la relación de {all_kw} con su categoría de herramientas.  *Si no hay datos sobre otras herramientas, esta sección se simplifica o se omite*.
    *   **Cálculos/Análisis:** (Dependerán de los datos disponibles). Ejemplos:
        *   *Si hay datos de otras herramientas:*
            *   Agrupar {all_kw} con otras herramientas que muestren patrones similares (si los hay).
            *   Identificar factores comunes de éxito/fracaso (si es posible).
            *   Analizar relaciones de tiempo de adopción (si es posible).
            *   Calcular métricas específicas de la categoría (si existen y son relevantes).
        *   *Si no hay datos de otras herramientas:*
            *   Simplemente *identificar* la categoría general de {all_kw} (ej., "herramienta de planificación estratégica", "herramienta de gestión de la calidad", etc.).
            *  Omitir el resto.
    *   **Interpretación Técnica:**  Describir *cualitativamente* la relación de {all_kw} con su categoría (si es posible) y *cualquier* patrón observable en relación con otras herramientas (si hay datos).

**Datos Requeridos:**

*   Datos de series temporales para {all_kw} en {dbs} (20, 15, 10, 5 y 1 año).
*   Tendencias y medias para {all_kw} y, *si están disponibles*, para otras herramientas ({csv_means_trends}).
*   *Si están disponibles*: Resultados de análisis de correlación y regresión ({csv_corr_matrix}, {csv_regression}).  *Si no están disponibles, estas secciones se omiten*.

**Resultados Anteriores:**
**`## Conexiones con Análisis Previos`** (Solo si *no* es el primer prompt)
    *   Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

trend_analysis_prompt_2 = """### **Investigate Cross-Source Trend Patterns**

**Objective:** To analyze how different data sources reflect general patterns in {all_kw} management tool adoption across:
1. General Publications (Google Books Ngram)
2. Specialized Publications (Crossref.org)
3. General Interest (Google Trends)
4. Industry Usability (Bain - Usabilidad)
5. Industry Satisfaction (Bain - Satisfacción)
If they are in the list: {selected_sources}
Management Tool: {all_kw}
Data Sources: {selected_sources}

**Tasks:**

1. **Cross-Source Pattern Analysis:**
    - Compare adoption patterns across sources
    - Identify source-specific reporting biases
    - Analyze temporal alignment between sources
    - Calculate cross-source pattern correlations

2. **Trend Validation Analysis:**
    - Evaluate trend consistency across sources
    - Identify significant pattern divergences
    - Analyze source reliability patterns
    - Calculate trend validation metrics

3. **Source Relationship Analysis:**
    - Analyze lead-lag relationships
    - Identify predictive indicators
    - Evaluate source complementarity
    - Calculate source alignment scores

**Data Required:**
- Combined source trends: {csv_combined_data}
- Cross-source correlations: {csv_corr_matrix}

Note: Visualizations will be handled separately - focus on numerical and statistical analysis only.
"""

arima_analysis_prompt_1 = """### **Analyze ARIMA Model Performance**

# Análisis ARIMA - {all_kw} ({dbs})

Herramienta: {all_kw}
Fuente: {dbs}

**Objetivo:** Evaluar la capacidad del modelo ARIMA para *predecir* los patrones de adopción/interés de {all_kw} en {dbs}, *interpretar* las implicaciones de las predicciones del modelo para la *futura evolución* de la herramienta, y *relacionar* estas predicciones con las antinomias del ecosistema transorganizacional, el ciclo de vida de las modas gerenciales y las preguntas de investigación.

**Tareas Específicas e Inferencias:**

1.  **Evaluación del Rendimiento del Modelo:**
    *   **Tarea:** Interpretar las métricas de ajuste del modelo (RMSE, MAE, AIC, BIC) *en el contexto de la variabilidad inherente a los datos de tendencias de gestión*.  No hay valores "buenos" o "malos" absolutos; lo importante es la *comparación relativa* con otros modelos y la *magnitud* de los errores en relación con la escala de los datos (0-100).  Evaluar la precisión a diferentes horizontes temporales (corto, medio, largo plazo) y analizar los intervalos de confianza.
    *   **Inferencias y Relevancia:**
        *   **RMSE/MAE:**  ¿Qué tan grandes son los errores de predicción en promedio? ¿Son aceptables dado el contexto?
        *   **AIC/BIC:**  ¿El modelo está bien ajustado o es demasiado complejo?
        *   **Precisión a Diferentes Horizontes:**  ¿El modelo es más preciso a corto plazo que a largo plazo? Esto es *esperable*, pero es importante cuantificarlo.
        *   **Intervalos de Confianza:**  ¿Qué tan amplios son los intervalos de confianza?  Intervalos amplios indican *mayor incertidumbre* en las predicciones.
        *   **Aporte a la Investigación:** La evaluación del rendimiento del modelo determina la *fiabilidad* de las predicciones y establece los *límites* de lo que se puede inferir sobre el futuro de la herramienta.

2.  **Análisis de Parámetros:**
    *   **Tarea:** Interpretar los parámetros del modelo ARIMA (p, d, q) y los coeficientes de los términos AR y MA.  Determinar si los parámetros son *estadísticamente significativos*.
    *   **Inferencias y Relevancia:**
        *   **p (orden autorregresivo):** Indica cuántos períodos pasados influyen en el valor actual. Un valor alto de *p* sugiere una fuerte dependencia de los valores pasados.
        *   **d (grado de diferenciación):** Indica cuántas veces se necesita diferenciar la serie para hacerla estacionaria.  Un valor alto de *d* sugiere una tendencia fuerte (lineal, cuadrática, etc.).
        *   **q (orden de media móvil):** Indica cuántos errores pasados influyen en el valor actual.
        *   **Coeficientes AR y MA:**  Indican la *dirección* y *magnitud* de la influencia de los valores pasados y los errores pasados.
        *   **Significancia Estadística:**  Los parámetros no significativos podrían indicar que el modelo es *demasiado complejo* o que ciertos componentes no son relevantes.
        *   **Aporte a la Investigación:** La interpretación de los parámetros ayuda a comprender las *características intrínsecas* de la serie temporal de {all_kw} (ej., si es fuertemente dependiente del pasado, si tiene una tendencia fuerte, si es muy volátil).

3.  **Perspectivas del Modelo (Predicciones):**
    *   **Tarea:**  Analizar las *predicciones* del modelo ARIMA para {all_kw}.  ¿El modelo predice un crecimiento, un declive, una estabilización, fluctuaciones cíclicas, u otro patrón?  Comparar las predicciones con los patrones observados en el pasado.
    *   **Inferencias y Relevancia:**
        *   **Tendencia Predicha:**  ¿Hacia dónde se dirige la herramienta, según el modelo?
        *   **Patrones Predichos:**  ¿El modelo predice ciclos, estacionalidad u otros patrones regulares?
        *   **Relación con el Ciclo de Vida:**  ¿Las predicciones son consistentes con la etapa actual del ciclo de vida de la herramienta (inferida del análisis temporal)?  ¿El modelo sugiere una transición a una nueva etapa?
        *   **Relación con las Antinomias:**  ¿Las predicciones sugieren que la herramienta será capaz de *mitigar* las tensiones entre innovación y ortodoxia, o que *sucumbirá* a ellas?  Por ejemplo, una predicción de declive podría indicar que la herramienta no ha logrado un equilibrio entre estos dos polos.
        *   **Aporte a la Investigación:** Las predicciones del modelo (junto con su evaluación de fiabilidad) proporcionan una *base cuantitativa* para discutir las *posibles trayectorias futuras* de {all_kw} y su relación con las preguntas de investigación.  *Importante:*  Las predicciones deben presentarse como *escenarios probables*, no como certezas.

**Resultados Anteriores:**
**`## Conexiones con Análisis Previos`** (Solo si *no* es el primer prompt)
    *   Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

**Data Input:**
ARIMA Model Results: {arima_results}

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

arima_analysis_prompt_2 = """### **Analyze Cross-Source ARIMA Model Performance**

**Objective:** To evaluate and compare ARIMA model forecasting performance across different data sources for {selected_keyword}:
1. General Publications (Google Books Ngram)
2. Specialized Publications (Crossref.org)
3. General Interest (Google Trends)
4. Industry Usability (Bain - Usabilidad)
5. Industry Satisfaction (Bain - Satisfacción)
If they are in the list: {selected_sources}
Management Tool: {selected_keyword}
Data Source: {selected_sources}

**Tasks:**

1. **Cross-Source Comparison:**
    - Compare accuracy metrics across sources:
        * Root Mean Square Error (RMSE)
        * Mean Absolute Error (MAE)
        * Error Cuadrático Medio (ECM)
    - Analyze prediction consistency between sources
    - Evaluate relative forecast reliability
    - Compare confidence intervals

2. **Source-Specific Analysis:**
    - Compare ARIMA specifications across sources
    - Analyze differences in model performance
    - Evaluate source-specific prediction patterns
    - Identify most reliable data sources

3. **Integrated Analysis:**
    - Identify convergent predictions across sources
    - Analyze divergent forecasts and potential causes
    - Evaluate overall trend consistency
    - Assess implications for tool adoption trends

**Data Input:**
Cross-source ARIMA Results: {arima_results}

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

seasonal_analysis_prompt_1 = """### **Interpret Seasonal Patterns**

# Análisis Estacional - {all_kw} ({dbs})

Herramienta: {all_kw}
Fuente: {dbs}

**Objetivo:** Identificar y analizar patrones estacionales en la adopción/interés de {all_kw} en {dbs}, *interpretar las causas* de estos patrones y *evaluar sus implicaciones* para la gestión y la investigación sobre modas gerenciales.

**Tareas Específicas, Cálculos e Interpretación Técnica:**

1.  **Identificación de Patrones Estacionales:**
    *   **Tarea:** Utilizar la descomposición estacional (si es aplicable a la fuente de datos y al tipo de datos) para identificar patrones estacionales *consistentes* en la serie temporal de {all_kw}. Determinar los *meses/trimestres* de mayor y menor interés/uso.  Si la descomposición estacional *no* es aplicable (ej., porque la fuente de datos no proporciona datos con la frecuencia necesaria), utilizar *otros métodos* para detectar posibles patrones estacionales. Estos métodos alternativos podrían incluir:
        *   **Análisis visual:** Examinar la serie temporal en busca de patrones repetitivos a lo largo del año.
        *   **Comparación de medias mensuales/trimestrales:** Calcular el promedio de interés/uso para cada mes/trimestre y comparar los valores para identificar posibles picos y valles.
        *   **Autocorrelación:** Calcular la función de autocorrelación para detectar posibles correlaciones entre valores separados por 12 meses (o el período estacional relevante).
    *  **Cálculos:**
        *   *Si se utiliza descomposición estacional:*
            *   Componente estacional de la serie temporal.
            *   Amplitud de la estacionalidad (ej., diferencia entre el máximo y el mínimo del componente estacional, o desviación estándar del componente estacional).
        *   *Si no se utiliza descomposición estacional:*
            *   Medias mensuales/trimestrales de interés/uso.
            *   *Opcional:* Función de autocorrelación.
        *   *En ambos casos:*
            *   Identificación de los meses/trimestres de mayor y menor interés/uso.
        *   *Opcional:* Pruebas estadísticas para la presencia de estacionalidad (ej., prueba de Kruskal-Wallis, ANOVA estacional). *Nota:* Estas pruebas deben usarse con precaución si los datos no cumplen los supuestos de las pruebas.
    *   **Interpretación Técnica:** Describir *cualitativamente* y *cuantitativamente* el patrón estacional (si existe). Ejemplo: "El análisis revela un patrón estacional [claro/débil/inexistente]. [Si hay un patrón:] Los picos de interés se observan consistentemente en los meses de [meses], mientras que los valles se presentan en los meses de [meses]. La amplitud de la estacionalidad es de [valor] unidades, lo que indica una influencia estacional [fuerte/moderada/débil]." Si *no* hay un patrón claro, indicarlo explícitamente: "No se identifica un patrón estacional consistente en los datos de {dbs} para {all_kw}."

2.  **Interpretación de las Causas:**
    *   **Tarea:** *Inferir* las *posibles causas* de los patrones estacionales observados (o la ausencia de ellos). Considerar:
        *   **Ciclos Empresariales:** Planificación estratégica anual, revisiones de presupuesto, cierres de año fiscal, lanzamientos de productos/servicios, etc.
        *   **Ciclos Académicos:** Publicación de artículos, conferencias, inicio/fin de semestres/trimestres, etc. (especialmente relevante para Crossref y, en menor medida, para Google Books).
        *   **Eventos Estacionales:** Vacaciones, feriados, eventos climáticos, etc. (podrían influir en Google Trends).
        *   **Factores Específicos de la Industria:** Si {all_kw} está asociada a una industria en particular, considerar los ciclos específicos de esa industria (ej., temporadas de siembra/cosecha en agricultura, temporadas de ventas en comercio minorista, etc.).
    *   **Inferencias y Relevancia:**
        *   **Causas Probables:** ¿Cuáles son las explicaciones *más plausibles* para los patrones estacionales (o la ausencia de ellos)?  *No* afirmar causalidad definitiva, sino *sugerir* posibles explicaciones basadas en el conocimiento del contexto.
        *   **Relación con las Antinomias:** ¿Los patrones estacionales reflejan una tensión entre la necesidad de planificación (estabilidad) y la necesidad de adaptación (cambio)? Por ejemplo, ¿los picos de interés coinciden con períodos en los que las organizaciones se centran en la planificación a largo plazo, o con períodos en los que necesitan adaptarse a cambios estacionales en la demanda?
        *   **Aporte a la Investigación:** La interpretación de las causas ayuda a comprender *por qué* la adopción/interés de {all_kw} varía a lo largo del año y cómo estos factores se relacionan con el contexto empresarial, académico y social.

3.  **Implicaciones Prácticas:**
    *   **Tarea:**  Discutir las *implicaciones prácticas* de los patrones estacionales para:
        *   **Organizaciones:**  ¿Cómo pueden las organizaciones *anticipar* y *aprovechar* los patrones estacionales? (ej., planificar la implementación de la herramienta en los períodos de mayor interés, evitar la competencia en los picos, etc.).
        *   **Consultores:**  ¿Cómo pueden los consultores *utilizar* esta información para asesorar a sus clientes? (ej., recomendar la herramienta en ciertos momentos del año, ajustar las estrategias de marketing, etc.).
        *   **Investigadores:** ¿Qué *nuevas preguntas* surgen a partir de estos patrones estacionales?
    *   **Inferencias y Relevancia:**
        *   **Planificación Estratégica:**  La estacionalidad puede informar la planificación estratégica relacionada con la adopción/uso de {all_kw}.
        *   **Marketing y Comunicación:**  Los patrones estacionales pueden guiar las estrategias de marketing y comunicación.
        *   **Investigación Futura:**  Los patrones estacionales pueden generar nuevas preguntas de investigación sobre los factores cíclicos que influyen en las modas gerenciales.
        *  **Aporte a la Investigación:** Esta discución conecta los hallazgos con el mundo real de las organizaciones, consultores e investigadores.

**Datos Requeridos:**
*   Datos de series temporales (idealmente, descompuestos si la fuente de datos lo permite y la herramienta lo soporta). Si la fuente de datos *no* permite la descomposición, se utilizarán los datos originales.
*   Cualquier información contextual relevante sobre ciclos empresariales, académicos, de la industria, etc.
*   Seasonal decomposition results: {csv_seasonal}


**Resultados Anteriores:**
**`## Conexiones con Análisis Previos`** (Solo si *no* es el primer prompt)
    *   Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

seasonal_analysis_prompt_2 = """### **Interpret Cross-Source Seasonal Patterns**

**Objective:** To analyze and compare seasonal patterns across different data sources: {selected_sources} tracking {selected_keyword} adoption:
- General Publications (Google Books Ngram)
- Specialized Publications (Crossref.org)
- General Interest (Google Trends)
- Industry Usability (Bain - Usabilidad)
- Industry Satisfaction (Bain - Satisfacción)
If they are in the list: {selected_sources}
Management Tool: {selected_keyword}
Data Source: {selected_sources}

**Tasks:**

1. **Cross-Source Pattern Analysis:**
    - Compare seasonal patterns between sources
    - Identify source-specific characteristics
    - Analyze pattern alignment
    - Evaluate pattern reliability

2. **Source Integration Analysis:**
    - Analyze correlation between sources
    - Identify complementary patterns
    - Evaluate conflicting signals
    - Assess overall trend consistency

3. **Holistic Assessment:**
    - Synthesize insights across sources
    - Evaluate pattern consistency
    - Analyze practical implications
    - Consider implementation timing

**Data Required:**
- Seasonal decomposition results: {csv_seasonal}
- Cross-source correlation matrix: {csv_correlation}

Note: 
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

prompt_6_single_analysis = """### **Cyclical Pattern Analysis for Management Tools**

# Análisis Cíclico - {all_kw} ({dbs})

Herramienta: {all_kw}
Fuente: {dbs}

**Objetivo:** Identificar y analizar patrones cíclicos *no estacionales* en la adopción/interés de {all_kw} en {dbs}, *interpretar las causas* de estos ciclos y *evaluar sus implicaciones* para la gestión y la investigación sobre modas gerenciales.

**Tareas Específicas e Inferencias:**

1.  **Identificación de Patrones Cíclicos:**
    *   **Tarea:** Utilizar el análisis de Fourier (u otras técnicas de análisis espectral) para identificar *frecuencias dominantes* en la serie temporal de {all_kw}. Convertir estas frecuencias en *períodos* (ej., un ciclo de 4 años).  Evaluar la *fuerza* de cada ciclo (amplitud).
    *   **Inferencias y Relevancia:**
        *   **Existencia de Ciclos:**  ¿Hay ciclos *claros y significativos*? Si no los hay, esto sugiere que los factores cíclicos *no estacionales* no son un impulsor importante.
        *   **Períodos Dominantes:**  ¿Cuáles son las duraciones de los ciclos más importantes?
        *   **Fuerza de los Ciclos:**  ¿Qué tan fuertes son los ciclos? Ciclos fuertes sugieren una influencia cíclica importante.
        *   **Aporte a la Investigación:** La identificación de ciclos ayuda a comprender los *patrones de fluctuación a largo plazo* que no están relacionados con la estacionalidad.

2.  **Interpretación de las Causas:**
    *   **Tarea:** *Inferir* las *posibles causas* de los patrones cíclicos observados. Considerar:
        *   **Ciclos Económicos:**  Recesiones, expansiones, etc.
        *   **Ciclos Tecnológicos:**  Aparición de nuevas tecnologías que complementan o sustituyen a {all_kw}.
        *   **Ciclos de la Industria:**  Ciclos específicos de la industria a la que pertenece {all_kw}.
        *   **Ciclos de "Moda Gerencial":**  Ciclos inherentes a la difusión y adopción de innovaciones gerenciales (independientes de factores externos).
        * **Ciclos Políticos:** Los cambios de gobierno, políticas públicas, etc.

    *   **Inferencias y Relevancia:**
        *   **Causas Probables:**  ¿Cuáles son las explicaciones *más plausibles* para los ciclos observados?
        *   **Relación con las Antinomias:**  ¿Los ciclos reflejan una tensión entre la necesidad de estabilidad y la necesidad de cambio? ¿Podrían los ciclos estar relacionados con períodos en los que las organizaciones son más propensas a adoptar nuevas herramientas (en tiempos de crisis o cambio) o a aferrarse a las existentes (en tiempos de estabilidad)?
        *   **Aporte a la Investigación:**  La interpretación de las causas ayuda a comprender *por qué* la adopción/interés de {all_kw} fluctúa a largo plazo y cómo estos factores se relacionan con el contexto económico, tecnológico y empresarial.

3.  **Implicaciones Prácticas:**

    *   **Tarea:**  Discutir las *implicaciones prácticas* de los patrones cíclicos para:
        *   **Organizaciones:**  ¿Cómo pueden las organizaciones *anticipar* y *adaptarse* a los ciclos? (ej., ser más cautelosas al adoptar la herramienta durante un posible pico del ciclo, prepararse para posibles declives, etc.).
        *   **Consultores:**  ¿Cómo pueden los consultores *utilizar* esta información para asesorar a sus clientes? (ej., recomendar la herramienta en ciertos momentos del ciclo, advertir sobre los riesgos de adopción en momentos inoportunos, etc.).
        *   **Investigadores:**  ¿Qué *nuevas preguntas* surgen a partir de estos patrones cíclicos?

    *   **Inferencias y Relevancia:**
        *   **Planificación Estratégica:**  Los ciclos pueden informar la planificación estratégica a largo plazo.
        *   **Gestión del Riesgo:**  La comprensión de los ciclos puede ayudar a las organizaciones a gestionar el riesgo asociado a la adopción de modas gerenciales.
        *   **Investigación Futura:**  Los patrones cíclicos pueden generar nuevas preguntas de investigación sobre los factores que impulsan los ciclos de las modas gerenciales.
        *  **Aporte a la Investigación:** Conecta los patrones con el mundo real.

**Data Input:** {csv_fourier}
*   Datos de series temporales.
*   Resultados del análisis de Fourier (u otras técnicas de análisis espectral).
*	Cualquier información contextual relevante sobre ciclos económicos, tecnológicos, etc.

**Resultados Anteriores:**
**`## Conexiones con Análisis Previos`** (Solo si *no* es el primer prompt)
    *   Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

Notes:
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

prompt_6_correlation = """### **Cross-Source Pattern Analysis for Management Tools**

**Objective:** Analyze and correlate cyclical patterns of {selected_keyword} across multiple data sources: {selected_sources} to validate trends.

**Analysis Requirements:**

1. **Multi-Source Pattern Comparison:**
   - Compare cycle strengths across:
     * General publications
     * Specialized publications
     * General interest metrics
     * Industry usability data
     * User satisfaction ratings
If they are in the list: {selected_sources}
Management Tool: {selected_keyword}
Data Source: {selected_sources}

2. **Correlation Analysis:**
   - Identify leading and lagging relationships between sources
   - Evaluate pattern synchronization across metrics
   - Quantify correlation strengths between different data sources

3. **Validation Framework:**
   - Assess pattern consistency across sources
   - Identify discrepancies and potential causes
   - Evaluate reliability of different data sources

**Data Input:** {csv_fourier}
**Raw Data:** {csv_combined_data}

Notes:
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""


prompt_conclusions_standalone = """## Synthesize Findings and Draw Conclusions - {all_kw} Analysis

# Síntesis de Hallazgos y Conclusiones - Análisis de [{all_kw}] en {dbs}

Herramienta: {all_kw}
Fuente: {dbs}

**Objetivo:** Sintetizar los hallazgos de los *diferentes análisis estadísticos* realizados sobre la herramienta {all_kw} en la fuente de datos {dbs}, extraer conclusiones *específicas* sobre su trayectoria, y conectar estos hallazgos con las preguntas de investigación y las implicaciones para la gestión.  Este prompt consolida los resultados *antes* de pasar a la síntesis general entre herramientas.

**Tareas:**

1.  **Revisión de Resultados Previos:** Revisar *cuidadosamente* los resultados de *todos* los prompts anteriores relacionados con {all_kw} en {dbs}:
    *   Análisis Temporal.
    *   Análisis de Patrones Generales de Tendencia.
    *   Análisis ARIMA.
    *   Análisis Estacional.
    *   Análisis Cíclico.
    *   Análisis de Relaciones Cruzadas (si aplica).

2.  **Síntesis de Hallazgos Clave:**  Elaborar una síntesis *concisa* pero *completa* de los hallazgos *más importantes* de cada análisis.  *No* repetir todos los detalles, sino *resaltar* los puntos *cruciales* que contribuyen a la comprensión de la trayectoria de {all_kw}.  Ejemplos:
    *   "El análisis temporal revela una tendencia general a la baja, con un declive más pronunciado en los primeros años y una estabilización posterior."
    *   "El modelo ARIMA predice una continuación de esta estabilización a la baja."
    *   "Se identifica un patrón estacional débil, con picos menores en [meses]."
    *   "El análisis cíclico sugiere la posible presencia de un ciclo de N años, aunque su fuerza es moderada."
    *  "No se identifican correlaciones estadísticamente significativas de factores externos con la herramienta" (si aplica)
   *  "La herramienta se agrupa en la categoría de Herramientas de X, sin presentar correlaciones fuertes con otras herramientas"

3.  **Análisis Integrado:** *Integrar* los hallazgos de los diferentes análisis para construir una *narrativa coherente* sobre la trayectoria de {all_kw} en {dbs}. Responder a preguntas como:
    *   ¿Cuál es la *tendencia general*?
    *   ¿En qué *etapa del ciclo de vida* parece encontrarse la herramienta?
    *   ¿Qué *factores* parecen estar impulsando la trayectoria de la herramienta (estacionalidad, ciclos, factores externos, relaciones con otras herramientas)?
    *   ¿Hay evidencia de *adaptación* o *evolución* de la herramienta?
    *   ¿Las *predicciones* del modelo ARIMA son consistentes con los patrones observados?
    * ¿Cómo se relacionan los patrones estacionales y cíclicos con los ciclos empresariales, académicos, o de la industria?
    * ¿Existen factores comunes de éxito o fracaso en esta categoría de herramientas que sean relevantes para la herramienta analizada?

4.  **Implicaciones (Integradas):**  Discutir las implicaciones de los hallazgos *integrados* para:
    *   **Investigadores:** ¿Cómo contribuyen estos hallazgos a la investigación sobre modas gerenciales? ¿Qué nuevas preguntas surgen?
    *   **Consultores:** ¿Qué consejos se pueden extraer para la recomendación y el uso de {all_kw}?
    *   **Organizaciones:** ¿Qué deben considerar las organizaciones al evaluar la adopción o el uso continuo de {all_kw}?
     *(Utilizar el formato de implicaciones integradas que definimos anteriormente, dirigiéndose a cada audiencia dentro del flujo natural del texto, sin subsecciones separadas).*

5. **Limitaciones Especificas:** Incluir las limitaciones de la fuente de datos, y otras.

**Data Integration:**
    # Temporal Trends
    {temporal_trends}
    # Cross-Tool Relationships
    {tool_relationships}
    # Industry-Specific Patterns
    {industry_patterns}
    # ARIMA Predictions
    {arima_predictions}
    # Seasonal Analysis
    {seasonal_analysis}
    # Cyclical Patterns
    {cyclical_patterns}

    **Datos Requeridos:**
*   Resultados de *todos* los prompts anteriores para {all_kw} en {dbs}.
**Resultados Anteriores:**
## Conexiones con Análisis Previos`**
    *   Referencia y discusión *explícita* de cómo los resultados de este prompt se optimizan o mejoran con los resultados de los prompts anteriores, identificando convergencias, divergencias, o nuevas perspectivas.

**Key Considerations:**
- Focus on practical implications for organizations
- Emphasize evidence-based conclusions
- Address both strategic and operational aspects
- Consider industry-specific contexts if any

Notes:
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

prompt_conclusions_comparative = """## Synthesize Findings and Draw Conclusions - Multi-Source {all_kw} Analysis

**Objective:** To analyze correlations and patterns across selected data sources measuring {all_kw} adoption and impact.

**Data Sources Analyzed:**
{selected_sources}
If they are in the list: {selected_sources}
Management Tool: {all_kw}
Data Source: {selected_sources}

**Tasks:**

1. **Cross-Source Pattern Analysis:**
    - Compare trends across the selected data sources

2. **Correlation Analysis:**
    - Evaluate relationships between available metrics

3. **Time-Lag Analysis:**
    - Identify lead/lag relationships between different metrics
    - Analyze how different measures influence each other over time
    - Evaluate predictive relationships between sources

4. **Synthesis and Recommendations:**
    - Identify reliable indicators for tool success
    - Suggest optimal timing for tool adoption
    - Provide framework for evaluating new management tools

**Data Integration:**
    # Temporal Trends
    {temporal_trends}
    # Cross-Tool Relationships
    {tool_relationships}
    # ARIMA Predictions
    {arima_predictions}
    # Seasonal Analysis
    {seasonal_analysis}
    # Cyclical Patterns
    {cyclical_patterns}

**Key Considerations:**
- Focus on relationships between selected data sources
- Identify leading indicators of tool success
- Evaluate reliability of different data sources
- Consider time delays between publication, interest, and adoption

Notes:
- Since Charts and Visualizations will be included at the end of the report, please don't mention them here.
- Avoid to give Recomendations for better or aditional analysis.
- Not mention about more data or data features extra you would like to have to do a better analisys. Just use what you have.
- Avoid a section about Analisys Limitations.
"""

prompt_sp = """
Translate the following Markdown text to Spanish, adhering to these guidelines:
1. Use formal academic Spanish suitable for business reports
2. Maintain technical and management terminology appropriate for enterprise contexts
3. Keep these specific terms unchanged: {all_kws}
4. Preserve all numerical values, dates, and data references
5. Maintain all Markdown formatting
6. Do not include any explanatory comments or suggestions
7. Provide only the direct translation without additional markup or annotations
8. Ensure consistent terminology throughout the translation
9. Maintain the hierarchical structure of headings and subheadings
10. Preserve all placeholder variables such as {selected_sources}
11. Do *not* include comments like: Okay, here is the Spanish translation following all guidelines
12. Do not include blocks of markdown code.

Text to translate:
"""

prompt_abstract = """
# IDENTITY and PURPOSE
You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.
Take a deep breath and think step by step about how to best accomplish this goal using the following steps.

# OUTPUT SECTIONS
- Combine all of your understanding of the content into a single, 20-word sentence in a section called #SUMMARY
- Output the 10 most important points of the content as a list with no more than 15 words per point into a section called ###1. Main Points
- Output a list of the 5 best takeaways from the content in a section called ###2. Key Points

# OUTPUT INSTRUCTIONS
- First section name is also the same Title #SUMMARY
- Create the output using the formatting above.
- You only output human readable Markdown.
- Output numbered lists, not bullets.
- Do not output warnings or notes—just the requested sections.
- Do not repeat items in the output sections.
- Do not start items with the same opening words.
- Do not include blocks of markdown code.

# INPUT

INPUT:
"""