import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def update_regression_analysis(click_data, selected_keyword, selected_sources, language, db_manager, dbase_options, get_text, map_display_names_to_source_ids, create_combined_dataset2, color_map):
    """
    Fixed version of the regression analysis callback function.
    
    This function properly validates the click_data structure before accessing it,
    preventing the application from crashing when users click on the correlation heatmap.
    """
    print(f"DEBUG: update_regression_analysis called")
    print(f"DEBUG: click_data={click_data}")
    print(f"DEBUG: selected_keyword={selected_keyword}")
    print(f"DEBUG: selected_sources={selected_sources}")
    
    if selected_sources is None:
        selected_sources = []

    selected_source_ids = map_display_names_to_source_ids(selected_sources)
    print(f"DEBUG: selected_source_ids={selected_source_ids}")

    # Proper validation of click_data structure
    if not selected_keyword or len(selected_sources) < 2 or not click_data:
        print(f"DEBUG: Returning empty figure - missing keyword, sources, or click_data")
        fig = go.Figure()
        fig.update_layout(
            title=get_text('click_heatmap', language),
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig, ""

    # Validate click_data structure before accessing it
    try:
        if not isinstance(click_data, dict) or 'points' not in click_data or not click_data['points']:
            print(f"DEBUG: Invalid click_data structure")
            fig = go.Figure()
            fig.update_layout(
                title="Error: Invalid click data structure",
                xaxis_title="",
                yaxis_title="",
                height=400
            )
            return fig, ""
            
        # Safely extract x and y variables with error handling
        point = click_data['points'][0]
        if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
            print(f"DEBUG: Invalid point structure in click_data")
            fig = go.Figure()
            fig.update_layout(
                title="Error: Invalid point data structure",
                xaxis_title="",
                yaxis_title="",
                height=400
            )
            return fig, ""
            
        x_var = point['x']
        y_var = point['y']
        
    except (KeyError, IndexError, TypeError) as e:
        print(f"DEBUG: Error extracting variables from click_data: {e}")
        fig = go.Figure()
        fig.update_layout(
            title=f"Error extracting click data: {str(e)}",
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig, ""

    try:
        datasets_norm, sl_sc = db_manager.get_data_for_keyword(selected_keyword, selected_source_ids)
        combined_dataset = create_combined_dataset2(datasets_norm=datasets_norm, selected_sources=sl_sc, dbase_options=dbase_options)

        combined_dataset = combined_dataset.reset_index()
        date_column = combined_dataset.columns[0]
        combined_dataset[date_column] = pd.to_datetime(combined_dataset[date_column])
        combined_dataset = combined_dataset.rename(columns={date_column: 'Fecha'})

        # Get display names from the actual data columns, not from dbase_options
        selected_source_names = list(combined_dataset.columns[1:])  # Skip 'Fecha' column

        # Debug: print available columns and clicked variables
        print(f"Available columns: {list(combined_dataset.columns)}")
        print(f"Clicked variables: x='{x_var}', y='{y_var}'")

        # Check if variables are the same (diagonal click on heatmap)
        if x_var == y_var:
            fig = go.Figure()
            fig.add_annotation(
                text=get_text('cannot_regress_same', language, var=x_var) + "<br>" + get_text('select_different_vars', language),
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(
                title=get_text('invalid_selection', language),
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
                height=400
            )
            return fig, get_text('invalid_selection', language)

        if x_var not in combined_dataset.columns or y_var not in combined_dataset.columns:
            print(f"Variables not found in dataset: x='{x_var}', y='{y_var}'")
            fig = go.Figure()
            fig.update_layout(
                title=get_text('variables_not_found', language, x_var=x_var, y_var=y_var),
                xaxis_title="",
                yaxis_title="",
                height=500
            )
            return fig, ""

        # Perform regression analysis with multiple polynomial degrees
        valid_data = combined_dataset[[x_var, y_var]].dropna()
        if len(valid_data) < 2:
            return {}

        X = valid_data[x_var].values.reshape(-1, 1)
        y = valid_data[y_var].values

        # Colors for different polynomial degrees
        poly_colors = ['red', 'blue', 'green', 'orange']
        degree_names = ['Lineal', 'Cuadrática', 'Cúbica', 'Cuártica']

        fig = go.Figure()

        # Add scatter plot of original data
        fig.add_trace(go.Scatter(
            x=valid_data[x_var],
            y=valid_data[y_var],
            mode='markers',
            name='Datos',
            marker=dict(color='gray', size=6, opacity=0.7)
        ))

        # Sort X for smooth polynomial curves
        X_sorted = np.sort(X.flatten())
        X_sorted_reshaped = X_sorted.reshape(-1, 1)

        # Annotations for formulas and R-squared
        annotations = []

        for degree in range(1, 5):  # Degrees 1, 2, 3, 4
            try:
                # Ensure data is numeric and properly shaped
                X_clean = X.astype(float)
                y_clean = y.astype(float)

                # Fit polynomial regression
                poly_features = PolynomialFeatures(degree=degree)
                X_poly = poly_features.fit_transform(X_clean)

                model = LinearRegression()
                model.fit(X_poly, y_clean)

                # Predict on sorted X values for smooth curve
                X_poly_sorted = poly_features.transform(X_sorted_reshaped)
                y_pred_sorted = model.predict(X_poly_sorted)

                # Calculate R-squared
                y_pred = model.predict(X_poly)
                r_squared = r2_score(y_clean, y_pred)

                # Create polynomial formula string with proper mathematical formatting
                coefs = model.coef_
                intercept = model.intercept_

                if degree == 1:
                    # Linear: y = mx + b
                    formula = f"y = {coefs[1]:.3f}x {'+' if intercept >= 0 else ''}{intercept:.3f}"
                else:
                    # Polynomial: y = dx³ + cx² + bx + a (highest power to lowest)
                    terms = []

                    # Polynomial terms (highest power first)
                    for i in range(len(coefs) - 1, 0, -1):  # Start from highest degree down to x term
                        if abs(coefs[i]) > 0.001:  # Only show significant coefficients
                            coef_str = f"{coefs[i]:+.3f}"
                            if i == 1:
                                terms.append(f"{coef_str}x")
                            else:
                                terms.append(f"{coef_str}x<sup>{i}</sup>")

                    # Intercept term (comes last)
                    if abs(intercept) > 0.001:
                        terms.append(f"{intercept:+.3f}")

                    # Join terms with proper spacing
                    formula = f"y = {' '.join(terms)}"

                # Add regression line
                fig.add_trace(go.Scatter(
                    x=X_sorted,
                    y=y_pred_sorted,
                    mode='lines',
                    name=f'{degree_names[degree-1]} (R² = {r_squared:.3f})',
                    line=dict(color=poly_colors[degree-1], width=2)
                ))

                # Add annotation for this degree
                annotations.append(
                    f"<b>{degree_names[degree-1]}:</b><br>"
                    f"{formula}<br>"
                    f"R² = {r_squared:.3f}"
                )
            except Exception as poly_e:
                print(f"Error fitting degree {degree} polynomial: {poly_e}")
                # Add error annotation for this degree
                annotations.append(
                    f"<b>{degree_names[degree-1]}:</b><br>"
                    f"Error fitting polynomial<br>"
                    f"R² = N/A"
                )

        # Update layout with increased height for legend and equations
        fig.update_layout(
            title={
                'text': get_text('regression_title', language, y_var=y_var, x_var=x_var),
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title=x_var,
            yaxis_title=y_var,
            height=600,  # Increased height to accommodate legend and equations
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,  # Moved 2 lines below the graph
                xanchor="center",
                x=0.5
            )
        )

        # Store annotation text for later use
        annotation_text = "<br><br>".join(annotations)
        print(f"Annotation text preview: {annotation_text[:200]}...")

        print(f"Returning regression figure with {len(fig.data)} traces")
        print(f"Equations content length: {len(annotation_text)}")

        # Create proper Dash components for HTML rendering
        if annotation_text:
            # Parse the annotation text and create proper components
            components = []
            for block in annotation_text.split('<br><br>'):
                if block.strip():
                    lines = block.split('<br>')
                    for i, line in enumerate(lines):
                        if i == 0:  # First line with bold text
                            if '<b>' in line and '</b>' in line:
                                # Extract bold text
                                bold_text = line.replace('<b>', '').replace('</b>', '')
                                components.append(html.P([
                                    html.Strong(bold_text)
                                ], style={'margin': '2px 0', 'lineHeight': '1.3'}))
                            else:
                                components.append(html.P(line, style={'margin': '2px 0', 'lineHeight': '1.3'}))
                        else:  # Other lines
                            # Handle superscript tags
                            if '<sup>' in line and '</sup>' in line:
                                # Split by superscript
                                parts = line.split('<sup>')
                                processed_parts = []
                                for j, part in enumerate(parts):
                                    if j == 0:
                                        processed_parts.append(part)
                                    else:
                                        if '</sup>' in part:
                                            sup_text, remaining = part.split('</sup>', 1)
                                            processed_parts.append(html.Sup(sup_text))
                                            processed_parts.append(remaining)
                                components.append(html.P(processed_parts, style={'margin': '2px 0', 'lineHeight': '1.3'}))
                            else:
                                components.append(html.P(line, style={'margin': '2px 0', 'lineHeight': '1.3'}))

            equations_content = html.Div(components, style={'textAlign': 'left'})
        else:
            equations_content = html.P(get_text('regression_equations', language), style={'textAlign': 'left'})

        return fig, equations_content
    except Exception as e:
        print(f"Error in regression analysis: {e}")
        import traceback
        traceback.print_exc()
        # Return empty figure and empty equations
        fig = go.Figure()
        fig.update_layout(
            title=get_text('regression_error', language),
            xaxis_title="",
            yaxis_title="",
            height=400
        )
        return fig, ""