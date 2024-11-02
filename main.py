import requests
from bs4 import BeautifulSoup
from pprint import pprint

# Base URL of the website
base_url = "https://rulebook.centralbank.ae"


def fetch_main_rulebooks(base_url):
    """Fetches main rulebooks and their links from the base URL."""
    response = requests.get(base_url)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.content, "html.parser")
    aside_menu = soup.find("div", class_="view-content row")

    rulebook_links = []

    # Iterate over the rows in the aside menu
    for views_row in aside_menu.find_all("div", class_="views-row"):
        anchor_tag = views_row.find("a")
        if anchor_tag:
            link_text = anchor_tag.text.strip()
            link_href = anchor_tag["href"]
            full_link = base_url + link_href

            # Initialize the rulebook entry
            rulebook_links.append(
                {"url": full_link, "title": link_text, "sub_sections": []}
            )

    return rulebook_links


def fetch_subsections(rulebooks):
    """Fetches sub-sections for each rulebook link."""
    for rulebook in rulebooks:
        rulebook_response = requests.get(rulebook["url"])
        rulebook_response.raise_for_status()
        rulebook_soup = BeautifulSoup(rulebook_response.content, "html.parser")

        # Find all top-level menu items
        top_level_items = rulebook_soup.find_all("li", class_="menu-item--expanded")

        for item in top_level_items:
            # Get the subsection title and link
            subsection_link = item.find("a", recursive=False)  # Only direct children
            if subsection_link:
                sub_section = {
                    "title": subsection_link.text.strip(),
                    "url": base_url + subsection_link["href"],
                    "circulars": []
                }
                
                # Find the nested ul.menu that contains circulars
                nested_menu = item.find("ul", class_="menu")
                if nested_menu:
                    # Find all circulars (collapsed menu items)
                    circular_items = nested_menu.find_all("li", class_="menu-item--collapsed")
                    for circular in circular_items:
                        circular_link = circular.find("a")
                        if circular_link:
                            circular_info = {
                                "title": circular_link.text.strip(),
                                "url": base_url + circular_link["href"]
                            }
                            sub_section["circulars"].append(circular_info)

                rulebook["sub_sections"].append(sub_section)

# Remove the separate fetch_circulars function since we're handling circulars 
# directly in fetch_subsections

def print_rulebook_links(rulebooks):
    """Prints the rulebook links and their hierarchy."""
    for rulebook in rulebooks:
        print(f"\nRulebook: {rulebook['title']}")
        print("=" * 80)
        
        for sub_section in rulebook["sub_sections"]:
            print(f"\nSubsection: {sub_section['title']}")
            print("-" * 40)
            
            print("\nCirculars:")
            for circular in sub_section["circulars"]:
                print(f"  - {circular['title']}")
            
        print("\n" + "=" * 80)

# Main script execution
if __name__ == "__main__":
    rulebooks = fetch_main_rulebooks(base_url)
    fetch_subsections(rulebooks)
    # print_rulebook_links(rulebooks)
    pprint(rulebooks)

    


