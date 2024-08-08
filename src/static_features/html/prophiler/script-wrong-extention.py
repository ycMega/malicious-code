import os

from bs4 import BeautifulSoup

# the presence of scripts with a wrong file name extension
from src.static_features.html import *


class ScriptWrongExtention(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "ScriptWrongExtention",
            "prophiler",
            "扩展名不合理的script数量",
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


def extract(html_content: str) -> int:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 合法扩展名列表
    valid_extensions = [".js", ".png", ".jpg", ".gif", ".ico"]

    # 统计不合法扩展名的脚本数量
    invalid_extension_count = 0

    # 查找所有 <script> 标签
    for script in soup.find_all("script"):
        src = script.get("src")
        if src:
            _, ext = os.path.splitext(src)
            if ext not in valid_extensions:
                invalid_extension_count += 1

    return invalid_extension_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://example.com/script.js"></script>
        <script src="https://example.com/script.txt"></script>
        <script src="https://example.com/image.jpg"></script>
        <script src="https://example.com/icon.ico"></script>
    </head>
    <body>
        <p>This is a sample page.</p>
        <script src="https://example.com/script.js"></script>
    </body>
    </html>
    """

    score = extract(sample_html)
    print(f"Number of scripts with invalid file name extensions: {score}")
