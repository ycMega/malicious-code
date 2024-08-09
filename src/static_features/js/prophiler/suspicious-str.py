# use certain strings as variable or function names
# 定义可疑字符串
from src.static_features.js import *


class SuspiciousStringJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "SuspiciousStringJS",
            "prophiler",
            "检测可疑字符串（目前是evil，shell，spray，crypt）出现次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, suspicious_strings = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": suspicious_strings,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


SUSPICIOUS_STRINGS = ["evil", "shell", "spray", "crypt"]


def extract(js_content: str) -> int:
    count_dict = {}

    # 使用正则表达式查找可疑字符串
    for suspicious_string in SUSPICIOUS_STRINGS:
        # 匹配整个单词
        pattern = r"\b" + re.escape(suspicious_string) + r"\b"
        matches = re.findall(pattern, js_content)
        count_dict[suspicious_string] = len(matches)

    return sum(count_dict.values()), count_dict


if __name__ == "__main__":
    # 测试示例
    js_content = """
    var evil = 1;
    function shell() { return 'shell'; }
    var data = 'this will spray'; 
    var crypt = 'encryption';
    """
    score, suspicious_strings = extract(js_content)
    print(f"Total suspicious strings: {score}:{suspicious_strings}")
