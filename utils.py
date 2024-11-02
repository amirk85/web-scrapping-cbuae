from typing import Dict, List


def extract_text_by_headers(
    text_lines: List[str], headers: List[str]
) -> Dict[str, List[str]]:
    header_dict = {}
    current_header = None
    current_text = []

    for line in text_lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if line in headers:
            # If we encounter a new header
            if current_header:
                # Store the previous header and its text if it exists
                header_dict[current_header] = current_text

            # Update the current header and reset the current text
            current_header = line
            current_text = []
        elif current_header:
            # Add the line to the current header's text
            current_text.append(line)

    # Add the last header and its text if it exists
    if current_header:
        header_dict[current_header] = current_text

    return header_dict


def txt_to_list(file_path: str) -> List[str]:
    lines = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            stripped_line = line.strip()  # Remove leading/trailing whitespace
            if stripped_line:  # Only append non-empty lines
                lines.append(stripped_line)
    return lines
