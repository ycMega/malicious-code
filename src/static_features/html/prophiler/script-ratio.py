from bs4 import BeautifulSoup

# the percentage of scripting content in a page
from src.static_features.html import *


class ScriptRatioHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "ScriptRatioHTML",
            "prophiler",
            "script tag的string内容占整个页面字符数的百分比",
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


def extract(html_content: str) -> float:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 获取整个页面的字符数
    total_chars = len(html_content)

    # 查找所有 <script> 标签并统计其内容的字符数
    script_content_length = sum(
        len(script.string) if script.string else 0 for script in soup.find_all("script")
    )

    # 计算脚本内容的百分比
    if total_chars == 0:
        return 0.0

    percentage = (script_content_length / total_chars) * 100

    return percentage


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

    percentage = extract(sample_html)
    print(f"Percentage of scripting content: {percentage:.2f}%")
