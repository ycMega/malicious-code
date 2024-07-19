from bs4 import BeautifulSoup


# hidden elements
def calculate_score(soup: BeautifulSoup):
    hidden_elements = soup.find_all(
        style=lambda value: value and "display:none" in value
    )
    score = len(hidden_elements)  #  * 20
    return score
