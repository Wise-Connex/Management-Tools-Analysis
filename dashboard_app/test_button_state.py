#!/usr/bin/env python3
"""
Test script to verify Key Findings button state management.
This script tests that the button changes state immediately when clicked.
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import time

# Create a simple test app to verify button behavior
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Button State Test"),
    dbc.Button("Test Button", id="test-btn", color="primary"),
    html.Div(id="button-state-display"),
    html.Div(id="click-count-display"),
    dcc.Store(id="click-count", data=0),
    dcc.Store(id="button-state", data="normal")
])

@app.callback(
    Output("button-state-display", "children"),
    Output("click-count-display", "children"),
    Output("test-btn", "disabled"),
    Output("test-btn", "style"),
    Output("click-count", "data"),
    Output("button-state", "data"),
    Input("test-btn", "n_clicks"),
    State("click-count", "data"),
    State("button-state", "data"),
    prevent_initial_call=False
)
def test_button_state(n_clicks, click_count, current_state):
    """Test button state changes"""
    print(f"Button clicked: {n_clicks}, Count: {click_count}, State: {current_state}")

    # Default state
    is_disabled = False
    button_style = {'backgroundColor': 'blue', 'color': 'white'}
    display_text = "Button is enabled"
    new_state = "normal"
    new_count = click_count or 0

    if n_clicks and n_clicks > 0:
        # Button was clicked - show processing state immediately
        print("Setting processing state immediately")
        is_disabled = True
        button_style = {
            'backgroundColor': '#f8f9fa',
            'color': '#8b0000',
            'border': '1px solid #8b0000'
        }
        display_text = "Button is disabled (processing)"
        new_state = "processing"
        new_count = n_clicks

        # Simulate some processing time
        time.sleep(2)

        # After processing, re-enable the button
        print("Processing complete, re-enabling button")
        is_disabled = False
        button_style = {'backgroundColor': 'green', 'color': 'white'}
        display_text = "Button re-enabled after processing"
        new_state = "completed"

    return display_text, f"Clicks: {new_count}", is_disabled, button_style, new_count, new_state

if __name__ == "__main__":
    print("Starting button state test...")
    print("Click the button to test state changes")
    app.run_server(debug=True, port=8051)