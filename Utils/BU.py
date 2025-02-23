import pandas as pd
import os
import random
import unicodedata
import re

def clean_filename(name):
    """Clean tool name to create valid filename"""
    # Remove accents and convert to ASCII
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Replace spaces with underscores and remove special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name

def generate_random_id():
    """Generate random 4-digit ID"""
    return str(random.randint(0, 9999)).zfill(4)

def process_data():
    # Create NewDBase directory if it doesn't exist
    os.makedirs('../NewDBase', exist_ok=True)
    
    # Read the input CSV file
    df = pd.read_csv('../rawData/Tabla Python Dimar - Bain - Usabilidad.csv')
    
    # Initialize index dataframe
    index_data = {'Keyword': [], 'Filename': []}
    
    # Process each unique tool
    for tool in df['Herramienta Gerencial'].unique():
        # Get data for this tool
        tool_data = df[df['Herramienta Gerencial'] == tool].copy()
        
        # Format year column
        tool_data['Year'] = tool_data['Year'].astype(str) + '-01'
        
        # Create output dataframe
        output_df = pd.DataFrame({
            'Year': tool_data['Year'],
            tool: tool_data['Usabilidad']
        })
        
        # Generate filename
        clean_name = clean_filename(tool)
        random_id = generate_random_id()
        filename = f'BU_{clean_name}_{random_id}.csv'
        
        # Save to CSV
        output_path = os.path.join('../NewDBase', filename)
        output_df.to_csv(output_path, index=False)
        
        # Add to index
        index_data['Keyword'].append(tool)
        index_data['Filename'].append(filename)
    
    # Save index file
    index_df = pd.DataFrame(index_data)
    index_df.to_csv('../NewDBase/BUIndex.csv', index=False)

if __name__ == '__main__':
    process_data() 