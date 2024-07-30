from bs4 import BeautifulSoup
import re

def calculate_score(html_content: str) -> dict:
    null_characters = html_content.count('\x00')
    
    return null_characters

# 示例调用
html_example = """
<html>
<head>
    <script src="https://example.com/script.js"></script>
</head>
<body>
    <div><img src="image.jpg"></div>
    <div>Content without closing tag
</body>
</html>
"""

result = calculate_score(html_example)
print("null characters:", result)