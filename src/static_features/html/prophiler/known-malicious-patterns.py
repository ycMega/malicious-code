from bs4 import BeautifulSoup

from src.static_features.html import *


class KnownMaliciousPatternsHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "KnownMaliciousPatternsHTML",
            "prophiler",
            "统计'index.php?spl='在meta http-equiv='refresh'中的出现次数",
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
    soup = BeautifulSoup(html_content, "html.parser")
    malicious_pattern_count = 0

    # 检查特定的 meta 标签
    for meta in soup.find_all("meta"):
        if meta.get("http-equiv") == "refresh":
            content = meta.get("content")
            if "index.php?spl=" in content:
                malicious_pattern_count += 1

    return malicious_pattern_count


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=index.php?spl=malicious">
            <meta http-equiv="refresh" content="5; url=another_page.html">
        </head>
        <body>
            <h1>Safe Content</h1>
        </body>
    </html>
    """
    count = extract(html_content)
    print(f"Number of known malicious patterns: {count}")
