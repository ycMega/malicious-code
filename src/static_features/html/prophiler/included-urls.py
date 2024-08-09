from xml.etree.ElementInclude import include

from bs4 import BeautifulSoup

# Elements such as script, iframe, frame, embed, form, object are considered in computing this feature,
# because they can be used to include external content in a web page.
# img elements and other elements are not considered, as they cannot be used to include any executable code.
# todo：img真的不行吗？？？
from src.static_features.html import *


class IncludedUrlsHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "IncludedUrlsHTML",
            "prophiler",
            "统计部分tag的src或data属性的URL数量",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, included_urls = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": included_urls,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    included_url_count = 0
    included_urls = []

    # 查找指定的元素
    for tag in soup.find_all(["script", "iframe", "frame", "embed", "form", "object"]):
        src = tag.get("src") or tag.get("data")  # 获取 src 或 data 属性
        if src:
            included_url_count += 1
            included_urls.append(src)

    return included_url_count, included_urls


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <script src="https://example.com/script.js"></script>
    <iframe src="https://example.com/frame.html"></iframe>
    <embed src="https://example.com/embed.swf"></embed>
    <form action="https://example.com/formSubmit"></form>
    <object data="https://example.com/objectData"></object>
    <div>Some content here.</div>
    """
    count, urls = extract(html_content)
    print(f"Number of included URLs: {count}")
    for url in urls:
        print(f"Detected included URL: {url}")
