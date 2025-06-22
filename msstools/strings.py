from pathlib import Path
import unicodedata

def remove_accents(input_text: str) -> str:
    """Removes accents from a string."""
    normalized_text = unicodedata.normalize('NFKD', input_text)
    text_without_accents = ''.join([c for c in normalized_text if unicodedata.category(c) != 'Mn'])
    return text_without_accents


def remove_accents_from_file(input_file_path: str|Path, output_file_path: str|Path) -> None:
    """Reads a file, removes accents from each line, and writes the cleaned lines to a new file."""
    if not input_file_path or not output_file_path:
        raise ValueError("Input and output file paths must be provided.")

    assert input_file_path != output_file_path, "Input and output file paths must be different."
    
    input_file_path = Path(input_file_path)
    if not input_file_path.exists():
        raise FileNotFoundError(f"Input file '{input_file_path}' does not exist.")
    
    # Ensure the output directory exists
    output_file_path = Path(output_file_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w', encoding='utf-8') as output_file:
        for line in input_file:
            cleaned_line = remove_accents(line)
            output_file.write(cleaned_line)
    print(f"Accents removed and saved to {output_file_path}")
