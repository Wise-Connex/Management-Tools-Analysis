import csv
import re

def reformat_notes(notes_text, tool_name, doi, source, links):
    """Reformat the notes text according to the specified format."""

    # Extract sections from the notes text using regex
    sections = {
        'Descriptores logicos': '',
        'Parametros de Busqueda': '',
        'Indice Relativo': '',
        'Metodologia': '',
        'Perfil de Usuarios': '',
        'Limitaciones': ''
    }

    # Use regex to find each section
    import re

    for section in sections.keys():
        # Look for the section header followed by content until the next section or end
        pattern = rf'{re.escape(section)}:\s*(.*?)(?=\. \w+:|Fuente:|$)'
        match = re.search(pattern, notes_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Clean up the content
            content = re.sub(r'\s+', ' ', content)  # Replace multiple whitespace with single space
            sections[section] = content

    # Build the reformatted text
    reformatted = f"{tool_name.upper()}\n\n"

    # Map to display names with accents
    display_names = {
        'Descriptores logicos': 'Descriptores lógicos',
        'Parametros de Busqueda': 'Parámetros de búsqueda',
        'Indice Relativo': 'Índice Relativo',
        'Metodologia': 'Metodología',
        'Perfil de Usuarios': 'Perfil de Usuarios',
        'Limitaciones': 'Limitaciones'
    }

    for section, content in sections.items():
        if content:  # Only include sections that have content
            display_name = display_names.get(section, section)
            reformatted += f"**{display_name}:** {content}\n\n"

    # Add Fuente y DOI at the end
    if source.startswith('BAIN'):
        # For BAIN sources, extract the "Fuente:" section from the notes
        fuente_match = re.search(r'Fuente:\s*(.*?)(?:\s*$)', notes_text, re.DOTALL)
        if fuente_match:
            fuente_content = fuente_match.group(1).strip()
            # Add BAIN type prefix
            bain_type = "Satisfaccion" if "Satisfacción" in source else "Usabilidad"
            reformatted += f"Fuente: Bain {bain_type}. {fuente_content} {doi}"
        else:
            reformatted += f"Fuente y DOI: {doi}"
    else:
        # For other sources, use the Links column
        if links and links.strip():
            reformatted += f"Fuente y DOI: {links.strip()} {doi}"
        else:
            reformatted += f"Fuente y DOI: {doi}"

    return reformatted

def main():
    input_file = 'pub-assets/notes_and_doi_spanish.csv'
    output_file = 'pub-assets/notes_and_doi_reformatted.csv'

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row['Notes'] and row['Notes'] != ',':
                # Reformat the Notes column
                reformatted_notes = reformat_notes(
                    row['Notes'],
                    row['Herramienta'],
                    row['DOI'],
                    row['Source'],
                    row['Links']
                )
                row['Notes'] = reformatted_notes

            writer.writerow(row)

    print(f"Reformatted notes saved to {output_file}")

if __name__ == "__main__":
    main()