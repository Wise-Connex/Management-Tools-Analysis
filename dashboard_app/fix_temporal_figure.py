#!/usr/bin/env python3
"""
Fix for create_temporal_2d_figure function to handle translation mapping.
"""

import os
import shutil
from datetime import datetime

def fix_temporal_figure():
    """Fix the create_temporal_2d_figure function"""
    
    # File paths
    app_py_path = "app.py"
    backup_path = f"app.py.backup.temporal.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=== Fixing Temporal Figure Function ===")
    print(f"Backing up app.py to {backup_path}")
    
    # Create backup
    if os.path.exists(app_py_path):
        shutil.copy2(app_py_path, backup_path)
        print("✓ Backup created successfully")
    else:
        print(f"❌ Error: {app_py_path} not found")
        return False
    
    # Read the original file
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the create_temporal_2d_figure function
    start_idx = content.find("def create_temporal_2d_figure(data, sources, translation_mapping=None, language='es', start_date=None, end_date=None):")
    if start_idx == -1:
        print("❌ Could not find create_temporal_2d_figure function")
        return False
    
    # Find the end of the function
    end_idx = content.find("\n\ndef ", start_idx + 1)
    if end_idx == -1:
        end_idx = len(content)
    
    # Extract the function
    original_function = content[start_idx:end_idx]
    
    # Create fixed version
    fixed_function = """def create_temporal_2d_figure(data, sources, translation_mapping=None, language='es', start_date=None, end_date=None):
    print(f"DEBUG: create_temporal_2d_figure called")
    print(f"DEBUG: data shape: {data.shape}")
    print(f"DEBUG: sources: {sources}")
    print(f"DEBUG: translation_mapping: {translation_mapping}")
    print(f"DEBUG: start_date: {start_date}, end_date: {end_date}")
    
    # Handle translation mapping
    if translation_mapping is None:
        translation_mapping = {}
    
    # Filter data by date range if provided
    filtered_data = data.copy()
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['Fecha'] >= pd.to_datetime(start_date)) &
            (filtered_data['Fecha'] <= pd.to_datetime(end_date))
        ]
        print(f"DEBUG: Filtered data shape: {filtered_data.shape}")

    fig = go.Figure()
    trace_count = 0

    # Optimize: Use fewer markers and simpler rendering for better performance
    for i, source in enumerate(sources):
        print(f"DEBUG: Processing source: {source}")
        
        # Get the original column name from translation mapping
        original_name = translation_mapping.get(source, source)
        print(f"DEBUG: Original column name: {original_name}")
        
        if original_name in filtered_data.columns:
            source_data = filtered_data[original_name]
            valid_mask = ~source_data.isna()
            print(f"DEBUG: Source {source} has {valid_mask.sum()} valid points out of {len(source_data)}")

            if valid_mask.any():
                # Use lines only for better performance, add markers only for sparse data
                mode = 'lines+markers' if valid_mask.sum() < 50 else 'lines'
                print(f"DEBUG: Using mode: {mode}")

                fig.add_trace(go.Scatter(
                    x=filtered_data['Fecha'][valid_mask],
                    y=source_data[valid_mask],
                    mode=mode,
                    name=source,  # Use translated name for display
                    line=dict(
                        color=color_map.get(original_name, '#000000'),
                        width=2
                    ),
                    marker=dict(size=4) if mode == 'lines+markers' else None,
                    connectgaps=False,
                    hovertemplate=f'{source}: %{{y:.2f}}<br>%{{x|%Y-%m-%d}}<extra></extra>'
                ))
                trace_count += 1
                print(f"DEBUG: Added trace for {source}")
        else:
            print(f"DEBUG: Source {source} (original: {original_name}) not found in filtered_data columns")
            print(f"DEBUG: Available columns: {list(filtered_data.columns)}")

    print(f"DEBUG: Total traces added: {trace_count}")
    print(f"DEBUG: Figure has {len(fig.data)} traces after creation")

    # Simplified tick calculation for better performance
    date_range_days = (filtered_data['Fecha'].max() - filtered_data['Fecha'].min()).days
    print(f"DEBUG: Date range in days: {date_range_days}")

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
            autorange=True  # Let Plotly optimize tick spacing
        ),
        # Performance optimizations
        hovermode='x unified',
        showlegend=True
    )

    # Reduce data points for very large datasets
    if len(filtered_data) > 1000:
        fig.update_traces(
            hoverinfo='skip'  # Reduce hover computation for large datasets
        )

    print(f"DEBUG: Final figure has {len(fig.data)} traces")
    return fig"""
    
    # Replace the function
    content = content[:start_idx] + fixed_function + content[end_idx:]
    
    # Write the modified content
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ create_temporal_2d_figure function fixed to handle translation mapping")
    return True


if __name__ == "__main__":
    # Change to the dashboard_app directory
    if os.path.exists("dashboard_app"):
        os.chdir("dashboard_app")
        print("Changed to dashboard_app directory")
    
    success = fix_temporal_figure()
    exit(0 if success else 1)