import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Optional, Dict, Union
import pandas as pd
from const import *
from utils import *
import re

# URL of the webpage to scrape


def extract_circular_texts(tag: Optional[Tag]) -> List[str]:
    output_file_path = "circular_output.txt"
    with open(output_file_path, "w", encoding="utf-8") as txt_file:

        def recursive_extract(li_tag: Tag):
            # Extract the header (h2) if it exists in the current li
            header = li_tag.find("h2", recursive=False)
            if header:
                header_text = header.get_text(strip=True)
                txt_file.write(f"\n\n{header_text}\n\n")  # Write header with new lines

            # Extract each tag's text within the <div> body
            body_div = li_tag.find("div", recursive=False)
            if body_div:
                for child in body_div.children:
                    if isinstance(child, Tag):
                        # Write text from paragraphs, headings, and lists
                        if child.name in ["p", "h3", "h4"]:
                            text = child.get_text(strip=True)
                            txt_file.write(f"{text}\n")  # Write each as a new line
                        elif child.name in ["ul", "ol"]:
                            for nested_li in child.find_all("li", recursive=False):
                                li_text = nested_li.get_text(strip=True)
                                txt_file.write(
                                    f"{li_text}\n"
                                )  # Write each list item as a new line

            # Find nested <ul> or <ol> within the current <li>
            nested_lists = li_tag.find_all(["ul", "ol"], recursive=False)
            for nested_list in nested_lists:
                for nested_li in nested_list.find_all("li", recursive=False):
                    recursive_extract(nested_li)

        # Find all top-level <ul> and <ol> in the content section
        top_level_lists = tag.find_all(["ul", "ol"], recursive=True)
        for list_tag in top_level_lists:
            for li_tag in list_tag.find_all("li", recursive=False):
                recursive_extract(li_tag)

    return txt_to_list(output_file_path)  # Return the path of the written file


def extract_circular_name_and_number(tag: Optional[Tag]) -> Optional[tuple[str, str]]:
    ul_element: Optional[Tag] = tag.find("ul", recursive=False)

    if not ul_element:
        print("extract_circular_name: Could not find ul element")
        return None

    first_li: Optional[Tag] = ul_element.find("li", recursive=False)
    if not first_li:
        print("First list item not found.")
        return None

    match = re.search(r"C \d+/\d+", first_li.get_text())

    circular_number = match.group() if match else None

    h2_element: Optional[Tag] = first_li.find("h2")
    if not h2_element:
        print("Header (h2) not found in the first list item.")
        return None

    circular_name = h2_element.text.strip()
    return circular_name, circular_number


def main():
    # base_url = (
    #     "https://rulebook.centralbank.ae/en/rulebook/consumer-protection-regulation"
    # )

    base_url = "https://rulebook.centralbank.ae/en/rulebook/small-medium-sized-enterprises-sme-market-conduct-regulation"

    response = requests.get(base_url)
    response.raise_for_status()
    soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

    content_section: Optional[Tag] = soup.find("div", id="viewall-entire-section")

    circular_name, circular_number = extract_circular_name_and_number(content_section)

    headers: List[str] = [h.text.strip() for h in content_section.findAll("h2")[1:]]
    circular_texts: List[str] = extract_circular_texts(content_section)
    header_with_section: Dict[str, List[str]] = extract_text_by_headers(
        circular_texts, headers
    )

    # Create lists to store the data for DataFrame
    all_headers = []
    all_texts = []

    # Iterate through the dictionary and create a row for each text item
    for header, text_list in header_with_section.items():
        for text in text_list:
            all_headers.append(header)
            all_texts.append(f"{header} - \n{text}")

    # Create DataFrame with the expanded data
    df = pd.DataFrame(
        {
            ACT_ID: range(1, len(all_headers) + 1),
            APPLICABILITY: "Yes",
            NAME_OF_REGULATORY_DOCUMENT: circular_name,
            REGULATORY_DOCUMENT_REFERENCE_NUMBER: circular_number,
            PARA_REFERENCE_NUMBER: all_headers,
            REGULATORY_TEXT_ARTICLE_BREAKDOWN: all_texts,
        }
    )

    df = df.reindex(columns=CBUAE_COLUMN_ORDER)

    # Export to Excel
    df.to_excel("report.xlsx", index=False)


main()
