import math
import re
from collections import Counter

# the entropy of the strings declared in the script,
#  the maximum entropy of all the script’s strings


def calculate_entropy(s: str) -> float:
    if len(s) == 0:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def extract_strings(js_content: str) -> list:
    # 匹配单引号、双引号和三重引号的字符串
    pattern = r"(['\"]{1,3})(.*?)(\1)"
    return re.findall(pattern, js_content)


def calculate_score(js_content: str) -> tuple:
    strings = extract_strings(js_content)
    entropies = {s: calculate_entropy(s) for s in strings}
    max_entropy = max(entropies.values())
    return round(max_entropy, 3), entropies


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    var a = "Hello World";
    var b = 'This is a test string!';
    var c = "Entropy calculation.";
    var d = 'Another example string.';
    """

    max_entropy, entropies = calculate_score(sample_js)
    for s, entropy in entropies.items():
        print(f"String: {s}, Entropy: {entropy:.3f}")
