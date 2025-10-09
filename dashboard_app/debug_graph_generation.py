#!/usr/bin/env python3
"""
Comprehensive debugging script for graph generation issues in the Management Tools Analysis Dashboard.

This script systematically tests each component of the graph generation pipeline:
1. Data retrieval from database
2. Data processing and formatting
3. Figure creation functions
4. Plotly figure validation
5. Dash component rendering simulation
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database_manager
from fix_source_mapping import map_display_names_to_source_ids, DBASE_OPTIONS

# Import figure creation functions
from app import (
    create_temporal_2d_figure,
    create_mean_analysis_figure,
    create_combined_dataset2,
    create_correlation_heatmap,
    create_pca_figure
)

def test_data_retrieval():
    """Test 1: Data retrieval from database"""
    print("=" * 60)
    print("TEST 1: DATA RETRIEVAL")
    print("=" * 60)

    try:
        db_manager = get_database_manager()

        # Test with a known keyword
        test_keyword = "Benchmarking"
        test_sources = ["Google Trends"]

        print(f"Testing data retrieval for keyword: '{test_keyword}'")
        print(f"Testing sources: {test_sources}")

        # Convert display names to source IDs
        source_ids = map_display_names_to_source_ids(test_sources)
        print(f"Converted to source IDs: {source_ids}")

        # Retrieve data
        datasets_norm, valid_sources = db_manager.get_data_for_keyword(test_keyword, source_ids)

        print(f"Retrieved datasets_norm keys: {list(datasets_norm.keys()) if datasets_norm else 'None'}")
        print(f"Valid sources: {valid_sources}")

        if datasets_norm:
            for source_id, data in datasets_norm.items():
                print(f"  Source {source_id}: shape {data.shape}, columns {list(data.columns)}")
                print(f"    Sample data:\n{data.head(3)}")
                print(f"    Data types:\n{data.dtypes}")
        else:
            print("ERROR: No data retrieved!")
            return None, None

        return datasets_norm, valid_sources

    except Exception as e:
        print(f"ERROR in data retrieval: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_data_processing(datasets_norm, valid_sources):
    """Test 2: Data processing and formatting"""
    print("\n" + "=" * 60)
    print("TEST 2: DATA PROCESSING")
    print("=" * 60)

    try:
        if not datasets_norm:
            print("ERROR: No datasets_norm provided")
            return None

        # Create combined dataset
        print("Creating combined dataset...")
        combined_dataset = create_combined_dataset2(
            datasets_norm=datasets_norm,
            selected_sources=valid_sources,
            dbase_options=DBASE_OPTIONS
        )

        print(f"Raw combined dataset shape: {combined_dataset.shape}")
        print(f"Raw combined dataset columns: {list(combined_dataset.columns)}")
        print(f"Raw combined dataset index: {combined_dataset.index.name}")

        # Apply the same processing as the main app
        print("Processing data (reset_index, convert to datetime, rename)...")
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Filter out rows where ALL selected sources are NaN
        data_columns = [DBASE_OPTIONS[src_id] for src_id in valid_sources]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        print(f"Processed combined dataset shape: {combined_dataset.shape}")
        print(f"Processed combined dataset columns: {list(combined_dataset.columns)}")
        print(f"Processed combined dataset dtypes:\n{combined_dataset.dtypes}")

        # Check for datetime column
        if 'Fecha' in combined_dataset.columns:
            print(f"Fecha column range: {combined_dataset['Fecha'].min()} to {combined_dataset['Fecha'].max()}")
        else:
            print("ERROR: Still no 'Fecha' column found after processing!")

        # Check for data columns
        data_columns = [col for col in combined_dataset.columns if col != 'Fecha']
        print(f"Data columns: {data_columns}")

        # Check for NaN values
        nan_counts = combined_dataset.isnull().sum()
        print(f"NaN counts per column:\n{nan_counts}")

        # Sample of processed data
        print(f"Sample of processed data:\n{combined_dataset.head(5)}")

        return combined_dataset, data_columns

    except Exception as e:
        print(f"ERROR in data processing: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_figure_creation(combined_dataset, source_names):
    """Test 3: Figure creation functions"""
    print("\n" + "=" * 60)
    print("TEST 3: FIGURE CREATION")
    print("=" * 60)

    test_results = {}

    # Test 3.1: Temporal 2D Figure
    print("\n3.1 Testing Temporal 2D Figure...")
    try:
        temporal_fig = create_temporal_2d_figure(combined_dataset, source_names)
        print(f"✓ Temporal 2D figure created successfully")
        print(f"  Figure has {len(temporal_fig.data)} traces")
        if hasattr(temporal_fig, 'data') and len(temporal_fig.data) > 0:
            for i, trace in enumerate(temporal_fig.data[:3]):  # Show first 3 traces
                trace_type = type(trace).__name__
                if hasattr(trace, 'mode'):
                    mode_info = f" ({trace.mode})"
                else:
                    mode_info = f" ({trace_type})"
                x_len = len(trace.x) if hasattr(trace, 'x') and trace.x is not None else 'no x data'
                print(f"    Trace {i}: {trace.name}{mode_info} - {x_len} points")
        test_results['temporal_2d'] = temporal_fig
    except Exception as e:
        print(f"✗ ERROR creating Temporal 2D figure: {e}")
        import traceback
        traceback.print_exc()
        test_results['temporal_2d'] = None

    # Test 3.2: Mean Analysis Figure
    print("\n3.2 Testing Mean Analysis Figure...")
    try:
        mean_fig = create_mean_analysis_figure(combined_dataset, source_names)
        print(f"✓ Mean analysis figure created successfully")
        print(f"  Figure has {len(mean_fig.data)} traces")
        if hasattr(mean_fig, 'data') and len(mean_fig.data) > 0:
            for i, trace in enumerate(mean_fig.data[:3]):  # Show first 3 traces
                trace_type = type(trace).__name__
                if hasattr(trace, 'mode'):
                    mode_info = f" ({trace.mode})"
                else:
                    mode_info = f" ({trace_type})"
                x_len = len(trace.x) if hasattr(trace, 'x') and trace.x is not None else 'no x data'
                print(f"    Trace {i}: {trace.name}{mode_info} - {x_len} points")
        test_results['mean_analysis'] = mean_fig
    except Exception as e:
        print(f"✗ ERROR creating Mean Analysis figure: {e}")
        import traceback
        traceback.print_exc()
        test_results['mean_analysis'] = None

    # Test 3.3: Correlation Heatmap (if multiple sources)
    if len(source_names) >= 2:
        print("\n3.3 Testing Correlation Heatmap...")
        try:
            corr_fig = create_correlation_heatmap(combined_dataset, source_names)
            print(f"✓ Correlation heatmap created successfully")
            print(f"  Figure has {len(corr_fig.data)} traces")
            test_results['correlation'] = corr_fig
        except Exception as e:
            print(f"✗ ERROR creating Correlation heatmap: {e}")
            import traceback
            traceback.print_exc()
            test_results['correlation'] = None

    # Test 3.4: PCA Figure (if multiple sources)
    if len(source_names) >= 2:
        print("\n3.4 Testing PCA Figure...")
        try:
            pca_fig = create_pca_figure(combined_dataset, source_names)
            print(f"✓ PCA figure created successfully")
            print(f"  Figure has {len(pca_fig.data)} traces")
            test_results['pca'] = pca_fig
        except Exception as e:
            print(f"✗ ERROR creating PCA figure: {e}")
            import traceback
            traceback.print_exc()
            test_results['pca'] = None

    return test_results

def test_figure_validation(figures):
    """Test 4: Figure validation"""
    print("\n" + "=" * 60)
    print("TEST 4: FIGURE VALIDATION")
    print("=" * 60)

    for fig_name, fig in figures.items():
        if fig is None:
            print(f"✗ {fig_name}: Figure is None")
            continue

        print(f"\n{fig_name.upper()} VALIDATION:")

        # Check if it's a valid Plotly figure
        if not hasattr(fig, 'data'):
            print(f"✗ {fig_name}: No 'data' attribute")
            continue

        if not hasattr(fig, 'layout'):
            print(f"✗ {fig_name}: No 'layout' attribute")
            continue

        print(f"✓ {fig_name}: Valid Plotly figure structure")

        # Check data traces
        if len(fig.data) == 0:
            print(f"⚠ {fig_name}: No data traces (figure will be empty)")
        else:
            print(f"✓ {fig_name}: Has {len(fig.data)} data traces")

        # Check for empty traces
        empty_traces = 0
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'x') and len(trace.x) == 0:
                empty_traces += 1
                print(f"⚠ {fig_name}: Trace {i} ({trace.name}) has empty x data")

        if empty_traces == 0:
            print(f"✓ {fig_name}: All traces have data")
        else:
            print(f"⚠ {fig_name}: {empty_traces} traces have empty data")

        # Check layout
        if hasattr(fig.layout, 'title') and fig.layout.title:
            print(f"✓ {fig_name}: Has title")
        else:
            print(f"⚠ {fig_name}: No title")

def test_dash_simulation(figures):
    """Test 5: Dash component simulation"""
    print("\n" + "=" * 60)
    print("TEST 5: DASH COMPONENT SIMULATION")
    print("=" * 60)

    import dash
    from dash import html, dcc

    # Create a minimal Dash app for testing
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    # Test layout creation
    layout_children = []

    for fig_name, fig in figures.items():
        if fig is None:
            layout_children.append(html.Div(f"ERROR: {fig_name} figure is None"))
            continue

        try:
            # Create a graph component
            graph = dcc.Graph(
                id=f'test-{fig_name}',
                figure=fig,
                style={'height': '400px'},
                config={'displaylogo': False, 'responsive': True}
            )
            layout_children.append(html.Div([
                html.H4(f"Test {fig_name.replace('_', ' ').title()}"),
                graph
            ]))
            print(f"✓ {fig_name}: Dash Graph component created successfully")
        except Exception as e:
            layout_children.append(html.Div(f"ERROR creating {fig_name} component: {str(e)}"))
            print(f"✗ {fig_name}: Failed to create Dash component: {e}")

    # Test layout
    try:
        app.layout = html.Div(layout_children)
        print("✓ Dash layout created successfully")
    except Exception as e:
        print(f"✗ Failed to create Dash layout: {e}")

    return app

def run_comprehensive_debug():
    """Run all debugging tests"""
    print("STARTING COMPREHENSIVE GRAPH GENERATION DEBUG")
    print("=" * 80)

    # Test 1: Data Retrieval
    datasets_norm, valid_sources = test_data_retrieval()
    if not datasets_norm:
        print("\n❌ DEBUG FAILED: Data retrieval failed")
        return

    # Test 2: Data Processing
    combined_dataset, source_names = test_data_processing(datasets_norm, valid_sources)
    if combined_dataset is None:
        print("\n❌ DEBUG FAILED: Data processing failed")
        return

    # Test 3: Figure Creation
    figures = test_figure_creation(combined_dataset, source_names)

    # Test 4: Figure Validation
    test_figure_validation(figures)

    # Test 5: Dash Simulation
    app = test_dash_simulation(figures)

    print("\n" + "=" * 80)
    print("DEBUG SUMMARY")
    print("=" * 80)

    success_count = sum(1 for fig in figures.values() if fig is not None)
    total_count = len(figures)

    print(f"Figures created successfully: {success_count}/{total_count}")

    if success_count == total_count:
        print("✅ ALL TESTS PASSED - Graphs should display correctly")
        print("\nIf graphs are still not showing in the app, the issue may be:")
        print("1. Browser caching - try hard refresh (Ctrl+F5)")
        print("2. JavaScript errors in browser console")
        print("3. Dash app not properly restarted after code changes")
        print("4. Port conflicts or firewall issues")
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
        print("\nMost likely causes:")
        print("1. Data format issues in figure creation functions")
        print("2. Missing dependencies (plotly, pandas, etc.)")
        print("3. Logic errors in figure creation algorithms")

    print(f"\nDebug data saved. You can now run the test app with: uv run python {__file__}")

if __name__ == "__main__":
    run_comprehensive_debug()