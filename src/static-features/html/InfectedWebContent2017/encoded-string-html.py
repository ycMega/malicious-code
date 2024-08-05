import re
import time
from tracemalloc import start

from bs4 import BeautifulSoup

from src.io.feature_extractor import (
    ExtractorMeta,
    FeatureExtractionResult,
    FeatureExtractor,
)

# encode--obfuscate


class EncodedStringHTML(FeatureExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "EncodedStringHTML",
            "InfectedWebContent2017",
            "The number of encoded URLs and The number of IP address in elements sources",
            "1.0",
        )

    def calculate_score(self):
        start_time = time.time()
        htmls = self.web_data.content["html"]
        html_content = "\n".join(d["content"] for d in htmls)
        res = calculate_score(html_content)
        return FeatureExtractionResult(
            self.meta.filetype, self.meta.name, res, time.time() - start_time
        )


def calculate_score(html_content: str) -> int:
    reserved_html_encodings = [
        "&lt;",
        "&gt;",
        "&amp;",
        "&quot;",
        "&apos;",
        "&nbsp;",
        "&times;",
        "&divide;",
    ]
    encoded_string_count = 0
    encoded_html_count = 0

    # 查找所有文本节点
    # text_nodes = soup.find_all(string=True)
    strings = html_content.split()
    for text in strings:
        # print(f"text:{text}")
        # 检查“&#+数字;”模式出现的次数
        if len(re.findall(r"&#[0-9]+;", text)) >= 2:
            encoded_string_count += 1

        # 检查是否包含HTML保留字符的编码形式
        if any(
            reserved_encoding in text for reserved_encoding in reserved_html_encodings
        ):
            encoded_html_count += 1

    return encoded_string_count + encoded_html_count


if __name__ == "__main__":
    # 示例HTML内容
    html_content = """
    &lt;iframe src=&quot; Evil.com &quot; width=0 height=0&gt;&lt;/iframe&gt;
    """
    # 调用函数并打印结果
    res = calculate_score(html_content)
    print(f"encoded count:{res}")
