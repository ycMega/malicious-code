import re
from collections import Counter

from src.utils.css import css_rules_listing, extract_css_features


# 检测可疑的CSS滤镜。滤镜主要用于图像处理和视觉效果
def extract(css_list: list):
    # 可疑滤镜
    suspicious_filters = [
        "blur",
        "brightness",
        "contrast",
        "drop-shadow",
        "grayscale",
        "hue-rotate",
        "invert",
        "opacity",
        "saturate",
        "sepia",
    ]

    # 检测滤镜
    filter_pattern = r"filter:\s*([^;]+);"
    all_filters = []
    for css_content in css_list:
        filters = re.findall(filter_pattern, css_content)
        all_filters.extend(filters)
    filter_usage = Counter()

    for f in all_filters:
        for suspicious in suspicious_filters:
            if suspicious in f:
                filter_usage[suspicious] += 1

    # # 检查 HTML 中的内联 CSS
    # inline_filter_pattern = r'style=["\'][^"\']*filter:\s*([^;]+);'
    # inline_filters = re.findall(inline_filter_pattern, html_content)

    # for f in inline_filters:
    #     for suspicious in suspicious_filters:
    #         if suspicious in f:
    #             filter_usage[suspicious] += 1

    return sum(filter_usage.values()), filter_usage


if __name__ == "__main__":
    # 测试 CSS 内容和 HTML 内容
    css_test_content = """
    .example1 {
        filter: blur(5px);
        mix-blend-mode: multiply;
    }
    .example2 {
        filter: brightness(150%);
        mix-blend-mode: darken;
    }
    """

    html_test_content = """
    <div style="filter: grayscale(100%); mix-blend-mode: normal;">Content</div>
    <p style="filter: sepia(100%); mix-blend-mode: screen;">Another Content</p>
    """
    css_list = extract_css_features(html_test_content) + css_rules_listing(
        css_test_content
    )
    # 运行检测
    count, filters = extract(css_list)
    print("Filter Usage Detected:", filters)
