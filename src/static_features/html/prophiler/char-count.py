from bs4 import BeautifulSoup

from src.static_features.html import *


# regex方法无法把包含属性的标签删掉而只保留其中属性，bs4可以做到
class CharCount(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "CharCount",
            "prophiler",
            "提取标签的属性和文本内容，统计总字符数",
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


def calculate_score(html_content):
    # 列出自闭合标签
    self_closing_tags = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "keygen",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    soup = BeautifulSoup(html_content, "lxml")
    # 访问所有标签
    reserved = []
    for tag in soup.find_all(True):
        # 提取并打印标签的属性
        attrs = " ".join(
            [f'{attr}="{tag[attr]}"' for attr in tag.attrs if attr != "style"]
        )
        if attrs:
            reserved.append(attrs)
            # print(f"[Attributes] {attrs}")

        # 提取标签内的文本内容，使用strip()避免提取空白字符
        if tag.string and tag.string.strip():
            reserved.append(tag.string.strip())
            # print(f"[Text] {tag.string.strip()}")

        # 清除已经访问的标签内容，避免重复
        tag.extract()

    # # 这个正则表达式尝试保留属性，但可能有局限性
    # tag_pattern = re.compile(r'<(?![^>]*\s[^= ]+="[^"]*")[^>]*>')
    # # 移除不包含属性的HTML标签
    # cleaned_content = tag_pattern.sub("", html_content)
    # # 进一步清理多余的空白字符
    # # text = re.sub(r"\s*>\s*", ">", cleaned_content)
    # text = re.sub(r"\s+", " ", cleaned_content).strip()  # 处理多余空格
    text = " ".join(reserved)
    # 统计字符数
    total_characters = len(text)

    return total_characters


if __name__ == "__main__":
    # 示例 HTML/CSS/JS 内容
    example_content = """
    <html>
        <head>
            <style>
                body { font-size: 16px; }
            </style>
            <script>
                console.log("Hello, world!");
            </script>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a sample paragraph.</p>
            <img src="https://www.example.com/image.jpg" alt="Example Image">
            <div>This is a div element.</div>
        </body>
    </html>
    """

    # 运行统计
    characters = calculate_score(example_content)
    print(f"Total Characters: {characters}")
