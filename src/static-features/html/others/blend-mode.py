import re
from collections import Counter

# 混合模式影响元素之间的视觉交互和颜色合成，通常用于重叠元素


def calculate_score(html_content, css_content: str | None = None):
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
    blend_modes = re.findall(blend_mode_pattern, css_content)
    blend_mode_usage = Counter()

    for b in blend_modes:
        if b in suspicious_blend_modes:
            blend_mode_usage[b] += 1

    # 检查 HTML 中的内联混合模式
    inline_blend_pattern = r'style=["\'][^"\']*mix-blend-mode:\s*([^;]+);'
    inline_blend_modes = re.findall(inline_blend_pattern, html_content)

    for b in inline_blend_modes:
        if b in suspicious_blend_modes:
            blend_mode_usage[b] += 1

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
    count, blend_modes = calculate_score(html_test_content, css_test_content)
    print("Blend Mode Usage Detected:", blend_modes)
