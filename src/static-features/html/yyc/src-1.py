# defined by yyc
from bs4 import BeautifulSoup


def calculate_score(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    score = 0
    src_count = len([tag for tag in soup.find_all(src=True)])
    score += src_count  # * 3
    return score
