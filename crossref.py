import requests
import csv
from datetime import datetime, timedelta
import paramiko
from io import StringIO
from habanero import Crossref
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_crossref_data(keyword):
    """
    Retrieves publication data from Crossref based on the given keyword.
    
    Args:
    keyword (str): The search term to query Crossref.
    
    Returns:
    list of tuples: Each tuple contains (datetime, count), where datetime is the publication date
                    and count is always 1 (representing one publication).
    """
    cr = Crossref()
    results = []
    
    current_year = datetime.now().year
    batch_size = 1000
    cursor = '*'
    
    logger.debug(f"Iniciando consulta de Crossref para la palabra clave: {keyword}")
    
    while cursor:
        logger.debug(f"Consultando Crossref con cursor: {cursor}")
        query_result = cr.works(query=keyword, select=['published', 'abstract'], 
                                limit=batch_size, cursor=cursor,
                                filter={'from-pub-date': '1950', 'until-pub-date': str(current_year)})
        
        # Check if query_result is a list or a dictionary
        if isinstance(query_result, list):
            items = query_result
            logger.debug(f"El resultado de la consulta es una lista con {len(items)} elementos")
            # If it's a list, we need to extract the actual items
            if items and isinstance(items[0], dict) and 'message' in items[0]:
                items = items[0].get('message', {}).get('items', [])
                logger.debug(f"Se extrajeron {len(items)} elementos de la lista")
        else:
            items = query_result.get('message', {}).get('items', [])
            logger.debug(f"El resultado de la consulta es un diccionario con {len(items)} elementos")
        
        if not items:
            logger.debug("No se encontraron elementos en este lote, terminando el bucle")
            break
        
        for item in items:
            if isinstance(item, dict) and 'published' in item and 'date-parts' in item['published']:
                date = item['published']['date-parts'][0]
                if len(date) >= 2:
                    year, month = date[0], date[1]
                    results.append((datetime(year, month, 1), 1))
            else:
                logger.debug(f"Se omitió un elemento debido a fecha faltante o inválida: {item.get('published', 'Sin datos de publicación')}")
        
        # Update cursor for next iteration
        if isinstance(query_result, dict):
            cursor = query_result.get('message', {}).get('next-cursor')
            logger.debug(f"Cursor actualizado a: {cursor}")
        else:
            cursor = None
            logger.debug("No se encontró cursor, finalizando consulta")
        
        if not cursor:
            logger.debug("No hay más resultados, terminando el bucle")
            break
    
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