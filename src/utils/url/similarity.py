import hashlib
from collections import Counter
from urllib.parse import urlparse

import numpy as np

# import fuzzywuzzy
# Levenshtein 距离是指将一个字符串转换为另一个字符串所需的最小编辑操作次数，包括插入、删除和替换字符


# 将字符串分割成连续的 N 个字符或词的序列.用于捕捉序列中的局部模式，能够有效反映文本的结构。可以识别恶意URL的伪装
def ngrams(domain, n):
    """生成 N-gram"""
    return [domain[i : i + n] for i in range(len(domain) - n + 1)]


# 通过比较两个集合的交集与并集的比率来衡量相似性。通过比较 URL 的 N-gram 集合，计算 Jaccard 相似度，可以有效识别与合法域名相似的恶意域名
def jaccard_similarity(domain1, domain2):
    """计算 Jaccard 相似度"""
    n = 2  # 使用 2-gram
    grams1 = set(ngrams(domain1, n))
    grams2 = set(ngrams(domain2, n))
    intersection = grams1.intersection(grams2)
    union = grams1.union(grams2)
    return len(intersection) / len(union) if union else 0


# 一个字符串的最短描述长度。即，能够生成该字符串的最短程序的长度。
# 该理论基于算法信息论，旨在量化信息的复杂度。
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
        "similarity_score": benign_complexity - malicious_complexity,
    }


if __name__ == "__main__":
    sample_url = "https://www.example.com/path/to/resource"
    benign_urls = [
        "https://www.google.com",
        "https://www.amazon.com",
        "https://www.wikipedia.org",
    ]
    malicious_urls = [
        "https://www.fakebank.com",
        "https://www.scamwebsite.com",
        "https://www.phishing.com",
    ]

    result = url_similarity(sample_url, benign_urls, malicious_urls)

    print("Similarity Results:", result)
