import requests
import csv
from datetime import datetime, timedelta
import logging
import os
import time
from urllib.parse import quote_plus, urlencode
import hashlib  # Add this import at the top of the file with other imports

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_crossref_data(keywords):
    results = []
    
    current_year = datetime.now().year
    rows = 1000
    cursor = '*'
    total_items = 0
    
    # Ensure keywords is a list, even if it's a single keyword
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # Join keywords with 'OR' instead of commas
    encoded_keywords = ' OR '.join(quote_plus(kw.strip()) for kw in keywords)
    base_url = "https://api.crossref.org/works"
    
    logger.debug(f"Iniciando consulta de Crossref para las palabras clave: {encoded_keywords}")
    
    # Initialize batch counter and total batches
    batch_counter = 0
    total_batches = None

    while cursor:
        batch_counter += 1
        try:
            params = {
                'query': encoded_keywords,
                'rows': rows,
                'cursor': cursor,
                'filter': f'from-pub-date:1950,until-pub-date:{current_year}',
                'select': 'DOI,title,published'  # Removed 'keyword' from select
            }
            
            full_url = f"{base_url}?{urlencode(params)}"
            
            logger.debug(f"Requesting URL: {full_url}")
            
            response = requests.get(full_url)
            response.raise_for_status()
            data = response.json()
            
            message = data.get('message', {})
            items = message.get('items', [])
            next_cursor = message.get('next-cursor')
            total_results = message.get('total-results', 0)
            
            # Calculate total batches if not done yet
            if total_batches is None:
                total_batches = -(-total_results // rows)  # Ceiling division
                logger.debug(f"Total de resultados esperados: {total_results}")
                logger.debug(f"Número total de batches esperados: {total_batches}")
            
            logger.debug(f"\nProcesando batch {batch_counter} de {total_batches}")
            logger.debug(f"Se obtuvieron {len(items)} elementos en este batch")
            
            selected_items = 0
            for item in items:
                if 'published' in item and 'date-parts' in item['published']:
                    date = item['published']['date-parts'][0]
                    if len(date) >= 2:
                        year, month = date[0], date[1]
                        results.append((datetime(year, month, 1), 1))
                        selected_items += 1
                else:
                    logger.debug(f"Se omitió un elemento debido a fecha faltante o inválida: {item.get('published', 'Sin datos de publicación')}")
            
            total_items += len(items)
            logger.debug(f"En este batch se trajeron {len(items)} elementos y se seleccionaron {selected_items}\n\n")
            
            # Check if we've processed all expected batches
            if batch_counter >= total_batches:
                logger.debug("Se han procesado todos los batches esperados. Terminando el bucle.")
                break
            
            cursor = next_cursor
            if not cursor:
                logger.debug("No hay más resultados, terminando el bucle")
                break
            
            time.sleep(1)  # Add a small delay to avoid hitting rate limits
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar Crossref: {str(e)}")
            logger.error(f"URL de la solicitud: {full_url}")
            logger.error(f"Respuesta del servidor: {response.text}")  # Log the response text
            return None  # Return None instead of breaking the loop
    
    logger.debug(f"Total de elementos consultados: {total_items}")
    logger.debug(f"Total de resultados recolectados: {len(results)}")
    return results

def group_by_month(data):
    """
    Groups the input data by month, including all months from 1950 to the current month.
    
    Args:
    data (list of tuples): Each tuple contains (datetime, count) as returned by get_crossref_data.
    
    Returns:
    dict: A dictionary with keys as 'YYYY-MM' strings and values as the count of publications for that month.
    """
    grouped = {}
    start_date = datetime(1950, 1, 1)
    current_date = datetime.now().replace(day=1)
    
    date = start_date
    while date <= current_date:
        key = date.strftime("%Y-%m")
        grouped[key] = 0
        date += timedelta(days=32)
        date = date.replace(day=1)
    
    for date, count in data:
        if date <= current_date:
            key = date.strftime("%Y-%m")
            grouped[key] += count
    
    return grouped

def save_to_local_csv(data, keywords):
    """
    Saves the grouped data into a CSV file in the local 'dbase' folder.
    
    Args:
    data (dict): The grouped data as returned by group_by_month.
    keywords (list): The search keywords used.
    
    Returns:
    str: The path to the saved CSV file.
    """
    # Ensure the 'dbase' directory exists
    os.makedirs('dbase', exist_ok=True)
    
    # Create a unique identifier using the first keyword and a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    keyword_hash = hashlib.md5(keywords[0].encode()).hexdigest()[:6]
    
    # Use only the first keyword
    keyword_prefix = keywords[0][:10]
    
    # Create filename, ensuring it's no longer than 20 characters
    filename = f"CR_{keyword_prefix}_{keyword_hash}_{timestamp}"
    filename = filename[:20] + '.csv'  # Truncate to 16 chars and add .csv extension
    
    filepath = os.path.join('dbase', filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", keywords[0]])
        for date, count in sorted(data.items()):
            writer.writerow([date, count])
    
    # Create or update index file
    index_filename = create_or_update_index(keywords[0], filename)
    
    return filepath, index_filename

def create_or_update_index(keyword, filename):
    base_name = "CR-index"
    extension = ".txt"
    index = 0
    
    # Ensure the 'dbase' directory exists
    os.makedirs('dbase', exist_ok=True)
    
    while True:
        index_filename = f"{base_name}{index:03d}{extension}"
        full_path = os.path.join('dbase', index_filename)
        if not os.path.exists(full_path):
            break
        index += 1
    
    with open(full_path, 'a') as index_file:
        index_file.write(f"{keyword},{filename}\n")
    
    return index_filename

def main(keywords):
    """
    Main function that orchestrates the entire process.
    
    Args:
    keywords (list): List of search terms for Crossref query.
    
    Returns:
    None
    """
    print(f"Retrieving data for keywords: {', '.join(keywords)}")
    
    # Test basic connectivity to Crossref API
    try:
        test_response = requests.get("https://api.crossref.org/works?query=test&rows=1")
        test_response.raise_for_status()
        print("Successfully connected to Crossref API")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Crossref API: {str(e)}")
        return

    data = get_crossref_data(keywords)
    if data is None:
        print("No se pudieron obtener datos de Crossref. Abortando el proceso.")
        return
    
    print(f"Data retrieved: {len(data)} items")
    if data:
        print("Sample of data:")
        for item in data[:5]:  # Print first 5 items
            print(item)
        grouped_data = group_by_month(data)
        filepath, index_filename = save_to_local_csv(grouped_data, keywords)
        print(f"Data saved to local file: {filepath}")
        print(f"Index updated in file: {index_filename}")
    else:
        print("No se encontraron datos para las palabras clave proporcionadas.")

def process_file(filename):
    """
    Procesa cada línea del archivo como un conjunto de palabras clave.
    
    Args:
    filename (str): Nombre del archivo que contiene las palabras clave.
    
    Returns:
    None
    """
    with open(filename, 'r') as file:
        keyword_lines = file.read().splitlines()
    
    for line in keyword_lines:
        keywords = [kw.strip() for kw in line.split(',') if kw.strip()]
        if keywords:  # Only process if there are keywords
            print(f"\nProcesando palabras clave: {', '.join(keywords)}")
            main(keywords)
        else:
            print(f"Línea vacía o inválida encontrada en {filename}. Saltando...")

if __name__ == "__main__":
    opcion = input("Elija una opción:\n1. Cargar palabras clave desde archivo 'tools.txt'\n2. Ingresar palabras clave específicas\nOpción: ")
    
    if opcion == "1":
        if os.path.exists("tools.txt"):
            process_file("tools.txt")
        else:
            print("El archivo 'tools.txt' no existe. Por favor, créelo y vuelva a intentar.")
    elif opcion == "2":
        keywords_input = input("Por favor, ingrese las Herramientas Gerenciales a buscar (separadas por comas): ")
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
        if keywords:
            main(keywords)
        else:
            print("No se ingresaron palabras clave válidas.")
    else:
        print("Opción no válida. Por favor, elija 1 o 2.")
