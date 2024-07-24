# defined by yyc
from bs4 import BeautifulSoup


# iframe
# e.g. count
def calculate_score(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    iframes = soup.find_all("iframe")
    score = len(iframes)  # * 5
    return score
