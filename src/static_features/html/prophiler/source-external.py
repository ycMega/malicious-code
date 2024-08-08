from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.static_features.html import *


class SourceExternal(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "SourceExternal",
            "prophiler",
            "urlparse(base_url).netloc 与当前domain不一致的img, script, a标签数量",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res = extract(h["content"], self.web_data.url)
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str, base_url: str) -> int:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 获取当前页面的域名
    base_domain = urlparse(base_url).netloc

    # 统计外部域的元素数量
    external_count = 0

    # 检查所有的 <img>, <script>, 和 <a> 标签
    for tag in soup.find_all(["img", "script", "a"]):
        src = tag.get("src") or tag.get("href")
        if src:
            src_domain = urlparse(src).netloc
            if src_domain and src_domain != base_domain:
                external_count += 1

    return external_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://external.com/script.js"></script>
        <script src="/internal/script.js"></script>
    </head>
    <body>
        <img src="https://external.com/image.png" />
        <img src="/internal/image.png" />
        <a href="https://external.com/page.html">External Link</a>
        <a href="/internal/page.html">Internal Link</a>
    </body>
    </html>
    """

    base_url = "https://example.com"
    score = extract(sample_html, base_url)
    print(f"External source element count: {score}")
