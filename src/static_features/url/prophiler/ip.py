import re
from typing import List, Tuple
from urllib.parse import urlparse


def calculate_score(url: str) -> Tuple[int, List[str]]:
    """
    检查URL中是否包含IP地址，并返回结果。
    :param url: 要检查的URL
    :return: IP地址存在与否（1或0）和匹配的特征列表
    """
    parsed_url = urlparse(url)
    host = parsed_url.netloc

    # 正则表达式匹配IP地址
    # 正则表达式匹配IPv4地址
    ipv4_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    # 正则表达式匹配IPv6地址
    ipv6_pattern = re.compile(r"^\[?([a-fA-F0-9:]+:+)+[a-fA-F0-9]+\]?$")

    matched_ips = []
    if ipv4_pattern.match(host):
        matched_ips.append(host)
    elif ipv6_pattern.match(host):
        matched_ips.append(host)

    has_ip_address = 1 if matched_ips else 0

    return has_ip_address, matched_ips


if __name__ == "__main__":
    # 示例URL
    urls = [
        "http://192.168.1.1",
        "http://example.com",
        "http://www.example.com",
        "http://172.16.254.1",
        "http://sub.example.com",
    ]

    # 检查每个URL中是否包含IP地址
    for url in urls:
        count, ips = calculate_score(url)
        print(f"URL: {url} - IP Address Present: {count} - Matched Patterns: {ips}")
