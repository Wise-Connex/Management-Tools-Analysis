"""
Comprehensive fix for Docker translation issue.

The problem is that when language is switched to English, the translated source names
don't match the column names in the dataframe, causing errors when trying to access data.

This fix ensures that:
1. Column names in dataframes always use the original database names
2. A mapping is maintained between translated display names and original column names
3. All data access uses the original column names, even when displaying translated names
"""

def create_translation_mapping(selected_source_ids, dbase_options, language='es'):
    """
    Create a mapping between translated display names and original database column names.
    
    Args:
        selected_source_ids: List of source IDs
        dbase_options: Mapping of source IDs to database names
        language: Current language ('es' or 'en')
        
    Returns:
        Dictionary mapping translated names to original column names
    """
    from translations import translate_source_name
    
    translation_mapping = {}
    
    for source_id in selected_source_ids:
        original_name = dbase_options.get(source_id, "")
        translated_name = translate_source_name(original_name, language)
        translation_mapping[translated_name] = original_name
    
    return translation_mapping


def create_combined_dataset2_with_translation_fix(datasets_norm, selected_sources, dbase_options, language='es'):
    """
    Enhanced version of create_combined_dataset2 that handles translation properly.
    
    Args:
        datasets_norm: Dictionary of normalized datasets by source ID
        selected_sources: List of selected source IDs
        dbase_options: Mapping of source IDs to database names
        language: Current language ('es' or 'en')
        
    Returns:
        Tuple of (combined_dataset, translation_mapping)
    """
    import pandas as pd
    
    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)

    # Sort dates
    all_dates = sorted(list(all_dates))

    # Create DataFrame with all dates
    combined_dataset = pd.DataFrame(index=all_dates)

    # Add data from each source using ORIGINAL database names as column names
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            source_data = datasets_norm[source].reindex(all_dates)
            # Use the original database name as the column name
            combined_dataset[source_name] = source_data.iloc[:, 0]

    # Create translation mapping
    translation_mapping = create_translation_mapping(selected_sources, dbase_options, language)
    
    return combined_dataset, translation_mapping


def fix_create_temporal_2d_figure_with_translation(data, sources, language='es', start_date=None, end_date=None):
    """
    Enhanced version of create_temporal_2d_figure that handles translation properly.
    
    Args:
        data: DataFrame with data (using original column names)
        sources: List of translated source names for display
        language: Current language
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Plotly figure
    """
    # This is a placeholder - the actual implementation would need to be integrated
    # into the app.py file
    pass


def fix_regression_analysis_with_translation(data, sources, language='es'):
    """
    Enhanced regression analysis that handles translation properly.
    
    Args:
        data: DataFrame with data (using original column names)
        sources: List of translated source names for display
        language: Current language
        
    Returns:
        Enhanced regression results
    """
    # This is a placeholder - the actual implementation would need to be integrated
    # into the app.py file
    pass


# Integration instructions:
"""
To integrate this fix into the app.py file:

1. Replace the create_combined_dataset2 function with create_combined_dataset2_with_translation_fix
2. Update all callbacks that use the combined dataset to use the translation mapping
3. In particular, update the following callbacks:
   - update_main_content
   - update_temporal_2d_analysis
   - update_regression_analysis
   - update_seasonal_analysis
   - update_fourier_analysis
   - create_correlation_heatmap

4. When accessing data columns, use the translation mapping to convert translated names back to original names

Example implementation in update_main_content:
```python
# Replace this:
combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

# With this:
combined_dataset, translation_mapping = create_combined_dataset2_with_translation_fix(
    datasets_norm=datasets_norm, 
    selected_sources=sl_sc, 
    dbase_options=dbase_options,
    language=language
)
```

5. When creating figures, use the original column names for data access but translated names for display:
```python
# For each translated source name, get the original column name
original_source_names = [translation_mapping.get(translated_name, translated_name) for translated_name in selected_source_names]

# Use original names for data access
for i, (translated_name, original_name) in enumerate(zip(selected_source_names, original_source_names)):
    if original_name in data.columns:
        # Access data using original name
        source_data = data[original_name]
        # Display using translated name
        fig.add_trace(go.Scatter(..., name=translated_name))
```
"""