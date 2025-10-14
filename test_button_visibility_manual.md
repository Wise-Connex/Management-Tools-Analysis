# Manual Test Guide: Key Findings Button Visibility Functionality

## Objective

To verify that the "Hallazgos Principales" (Key Findings) button is properly hidden when no tool or data sources are selected, and only appears when both are selected.

## Test Steps

### 1. Initial State Verification

1. Open the dashboard in your browser (http://localhost:8051)
2. **Expected Result**: The "Hallazgos Principales" button should not be visible when the page loads
3. **Verification**: The button should be completely hidden (not taking up any space)

### 2. Tool Selection Only

1. Select a tool from the dropdown (e.g., "Alianzas y Capital de Riesgo")
2. **Expected Result**: The button should remain hidden
3. **Verification**: The button should still not be visible

### 3. Data Sources Selection Only

1. Clear the tool selection (if any)
2. Select one or more data sources by clicking on the source buttons
3. **Expected Result**: The button should remain hidden
4. **Verification**: The button should still not be visible

### 4. Both Tool and Data Sources Selected

1. Select a tool from the dropdown
2. Select one or more data sources
3. **Expected Result**: The button should become visible
4. **Verification**: The button should appear in its normal color and be clickable

### 5. Deselect Tool

1. With both tool and data sources selected, clear the tool selection
2. **Expected Result**: The button should disappear again
3. **Verification**: The button should be completely hidden

### 6. Deselect Data Sources

1. Select a tool again
2. Deselect all data sources
3. **Expected Result**: The button should disappear
4. **Verification**: The button should be completely hidden

## Technical Implementation Details

The button visibility functionality is implemented through a Dash callback that:

- Monitors the `keyword-dropdown` (tool selection)
- Monitors the `data-sources-store-v2` (data sources selection)
- Sets the `display` style of the `key-findings-button-container` based on:
  - `display='none'` when no tool OR no data sources are selected
  - `display='block'` when both a tool AND at least one data source are selected

## Expected Behavior Summary

| Tool Selected | Data Sources Selected | Button State |
| ------------- | --------------------- | ------------ |
| No            | No                    | Hidden       |
| Yes           | No                    | Hidden       |
| No            | Yes                   | Hidden       |
| Yes           | Yes                   | Visible      |

## Troubleshooting

If the button is not behaving as expected:

1. Check the browser console for any JavaScript errors
2. Verify the callback is properly registered in the app.py file
3. Ensure the button container ID matches between the layout and callback
4. Check that the input components have the correct IDs
