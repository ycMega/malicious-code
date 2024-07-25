import re

# use certain strings as variable or function names
# 定义可疑字符串
SUSPICIOUS_STRINGS = ["evil", "shell", "spray", "crypt"]


def calculate_score(js_code: str) -> int:
    count = 0

    # 使用正则表达式查找可疑字符串
    for suspicious_string in SUSPICIOUS_STRINGS:
        # 匹配整个单词
        pattern = r"\b" + re.escape(suspicious_string) + r"\b"
        matches = re.findall(pattern, js_code)
        count += len(matches)

    return count


if __name__ == "__main__":
    # 测试示例
    js_code = """
    var evil = 1;
    function shell() { return 'shell'; }
    var data = 'this will spray'; 
    var crypt = 'encryption';
    """
    score = calculate_score(js_code)
    print(f"Total suspicious strings: {score}")
