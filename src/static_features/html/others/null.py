import re

from bs4 import BeautifulSoup

from src.static_features.html import *


# NULL字符（\x00）可能被恶意使用来进行注入攻击或其他安全漏洞利用：
# 字符串截断导致SQL注入或路径截断；绕过HTML或JavaScript的安全过滤，从而注入恶意脚本
class NullCharacterHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "NullCharacterHTML",
            "others",
            "'\x00'的出现次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str) -> dict:
    null_characters = html_content.count("\x00")
    return null_characters


if __name__ == "__main__":
    # 示例调用
    html_example = """
    <html>
    <head>
        <script src="https://example.com/script.js"></script>
    </head>
    <body>
        <div><img src="image.jpg"></div>
        <div>Content with NULL character\x00 here</div>
        <div>Another NULL character\x00 here</div>
    </body>
    </html>
    """

    result = extract(html_example)
    print("null characters:", result)
