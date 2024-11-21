import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from correlation import calculate_correlation  # Import your correlation function

# Set page configuration
st.set_page_config(
    page_title="Correlation Dashboard",
    layout="wide"
)

# Title
st.title("Correlation Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the data
    df = pd.read_csv(uploaded_file)
    
    # Sidebar for controls
    st.sidebar.header("Settings")
    
    # Select columns for correlation
    columns = df.select_dtypes(include=['float64', 'int64']).columns
    col1 = st.sidebar.selectbox("Select first variable", columns)
    col2 = st.sidebar.selectbox("Select second variable", columns, index=1 if len(columns) > 1 else 0)
    
    # Create two columns for the layout
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("Scatter Plot")
        fig = px.scatter(df, x=col1, y=col2, trendline="ols")
        st.plotly_chart(fig)
    
    with right_col:
        st.subheader("Correlation Heatmap")
        corr_matrix = df[columns].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        st.pyplot(fig)
    
    # Calculate and display correlation statistics
    st.subheader("Correlation Statistics")
    if hasattr(calculate_correlation, '__call__'):
        correlation_result = calculate_correlation(df[col1], df[col2])
        st.write(correlation_result) 