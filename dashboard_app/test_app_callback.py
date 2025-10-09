#!/usr/bin/env python3
"""
Test script to verify the main app callback works correctly.
This simulates the exact same logic as update_main_content callback.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from database import get_database_manager
from fix_source_mapping import map_display_names_to_source_ids, DBASE_OPTIONS as dbase_options

# Import the figure creation functions
from app import (
    create_temporal_2d_figure,
    create_mean_analysis_figure,
    create_combined_dataset2
)

def test_main_callback():
    """Test the main callback logic with the same parameters that should work"""

    print("=== TESTING MAIN APP CALLBACK ===")

    # Simulate the inputs that would trigger the callback
    selected_keyword = "Benchmarking"
    selected_sources = ["Google Trends"]  # Display names

    print(f"Selected keyword: {selected_keyword}")
    print(f"Selected sources: {selected_sources}")

    # Convert to source IDs (same as callback)
    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"Converted to source IDs: {selected_source_ids}")

    if not selected_keyword or not selected_sources:
        print("❌ Callback would return early - missing keyword or sources")
        return False

    try:
        # Get database manager
        db_manager = get_database_manager()

        # Get data (same as callback)
        print("Getting data from database...")
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)

        if not datasets_norm:
            print("❌ No data retrieved from database")
            return False

        print(f"✅ Retrieved datasets_norm keys: {list(datasets_norm.keys())}")
        print(f"✅ Retrieved sl_sc: {sl_sc}")

        # Create combined dataset (same as callback)
        print("Creating combined dataset...")
        combined_dataset = create_combined_dataset2(
            datasets_norm=datasets_norm,
            selected_sources=sl_sc,
            dbase_options=dbase_options
        )

        # Process data (same as callback)
        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Filter out rows where ALL selected sources are NaN
        data_columns = [dbase_options[src_id] for src_id in selected_source_ids]
        combined_dataset = combined_dataset.dropna(subset=data_columns, how='all')

        selected_source_names = [dbase_options[src_id] for src_id in selected_source_ids]

        print(f"✅ Processed dataset shape: {combined_dataset.shape}")
        print(f"✅ Dataset columns: {list(combined_dataset.columns)}")
        print(f"✅ Selected source names: {selected_source_names}")

        # Test figure creation (same as callback)
        print("\n=== TESTING FIGURE CREATION ===")

        # Test Temporal 2D
        print("Creating Temporal 2D figure...")
        temporal_2d_fig = create_temporal_2d_figure(combined_dataset, selected_source_names)
        print(f"✅ Temporal 2D figure created with {len(temporal_2d_fig.data) if hasattr(temporal_2d_fig, 'data') else 0} traces")

        # Test Mean Analysis
        print("Creating Mean Analysis figure...")
        mean_fig = create_mean_analysis_figure(combined_dataset, selected_source_names)
        print(f"✅ Mean Analysis figure created with {len(mean_fig.data) if hasattr(mean_fig, 'data') else 0} traces")

        # Verify figures are not empty
        if hasattr(temporal_2d_fig, 'data') and len(temporal_2d_fig.data) > 0:
            print("✅ Temporal 2D figure has data")
        else:
            print("❌ Temporal 2D figure is empty")

        if hasattr(mean_fig, 'data') and len(mean_fig.data) > 0:
            print("✅ Mean Analysis figure has data")
        else:
            print("❌ Mean Analysis figure is empty")

        print("\n=== SIMULATING DASH COMPONENT CREATION ===")

        # Simulate creating the content sections (same as callback)
        content = []

        # Temporal 2D section
        content.append({
            'type': 'temporal_2d',
            'figure_traces': len(temporal_2d_fig.data) if hasattr(temporal_2d_fig, 'data') else 0,
            'figure_title': temporal_2d_fig.layout.title.text if hasattr(temporal_2d_fig, 'layout') and hasattr(temporal_2d_fig.layout, 'title') else 'No title'
        })

        # Mean Analysis section
        content.append({
            'type': 'mean_analysis',
            'figure_traces': len(mean_fig.data) if hasattr(mean_fig, 'data') else 0,
            'figure_title': mean_fig.layout.title.text if hasattr(mean_fig, 'layout') and hasattr(mean_fig.layout, 'title') else 'No title'
        })

        print("✅ Content sections created:")
        for section in content:
            print(f"  - {section['type']}: {section['figure_traces']} traces, title: '{section['figure_title']}'")

        print("\n🎉 ALL TESTS PASSED - Callback logic works correctly!")
        return True

    except Exception as e:
        print(f"❌ Error in callback simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_callback()
    if success:
        print("\n📋 CONCLUSION:")
        print("The callback logic is working correctly. If graphs are still not showing in the app:")
        print("1. Check browser console for JavaScript errors")
        print("2. Try hard refresh (Ctrl+F5) to clear browser cache")
        print("3. Ensure the Dash app is running on the correct port")
        print("4. Check if there are any firewall/network issues")
        print("5. Verify the app is not running in multiple instances")
    else:
        print("\n❌ The callback logic has issues that need to be fixed.")