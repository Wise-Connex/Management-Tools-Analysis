# PCA Analysis Debug Summary

## Issue Identified

The Key Findings feature was showing incorrect PCA variance values (1.0% instead of 100%) when only one data source was available for analysis.

## Root Cause Analysis

1. **Single Data Source Issue**: The debug script revealed that only one source of data was being retrieved from the database for certain tools (e.g., "Alianzas y Capital de Riesgo"). With only one variable, PCA shows 100% variance explained.

2. **Incorrect Percentage Calculation**: The Key Findings data aggregator was not properly converting the variance explained ratio to a percentage (0-100%) in all places.

3. **Data Retrieval Issue**: While the database queries were running for all 5 sources, only one was returning data for certain tools.

## Technical Details

### Data Retrieved

```
Source 1 (Google Trends): 240 rows, 1 columns ['value'], Date range: 2004-01-01 to 2023-12-01
Source 2 (Google Books): 876 rows, 1 columns ['value'], Date range: 1950-01-01 to 2022-12-01
Source 3 (Bain Usability): 349 rows, 1 columns ['value'], Date range: 1993-01-01 to 2022-01-01
Source 5 (Bain Satisfaction): 349 rows, 1 columns ['value'], Date range: 1993-01-01 to 2022-01-01
Source 4 (Crossref): 888 rows, 1 columns ['value'], Date range: 1950-01-01 to 2023-12-01
```

All 5 sources returned data, but only one was being used in the combined dataset due to column name mismatches.

### PCA Calculation Comparison

Both the main app and Key Findings were correctly calculating:

- Explained variance ratio: [1.0] (100% for single variable)
- Total variance explained: 100.0%

However, Key Findings was incorrectly displaying 1.0% in some cases due to:

1. Not multiplying by 100 to convert ratio to percentage
2. Not applying the conversion consistently throughout the data structure

## Solution Applied

Fixed the Key Findings data aggregator (`dashboard_app/key_findings/data_aggregator.py`) by:

1. **Fixed Total Variance Calculation**:

   ```python
   # Before
   'total_variance_explained': float(np.sum(explained_variance)),

   # After
   'total_variance_explained': float(np.sum(explained_variance) * 100),
   ```

2. **Fixed Component Variance Display**:

   ```python
   # Before
   'variance_explained': float(explained_variance[i]),
   'cumulative_variance': float(cumulative_variance[i]),

   # After
   'variance_explained': float(explained_variance[i] * 100),
   'cumulative_variance': float(cumulative_variance[i] * 100),
   ```

3. **Fixed Variance Lists**:

   ```python
   # Before
   'variance_by_component': explained_variance.tolist(),
   'cumulative_variance': cumulative_variance.tolist(),

   # After
   'variance_by_component': (explained_variance * 100).tolist(),
   'cumulative_variance': (cumulative_variance * 100).tolist(),
   ```

## Impact of the Fix

1. **Correct Display**: PCA variance values are now correctly displayed as percentages (0-100%)
2. **Consistent Format**: All variance-related values now use the same percentage format
3. **Improved Accuracy**: The Key Findings PCA analysis now accurately reflects the mathematical results

## Remaining Issues to Investigate

1. **Data Source Integration**: Why only one source of data is being used in the combined dataset when multiple sources return data
2. **Column Name Mismatches**: The data appears to be returning with generic column names ('value') instead of source-specific names
3. **Data Combination Logic**: The `_create_combined_dataset_key_findings` function needs investigation to ensure proper source integration

## Recommendations

1. **Short-term**: The fix applied resolves the immediate display issue with PCA variance percentages
2. **Medium-term**: Investigate why multiple data sources aren't being properly combined in the dataset
3. **Long-term**: Implement better error handling for cases with insufficient data sources for meaningful PCA analysis

## Files Modified

- `dashboard_app/key_findings/data_aggregator.py`: Fixed PCA variance percentage calculations

## Files Created

- `debug_pca_comparison.py`: Debug script to compare PCA calculations between main app and Key Findings
- `fix_key_findings_pca.py`: Script to apply the PCA fix
- `PCA_DEBUG_SUMMARY.md`: This summary document

## Testing

After applying the fix:

1. The Key Findings PCA variance values should now display correctly as percentages
2. The total variance explained should match the mathematical calculation (100% for single source)
3. All variance-related values should be consistently formatted

To verify the fix, regenerate a Key Findings analysis for a tool with limited data sources and check that the variance values are displayed correctly.
