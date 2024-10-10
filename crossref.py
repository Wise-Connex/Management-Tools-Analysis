import requests
import csv
from datetime import datetime, timedelta
import logging
import os
import time
from urllib.parse import quote_plus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_crossref_data(keyword):
    results = []
    
    current_year = datetime.now().year
    rows = 1000
    cursor = '*'
    total_items = 0
    max_results = 1000000  # Set a high limit to ensure we get all results
    
    encoded_keyword = quote_plus(keyword)
    base_url = "https://api.crossref.org/works"
    
    logger.debug(f"Iniciando consulta de Crossref para la palabra clave codificada: {encoded_keyword}")
    
    # Initialize batch counter and total batches
    batch_counter = 0
    total_batches = None

    while cursor and total_items < max_results:
        batch_counter += 1
        #logger.debug(f"Consultando Crossref con cursor: {cursor}")
        try:
            params = {
                'query': encoded_keyword,
                'rows': rows,
                'cursor': cursor,
                'filter': f'from-pub-date:1950,until-pub-date:{current_year}',
                'select': 'published'
            }
            response = requests.get(base_url, params=params)
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
            
            logger.debug(f"Procesando batch {batch_counter} de {total_batches}")
            logger.debug(f"Se obtuvieron {len(items)} elementos en este batch")
            
            # Add this check to break the loop if we've processed all batches
            if batch_counter >= total_batches:
                logger.debug("Se han procesado todos los batches esperados. Terminando el bucle.")
                break

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
            logger.debug(f"En este batch se trajeron {len(items)} elementos y se seleccionaron {selected_items}")
            
            cursor = next_cursor
            if not cursor:
                logger.debug("No hay más resultados, terminando el bucle")
                break
            
            time.sleep(1)  # Add a small delay to avoid hitting rate limits
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar Crossref: {str(e)}")
            break
    
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

def save_to_local_csv(data, keyword):
    """
    Saves the grouped data into a CSV file in the local 'dbase' folder.
    
    Args:
    data (dict): The grouped data as returned by group_by_month.
    keyword (str): The search keyword used, which becomes part of the filename.
    
    Returns:
    str: The path to the saved CSV file.
    """
    import os
    
    # Ensure the 'dbase' directory exists
    os.makedirs('dbase', exist_ok=True)
    
    filename = f"CR_{keyword.replace(' ', '_')}.csv"
    filepath = os.path.join('dbase', filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", keyword])
        for date, count in sorted(data.items()):
            writer.writerow([date, count])
    
    return filepath

def main(keyword):
    """
    Main function that orchestrates the entire process.
    
    Args:
    keyword (str): The search term for Crossref query.
    
    Returns:
    None
    """
    print(f"Retrieving data for keyword: {keyword}")
    data = get_crossref_data(keyword)
    print(f"Data retrieved: {len(data)} items")
    if data:
        print("Sample of data:")
        for item in data[:5]:  # Print first 5 items
            print(item)
    grouped_data = group_by_month(data)
    filepath = save_to_local_csv(grouped_data, keyword)
    print(f"Data saved to local file: {filepath}")

def process_file(filename):
    """
    Procesa cada línea del archivo como una palabra clave.
    
    Args:
    filename (str): Nombre del archivo que contiene las palabras clave.
    
    Returns:
    None
    """
    with open(filename, 'r') as file:
        keywords = file.read().splitlines()
    
    for keyword in keywords:
        print(f"\nProcesando palabra clave: {keyword}")
        main(keyword)

if __name__ == "__main__":
    opcion = input("Elija una opción:\n1. Cargar palabras clave desde archivo 'tools.txt'\n2. Ingresar una palabra clave específica\nOpción: ")
    
    if opcion == "1":
        if os.path.exists("tools.txt"):
            process_file("tools.txt")
        else:
            print("El archivo 'tools.txt' no existe. Por favor, créelo y vuelva a intentar.")
    elif opcion == "2":
        keyword = input("Por favor, ingrese la Herramienta Gerencial a buscar: ")
        main(keyword)
    else:
        print("Opción no válida. Por favor, elija 1 o 2.")