import re
from typing import List, Tuple

# 定义已知的可疑URL模式
suspicious_patterns = [
    r"swfNode\.php",
    r"pdfNode\.php",
    r"exploit\.js",
    r"attack\.html",
    r"malware\.exe",
    r"driveby\.zip",
    r"payload\.bin",
    r"infected\.dll",
    r"trojan\.jar",
    r"virus\.apk",
]


def calculate_score(url: str) -> Tuple[int, List[str]]:
    """
    检查URL中包含的可疑模式数量，并返回匹配的模式列表。
    :param url: 要检查的URL
    :return: 匹配的可疑模式数量和匹配的模式列表
    """
    count = 0
    matched_patterns = []
    for pattern in suspicious_patterns:
        if re.search(pattern, url):
            count += 1
            matched_patterns.append(pattern)
    return count, matched_patterns


if __name__ == "__main__":
    # 示例URL
    urls = [
        "http://example.com/swfNode.php",
        "http://example.com/normalpage.html",
        "http://example.com/pdfNode.php?file=exploit.js",
        "http://example.com/attack.html",
        "http://example.com/malware.exe",
    ]

    # 检查每个URL中的可疑模式数量和匹配的模式
    for url in urls:
        count, patterns = calculate_score(url)
        print(
            f"URL: {url} - Suspicious Patterns Count: {count} - Matched Patterns: {patterns}"
        )
