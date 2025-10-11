# Docker Translation Issue - Diagnosis and Fix

## Issue Summary

When running the dashboard app in Docker and switching the language to English, the "Bain - Usability" and "Bain - Satisfaction" sources were not being recognized, causing errors when trying to display data.

## Root Cause Analysis

Through comprehensive debugging, I identified that the issue was in the `dashboard_app/fix_source_mapping.py` file. There were conflicting assignments to the `map_display_names_to_source_ids` function:

1. Line 119: `map_display_names_to_source_ids = enhanced_display_names_to_ids` (the enhanced function with English support)
2. Line 123: `map_display_names_to_source_ids = display_names_to_ids` (the standard function without English support)

The second assignment was overriding the first one, causing the app to use the standard function that doesn't properly map English source names to database IDs.

## The Fix

I fixed the issue by commenting out the conflicting assignment on line 123 in `dashboard_app/fix_source_mapping.py`:

```python
# Export the main conversion function for backward compatibility
# Note: This is now handled by the enhanced function above
# map_display_names_to_source_ids = display_names_to_ids
```

This ensures that the enhanced mapping function (which includes fallback mappings for English names) is used throughout the application.

## Testing

I created comprehensive test scripts to verify the fix:

1. `debug_docker_translation_comprehensive.py` - Detailed debugging script that tests all translation components
2. `test_translation_fix.py` - Simple verification script to test the fix
3. `rebuild_and_test_docker_with_fix.sh` - Script to rebuild Docker with the fix and test it

## How to Apply the Fix

1. The fix has already been applied to `dashboard_app/fix_source_mapping.py`
2. Rebuild your Docker image using:
   ```bash
   docker build -t dash_dashboard_fixed .
   ```
3. Run the container with the fix:
   ```bash
   docker run -p 8050:8050 -v $(pwd)/dashboard_app/data.db:/app/dashboard_app/data.db dash_dashboard_fixed
   ```
4. Test by switching the language to English and selecting Bain sources

## Verification

The fix has been tested locally and confirmed to work correctly. When English source names like "Bain - Usability" and "Bain - Satisfaction" are selected, they are now properly mapped to the correct database IDs (3 and 5, respectively).

## Additional Enhancements

The enhanced mapping function includes fallback translations for:

- "Bain - Usability" → ID 3
- "Bain - Satisfaction" → ID 5
- "Google Trends" → ID 1
- "Google Books" → ID 2
- "Crossref" → ID 4

This ensures the application works correctly regardless of whether Spanish or English source names are used.
