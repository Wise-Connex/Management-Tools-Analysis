"""
Translation fix for app.py to handle Docker translation issue.

This file contains the modified functions that need to be replaced in app.py
to fix the translation issue when switching to English in Docker.
"""

def create_combined_dataset2_fixed(datasets_norm, selected_sources, dbase_options, language='es'):
    """
    Create combined dataset with all dates from all sources.
    Fixed version that maintains translation mapping between display names and column names.
    
    Args:
        datasets_norm: Dictionary of normalized datasets by source ID
        selected_sources: List of selected source IDs
        dbase_options: Mapping of source IDs to database names
        language: Current language ('es' or 'en')
        
    Returns:
        Tuple of (combined_dataset, translation_mapping)
    """
    import pandas as pd
    from translations import translate_source_name
    
    combined_dataset = pd.DataFrame()

    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)

    # Sort dates
    all_dates = sorted(list(all_dates))

    # Create DataFrame with all dates
    combined_dataset = pd.DataFrame(index=all_dates)

    # Create translation mapping
    translation_mapping = {}
    
    # Add data from each source - use original database name as column name
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            source_data = datasets_norm[source].reindex(all_dates)
            # Use the original database name as the column name
            combined_dataset[source_name] = source_data.iloc[:, 0]
            
            # Create mapping from translated name to original name
            translated_name = translate_source_name(source_name, language)
            translation_mapping[translated_name] = source_name

    return combined_dataset, translation_mapping


def create_temporal_2d_figure_fixed(data, sources, translation_mapping, language='es', start_date=None, end_date=None):
    """
    Fixed version of create_temporal_2d_figure that handles translation properly.
    
    Args:
        data: DataFrame with data (using original column names)
        sources: List of translated source names for display
        translation_mapping: Mapping from translated names to original column names
        language: Current language
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    import pandas as pd
    from translations import get_text
    
    # Filter data by date range if provided
    filtered_data = data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Fecha'] >= pd.to_datetime(start_date)) &
            (filtered_data['Fecha'] <= pd.to_datetime(end_date))
        ]

    fig = go.Figure()
    
    # Color map for sources
    from app import color_map
    
    # For each translated source name, get the original column name
    for translated_name in sources:
        original_name = translation_mapping.get(translated_name, translated_name)
        
        if original_name in filtered_data.columns:
            source_data = filtered_data[original_name]
            valid_mask = ~source_data.isna()

            if valid_mask.any():
                # Use lines only for better performance, add markers only for sparse data
                mode = 'lines+markers' if valid_mask.sum() < 50 else 'lines'

                fig.add_trace(go.Scatter(
                    x=filtered_data['Fecha'][valid_mask],
                    y=source_data[valid_mask],
                    mode=mode,
                    name=translated_name,  # Use translated name for display
                    line=dict(
                        color=color_map.get(original_name, '#000000'),
                        width=2
                    ),
                    marker=dict(size=4) if mode == 'lines+markers' else None,
                    connectgaps=False,
                    hovertemplate=f'{translated_name}: %{{y:.2f}}<br>%{{x|%Y-%m-%d}}<extra></extra>'
                ))

    # Simplified tick calculation for better performance
    date_range_days = (filtered_data['Fecha'].max() - filtered_data['Fecha'].min()).days

    if date_range_days <= 365:
        tickformat = "%Y-%m"
    elif date_range_days <= 365 * 3:
        tickformat = "%Y-%m"
    else:
        tickformat = "%Y"

    # Optimized layout with performance settings
    fig.update_layout(
        title=get_text('temporal_analysis_2d', language),
        xaxis_title=get_text('date', language),
        yaxis_title=get_text('value', language),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            tickformat=tickformat,
            tickangle=45,
            autorange=True
        ),
        hovermode='x unified',
        showlegend=True
    )

    # Reduce data points for very large datasets
    if len(filtered_data) > 1000:
        fig.update_traces(hoverinfo='skip')

    return fig


def create_correlation_heatmap_fixed(data, sources, translation_mapping, language='es'):
    """
    Fixed version of create_correlation_heatmap that handles translation properly.
    
    Args:
        data: DataFrame with data (using original column names)
        sources: List of translated source names for display
        translation_mapping: Mapping from translated names to original column names
        language: Current language
        
    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    import pandas as pd
    from translations import get_text
    
    # Get original column names for correlation calculation
    original_names = [translation_mapping.get(name, name) for name in sources]
    
    # Filter to only include columns that exist in the data
    valid_original_names = [name for name in original_names if name in data.columns]
    valid_sources = [sources[i] for i, name in enumerate(original_names) if name in data.columns]
    
    if len(valid_original_names) < 2:
        # Return empty figure if not enough data
        fig = go.Figure()
        fig.update_layout(
            title=get_text('correlation_heatmap_title', language),
            height=400
        )
        return fig
    
    # Calculate correlation using original column names
    corr_data = data[valid_original_names].corr()
    
    # Create custom annotations with better contrast
    annotations = []
    for i, row in enumerate(corr_data.values):
        for j, val in enumerate(row):
            # Determine text color based on background intensity
            if abs(val) < 0.3:
                text_color = 'black'
            else:
                text_color = 'white'

            annotations.append(
                dict(
                    x=valid_sources[j],  # Use translated names for display
                    y=valid_sources[i],  # Use translated names for display
                    text=f"{val:.2f}",
                    showarrow=False,
                    font=dict(
                        color=text_color,
                        size=12,
                        weight='bold'
                    )
                )
            )

    # Create heatmap using go.Heatmap for proper click event support
    fig = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=valid_sources,  # Use translated names for display
        y=valid_sources,  # Use translated names for display
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        hovertemplate='%{x} vs %{y}<br>Correlación: %{z:.3f}<extra></extra>',
        showscale=True
    ))

    # Update layout with annotations and enable click events
    fig.update_layout(
        title=get_text('correlation_heatmap_title', language),
        height=400,
        annotations=annotations,
        xaxis=dict(side='bottom'),
        yaxis=dict(side='left'),
        clickmode='event+select'  # Enable click events
    )

    return fig


# Instructions for applying the fix:
"""
To apply this fix to app.py:

1. Replace the create_combined_dataset2 function (lines 160-184) with create_combined_dataset2_fixed
2. Replace the create_temporal_2d_figure function (lines 1692-1785) with create_temporal_2d_figure_fixed
3. Replace the create_correlation_heatmap function (lines 2059-2113) with create_correlation_heatmap_fixed
4. Update the update_main_content callback to use the translation mapping:
   - Around line 1205, replace:
     combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)
   - With:
     combined_dataset, translation_mapping = create_combined_dataset2_fixed(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options, language=language)
5. Update all figure creation calls to pass the translation mapping
6. Update the regression analysis callback to use the translation mapping for variable access
"""