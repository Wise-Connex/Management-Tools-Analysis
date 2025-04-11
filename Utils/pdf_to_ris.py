import os
import re
# from PyPDF2 import PdfReader # No longer needed
import logging
import urllib.parse

# --- Configuration ---
INFORMES_DIR = "../Informes"  # Relative path from utils script to Informes
README_FILENAME = "README.md"
OUTPUT_RIS_FILE = "catalog.ris"  # Output file in the same directory as the script
LOG_FILE = "pdf_to_ris.log" # Log file in the same directory as the script

# --- Hardcoded Values ---
HARDCODED_AUTHORS = ["Diomar G Añez B", "Dimar J Añez B"]
HARDCODED_PUBLISHER = "Ediciones Solidum Producciones"
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
    """Parses a README.md file to extract titles and links, keyed by filename.

    Assumes markdown links like: [Title](.../filename.pdf)
    Returns a dictionary: { "filename.pdf": {"title": "...", "link": "..."} }
    """
    link_data = {}
    # Regex to find markdown links: [text](url)
    # It captures the link text (title) and the URL
    # It's simplified and might need adjustment for complex markdown.
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = link_pattern.findall(content)
        for title, url in matches:
            title = title.strip()
            url = url.strip()
            try:
                # Extract filename from the URL path
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if filename.lower().endswith('.pdf'): # Only consider links ending in .pdf
                    if filename in link_data:
                        logging.warning(f"Duplicate filename found in README links: {filename}. Overwriting entry.")
                    link_data[filename] = {"title": title, "link": url}
                else:
                    logging.debug(f"Skipping non-PDF link in README: {url}")
            except Exception as e:
                logging.warning(f"Could not parse filename from URL '{url}' in README: {e}")

    except FileNotFoundError:
        logging.error(f"README file not found at: {readme_path}")
        return None # Indicate failure
    except Exception as e:
        logging.error(f"Error reading or parsing README file {readme_path}: {e}")
        return None # Indicate failure

    if not link_data:
        logging.warning(f"No valid markdown PDF links found in {readme_path}")

    return link_data

# Removed extract_text_from_pdf function
# Removed guess_bibliographic_info function

def format_ris_record(title, link, pdf_filename):
    """Formats the extracted information into an RIS record string using hardcoded values and README data."""
    ris_record = []
    ris_record.append("TY  - GEN")
    ris_record.append(f"TI  - {title}") # Title from README
    for author in HARDCODED_AUTHORS:
        ris_record.append(f"AU  - {author}") # Hardcoded Authors
    ris_record.append(f"PB  - {HARDCODED_PUBLISHER}") # Hardcoded Publisher
    ris_record.append(f"PY  - {HARDCODED_YEAR}") # Hardcoded Year
    if link:
        ris_record.append(f"UR  - {link}") # Link from README
    else:
        # If no link, maybe use local file path as fallback? Requires INFORMES_DIR
        # Construct absolute path for UR field relative to the project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        informes_base_path = os.path.abspath(os.path.join(script_dir, INFORMES_DIR))
        pdf_abs_path = os.path.join(informes_base_path, pdf_filename)
        pdf_uri = 'file:///' + pdf_abs_path.replace('\\', '/')
        ris_record.append(f"UR  - {pdf_uri}") # Fallback to local file URI
        logging.debug(f"No link found for {pdf_filename} in README, using local file URI as fallback.")

    ris_record.append(f"FN  - {pdf_filename}") # Original PDF filename
    ris_record.append("ER  -")
    return "\n".join(ris_record)

# --- Main Script Logic ---
def main():
    logging.info("Starting PDF to RIS conversion process using README.md for metadata.")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    informes_abs_path = os.path.abspath(os.path.join(script_dir, INFORMES_DIR))
    readme_path = os.path.join(informes_abs_path, README_FILENAME)
    output_ris_path = os.path.join(script_dir, OUTPUT_RIS_FILE)

    logging.info(f"Reading metadata from: {readme_path}")
    readme_data = parse_readme_links(readme_path)

    if readme_data is None:
        logging.error("Failed to read or parse README.md. Aborting.")
        print("Error: Could not process README.md. Please check the log file.")
        return
    elif not readme_data:
        logging.warning("README.md parsed, but no valid [Title](.../filename.pdf) links found. Output may be incomplete.")

    logging.info(f"Scanning directory for PDF files: {informes_abs_path}")
    if not os.path.isdir(informes_abs_path):
        logging.error(f"Directory not found: {informes_abs_path}")
        print(f"Error: Directory not found: {informes_abs_path}")
        return

    pdf_files = [f for f in os.listdir(informes_abs_path) if f.lower().endswith('.pdf')]
    logging.info(f"Found {len(pdf_files)} PDF files in the directory.")

    all_ris_records = []
    processed_count = 0
    missing_readme_entry = []

    for pdf_filename in pdf_files:
        logging.info(f"Processing file: {pdf_filename}")

        if pdf_filename in readme_data:
            entry = readme_data[pdf_filename]
            title = entry['title']
            link = entry['link']
            logging.info(f"  -> Found in README: Title='{title}', Link='{link}'")
        else:
            logging.warning(f"  -> Entry for {pdf_filename} not found in {README_FILENAME}. Using placeholders.")
            title = f"{pdf_filename} - Title Not Found in README"
            link = "" # No link available, format_ris_record will use local file URI
            missing_readme_entry.append(pdf_filename)

        # Don't need to extract text anymore
        ris_record = format_ris_record(title, link, pdf_filename)
        all_ris_records.append(ris_record)
        processed_count += 1

    if all_ris_records:
        try:
            with open(output_ris_path, 'w', encoding='utf-8') as f:
                f.write("\n\n".join(all_ris_records))
            logging.info(f"Successfully created RIS file: {output_ris_path}")
            print(f"\nSuccessfully created RIS file: {output_ris_path}")
            print(f"Processed {processed_count} PDF files found in the directory.")
            if missing_readme_entry:
                logging.warning(f"Entries missing in {README_FILENAME} for {len(missing_readme_entry)} PDF files: {', '.join(missing_readme_entry)}")
                print(f"Warning: {len(missing_readme_entry)} PDF files were found in the directory but had no matching entry in {README_FILENAME}. See log for details.")

        except Exception as e:
            logging.error(f"Error writing RIS file {output_ris_path}: {e}")
            print(f"Error: Could not write RIS file: {e}")
    else:
        logging.warning("No PDF files found or processed in the directory.")
        print("No PDF files found in the Informes directory.")

    logging.info("RIS generation process finished.")

if __name__ == "__main__":
    # PyPDF2 no longer required
    main() 