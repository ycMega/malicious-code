from src.static_features.js import *


class KeywordRatioJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "KeywordRatioJS",
            "prophiler",
            "keyword在所有单词（'\b\w+\b'）中的占比",
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


# 恶意字符串的关键字相对少，而运算，instantiations, arithmetical operations, function calls可能相对多
# TODO: 设定合适的公式来计算恶意分数


def extract(js_content: str) -> float:
    # 定义JavaScript关键字列表
    js_keywords = {
        "break",
        "case",
        "catch",
        "class",
        "const",
        "continue",
        "debugger",
        "default",
        "delete",
        "do",
        "else",
        "export",
        "extends",
        "finally",
        "for",
        "function",
        "if",
        "import",
        "in",
        "instanceof",
        "new",
        "return",
        "super",
        "switch",
        "this",
        "throw",
        "try",
        "typeof",
        "var",
        "void",
        "while",
        "with",
        "yield",
        "let",
        "static",
        "await",
        "async",
    }

    # 使用正则表达式分词
    words = re.findall(r"\b\w+\b", js_content)

    # 统计关键字数量和总词数
    keyword_count = sum(1 for word in words if word in js_keywords)
    total_words = len(words)

    # 计算并返回关键字与总词数的比率
    if total_words == 0:  # 避免除以零的错误
        return 0.0
    return round(keyword_count / total_words, 5)


if __name__ == "__main__":
    # 测试示例
    js_code = """
    var a = 10;
    function test() {
        for (var i = 0; i < a; i++) {
            console.log(i);
        }
    }
    """
    ratio = extract(js_code)
    print(f"Keywords-to-words ratio: {ratio:.2f}")
