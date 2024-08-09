from src.static_features.js import *


class SuspiciousTagJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "SuspiciousTagJS",
            "prophiler",
            "检测可疑tag（目前是script、object、embed、frame）出现次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, count_dict = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": count_dict,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 定义可疑标签
SUSPICIOUS_TAGS = ["script", "object", "embed", "frame"]


def extract(js_content: str) -> int:
    count_dict = {}

    # 使用正则表达式查找可疑标签
    for tag in SUSPICIOUS_TAGS:
        pattern = r"<\s*" + re.escape(tag) + r"\b"
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        count_dict[tag] = len(matches)

    return sum(count_dict.values()), count_dict


if __name__ == "__main__":
    # 测试示例
    js_content = """
    var html = '<script src="file.js"></script>';
    var obj = '<object type="application/x-foo"></object>';
    var embedCode = '<embed src="audio.mp3"></embed>';
    var frameCode = '<frame src="frame.html">';
    var normalText = 'This is not a script object tag.';
    """
    score, count_dict = extract(js_content)
    print(f"Total suspicious tag strings: {score}: {count_dict}")
