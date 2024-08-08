import re

# from cssutils import parseString, parseStyle
from src.utils.css import css_rules_listing, extract_css_features


def contains_font_face(block):
    # 检查块中是否包含 @font-face
    return "@font-face" in block


def extract_font_family(block):
    # 从块中提取 font-family 的值
    match = re.search(r'font-family\s*:\s*["\']?([^"\';}]+)', block)
    return match.group(1) if match else None


def extract_font_faces(css_content):
    font_face_pattern = r"@font-face\s*\{[^@]*?font-family\s*:\s*[\"']([^\"']+)[\"']"
    font_faces = re.findall(font_face_pattern, css_content)
    return set(font_faces)  # 使用集合避免重复


def extract_used_fonts(css_content, loaded_fonts):
    pattern = r"(?<!@font-face\s{0,1}\{)font-family\s*:([^;}]*)(?<!style=)"
    used_fonts = re.findall(pattern, css_content)
    used_fonts = set(used_fonts)  # 转换为集合去重
    return used_fonts
    # font_family_pattern = r"font-family\s*:\s*[\"']([^\"';},]+)[\"']"
    # used_fonts = re.findall(font_family_pattern, css_content)
    # # 清洗和分割多个字体名称
    # used_fonts = [
    #     font.strip().split(",")[0] for font in used_fonts
    # ]  # 简单的分割，可能需要更复杂的处理
    # # 过滤出实际使用的字体
    # actual_used_fonts = [font for font in used_fonts if font not in loaded_fonts]
    # return set(actual_used_fonts)


# 加载异常的字体，特别是那些（来自不受信任的源或）在页面上没有明显用途的字体，可能用于追踪用户或作为加载恶意内容的载体
# 有可能会读取CSS文件的内容，并作为参数传进来？还是只传CSS文件路径呢？
def extract(css_list: list):
    font_faces = []
    font_used = []
    font_face_pattern = r"@font-face\s*\{[^@]*?font-family\s*:\s*[\"']([^\"']+)[\"']"
    font_usage_pattern = r'font-family:\s*["\']?([^"\';]+)["\']?'
    for css_pattern in css_list:
        if contains_font_face(css_pattern):
            font_faces.extend(re.findall(font_face_pattern, css_pattern))
        else:
            font_used.extend(re.findall(font_usage_pattern, css_pattern))
    # print(f"font loaded:{font_faces}, font used:{font_used}")
    font_unused = set(font_faces) - set(font_used)
    return len(font_unused), font_unused
    # css_content = " ".join(css_list)
    # loaded_fonts = extract_font_faces(css_content)

    # 提取实际使用的字体
    # used_fonts = extract_used_fonts(css_content, loaded_fonts)
    # unused_fonts = loaded_fonts - used_fonts
    # return len(unused_fonts), unused_fonts

    # print(f"css content:{css_content}")
    # 提取加载的字体

    # loaded_fonts_pattern = r'@font-face\s*{[^}]*?font-family:\s*["\']?([^"\';]+)["\']?;'
    # loaded_fonts = re.findall(loaded_fonts_pattern, css_content)
    # print(f"loaded fonts:{loaded_fonts}")
    # # 提取页面使用的字体
    # used_fonts = set()
    # font_usage_pattern = r'font-family:\s*["\']?([^"\';]+)["\']?'
    # used_fonts_matches = re.findall(font_usage_pattern, css_content)

    # # 过滤掉 @font-face 规则中的字体
    # for match in used_fonts_matches:
    #     if f"@font-face {{ font-family: '{match}'" not in css_content:
    #         used_fonts.add(match)
    # print(f"used fonts:{used_fonts}")
    # unused_fonts = [font for font in loaded_fonts if font not in used_fonts]

    # return len(unused_fonts), unused_fonts


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
    css_list = extract_css_features(html_test_content) + css_rules_listing(
        css_test_content
    )
    # 运行检测
    count, unused_fonts = extract(css_list)
    print("Unused Fonts Detected:", unused_fonts)
