import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager
from fix_source_mapping import map_display_names_to_source_ids

def run_test():
    """
    Instantiates the DatabaseManager and calls the method
    that is suspected to be failing.
    """
    print("Attempting to connect to the database and retrieve data...")
    try:
        db_manager = DatabaseManager()
        # The user should replace 'some_keyword' and 'some_source' with values
        # that are expected to return data but are currently failing.
        # For example, 'Benchmarking' and a valid source like 'Crossref'.
        keyword_to_test = "Benchmarking"
        sources_to_test = ["Crossref"]
        source_ids_to_test = map_display_names_to_source_ids(sources_to_test)

        print(f"Testing with keyword: '{keyword_to_test}' and sources: '{sources_to_test}' (IDs: {source_ids_to_test})")
        datasets, valid_sources = db_manager.get_data_for_keyword(keyword_to_test, source_ids_to_test)
        
        if datasets:
            total_points = sum(len(df) for df in datasets.values())
            print(f"Successfully retrieved {total_points} data points from {len(valid_sources)} sources.")
        else:
            print("No data was returned. Check the console for the logged SQL query.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Check the console output for the exact SQL query that was executed.")

if __name__ == "__main__":
    run_test()