import re


def calculate_score(js_code: str) -> int:
    # 使用正则表达式查找包含 "iframe" 的字符串
    pattern = r"\biframe\b"
    matches = re.findall(pattern, js_code, re.IGNORECASE)
    return len(matches)


if __name__ == "__main__":
    # 测试示例
    js_code = """
    var frame = '<iframe src="example.com"></iframe>';
    document.body.innerHTML += '<iframe src="test.com"></iframe>';
    var data = 'this is not an iframe';
    """
    score = calculate_score(js_code)
    print(f'Total "iframe" strings: {score}')
