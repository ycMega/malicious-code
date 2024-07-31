import re

from bs4 import BeautifulSoup


def is_complex_selector(selector):
    # 检测选择器的复杂性，包括以下特征：
    # 1. 选择器中包含多个层级（>、+、~） \s+|> 对应 div > p。~对应兄弟选择器 div ~ p
    # 2. 包含伪类和伪元素（如 :hover、:before）匹配:
    # 3. 使用了 ID 选择器和类选择器的组合。匹配\.和\#
    complex_pattern = r"(>|~|\+|:|\.|\#)"
    return (
        len(re.findall(complex_pattern, selector)) > 2 or len(selector.split(" ")) > 3
    )


def calculate_score(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    complex_selectors = []

    # 检查 <style> 块中的 CSS
    for style_tag in soup.find_all("style"):
        css_content = style_tag.string or ""
        selectors = re.findall(r"([^{]+)\{", css_content)
        for selector in selectors:
            selector = selector.strip()
            if is_complex_selector(selector):
                complex_selectors.append(selector)

    # 检查内联样式
    for element in soup.find_all(True):
        style = element.get("style", "")
        if style:
            selectors = re.findall(r"([^{]+)\{", style)
            for selector in selectors:
                selector = selector.strip()
                if is_complex_selector(selector):
                    complex_selectors.append(selector)

    return len(complex_selectors), complex_selectors


if __name__ == "__main__":
    # 示例 HTML
    html_content = """
    <style>
        div > p:hover .class1 #id1 {
            color: red;
        }
        .class2 .class3 {
            background: blue;
        }
        #id2 + div > span ~ p {
            display: none;
        }
    </style>
    <div style="color: green;">
        <p class="class1">Test</p>
    </div>
    """

    # 检测
    count, selectors = calculate_score(html_content)
    print("Complex Selectors Found:", selectors)
