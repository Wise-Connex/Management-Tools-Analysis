# *************************************************************************************
# FILE INDEX BUILDER
# *************************************************************************************

import csv
import os
from typing import Dict, List, Optional
from pprint import pformat

def read_index_file(file_path: str) -> Dict[str, str]:
    """Read an index file and return a dictionary mapping keywords to filenames."""
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result[row['Keyword']] = row['Filename']
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}
    return result

def create_tools_dictionary() -> Dict[str, List[str]]:
    """Create the tools dictionary from index files."""
    # Initialize empty dictionary for results
    tools_dict: Dict[str, List[str]] = {}
    
    # Get the root path (two levels up from this script)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define index files and their positions
    index_files = {
        os.path.join(root_path, 'NewDBase/GTIndex.csv'): 0,  # Google Trends
        os.path.join(root_path, 'NewDBase/GBIndex.csv'): 2,  # Google Books
        os.path.join(root_path, 'NewDBase/BUIndex.csv'): 3,  # Bain Usage
        os.path.join(root_path, 'NewDBase/CRIndex.csv'): 4,  # Crossref
        os.path.join(root_path, 'NewDBase/BSIndex.csv'): 5   # Bain Satisfaction
    }
    
    # Process each index file
    for file_path, position in index_files.items():
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found")
            continue
            
        index_data = read_index_file(file_path)
        
        # Update dictionary with data from this index
        for keyword, filename in index_data.items():
            if keyword not in tools_dict:
                # Initialize new entry with empty strings and keyword list
                tools_dict[keyword] = [''] * 6
                tools_dict[keyword][1] = [keyword]
            
            # Update the specific position if it's empty
            if not tools_dict[keyword][position]:
                tools_dict[keyword][position] = filename
                print(f"Updated {keyword} position {position} with {filename}")
    
    # Sort dictionary alphabetically
    return dict(sorted(tools_dict.items()))

def write_tools_file(tools_dict: Dict[str, List[str]]) -> None:
    """Write the tools dictionary to tools.py in a clean, readable format."""
    header = '''# *************************************************************************************
# TOOLS DICTIONARY
# *************************************************************************************

# Dictionary Structure:
#   "Tool Name": [
#       "Google_Trends_file.csv",      # Index 0: Google Trends (GT)
#       ["Tool Name"],                 # Index 1: Keywords list
#       "Google_Books_file.csv",       # Index 2: Google Books (GB)
#       "Bain_Usage_file.csv",         # Index 3: Bain Usage (BU)
#       "Crossref_file.csv",           # Index 4: Crossref (CR)
#       "Bain_Satisfaction_file.csv"   # Index 5: Bain Satisfaction (BS)
#   ]

'''
    
    # Format the dictionary in a readable way
    dict_str = pformat(tools_dict, indent=4, width=100)
    
    # Get the root path and create the output file path
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_path, 'tools.py')
    
    # Write to tools.py in the root directory
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write('tool_file_dic = ')
        f.write(dict_str)

def main():
    """Main function to build and save the tools dictionary."""
    print("Building tools dictionary...")
    tools_dict = create_tools_dictionary()
    
    print("\nWriting tools.py file...")
    write_tools_file(tools_dict)
    
    print("\nDictionary Summary:")
    print("------------------")
    for tool, data in tools_dict.items():
        print(f"\n{tool}:")
        print(f"  GT: {data[0]}")
        print(f"  Keywords: {data[1]}")
        print(f"  GB: {data[2]}")
        print(f"  BU: {data[3]}")
        print(f"  CR: {data[4]}")
        print(f"  BS: {data[5]}")
    
    print("\nProcess completed. tools.py has been created in the root directory.")

if __name__ == "__main__":
    main()