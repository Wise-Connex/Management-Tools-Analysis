#!/usr/bin/env python3
"""
Debug script to compare PCA calculations between main app and Key Findings.

This script will help identify why the Key Findings PCA shows 1.0% variance
while the main app shows 100% variance for the same data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Import database manager
from database import get_database_manager

# Import source mapping
# Import source mapping
try:
    from fix_source_mapping import map_display_names_to_source_ids, DISPLAY_NAMES
except ImportError:
    # Fallback for testing
    DISPLAY_NAMES = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    def map_display_names_to_source_ids(display_names):
        mapping = {
            "Google Trends": 1,
            "Google Books": 2,
            "Bain Usability": 3,
            "Bain Satisfaction": 5,
            "Crossref": 4
        }
        return [mapping.get(name, 1) for name in display_names]

# Import Key Findings data aggregator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard_app'))
from key_findings.data_aggregator import DataAggregator
from key_findings.database_manager import KeyFindingsDBManager

def main_app_pca_analysis(combined_dataset, selected_source_names, language='es'):
    """
    Replicate the main app's PCA calculation from perform_comprehensive_pca_analysis
    """
    print("\n" + "="*60)
    print("MAIN APP PCA ANALYSIS")
    print("="*60)
    
    print(f"Combined dataset shape: {combined_dataset.shape}")
    print(f"Columns: {list(combined_dataset.columns)}")
    print(f"Selected source names: {selected_source_names}")
    
    # Prepare data for PCA - use original column names
    original_columns = []
    for source in selected_source_names:
        if source in combined_dataset.columns:
            original_columns.append(source)
    
    print(f"Original columns for PCA: {original_columns}")
    
    if not original_columns:
        print("❌ No valid columns found for PCA analysis")
        return None
    
    pca_data = combined_dataset[original_columns].dropna()
    print(f"PCA data shape after dropping NaN: {pca_data.shape}")
    
    if len(pca_data) < 2:
        print("❌ Insufficient data for PCA")
        return None
    
    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pca_data)
    print(f"Scaled data shape: {scaled_data.shape}")
    print(f"Scaled data sample:\n{scaled_data[:5]}")
    
    # Perform PCA
    pca = PCA()
    pca_result = pca.fit_transform(scaled_data)
    
    # Calculate explained variance
    explained_var = pca.explained_variance_ratio_ * 100
    cumulative_var = explained_var.cumsum()
    
    print(f"\n📊 MAIN APP PCA RESULTS:")
    print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
    print(f"Explained variance (%): {explained_var}")
    print(f"Cumulative variance (%): {cumulative_var}")
    print(f"Total variance explained: {cumulative_var[-1]:.1f}%")
    
    # Determine number of components to analyze (Kaiser criterion: eigenvalues > 1)
    eigenvalues = pca.explained_variance_
    components_to_analyze = sum(eigenvalues > 1)
    print(f"Eigenvalues: {eigenvalues}")
    print(f"Components to analyze (Kaiser criterion): {components_to_analyze}")
    
    # Component loadings
    print(f"\n📋 COMPONENT LOADINGS:")
    for i in range(min(3, len(pca.components_))):
        pc_num = i + 1
        loadings = pca.components_[i]
        print(f"\nPC{pc_num} Loadings:")
        for j, (col, loading) in enumerate(zip(original_columns, loadings)):
            print(f"  {col}: {loading:.4f}")
    
    return {
        'explained_variance': explained_var,
        'cumulative_variance': cumulative_var,
        'eigenvalues': eigenvalues,
        'components_to_analyze': components_to_analyze,
        'loadings': pca.components_,
        'total_variance_explained': cumulative_var[-1]
    }

def key_findings_pca_analysis(combined_dataset, selected_sources, language='es'):
    """
    Replicate the Key Findings PCA calculation from extract_pca_insights
    """
    print("\n" + "="*60)
    print("KEY FINDINGS PCA ANALYSIS")
    print("="*60)
    
    print(f"Combined dataset shape: {combined_dataset.shape}")
    print(f"Columns: {list(combined_dataset.columns)}")
    print(f"Selected sources: {selected_sources}")
    
    # Prepare data for PCA (Key Findings method)
    pca_data = combined_dataset.dropna()
    print(f"PCA data shape after dropping NaN: {pca_data.shape}")
    
    if len(pca_data) < 10:  # Key Findings requires at least 10 data points
        print("❌ Insufficient data for PCA (need at least 10 data points)")
        return None
    
    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pca_data)
    print(f"Scaled data shape: {scaled_data.shape}")
    print(f"Scaled data sample:\n{scaled_data[:5]}")
    
    # Perform PCA (Key Findings method)
    n_components = min(len(selected_sources), len(pca_data.columns))
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)
    
    # Calculate explained variance
    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)
    
    print(f"\n📊 KEY FINDINGS PCA RESULTS:")
    print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
    print(f"Explained variance (%): {explained_variance * 100}")
    print(f"Cumulative variance (%): {cumulative_variance * 100}")
    print(f"Total variance explained: {np.sum(explained_variance) * 100:.1f}%")
    
    # Analyze component loadings (Key Findings method)
    loadings = pca.components_.T * np.sqrt(explained_variance)
    print(f"\n📋 COMPONENT LOADINGS (Key Findings method):")
    print(f"Loadings shape: {loadings.shape}")
    
    for i in range(min(3, loadings.shape[1])):
        pc_num = i + 1
        component_loadings = loadings[:, i]
        print(f"\nPC{pc_num} Loadings:")
        for j, (col, loading) in enumerate(zip(pca_data.columns, component_loadings)):
            print(f"  {col}: {loading:.4f}")
    
    return {
        'explained_variance': explained_variance * 100,
        'cumulative_variance': cumulative_variance * 100,
        'total_variance_explained': float(np.sum(explained_variance) * 100),
        'loadings': loadings,
        'n_components': n_components
    }

def compare_pca_results(main_app_results, key_findings_results):
    """Compare the two PCA calculation methods"""
    print("\n" + "="*60)
    print("PCA COMPARISON")
    print("="*60)
    
    if main_app_results is None or key_findings_results is None:
        print("❌ Cannot compare - one of the methods failed")
        return
    
    print(f"Main App Total Variance Explained: {main_app_results['total_variance_explained']:.1f}%")
    print(f"Key Findings Total Variance Explained: {key_findings_results['total_variance_explained']:.1f}%")
    
    variance_diff = abs(main_app_results['total_variance_explained'] - key_findings_results['total_variance_explained'])
    print(f"Difference: {variance_diff:.1f}%")
    
    if variance_diff > 1.0:
        print("⚠️ SIGNIFICANT DIFFERENCE DETECTED!")
        
        print("\n🔍 DETAILED COMPARISON:")
        print(f"Main App explained variance: {main_app_results['explained_variance']}")
        print(f"Key Findings explained variance: {key_findings_results['explained_variance']}")
        
        print(f"\nMain App eigenvalues: {main_app_results['eigenvalues']}")
        print(f"Key Findings n_components: {key_findings_results['n_components']}")
        
        # Check if it's a calculation difference
        if np.allclose(main_app_results['explained_variance'], key_findings_results['explained_variance']):
            print("✅ The explained variance values are actually the same - might be a display issue")
        else:
            print("❌ The explained variance values are genuinely different")
            
            # Check for data differences
            print("\n🔍 POSSIBLE CAUSES:")
            print("1. Different data preprocessing (NaN handling)")
            print("2. Different standardization methods")
            print("3. Different PCA parameters")
            print("4. Different column selection/ordering")
    else:
        print("✅ Both methods produce similar results")

def main():
    """Main function to run the comparison"""
    print("🔍 PCA COMPARISON DEBUG SCRIPT")
    print("="*60)
    
    # Test with the problematic tool
    tool_name = "Alianzas y Capital de Riesgo"
    selected_display_names = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    
    try:
        # Initialize database manager
        db_manager = get_database_manager()
        
        # Convert display names to source IDs
        selected_source_ids = map_display_names_to_source_ids(selected_display_names)
        print(f"Selected source IDs: {selected_source_ids}")
        
        # Get data from database
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(tool_name, selected_source_ids)
        print(f"Retrieved {len(datasets_norm)} datasets")
        print(f"Source list: {sl_sc}")
        
        if not datasets_norm:
            print("❌ No data retrieved from database")
            return
        
        # Create combined dataset using main app method
        from tools import tool_file_dic
        dbase_options = {}
        for tool_list in tool_file_dic.values():
            for i, source_key in enumerate([1, 2, 3, 4, 5]):
                if i < len(tool_list) and i < len(tool_list[1]):
                    dbase_options[source_key] = tool_list[i]
        
        combined_dataset = pd.DataFrame()
        
        # Get all unique dates from all datasets
        all_dates = set()
        for source_data in datasets_norm.values():
            if source_data is not None and not source_data.empty:
                all_dates.update(source_data.index)
        
        if not all_dates:
            print("❌ No dates found in datasets")
            return
        
        # Sort dates
        all_dates = sorted(list(all_dates))
        
        # Create DataFrame with all dates
        combined_dataset = pd.DataFrame(index=all_dates)
        
        # Add data from each source
        for source_id in sl_sc:
            if source_id in datasets_norm and source_id in dbase_options:
                source_name = dbase_options[source_id]
                source_data = datasets_norm[source_id]
                
                # Reindex to match all dates
                aligned_data = source_data.reindex(all_dates)
                combined_dataset[source_name] = aligned_data.iloc[:, 0] if len(aligned_data.columns) > 0 else aligned_data
        
        # Remove rows where all sources are NaN
        combined_dataset = combined_dataset.dropna(how='all')
        
        print(f"\n📊 Combined dataset created:")
        print(f"Shape: {combined_dataset.shape}")
        print(f"Columns: {list(combined_dataset.columns)}")
        print(f"Date range: {combined_dataset.index.min()} to {combined_dataset.index.max()}")
        print(f"Sample data:\n{combined_dataset.head()}")
        print(f"Data types:\n{combined_dataset.dtypes}")
        print(f"Missing values:\n{combined_dataset.isna().sum()}")
        
        # Get source names for analysis
        selected_source_names = []
        for src_id in sl_sc:
            if src_id in dbase_options:
                selected_source_names.append(dbase_options[src_id])
            else:
                print(f"⚠️ Source ID {src_id} not found in dbase_options")
        
        print(f"Selected source names: {selected_source_names}")
        
        # Run both PCA analyses
        main_app_results = main_app_pca_analysis(combined_dataset, selected_source_names)
        key_findings_results = key_findings_pca_analysis(combined_dataset, selected_source_names)
        
        # Compare results
        compare_pca_results(main_app_results, key_findings_results)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()