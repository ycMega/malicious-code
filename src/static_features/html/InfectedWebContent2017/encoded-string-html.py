from src.static_features.html import *

# from tracemalloc import start


# encode--obfuscate


class EncodedStringHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "EncodedStringHTML",
            "InfectedWebContent2017",
            "按space分词，检查“&#+数字;”模式出现的次数是否>=2，以及是否出现HTML保留字符的编码形式",
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
    # print(f"split:{html_content.split()}")
    # 调用函数并打印结果
    # web_data = WebData()
    # extractor = EncodedStringHTML(
    #     WebData(content={"html": [{"content": html_content}]})
    # )
    res = extract(html_content)
    print(f"encoded count:{res}")
