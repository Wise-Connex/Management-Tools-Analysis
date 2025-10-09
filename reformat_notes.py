import csv
import re

def reformat_notes(notes_text, tool_name, doi, source, links):
    """Reformat the notes text according to the specified format."""

    # Extract the tool name from the beginning if present
    if ':' in notes_text and not notes_text.startswith('http'):
        tool_part, content = notes_text.split(':', 1)
        content = content.strip()
    else:
        content = notes_text

    # Format source name properly (replace underscores with spaces)
    source_display = source.replace('_', ' ')
    
    # Build the reformatted text with bold larger title (using ** for bold, +3px handled in CSS)
    reformatted = f"**{tool_name.upper()} - {source_display}**\n\n"

    # Find all sections using regex with specific headers
    section_pattern = r'(Descriptores lógicos|Parámetros de búsqueda|Índice Relativo|Índice|Metodología|Perfil de Usuarios|Limitaciones):\s*(.*?)(?=(?:Descriptores lógicos|Parámetros de búsqueda|Índice Relativo|Índice|Metodología|Perfil de Usuarios|Limitaciones|Fuente):|$)'
    sections = re.findall(section_pattern, content, re.DOTALL)

    for section_name, section_content in sections:
        section_content = section_content.strip()
        # Clean up the content
        section_content = re.sub(r'\s+', ' ', section_content)
        if section_content:
            reformatted += f"**{section_name}:** {section_content}\n\n"

    # Handle Fuente section - extract but don't add to body
    # The fuente will be displayed separately in the modal footer
    # For BAIN sources, keep the citation references
    fuente_match = re.search(r'Fuente:\s*(.*)', content, re.DOTALL)
    if fuente_match:
        fuente_content = fuente_match.group(1).strip()
        # Check if this is a BAIN source (contains Rigby citations)
        if 'Rigby' in fuente_content:
            # BAIN source - add the citation as "Fuente:" in the body
            reformatted += f"**Fuente:** {fuente_content}"
        # For non-BAIN sources, don't add anything to the body
        # The URL and DOI will be shown in the modal footer by app.py

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