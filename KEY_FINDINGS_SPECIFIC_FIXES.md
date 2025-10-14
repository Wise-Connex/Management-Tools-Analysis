# Key Findings Specific Fixes - Targeted Solutions

## 🎯 FOCUSED DIAGNOSIS

**Working Components** ✅ (DO NOT MODIFY):

- PCA Analysis section that generates graphs
- Data aggregation pipeline
- Statistical analysis
- Trends and patterns detection
- Modal component display

**Issue Location** 🎯:

- **Key Findings AI analysis** only (the text report generation)
- **Data source mapping** for Key Findings specifically

---

## 🔍 ROOT CAUSE FOR KEY FINDINGS ONLY

The Key Findings AI is getting the wrong data because:

1. **Data Source Mapping Issue**: Key Findings requests "Alianzas y Capital de Riesgo" but gets "GT_Talento_y_Compromiso_9324.csv"
2. **Single Source for AI**: Only 1 data source instead of 5 for the AI analysis
3. **Low Variance for AI**: 1% variance explained makes meaningful AI analysis impossible

**The PCA graph works because it uses different data pipeline!**

---

## 🛠️ TARGETED FIXES (Key Findings Only)

### Fix 1: Data Source Mapping for Key Findings

**File**: `dashboard_app/key_findings/data_aggregator.py`
**Method**: `_create_combined_dataset`

**Current Issue**:

```python
# This mapping logic is wrong for Key Findings
for tool_list in tool_file_dic.values():
    for i, source_key in enumerate([1, 2, 3, 4, 5]):
        if i < len(tool_list) and i < len(tool_list[1]):
            dbase_options[source_key] = tool_list[i]
```

**Targeted Fix**:

```python
def _create_combined_dataset_key_findings(self, datasets_norm: Dict[int, pd.DataFrame],
                                        sl_sc: List[int], tool_name: str) -> pd.DataFrame:
    """Create combined dataset specifically for Key Findings with correct tool mapping."""

    # Use proper tool-to-file mapping for Key Findings
    from tools import get_tool_files_for_keyword

    try:
        # Get the correct files for this specific tool
        tool_files = get_tool_files_for_keyword(tool_name)
        logging.info(f"🔍 Key Findings - Tool '{tool_name}' mapped to files: {tool_files}")

        # Create mapping from source IDs to correct file names
        source_mapping = {}
        for i, source_id in enumerate(sl_sc):
            if i < len(tool_files):
                source_mapping[source_id] = tool_files[i]

        # Create combined dataset with correct mapping
        combined_data = pd.DataFrame()
        all_dates = set()

        # Get all unique dates
        for source_data in datasets_norm.values():
            if source_data is not None and not source_data.empty:
                all_dates.update(source_data.index)

        if not all_dates:
            return pd.DataFrame()

        all_dates = sorted(list(all_dates))
        combined_data = pd.DataFrame(index=all_dates)

        # Add data with correct source names
        for source_id in sl_sc:
            if source_id in datasets_norm and source_id in source_mapping:
                source_name = source_mapping[source_id]
                source_data = datasets_norm[source_id]

                aligned_data = source_data.reindex(all_dates)
                combined_data[source_name] = aligned_data.iloc[:, 0] if len(aligned_data.columns) > 0 else aligned_data

        return combined_data.dropna(how='all')

    except Exception as e:
        logging.error(f"❌ Key Findings data mapping failed: {e}")
        # Fallback to current method
        return self._create_combined_dataset(datasets_norm, sl_sc)
```

### Fix 2: Key Findings Data Validation

**File**: `dashboard_app/key_findings/data_aggregator.py`
**Method**: `collect_analysis_data`

**Add validation before PCA**:

```python
def collect_analysis_data(self, tool_name: str, selected_sources: List[Any],
                        language: str = 'es', source_display_names: List[str] = None) -> Dict[str, Any]:
    # ... existing code ...

    # Create combined dataset with Key Findings specific method
    combined_dataset = self._create_combined_dataset_key_findings(datasets_norm, sl_sc, tool_name)

    # Key Findings specific validation
    if len(combined_dataset.columns) < 2:
        logging.warning(f"⚠️ Key Findings: Insufficient data sources for '{tool_name}'. Got {len(combined_dataset.columns)}, expected 2+")
        return {
            'error': f"Key Findings requires at least 2 data sources for meaningful analysis. Tool '{tool_name}' has {len(combined_dataset.columns)} source(s): {list(combined_dataset.columns)}",
            'tool_name': tool_name,
            'selected_sources': selected_sources,
            'language': language,
            'data_points_analyzed': len(combined_dataset),
            'sources_count': len(combined_dataset.columns),
            'available_sources': list(combined_dataset.columns),
            'recommendation': "Verify that the correct data files are mapped to this tool in the Key Findings system"
        }

    # Validate data content matches tool name
    first_source = combined_dataset.columns[0] if combined_dataset.columns else ""
    if self._is_data_mismatch(tool_name, first_source):
        logging.warning(f"⚠️ Key Findings: Data mismatch detected for tool '{tool_name}' -> data '{first_source}'")
        # Continue but add warning to analysis

    # ... continue with existing PCA analysis ...
```

### Fix 3: Enhanced AI Prompt for Data Issues

**File**: `dashboard_app/key_findings/prompt_engineer.py`
**Method**: `_build_pca_section`

**Add context-aware prompting**:

```python
def _build_pca_section(self, pca_insights: Dict[str, Any]) -> str:
    """Build PCA emphasis section with enhanced context for Key Findings."""

    if not pca_insights or pca_insights.get('error'):
        return ""

    components = pca_insights.get('dominant_patterns', [])
    variance_explained = pca_insights.get('total_variance_explained', 0)
    tool_name = pca_insights.get('tool_name', 'Unknown Tool')

    # Check for data quality issues
    sources_count = len(components[0].get('loadings', {})) if components else 0

    if self.language == 'es':
        section = f"""
### ANÁLISIS DE COMPONENTES PRINCIPALES (PCA) - NARRATIVA UNIFICADA

**Datos PCA Adjuntos:**
- Herramienta de Gestión Analizada: {tool_name}
- Varianza Total Explicada: {variance_explained:.1f}%
- Componentes Principales Identificados: {len(components)}
- Fuentes de Datos Disponibles: {sources_count}

"""

        # Add specific guidance based on data quality
        if variance_explained < 5 or sources_count < 2:
            section += f"""
**⚠️ NOTA IMPORTANTE: CALIDAD DE DATOS LIMITADA**

El análisis actual muestra limitaciones significativas:
- Varianza explicada muy baja ({variance_explained:.1f}%)
- {sources_count} fuente(s) de datos disponible(s)

**Instrucciones Específicas para este Escenario:**
1. **Enfócate en identificar problemas de datos** más que patrones
2. **Sugiere mejoras específicas** para la calidad de datos
3. **Recomienda fuentes adicionales** que podrían enriquecer el análisis
4. **Proporciona insights estratégicos** basados en las limitaciones actuales
5. **Sé honesto sobre las limitaciones** pero proporciona valor ejecutivo

**Ejemplo de Análisis Esperado:**
"El análisis PCA actual está limitado por {sources_count} fuente(s) de datos, explicando solo el {variance_explained:.1f}% de la varianza. Esto sugiere la necesidad de incorporar fuentes adicionales como [sugerir fuentes específicas] para obtener una visión más completa. Mientras tanto, los datos disponibles indican [extraer cualquier insight posible]..."

"""

        # Continue with regular PCA instructions
        section += """
**INSTRUCCIONES GENERALES PARA ANÁLISIS PCA:**

Proporciona una sola narrativa unificada que fusione insights desde una perspectiva [estratégica empresarial] con una perspectiva [académica/organizacional].

Tu análisis debe enfocarse en la historia central que los datos cuentan, especialmente las relaciones clave y tensiones entre factores.

Asegúrate de fundamentar todas las conclusiones incorporando datos numéricos específicos de las gráficas, tales como cargas de componentes y el porcentaje de varianza explicada.

**Patrones Dominantes Identificados:**
"""
```

### Fix 4: Tool Name Validation

**File**: `dashboard_app/key_findings/data_aggregator.py`

**Add method to detect data mismatches**:

```python
def _is_data_mismatch(self, tool_name: str, data_source_name: str) -> bool:
    """Check if the loaded data matches the requested tool."""

    # Common mismatch patterns
    tool_keywords = {
        'Capital': ['capital', 'inversión', 'financiamiento', 'riesgo'],
        'Alianzas': ['alianza', 'sociedad', 'colaboración', 'partnership'],
        'Talento': ['talento', 'compromiso', 'empleados', 'rrhh'],
        'Calidad': ['calidad', 'mejora', 'excelencia', 'six sigma'],
        'Procesos': ['proceso', 'reingeniería', 'optimización', 'flujo']
    }

    # Check if tool name keywords don't match data source name
    for category, keywords in tool_keywords.items():
        if category.lower() in tool_name.lower():
            # Tool belongs to this category, check if data matches
            if not any(keyword in data_source_name.lower() for keyword in keywords):
                return True

    return False
```

---

## 🎯 IMPLEMENTATION PLAN (Key Findings Only)

### Step 1: Fix Data Mapping (1 day)

1. Create `_create_combined_dataset_key_findings` method
2. Implement proper tool-to-file mapping
3. Test with "Alianzas y Capital de Riesgo"

### Step 2: Add Validation (0.5 day)

1. Add data source count validation
2. Implement mismatch detection
3. Add helpful error messages

### Step 3: Enhance AI Prompt (0.5 day)

1. Add context-aware prompting
2. Provide specific guidance for low-variance scenarios
3. Maintain existing functionality for good data

### Step 4: Testing (0.5 day)

1. Test with various tools
2. Verify PCA graphs still work
3. Confirm Key Findings reports improve

---

## ✅ WHAT WILL NOT CHANGE

**Working Components** (Leave untouched):

- PCA graph generation
- Statistical analysis methods
- Trends detection
- Modal component
- Database operations
- Data aggregation for other parts

**Only Modified**:

- Key Findings data mapping
- Key Findings validation
- Key Findings AI prompting

---

## 🎯 EXPECTED OUTCOME

After these targeted fixes:

1. **Correct Data Loading**: Key Findings will load the right data for each tool
2. **Multiple Sources**: 4-5 data sources instead of 1
3. **Meaningful Variance**: 60-80%+ variance explained
4. **Rich AI Analysis**: Deep insights instead of basic observations
5. **Preserved Functionality**: PCA graphs and other features remain unchanged

The Key Findings should transform from basic data quality warnings to sophisticated strategic insights while preserving all existing functionality.
