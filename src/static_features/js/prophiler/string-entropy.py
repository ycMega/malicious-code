import math
from collections import Counter

from src.static_features.js import *


class StringEntropyJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "StringEntropyJS",
            "prophiler",
            "检测js字符串的熵（以字符为单位）",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, entropies = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": entropies,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# the entropy of the strings declared in the script,
#  the maximum entropy of all the script’s strings


def calculate_entropy(s: str) -> float:
    if len(s) == 0:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def extract_strings(js_content: str) -> list:
    # 匹配单引号、双引号和三重引号的字符串——js中没有三重引号，但是有模板字符串？
    string_pattern = r"""
    "(?:\\.|[^"\\\n])*"         |  # 双引号字符串，支持换行
    '(?:\\.|[^'\\\n])*'         |  # 单引号字符串，支持换行
    `(?:\\.|[^`\\\n])*`         # 模板字符串，支持换行
"""
    # pattern = r"(['\"]{1,3})(.*?)(\1)"
    return re.findall(
        string_pattern, js_content, re.VERBOSE | re.DOTALL
    )  # 允许在正则表达式中使用空格和注释；使 . 匹配所有字符，包括换行符（允许跨多行的匹配）


def extract(js_content: str) -> tuple:
    strings = extract_strings(js_content)
    if strings == []:
        return 0, {}
    entropies = {s: calculate_entropy(s) for s in strings}
    max_entropy = max(entropies.values())  # max函数要求列表非空
    return round(max_entropy, 3), entropies


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    const lowEntropyString = "Hello, world!";
    const highEntropyString = "9f$gH@1qZx!2*Ds#4pLm&8vYw^nJ$kA7";
    """

    max_entropy, entropies = extract(sample_js)
    for s, entropy in entropies.items():
        print(f"String: {s}, Entropy: {entropy:.3f}")
