import re
from urllib.parse import urlparse
from collections import Counter

def extract_url_features(url):
    # 解析 URL
    parsed_url = urlparse(url)
    
    # 统计特征
    url_length = len(url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""
    tld = parsed_url.netloc.split('.')[-1] if '.' in parsed_url.netloc else ""
    primary_domain = '.'.join(parsed_url.netloc.split('.')[-2:]) if '.' in parsed_url.netloc else ""
    
    features = {
        "url_length": url_length,
        "hostname_length": len(hostname),
        "tld_length": len(tld),
        "primary_domain_length": len(primary_domain),
        "path_length": len(path),
        "special_char_count": len(re.findall(r'[/.?=&]', url))
    }
    
    # 分词
    words = re.split(r'[/.?=&]', url)
    words = [word for word in words if word]  # 去除空字符串
    word_counter = Counter(words)
    
    # n-gram 特征
    n_gram_features = Counter()
    for word in words:
        for i in range(len(word) - 1):
            n_gram_features[word[i:i+2]] += 1  # bi-gram

    return features, word_counter, n_gram_features

if __name__ == "__main__":
    sample_url = "https://www.example.com/path/to/resource?query=1&value=2"
    
    features, word_counter, n_gram_features = extract_url_features(sample_url)
    
    print("URL Features:", features)
    print("Word Counts:", word_counter)
    print("N-Gram Features:", n_gram_features)