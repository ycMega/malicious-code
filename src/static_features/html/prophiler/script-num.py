from bs4 import BeautifulSoup

# the number of script elements (both included via the src attribute, and inline)
from src.static_features.html import *


class ScriptNum(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "ScriptNum",
            "prophiler",
            "script tag数量",
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
    soup = BeautifulSoup(html_content, "lxml")

    # 查找所有 <script> 标签
    script_tags = soup.find_all("script")

    # 统计 <script> 标签的数量
    script_count = len(script_tags)

    return script_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://example.com/script.js"></script>
        <script>
            console.log('Inline script');
        </script>
    </head>
    <body>
        <p>This is a sample page.</p>
        <script src="/internal/script.js"></script>
    </body>
    </html>
    """

    score = extract(sample_html)
    print(f"Number of <script> elements: {score}")
