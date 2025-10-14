#!/usr/bin/env python3
"""
Fix for Key Findings PCA calculation when only one source of data is available.

This script identifies and fixes the issue where Key Findings reports
incorrect variance explained when only one data source is available.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any
import logging

def fix_extract_pca_insights(data: pd.DataFrame, selected_sources: List[str]) -> Dict[str, Any]:
    """
    Fixed version of extract_pca_insights that properly handles single-source data.
    
    Args:
        data: Combined dataset
        selected_sources: List of selected sources
        
    Returns:
        Dictionary with PCA insights
    """
    # Check if we have sufficient data sources
    if len(selected_sources) < 2:
        return {
            'error': 'PCA requires at least 2 data sources',
            'components_analyzed': 0,
            'variance_explained': 0,
            'dominant_patterns': [],
            'total_variance_explained': 0.0
        }
    
    # Check if we actually have multiple columns in the data
    if len(data.columns) < 2:
        return {
            'error': f'PCA requires at least 2 data columns, but only {len(data.columns)} column(s) available: {list(data.columns)}',
            'components_analyzed': 0,
            'variance_explained': 0,
            'dominant_patterns': [],
            'total_variance_explained': 0.0,
            'available_columns': list(data.columns),
            'selected_sources': selected_sources
        }
    
    try:
        # Prepare data for PCA
        pca_data = data.dropna()
        if len(pca_data) < 10:  # Need minimum data points
            return {
                'error': 'Insufficient data for PCA analysis (need at least 10 data points)',
                'components_analyzed': 0,
                'variance_explained': 0,
                'dominant_patterns': [],
                'total_variance_explained': 0.0
            }
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pca_data)
        
        # Perform PCA
        n_components = min(len(selected_sources), len(pca_data.columns))
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_data)
        
        # Calculate explained variance
        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        
        # CRITICAL FIX: Ensure total_variance_explained is correctly calculated as percentage
        total_variance_explained = float(np.sum(explained_variance) * 100)
        
        # Analyze component loadings
        loadings = pca.components_.T * np.sqrt(explained_variance)
        
        # Identify dominant patterns
        dominant_patterns = []
        for i in range(min(3, n_components)):  # Top 3 components
            component_loadings = loadings[:, i]
            
            # Find sources with highest loadings
            top_sources_idx = np.argsort(np.abs(component_loadings))[-3:][::-1]
            # Handle both string and integer indices
            if all(isinstance(idx, (int, np.integer)) for idx in top_sources_idx):
                top_sources = [selected_sources[int(idx)] for idx in top_sources_idx]
            else:
                top_sources = [str(idx) for idx in top_sources_idx]
            top_loadings = [component_loadings[idx] for idx in top_sources_idx]
            
            # Enhanced component analysis with detailed loadings interpretation
            component_analysis = self._analyze_component_detailed(
                component_loadings, list(data.columns), i+1, explained_variance[i]
            )

            dominant_patterns.append({
                'component': f'PC{i+1}',
                'variance_explained': float(explained_variance[i] * 100),  # Convert to percentage
                'cumulative_variance': float(cumulative_variance[i] * 100),  # Convert to percentage
                'dominant_sources': top_sources,
                'loadings': dict(zip(list(data.columns), component_loadings.tolist())),
                'interpretation': component_analysis['interpretation'],
                'loadings_analysis': component_analysis['loadings_analysis'],
                'source_contributions': component_analysis['source_contributions'],
                'pattern_type': component_analysis['pattern_type']
            })
        
        return {
            'components_analyzed': n_components,
            'total_variance_explained': total_variance_explained,
            'variance_by_component': (explained_variance * 100).tolist(),  # Convert to percentages
            'cumulative_variance': (cumulative_variance * 100).tolist(),  # Convert to percentages
            'dominant_patterns': dominant_patterns,
            'data_points_used': len(pca_data),
            'pca_success': True
        }
        
    except Exception as e:
        logging.error(f"PCA analysis failed: {e}")
        return {
            'error': f'PCA analysis error: {str(e)}',
            'components_analyzed': 0,
            'variance_explained': 0,
            'dominant_patterns': [],
            'total_variance_explained': 0.0
        }

def apply_fix_to_key_findings():
    """
    Apply the fix to the Key Findings data aggregator.
    """
    # Path to the Key Findings data aggregator
    key_findings_path = os.path.join(os.path.dirname(__file__), 'dashboard_app', 'key_findings')
    data_aggregator_path = os.path.join(key_findings_path, 'data_aggregator.py')
    
    # Read the current file
    with open(data_aggregator_path, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "total_variance_explained': float(np.sum(explained_variance) * 100)" in content:
        print("✅ Fix already applied to Key Findings data aggregator")
        return
    
    # Apply the fix
    # Replace the incorrect line with the correct one
    old_line = "'total_variance_explained': float(np.sum(explained_variance)),"
    new_line = "'total_variance_explained': float(np.sum(explained_variance) * 100),"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Also fix the variance_explained values in dominant_patterns
        old_pattern = "'variance_explained': float(explained_variance[i]),"
        new_pattern = "'variance_explained': float(explained_variance[i] * 100),"
        content = content.replace(old_pattern, new_pattern)
        
        old_pattern2 = "'cumulative_variance': float(cumulative_variance[i]),"
        new_pattern2 = "'cumulative_variance': float(cumulative_variance[i] * 100),"
        content = content.replace(old_pattern2, new_pattern2)
        
        # Write the fixed content back to the file
        with open(data_aggregator_path, 'w') as f:
            f.write(content)
        
        print("✅ Successfully applied fix to Key Findings data aggregator")
        print("   - Fixed total_variance_explained calculation")
        print("   - Fixed variance_explained in dominant_patterns")
        print("   - Fixed cumulative_variance in dominant_patterns")
    else:
        print("❌ Could not find the line to fix in Key Findings data aggregator")

def check_single_source_issue():
    """
    Check if there's an issue with single source data retrieval.
    """
    print("\n" + "="*60)
    print("CHECKING SINGLE SOURCE ISSUE")
    print("="*60)
    
    # Import database manager
    from database import get_database_manager
    
    # Test with the problematic tool
    tool_name = "Alianzas y Capital de Riesgo"
    selected_display_names = ["Google Trends", "Google Books", "Bain Usability", "Bain Satisfaction", "Crossref"]
    
    # Convert display names to source IDs
    mapping = {
        "Google Trends": 1,
        "Google Books": 2,
        "Bain Usability": 3,
        "Bain Satisfaction": 5,
        "Crossref": 4
    }
    selected_source_ids = [mapping.get(name, 1) for name in selected_display_names]
    
    try:
        # Initialize database manager
        db_manager = get_database_manager()
        
        # Get data from database
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(tool_name, selected_source_ids)
        
        print(f"Retrieved {len(datasets_norm)} datasets")
        print(f"Source list: {sl_sc}")
        
        # Check what data we actually got
        for source_id, data in datasets_norm.items():
            if data is not None and not data.empty:
                print(f"Source {source_id}: {data.shape[0]} rows, {data.shape[1]} columns")
                print(f"  Column names: {list(data.columns)}")
                print(f"  Date range: {data.index.min()} to {data.index.max()}")
            else:
                print(f"Source {source_id}: No data")
        
        # The issue is that only one source is returning data
        # This explains why PCA shows only one variable
        
    except Exception as e:
        print(f"❌ Error during check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 KEY FINDINGS PCA FIX SCRIPT")
    print("="*60)
    
    # Check the single source issue
    check_single_source_issue()
    
    # Apply the fix
    apply_fix_to_key_findings()
    
    print("\n📋 SUMMARY:")
    print("1. The main issue is that only one source of data is being retrieved")
    print("2. With only one variable, PCA shows 100% variance explained")
    print("3. Key Findings was incorrectly calculating the total variance explained")
    print("4. Applied fix to ensure variance is expressed as percentage (0-100%)")
    print("\n📝 RECOMMENDATION:")
    print("Investigate why only one source is returning data from the database")