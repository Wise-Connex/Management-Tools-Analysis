import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict
from mta import (
    get_ngram_data,
    get_crossref_data,
    get_bain_data,
    get_google_trends_data,
    analyze_data,  # Assuming this function exists in mta.py
)

def choose_keyword() -> str:
    """Prompt the user to choose a keyword."""
    return input("Enter the keyword to analyze: ")

def choose_data_sources() -> List[str]:
    """Prompt the user to choose one or more data sources."""
    sources = ["Google Books Ngram", "Crossref.org", "Bain", "Google Trends"]
    print("Available data sources:")
    for i, source in enumerate(sources, 1):
        print(f"{i}. {source}")
    
    choices = input("Enter the numbers of the data sources you want to use (comma-separated): ")
    selected = [sources[int(i) - 1] for i in choices.split(',')]
    return selected

def get_and_process_data(keyword: str, sources: List[str]) -> Dict[str, pd.DataFrame]:
    """Retrieve and process data for the given keyword from selected sources."""
    data = {}
    for source in sources:
        if source == "Google Books Ngram":
            data[source] = get_ngram_data(keyword)
        elif source == "Crossref.org":
            data[source] = get_crossref_data(keyword)
            data[source] = group_yearly_sum(data[source])
        elif source == "Bain":
            data[source] = get_bain_data(keyword)
            data[source] = group_yearly_mean(data[source])
        elif source == "Google Trends":
            data[source] = get_google_trends_data(keyword)
            data[source] = group_yearly_mean(data[source])
    return data

def group_yearly_sum(df: pd.DataFrame) -> pd.DataFrame:
    """Group Crossref.org data yearly by summing all 12 months before."""
    df['date'] = pd.to_datetime(df['date'])
    return df.groupby(df['date'].dt.year).sum().reset_index()

def group_yearly_mean(df: pd.DataFrame) -> pd.DataFrame:
    """Group data yearly by calculating mean from July to June."""
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year + (df['date'].dt.month > 6).astype(int)
    return df.groupby('year').mean().reset_index()

def visualize_data(data: Dict[str, pd.DataFrame], keyword: str):
    """Visualize the data from different sources."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for source, df in data.items():
        x_column = 'date' if 'date' in df.columns else 'year'
        ax.plot(df[x_column], df['value'], label=source)
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Value')
    ax.set_title(f'Comparison of "{keyword}" across different data sources')
    ax.legend()
    plt.show()

def main():
    keyword = choose_keyword()
    sources = choose_data_sources()
    data = get_and_process_data(keyword, sources)
    visualize_data(data, keyword)
    
    # Perform additional analysis using the analyze_data function from mta.py
    for source, df in data.items():
        print(f"\nAnalysis for {source}:")
        analyze_data(df, keyword)

if __name__ == "__main__":
    main()
