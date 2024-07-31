import re

from src.utils.css import extract_css_features


# 加载异常的字体，特别是那些（来自不受信任的源或）在页面上没有明显用途的字体，可能用于追踪用户或作为加载恶意内容的载体
# 有可能会读取CSS文件的内容，并作为参数传进来？还是只传CSS文件路径呢？
def detect_unused_fonts(html_content, external_css_content: str | None = None):
    inline_css, _, element_css = extract_css_features(html_content)
    css_content = (
        " ".join(inline_css + element_css) + (" " + external_css_content)
        if external_css_content
        else ""
    )  # 提取所有 CSS 内容
    # 提取加载的字体
    loaded_fonts_pattern = r'@font-face\s*{[^}]*font-family:\s*["\']([^"\']+)["\'];'
    loaded_fonts = re.findall(loaded_fonts_pattern, css_content)

    # 提取页面使用的字体
    used_fonts = set()
    font_usage_pattern = r'font-family:\s*["\']([^"\']+)["\']'
    used_fonts_matches = re.findall(font_usage_pattern, css_content)
    used_fonts.update(used_fonts_matches)

    # 检查 HTML 中的字体
    html_font_pattern = (
        r'style=["\'][^"\']*font-family:\s*["\']([^"\']+)["\'][^"\']*["\']'
    )
    html_used_fonts = re.findall(html_font_pattern, html_content)
    used_fonts.update(html_used_fonts)

    # 找出未使用的字体
    unused_fonts = [font for font in loaded_fonts if font not in used_fonts]

    return len(unused_fonts), unused_fonts


if __name__ == "__main__":
    # 测试 CSS 和 HTML 内容
    css_test_content = """
    @font-face {
        font-family: "StrangeFont";
        src: url("https://example.com/strange-font.woff2");
    }
    @font-face {
        font-family: "CommonFont";
        src: url("https://example.com/common-font.woff2");
    }
    body {
        font-family: "CommonFont", sans-serif;
    }
    """

    html_test_content = """
    <div style="font-family: 'Arial';">Hello World</div>
    <p>This is a paragraph.</p>
    """

    # 运行检测
    count, unused_fonts = detect_unused_fonts(html_test_content, css_test_content)
    print("Unused Fonts Detected:", unused_fonts)
