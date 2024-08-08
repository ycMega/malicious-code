from bs4 import BeautifulSoup

from src.static_features.html import *


class UnknownTags(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "UnknownTags",
            "prophiler",
            "未知标签的百分比",
            "1.0",
        )

    def calculate_score(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res = calculate_score(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# the percentage of unknown tags
known_tags = {
    "html",
    "head",
    "title",
    "base",
    "link",
    "meta",
    "style",
    "script",
    "body",
    "section",
    "article",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "footer",
    "nav",
    "main",
    "p",
    "blockquote",
    "ol",
    "ul",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "div",
    "a",
    "img",
    "picture",
    "source",
    "audio",
    "video",
    "track",
    "embed",
    "object",
    "param",
    "canvas",
    "svg",
    "math",
    "table",
    "caption",
    "tr",
    "th",
    "td",
    "thead",
    "tbody",
    "tfoot",
    "form",
    "label",
    "input",
    "button",
    "select",
    "datalist",
    "optgroup",
    "option",
    "textarea",
    "fieldset",
    "legend",
    "details",
    "summary",
    "dialog",
    "template",
    "slot",
}


def calculate_score(html_content: str) -> float:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 获取所有标签
    all_tags = soup.find_all()

    # 计算已知和未知标签的数量
    known_count = sum(1 for tag in all_tags if tag.name in known_tags)
    unknown_count = len(all_tags) - known_count

    # 计算总标签数量
    total_count = len(all_tags)

    # 计算未知标签的百分比
    if total_count == 0:
        return 0.0

    percentage = (unknown_count / total_count) * 100
    return percentage


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <custom-tag>Some content</custom-tag>
        <script src="https://example.com/script.js"></script>
    </head>
    <body>
        <p>This is a sample page.</p>
        <unknown-tag>More content</unknown-tag>
    </body>
    </html>
    """

    percentage = calculate_score(sample_html)
    print(f"Percentage of unknown tags: {percentage:.2f}%")
