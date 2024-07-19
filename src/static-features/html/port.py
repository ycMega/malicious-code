import re

from bs4 import BeautifulSoup


# use non standard ports to bypass firewalls
def calculate_score(soup: BeautifulSoup):
    links = soup.find_all("a", href=True)
    non_standard_ports = sum(
        1
        for link in links
        if re.search(r":\d+", link["href"])
        and not re.search(r":(80|443)\b", link["href"])
    )
    score = non_standard_ports  # * 20
    return score
