import re
from typing import List, Tuple
from urllib.parse import urlparse

import dns.resolver


# todo: 对TTL的正确收集和处理
def get_ttl_for_a_record(domain: str) -> int:
    """
    获取域名的第一个A记录的TTL值
    :param domain: 域名
    :return: TTL值
    """
    try:
        answers = dns.resolver.resolve(domain, "A")
        for rdata in answers:
            return answers.rrset.ttl
    except Exception as e:
        print(f"Error resolving A record for {domain}: {e}")
        return -1


def get_ttl_for_ns_record(domain: str) -> int:
    """
    获取域名的第一个NS记录的TTL值
    :param domain: 域名
    :return: TTL值
    """
    try:
        answers = dns.resolver.resolve(domain, "NS")
        for rdata in answers:
            return answers.rrset.ttl
    except Exception as e:
        print(f"Error resolving NS record for {domain}: {e}")
        return -1


def calculate_scores(url: str) -> Tuple[int, List[str], int, int]:
    """
    检查URL中是否包含IP地址，并返回结果。
    :param url: 要检查的URL
    :return: IP地址存在与否（1或0）、匹配的IP地址列表、A记录的TTL值、NS记录的TTL值
    """
    parsed_url = urlparse(url)
    host = parsed_url.netloc

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

    # 获取A记录和NS记录的TTL值
    a_ttl = get_ttl_for_a_record(host) if matched_ips else -1
    ns_ttl = get_ttl_for_ns_record(host) if matched_ips else -1
    return -1
    return has_ip_address, matched_ips, a_ttl, ns_ttl


if __name__ == "__main__":
    # 示例URL
    urls = [
        "http://192.168.1.1",
        "http://example.com",
        "http://www.example.com",
        "http://172.16.254.1",
        "http://sub.example.com",
        "http://[2001:db8::1]",
        "http://[2001:0db8:85a3:0000:0000:8a2e:0370:7334]",
    ]

    # 检查每个URL中是否包含IP地址，并获取TTL值
    for url in urls:
        count, ips, a_ttl, ns_ttl = calculate_scores(url)
        print(
            f"URL: {url} - IP Address Present: {count} - Matched IPs: {ips} - A TTL: {a_ttl} - NS TTL: {ns_ttl}"
        )
