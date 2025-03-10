#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV Reader for Management Tools Analysis Project

This script provides utility functions to read and process the CSV files
containing management tools analysis data from different sources.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory containing the CSV files
CSV_DIR = "pub-assets"

# List of data source prefixes
DATA_SOURCES = {
    "BS": "Bain & Company Satisfaction",
    "BU": "Bain & Company Usability",
    "GT": "Google Trends",
    "CR": "Crossref Academic Publications",
    "GB": "Google Books Ngram"
}

def read_csv_file(filename, directory=CSV_DIR):
    """
    Read a CSV file with proper encoding and delimiter settings.
    
    Args:
        filename: Name of the CSV file
        directory: Directory containing the CSV file
        
    Returns:
        pandas DataFrame with the CSV data
    """
    file_path = os.path.join(directory, filename)
    
    try:
        # Read the file with UTF-8 encoding and semicolon delimiter
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        print(f"Successfully read {filename}")
        return df
    except UnicodeDecodeError:
        # Fallback to Latin-1 encoding if UTF-8 fails
        df = pd.read_csv(file_path, sep=';', encoding='latin1')
        print(f"Read {filename} using Latin-1 encoding")
        return df
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def get_all_data():
    """
    Read all CSV files and return them as a dictionary of DataFrames.
    
    Returns:
        Dictionary with data source keys and DataFrame values
    """
    data = {}
    
    for source_prefix in DATA_SOURCES.keys():
        filename = f"{source_prefix}-Portada.csv"
        df = read_csv_file(filename)
        
        if df is not None:
            # Clean the DataFrame
            data[source_prefix] = df
            
    return data

def get_tools_list(data):
    """
    Extract the list of management tools from the data.
    
    Args:
        data: Dictionary with data source keys and DataFrame values
        
    Returns:
        List of management tools
    """
    # Use BS data as reference since all sources have the same tools
    if "BS" in data:
        return data["BS"]["Herramienta"].tolist()
    
    # Fallback to any available source
    for source_prefix in DATA_SOURCES.keys():
        if source_prefix in data:
            return data[source_prefix]["Herramienta"].tolist()
    
    return []

def summarize_data(data):
    """
    Print a summary of the data for each source.
    
    Args:
        data: Dictionary with data source keys and DataFrame values
    """
    print("\nData Summary:")
    print("="*50)
    
    for source_prefix, df in data.items():
        print(f"\n{DATA_SOURCES[source_prefix]} Data:")
        print("-"*50)
        print(f"Number of records: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        print("\nSample data:")
        print(df.head(2))
    
    # List all management tools
    tools = get_tools_list(data)
    print("\nManagement Tools Analyzed:")
    print("-"*50)
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")

def create_tools_dataframe(data):
    """
    Create a consolidated DataFrame with all management tools.
    
    Args:
        data: Dictionary with data source keys and DataFrame values
        
    Returns:
        DataFrame with management tools and their source codes
    """
    tools_data = []
    
    for source_prefix, df in data.items():
        for _, row in df.iterrows():
            tools_data.append({
                'Source': DATA_SOURCES[source_prefix],
                'SourceCode': source_prefix,
                'Tool': row['Herramienta'],
                'ToolCode': row['Cód'],
                'Title': row['Título'],
                'Subtitle': row['Subtítulo']
            })
    
    return pd.DataFrame(tools_data)

def visualize_tools_count(tools_df):
    """
    Create a visualization of the tools count across sources.
    
    Args:
        tools_df: DataFrame with tool data
    """
    plt.figure(figsize=(12, 8))
    
    # Count tools by source
    source_counts = tools_df.groupby('Source').size().reset_index(name='Count')
    
    # Create bar plot
    sns.barplot(x='Source', y='Count', data=source_counts)
    plt.title('Management Tools Count by Data Source')
    plt.xlabel('Data Source')
    plt.ylabel('Number of Tools')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'tools_by_source.png'))
    plt.close()
    
    print(f"Visualization saved to {output_dir}/tools_by_source.png")

def main():
    """Main function to execute the script."""
    print("Management Tools Analysis Project - CSV Reader")
    print("="*50)
    
    # Read all CSV files
    data = get_all_data()
    
    # Summarize the data
    summarize_data(data)
    
    # Create consolidated DataFrame
    tools_df = create_tools_dataframe(data)
    
    # Save consolidated DataFrame
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    tools_df.to_csv(os.path.join(output_dir, 'management_tools.csv'), index=False)
    print(f"\nConsolidated data saved to {output_dir}/management_tools.csv")
    
    # Visualize the data
    visualize_tools_count(tools_df)

if __name__ == "__main__":
    main() 