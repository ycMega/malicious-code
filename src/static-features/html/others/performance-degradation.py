import re
from collections import Counter


# 如果CSS规则导致页面渲染性能显著下降，这可能是攻击者故意使用资源密集型的CSS规则来拖慢页面响应，作为DoS攻击的一种形式
def detect_performance_degradation(css_content):
    # 初始化计数器
    rule_usage = Counter()

    # 检测复杂选择器
    complex_selector_pattern = r"([^{]+)\{[^}]*\}"
    complex_selectors = re.findall(complex_selector_pattern, css_content)

    for selector in complex_selectors:
        # 检测深层嵌套
        if ">" in selector or len(selector.split()) > 2:
            rule_usage["complex_selectors"] += 1

        # 检测通配符
        if "*" in selector:
            rule_usage["wildcard_selectors"] += 1

    # 检测频繁使用的属性
    properties = [
        "box-shadow",
        "filter",
        "opacity",
        "background-image",
        "background-size",
        "position",
        "transform",
        "animation",
        "transition",
        "flex",
        "grid",
        "text-shadow",
        "font-size",
        "line-height",
        "letter-spacing",
    ]

    for prop in properties:
        prop_pattern = rf"{prop}:\s*[^;]+;"
        matches = re.findall(prop_pattern, css_content)
        rule_usage[prop] += len(matches)

    return sum(rule_usage.values()), rule_usage


if __name__ == "__main__":
    # 测试 CSS 内容
    css_test_content = """
    .example1 {
        filter: blur(5px);
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        opacity: 0.9;
    }
    .example2 {
        transition: all 0.5s;
        animation: spin 1s infinite;
    }
    div > p > span {
        color: red;
    }
    * {
        margin: 0;
    }
    """

    # 运行检测
    result = detect_performance_degradation(css_test_content)
    print("Performance Degradation Rules Detected:", result)
