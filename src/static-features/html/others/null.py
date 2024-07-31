import re

from bs4 import BeautifulSoup

# NULL字符（\x00）可能被恶意使用来进行注入攻击或其他安全漏洞利用：
# 字符串截断导致SQL注入或路径截断；绕过HTML或JavaScript的安全过滤，从而注入恶意脚本


def calculate_score(html_content: str) -> dict:
    null_characters = html_content.count("\x00")
    return null_characters


# 示例调用
html_example = """
<html>
<head>
    <script src="https://example.com/script.js"></script>
</head>
<body>
    <div><img src="image.jpg"></div>
    <div>Content with NULL character\x00 here</div>
    <div>Another NULL character\x00 here</div>
</body>
</html>
"""

result = calculate_score(html_example)
print("null characters:", result)
