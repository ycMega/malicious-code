from datetime import datetime
from typing import Tuple
from urllib.parse import urlparse

import whois


def get_registration_date(domain: str) -> Tuple[str, str]:
    """
    获取域名的注册日期和过期日期
    :param domain: 域名
    :return: 注册日期和过期日期
    """
    try:
        w = whois.query(domain)
        registration_date = w.creation_date
        expiration_date = w.expiration_date

        # 处理可能返回多个日期的情况
        if isinstance(registration_date, list):
            registration_date = registration_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        return registration_date.strftime("%Y-%m-%d"), expiration_date.strftime(
            "%Y-%m-%d"
        )
    except Exception as e:
        print(f"Error fetching Whois data for {domain}: {e}")
        return "", ""


def calculate_registration_info(url: str) -> Tuple[str, str, str]:
    """
    检查URL的域名注册日期和过期日期
    :param url: 要检查的URL
    :return: 域名、注册日期、过期日期
    """
    parsed_url = urlparse(url)
    host = parsed_url.netloc

    registration_date, expiration_date = get_registration_date(host)

    return host, registration_date, expiration_date


if __name__ == "__main__":
    # 示例URL
    urls = ["http://example.com", "http://www.example.com"]

    # 检查每个URL的域名注册日期和过期日期
    for url in urls:
        domain, reg_date, exp_date = calculate_registration_info(url)
        print(
            f"URL: {url} - Domain: {domain} - Registration Date: {reg_date} - Expiration Date: {exp_date}"
        )
