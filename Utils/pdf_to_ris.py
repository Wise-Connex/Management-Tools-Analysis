import os
import re
# from PyPDF2 import PdfReader # No longer needed
import logging
import urllib.parse

# --- Configuration ---
INFORMES_DIR = "../Informes"  # Relative path from utils script to Informes
README_FILENAME = "README.md"
OUTPUT_RIS_FILE = "catalog.ris"  # Output file in the Informes directory
LOG_FILE = "pdf_to_ris.log" # Log file in the same directory as the script

# --- Hardcoded Values ---
# HARDCODED_AUTHORS = ["Diomar G Añez B", "Dimar J Añez B"]
# HARDCODED_AUTHORS = ["Añez B, Diomar G", "Añez B, Dimar J"] # Old Format
HARDCODED_AUTHORS = ["Añez, Diomar", "Añez, Dimar"] # Final Format: Last, First
HARDCODED_PUBLISHER_FALLBACK = "Ediciones Solidum Producciones" # Used if README data missing
HARDCODED_YEAR = "2025"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_FILE, mode='w'), # Overwrite log each run
                        logging.StreamHandler() # Also print logs to console
                    ])

# --- Helper Functions ---

def parse_readme_links(readme_path):
    """Parses a README.md file containing a Markdown table to extract Nro, Informe, Título, Link, and optional DOI, keyed by filename.

    Assumes a table structure like:
    | Nro | Informe | Título | Enlace | DOI? |
    |---|---|---|---|---|
    | 1   | 01-XX   | Title  | [Filename.pdf](URL) | 10.1234/abc or https://doi.org/10.1234/abc |

    Returns a dictionary: { "Filename.pdf": {"nro": "1", "informe": "01-XX", "title": "...", "link": "...", "doi": "10.xxxx/..."} }
    """
    link_data = {}
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    doi_pattern = re.compile(r"\b10\.\d{4,9}/\S+\b")

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        separator_found = False
        data_lines = []
        for line in lines:
            if separator_found and line.strip().startswith('|'):
                 data_lines.append(line.strip())
            elif '|---' in line:
                 separator_found = True
        
        if not separator_found:
             logging.warning(f"Could not find Markdown table separator '|---' in {readme_path}. Cannot parse table.")
             return {}

        for line in data_lines:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 4:
                nro_cell = cells[0]
                informe_cell = cells[1]
                title_cell = cells[2]
                link_cell = cells[3]
                doi_cell = cells[4] if len(cells) >= 5 else ""

                match = link_pattern.search(link_cell)
                if match:
                    filename_from_link_text = match.group(1).strip()
                    url = match.group(2).strip()
                    actual_title = title_cell
                    nro_val = nro_cell # Keep as string for now
                    informe_val = informe_cell

                    if filename_from_link_text.lower().endswith('.pdf'):
                        filename = filename_from_link_text
                        if filename in link_data:
                            logging.warning(f"Duplicate filename found in README table: {filename}. Overwriting entry.")
                        # Extract DOI if present in the optional column
                        doi_value = ""
                        if doi_cell:
                            # Try direct DOI pattern first
                            doi_match = doi_pattern.search(doi_cell)
                            if doi_match:
                                doi_value = doi_match.group(0).strip().rstrip('.')
                            else:
                                # Try to extract from a URL containing doi.org
                                doi_org_match = re.search(r"doi\.org/([^\s)\]]+)", doi_cell, flags=re.IGNORECASE)
                                if doi_org_match:
                                    doi_value = doi_org_match.group(1).strip().rstrip('.')

                        link_data[filename] = {
                            "nro": nro_val,
                            "informe": informe_val,
                            "title": actual_title,
                            "link": url,
                            "doi": doi_value
                        }
                    else:
                        logging.debug(f"Skipping row, filename in link text is not a PDF: {filename_from_link_text} in line: {line}")
                else:
                    logging.warning(f"Could not find valid markdown link '[Filename.pdf](URL)' in Enlace column for line: {line}")
            else:
                logging.warning(f"Skipping malformed table row (expected >= 4 cells): {line}")

    except FileNotFoundError:
        logging.error(f"README file not found at: {readme_path}")
        return None # Indicate critical failure
    except Exception as e:
        logging.error(f"Error reading or parsing README table in {readme_path}: {e}")
        return None # Indicate critical failure

    if not link_data:
        logging.warning(f"No valid table rows with PDF links found in {readme_path}")

    return link_data

# Removed extract_text_from_pdf function
# Removed guess_bibliographic_info function

def format_ris_record(title, link, pdf_filename, nro='000', informe='XX-XX', doi: str = ""):
    """Formats the RIS record using hardcoded/README data, including dynamic publisher, and optional DOI."""
    ris_record = []
    # ris_record.append("TY  - GEN") # Old Type
    # ris_record.append("TY  - RPRT") # Old Type
    # ris_record.append("TY  - EBOOK") # Old Type
    ris_record.append("TY  - BOOK") # Final Type: Book
    ris_record.append(f"TI  - {title}")
    for author in HARDCODED_AUTHORS: # Using updated format
        ris_record.append(f"AU  - {author}")
    # Language
    ris_record.append("LA  - es")

    # Format Nro with zero padding
    try:
        nro_padded = str(int(nro)).zfill(3)
    except ValueError:
        logging.warning(f"Could not parse Nro '{nro}' as integer for {pdf_filename}. Using default '000'.")
        nro_padded = '000'

    # Construct dynamic publisher string
    publisher_str = f"Informe Técnico {informe} ({nro_padded}/115). Serie de Informes Técnicos sobre Herramientas Gerenciales. Ediciones Solidum Producciones."
    ris_record.append(f"PB  - {publisher_str}") # Dynamic Publisher

    ris_record.append(f"PY  - {HARDCODED_YEAR}")
    if doi:
        ris_record.append(f"DO  - {doi}")
    if link:
        ris_record.append(f"UR  - {link}")
    else:
        # Fallback to local file URI
        script_dir = os.path.dirname(os.path.abspath(__file__))
        informes_base_path = os.path.abspath(os.path.join(script_dir, INFORMES_DIR))
        pdf_abs_path = os.path.join(informes_base_path, pdf_filename)
        pdf_uri = 'file:///' + pdf_abs_path.replace('\\', '/')
        ris_record.append(f"UR  - {pdf_uri}")
        logging.debug(f"No link found for {pdf_filename} in README, using local file URI as fallback.")

    ris_record.append(f"FN  - {pdf_filename}")
    ris_record.append("ER  -")
    return "\n".join(ris_record)

# --- Main Script Logic ---
def main():
    logging.info("Starting RIS generation using README.md metadata only (no PDF scanning).")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    informes_abs_path = os.path.abspath(os.path.join(script_dir, INFORMES_DIR))
    readme_path = os.path.join(informes_abs_path, README_FILENAME)
    output_ris_path = os.path.join(informes_abs_path, OUTPUT_RIS_FILE)

    logging.info(f"Reading metadata from: {readme_path}")
    readme_data = parse_readme_links(readme_path)

    if readme_data is None:
        logging.error("Failed to read or parse README.md. Aborting.")
        print("Error: Could not process README.md. Please check the log file.")
        return
    elif not readme_data:
        logging.warning("README.md parsed, but no valid table rows with PDF links found. Output will be empty.")

    # Build RIS exclusively from README rows
    all_ris_records = []
    processed_count = 0

    # Optionally sort by numeric Nro to ensure deterministic order
    def _nro_key(item):
        filename, data = item
        try:
            return int(data.get('nro', '0'))
        except ValueError:
            return 0

    for pdf_filename, entry in sorted(readme_data.items(), key=_nro_key):
        title = entry.get('title', pdf_filename)
        link = entry.get('link', '')
        nro = entry.get('nro', '000')
        informe = entry.get('informe', 'XX-XX')
        doi = entry.get('doi', '')
        logging.info(f"Processing README entry: file='{pdf_filename}', Nro='{nro}', Informe='{informe}', DOI='{doi}'")

        ris_record = format_ris_record(title, link, pdf_filename, nro, informe, doi)
        all_ris_records.append(ris_record)
        processed_count += 1

    try:
        with open(output_ris_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(all_ris_records))
        logging.info(f"Successfully created RIS file: {output_ris_path}")
        print(f"\nSuccessfully created RIS file: {output_ris_path}")
        print(f"Processed {processed_count} entries from {README_FILENAME}.")
    except Exception as e:
        logging.error(f"Error writing RIS file {output_ris_path}: {e}")
        print(f"Error: Could not write RIS file: {e}")

    logging.info("RIS generation process finished.")

if __name__ == "__main__":
    # PyPDF2 no longer required
    main() 