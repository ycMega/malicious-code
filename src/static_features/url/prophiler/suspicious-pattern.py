from typing import List, Tuple

from src.static_features.url import *


class SuspiciousPatternURL(URLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "url",
            "SuspiciousPatternURL",
            "prophiler",
            "可疑模式（比如exploit\.js，infected\.dll）数量",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        url_list = self.web_data.content["url"]
        info_dict = {}
        for h in url_list:
            start_time = time.time()
            res, matched_patterns = extract(h)
            info_dict["all_urls"] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": matched_patterns,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


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


def extract(url: str) -> Tuple[int, List[str]]:
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
        count, patterns = extract(url)
        print(
            f"URL: {url} - Suspicious Patterns Count: {count} - Matched Patterns: {patterns}"
        )
