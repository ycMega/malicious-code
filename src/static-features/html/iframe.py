from bs4 import BeautifulSoup


# iframe
# e.g. count
def calculate_score(soup: BeautifulSoup):
    iframes = soup.find_all("iframe")
    score = len(iframes)  # * 5
    return score
