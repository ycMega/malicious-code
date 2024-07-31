import re
from typing import List, Tuple
from urllib.parse import urlparse

import dns.resolver
import dns.reversename


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


def get_a_record(domain: str) -> str:
    """
    获取域名的第一个A记录的IP地址
    :param domain: 域名
    :return: IP地址
    """
    try:
        answers = dns.resolver.resolve(domain, "A")
        for rdata in answers:
            return rdata.address
    except Exception as e:
        print(f"Error resolving A record for {domain}: {e}")
        return ""


def get_ptr_record(ip: str) -> str:
    """
    获取IP地址的PTR记录
    :param ip: IP地址
    :return: PTR记录
    """
    try:
        reverse_name = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(reverse_name, "PTR")
        for rdata in answers:
            return str(rdata.target).rstrip(".")
    except Exception as e:
        print(f"Error resolving PTR record for {ip}: {e}")
        return ""


def calculate_score(url: str) -> Tuple[int, List[str], int, int, str, str, bool]:
    """
    检查URL中是否包含IP地址，并返回结果。
    :param url: 要检查的URL
    :return: IP地址存在与否（1或0）、匹配的IP地址列表、A记录的TTL值、NS记录的TTL值、A记录的IP地址、PTR记录的域名、是否一致
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
    a_ttl = get_ttl_for_a_record(host) if not matched_ips else -1
    ns_ttl = get_ttl_for_ns_record(host) if not matched_ips else -1

    # 获取A记录的IP地址和PTR记录的域名，并检查它们是否一致
    a_record_ip = get_a_record(host) if not matched_ips else ""
    ptr_record_domain = get_ptr_record(a_record_ip) if a_record_ip else ""
    is_consistent = host == ptr_record_domain

    return (
        has_ip_address,
        matched_ips,
        a_ttl,
        ns_ttl,
        a_record_ip,
        ptr_record_domain,
        is_consistent,
    )


if __name__ == "__main__":
    # 示例URL
    urls = ["http://example.com", "http://www.example.com"]

    # 检查每个URL中是否包含IP地址，并获取TTL值和PTR记录关系
    for url in urls:
        count, ips, a_ttl, ns_ttl, a_ip, ptr_domain, consistent = calculate_score(url)
        print(
            f"URL: {url} - IP Address Present: {count} - Matched IPs: {ips} - A TTL: {a_ttl} - NS TTL: {ns_ttl} - A Record IP: {a_ip} - PTR Record Domain: {ptr_domain} - Consistent: {consistent}"
        )
