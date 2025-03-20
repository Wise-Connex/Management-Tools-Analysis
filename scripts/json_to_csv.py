import json
import csv
import os
import argparse

def convert_json_to_csv(json_file_path, csv_file_path, fieldnames=None):
    """
    Convierte un archivo JSON a CSV.
    
    Args:
        json_file_path (str): Ruta al archivo JSON de entrada
        csv_file_path (str): Ruta al archivo CSV de salida
        fieldnames (list): Lista opcional de campos a extraer
    """
    # Verificar si el archivo JSON existe
    if not os.path.exists(json_file_path):
        print(f"Error: El archivo JSON no existe en la ruta: {json_file_path}")
        return False

    try:
        # Leer el archivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraer los items
        items = data.get('items', data)  # Intenta obtener 'items' o usa todo el data si no existe
        
        # Si no se especifican fieldnames, usar todas las claves del primer item
        if not fieldnames and items:
            if isinstance(items, list) and items:
                fieldnames = list(items[0].keys())
            else:
                print("Error: El JSON no contiene una lista de items válida")
                return False

        # Escribir el CSV
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                row = {}
                for field in fieldnames:
                    value = item.get(field, [])
                    # Manejar campos que pueden ser listas
                    if isinstance(value, list):
                        value = value[0] if value else ''
                    # Limpiar strings de saltos de línea
                    if isinstance(value, str):
                        value = value.replace('\n', ' ').replace('\r', '')
                    row[field] = value
                writer.writerow(row)

        print(f"CSV file created successfully at: {csv_file_path}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convierte un archivo JSON a CSV.')
    parser.add_argument('json_file', help='Ruta al archivo JSON de entrada')
    parser.add_argument('csv_file', help='Ruta al archivo CSV de salida')
    parser.add_argument('--fields', nargs='+', help='Campos a extraer (opcional)')
    
    args = parser.parse_args()
    
    convert_json_to_csv(args.json_file, args.csv_file, args.fields)

if __name__ == "__main__":
    main()
