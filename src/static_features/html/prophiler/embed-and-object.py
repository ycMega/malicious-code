from bs4 import BeautifulSoup

from src.static_features.html import *


class EmbedAndObject(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "EmbedAndObject",
            "prophiler",
            "统计embed和object标签的数量",
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

    # 统计 <embed> 和 <object> 标签的数量
    embed_count = len(
        soup.find_all("embed")
    )  # 递归地统计<embed> tag（findall方法返回的就是tags）。recursive=False就是不嵌套
    object_count = len(soup.find_all("object"))

    # 返回总数量
    return embed_count + object_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <embed src="https://example.com/media" />
        <object data="https://example.com/object" type="application/pdf"></object>
        <embed src="https://example.com/media2" />
        <p>This is a paragraph.</p>
        <object data="https://example.com/object2" type="application/pdf"></object>
    </body>
    </html>
    """

    score = extract(sample_html)
    print(f"Number of <embed> and <object> tags: {score}")
