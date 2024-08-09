from src.static_features.js import *


class IframeJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "IframeJS",
            "prophiler",
            "'<\s*iframe\b'的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
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

    # 匹配 <iframe 开头的标签，允许空白字符
    iframe_pattern = r"<\s*iframe\b"

    # 查找所有匹配的 iframe 标签
    iframe_tags = re.findall(iframe_pattern, js_content)

    # 计算总数
    total_iframes = len(iframe_tags)

    return total_iframes
    # pattern = r"\biframe\b"
    # matches = re.findall(pattern, js_content, re.IGNORECASE)
    # return len(matches)


if __name__ == "__main__":
    # 测试示例
    js_content = """
    var frame = '<iframe src="example.com"></iframe>';
    document.body.innerHTML += '<iframe src="test.com"></iframe>';
    var data = 'this is not an iframe';
    """
    score = extract(js_content)
    print(f'Total "iframe" strings: {score}')
