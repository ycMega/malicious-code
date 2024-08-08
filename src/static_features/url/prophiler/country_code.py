import geoip2.database


def get_country_code(ip_address: str) -> str:
    """
    获取IP地址对应的国家代码
    :param ip_address: IP地址
    :return: 国家代码
    """
    try:
        # 使用GeoLite2数据库
        with geoip2.database.Reader("GeoLite2-Country.mmdb") as reader:
            response = reader.country(ip_address)
            return response.country.iso_code
    except Exception as e:
        print(f"Error fetching country code for IP {ip_address}: {e}")
        return ""


def extract(url: str) -> int:
    return -1


if __name__ == "__main__":
    # 示例IP地址
    ip_addresses = ["8.8.8.8", "1.1.1.1"]

    # 获取每个IP地址的国家代码
    for ip in ip_addresses:
        country_code = get_country_code(ip)
        print(f"IP: {ip} - Country Code: {country_code}")
