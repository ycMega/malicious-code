# defined by yyc
from bs4 import BeautifulSoup


# external scripts
def calculate_score(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    score = 0
    external_scripts = soup.find_all("script", attrs={"src": True})
    score += len(external_scripts)  # * 5
    return score
