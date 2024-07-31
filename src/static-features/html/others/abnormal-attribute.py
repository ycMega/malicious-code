import re

from bs4 import BeautifulSoup


def is_abnormal_css_usage(style):
    # 检测异常使用的 CSS 属性
    abnormal_patterns = [
        # 隐藏内容
        r"opacity:\s*0",  # 完全透明
        r"visibility:\s*hidden",  # 隐藏元素
        r"display:\s*none",  # 不显示元素
        r"transform:\s*translate\(\s*0\s*,\s*0\s*\)",  # 使用 translate 隐藏
        r"position:\s*absolute",  # 绝对定位，可能用于重叠
        r"position:\s*fixed",  # 固定定位，可能用于重叠
        r"position:\s*relative",  # 相对定位，可能造成重叠
        r"z-index:\s*-?\d+",  # 非常低的 z-index 值
        r"opacity:\s*0\.?\d+",  # 部分透明（接近 0）
        # 内容重定向
        r"overflow:\s*hidden",  # 隐藏溢出内容
        r"clip:\s*rect\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0\s*\)",  # 完全剪裁
        r"filter:\s*alpha\(opacity\s*=\s*0\)",  # IE 透明度
        r"pointer-events:\s*none",  # 禁止鼠标事件
        r'content:\s*""',  # 使用伪元素隐藏内容
    ]

    for pattern in abnormal_patterns:
        if re.search(pattern, style, re.IGNORECASE):
            return True
    return False


def calculate_score(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    abnormal_styles = []

    # 检查内联样式
    for element in soup.find_all(True):
        style = element.get("style", "")
        if style and is_abnormal_css_usage(style):
            abnormal_styles.append((element.name, style))

    # 检查 <style> 标签中的 CSS
    for style_tag in soup.find_all("style"):
        css_content = style_tag.string or ""
        rules = re.findall(
            r"([^{]+)\{([^}]+)\}", css_content
        )  # 匹配选择器部分和属性部分。比如.hidden{opacity:0;}
        for selector, style in rules:
            if is_abnormal_css_usage(style):
                abnormal_styles.append((selector.strip(), style.strip()))

    return len(abnormal_styles), abnormal_styles


if __name__ == "__main__":
    # 示例 HTML
    html_content = """
    <style>
        .hidden {
            opacity: 0;
            position: absolute;
        }
        .redirect {
            transform: translate(0, 0);
        }
    </style>
    <div style="opacity: 0; position: fixed;">Invisible</div>
    <div style="transform: translate(0, 0);">Hidden Content</div>
    """

    # 检测
    count, abnormal_styles = calculate_score(html_content)
    print("Abnormal CSS Usage Found:", abnormal_styles)
