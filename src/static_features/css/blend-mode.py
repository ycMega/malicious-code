import re
from collections import Counter

from src.utils.css import css_rules_listing, extract_css_features

# 混合模式影响元素之间的视觉交互和颜色合成，通常用于重叠元素


def calculate_score(css_list: list):
    # 可疑混合模式

    suspicious_blend_modes = [
        "multiply",
        "screen",
        "overlay",
        "darken",
        "lighten",
        "color-dodge",
        "color-burn",
        "hard-light",
        "soft-light",
        "difference",
        "exclusion",
    ]

    # 检测混合模式
    blend_mode_pattern = r"mix-blend-mode:\s*([^;]+);"
    all_blend_modes = []
    for css_content in css_list:
        blend_modes = re.findall(blend_mode_pattern, css_content)
        all_blend_modes.extend(blend_modes)
    blend_mode_usage = Counter()

    for b in all_blend_modes:
        if b in suspicious_blend_modes:
            blend_mode_usage[b] += 1

    # 检查 HTML 中的内联混合模式
    # inline_blend_pattern = r'style=["\'][^"\']*mix-blend-mode:\s*([^;]+);'
    # inline_blend_modes = re.findall(inline_blend_pattern, html_content)

    # for b in inline_blend_modes:
    #     if b in suspicious_blend_modes:
    #         blend_mode_usage[b] += 1

    return sum(blend_mode_usage.values()), blend_mode_usage


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

    # 运行检测
    css_list = extract_css_features(html_test_content) + css_rules_listing(
        css_test_content
    )
    count, blend_modes = calculate_score(css_list)
    print(f"Blend Mode Usage Detected count = {count}:", blend_modes)
