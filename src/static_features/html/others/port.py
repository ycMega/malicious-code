# defined by yyc
import re

from bs4 import BeautifulSoup

from src.static_features.html import *


class Port(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "Port",
            "others",
            "查找链接中':\d+'且不是80、443（也就是其他端口）的出现次数",
            "1.0",
        )

    def calculate_score(self) -> FeatureExtractionResult:
        start_time = time.time()
        htmls = self.web_data.content["html"]
        html_content = "\n".join(d["content"] for d in htmls)
        res = calculate_score(html_content)
        return FeatureExtractionResult(
            self.meta.filetype, self.meta.name, res, time.time() - start_time
        )


# use non standard ports to bypass firewalls
def calculate_score(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    links = soup.find_all("a", href=True)
    non_standard_ports = sum(
        1
        for link in links
        if re.search(r":\d+", link["href"])
        and not re.search(r":(80|443)\b", link["href"])
    )
    score = non_standard_ports  # * 20
    return score
