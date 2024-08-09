import math
from collections import Counter

from src.static_features.js import *


class ContentEntropyJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "ContentEntropyJS",
            "prophiler",
            "检测js内容的熵（以字符为单位）",
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


def calculate_entropy(s: str) -> float:
    if len(s) == 0:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    # print(f"prob:{[{c: s.count(c)} for c in set(s)]}")
    return -sum(p * math.log2(p) for p in prob)


def extract(js_content: str):
    # 计算整个脚本的熵
    entropy = calculate_entropy(js_content)
    return entropy


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    function add(a, b) {
    return a + b;
}

console.log(add(5, 3)); // 输出：8
    
    """
    # (function(a,b,c){var d='';for(var e=0;e<a.length;e++){d+=String.fromCharCode(a.charCodeAt(e)+1);}console.log(d);})('Hello', 'World', 123);
    entropy = extract(sample_js)
    print(f"Total Entropy of the script: {entropy:.4f}")
