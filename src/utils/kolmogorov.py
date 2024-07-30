import hashlib
import numpy as np

def kolmogorov_complexity(url: str) -> int:
    """计算给定字符串的 Kolmogorov 复杂度（近似值）。"""
    return len(hashlib.md5(url.encode()).hexdigest())

def conditional_kolmogorov_complexity(url: str, url_set: list) -> float:
    """计算给定 URL 相对于 URL 集的条件 Kolmogorov 复杂度。"""
    complexities = [kolmogorov_complexity(existing_url) for existing_url in url_set]
    return np.mean(complexities)

def url_similarity(url: str, benign_urls: list, malicious_urls: list) -> dict:
    """计算 URL 与良性和恶意 URL 集合的相似度。"""
    benign_complexity = conditional_kolmogorov_complexity(url, benign_urls)
    malicious_complexity = conditional_kolmogorov_complexity(url, malicious_urls)

    return {
        "benign_complexity": benign_complexity,
        "malicious_complexity": malicious_complexity,
        "similarity_score": benign_complexity - malicious_complexity
    }

if __name__ == "__main__":
    sample_url = "https://www.example.com/path/to/resource"
    benign_urls = [
        "https://www.google.com",
        "https://www.amazon.com",
        "https://www.wikipedia.org"
    ]
    malicious_urls = [
        "https://www.fakebank.com",
        "https://www.scamwebsite.com",
        "https://www.phishing.com"
    ]

    result = url_similarity(sample_url, benign_urls, malicious_urls)
    
    print("Similarity Results:", result)