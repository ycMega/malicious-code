import math
from collections import Counter


def calculate_entropy(s: str) -> float:
    if len(s) == 0:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def calcluate_score(js_content: str):
    # 计算整个脚本的熵
    entropy = calculate_entropy(js_content)
    return entropy


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    var a = "Hello World";
    var b = 'This is a test string!';
    var c = "Entropy calculation.";
    var d = 'Another example string.';
    """

    entropy = calcluate_score(sample_js)
    print(f"Total Entropy of the script: {entropy:.4f}")
