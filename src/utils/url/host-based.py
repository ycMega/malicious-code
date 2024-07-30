import whois
import socket
import requests
# IP 地址属性、WHOIS 信息、地理位置、域名属性等
def get_ip_info(domain):
    """获取 IP 地址信息，包括 IP 地址和 ASN。"""
    ip_address = socket.gethostbyname(domain)
    asn_info = requests.get(f'https://api.ip2asn.com/v1/{ip_address}').json()
    return ip_address, asn_info

def get_whois_info(domain):
    """获取 WHOIS 信息。"""
    return whois.whois(domain)

def get_geolocation(ip_address):
    """获取 IP 地址的地理位置。"""
    response = requests.get(f'https://ipapi.co/{ip_address}/json/')
    return response.json()

def extract_host_features(url):
    """提取 URL 的 host-based 特征。"""
    domain = url.split('//')[-1].split('/')[0]
    
    # 获取 IP 地址和 ASN 信息
    ip_address, asn_info = get_ip_info(domain)
    
    # 获取 WHOIS 信息
    whois_info = get_whois_info(domain)
    
    # 获取地理位置
    location_info = get_geolocation(ip_address)
    
    features = {
        "domain": domain,
        "ip_address": ip_address,
        "asn": asn_info.get('asn', 'N/A'),
        "whois_registration_date": whois_info.creation_date,
        "whois_registrar": whois_info.registrar,
        "geolocation": location_info.get('country', 'N/A'),
        "domain_age": (whois_info.expiration_date - whois_info.creation_date).days if whois_info.creation_date and whois_info.expiration_date else None
    }
    
    return features

if __name__ == "__main__":
    sample_url = "https://www.example.com/path/to/resource"
    host_features = extract_host_features(sample_url)
    
    print("Host-Based Features:", host_features)