import re

# 定义可疑标签
SUSPICIOUS_TAGS = ["script", "object", "embed", "frame"]


def calculate_score(js_content: str) -> int:
    count = 0

    # 使用正则表达式查找可疑标签
    for tag in SUSPICIOUS_TAGS:
        pattern = r"\b" + re.escape(tag) + r"\b"
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        count += len(matches)

    return count


if __name__ == "__main__":
    # 测试示例
    js_content = """
    var html = '<script src="file.js"></script>';
    var obj = '<object type="application/x-foo"></object>';
    var embedCode = '<embed src="audio.mp3"></embed>';
    var frameCode = '<frame src="frame.html">';
    var normalText = 'This is not a tag.';
    """
    score = calculate_score(js_content)
    print(f"Total suspicious tag strings: {score}")
