import re

# 恶意字符串的关键字相对少，而运instantiations, arithmetical operations, function calls可能相对多
# TODO: 设定合适的公式来计算恶意分数


def calculate_score(js_content: str, js_path: str = "") -> float:
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
    return round(keyword_count / total_words, 2)


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
    ratio = calculate_score(js_code)
    print(f"Keywords-to-words ratio: {ratio:.2f}")
