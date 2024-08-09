import re

from bs4 import BeautifulSoup

from src.static_features.css import *
from src.utils.css import css_rules_listing, extract_css_features


class ComplexSelectorCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "ComplexSelectorCSS",
            "others",
            "复杂的选择器：包含多个层级/伪类/伪元素/ID和类选择器的组合，至少匹配两个特征或用' '分为至少三部分",
            "1.0",
        )

    # 似乎不能执行typechecked？会导致在模块加载阶段（而不是执行）报错，因为sys.modules中还没有对应的key
    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"]
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            input_list = css_rules_listing(css["content"])
            res, complex_selectors_list = extract(input_list)
            info_dict[css["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": complex_selectors_list,
            }

        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def is_complex_selector(selector):
    # 检测选择器的复杂性，包括以下特征：
    # 1. 选择器中包含多个层级（>、+、~） \s+|> 对应 div > p。~对应兄弟选择器 div ~ p
    # 2. 包含伪类和伪元素（如 :hover、:before）匹配:
    # 3. 使用了 ID 选择器和类选择器的组合。匹配\.和\#
    complex_pattern = r"(>|~|\+|:|\.|\#)"
    matches = re.findall(complex_pattern, selector)
    selector_count = len(selector.split(" "))
    # 这里允许=2，使得最基本的复杂形式也能被检测到？
    return (
        len(matches) >= 2
        or len(matches) + selector_count >= 3  # or selector_count >= 3
    )


def extract(css_list: list):
    complex_selectors = []
    for style in css_list:
        # 提取选择器部分
        selectors = re.findall(r"([^{]+)\{", style)
        for selector in selectors:
            selector = selector.strip()
            if is_complex_selector(selector):
                complex_selectors.append(selector)

    # # 检查 <style> 块中的 CSS
    # for style_tag in soup.find_all("style"):
    #     css_content = style_tag.string or ""
    #     selectors = re.findall(r"([^{]+)\{", css_content)
    #     for selector in selectors:
    #         selector = selector.strip()
    #         if is_complex_selector(selector):
    #             complex_selectors.append(selector)

    # # 检查内联样式
    # for element in soup.find_all(True):
    #     style = element.get("style", "")
    #     if style:
    #         selectors = re.findall(r"([^{]+)\{", style)
    #         for selector in selectors:
    #             selector = selector.strip()
    #             if is_complex_selector(selector):
    #                 complex_selectors.append(selector)

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
    css_content = """
    /* 正常特征 1 */
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }

    /* 正常特征 2 */
    h1 {
        color: #333;
        font-size: 24px;
        text-align: center;
    }

    /* 复杂选择器 1 */
    ul li:first-child {
        color: red;
    }

    /* 复杂选择器 2 */
    div > p + a {
        font-weight: bold;
    }

    /* 复杂选择器 3 */
    #main .content > .article:first-of-type {
        border: 1px solid #ccc;
    }

    /* 复杂选择器 4 但是暂不支持检测这种复杂检测器！  */ 
    input[type="text"]:focus {
        border-color: blue;
    }

    /* 复杂选择器 5 */
    a[href^="https"] {
        color: green;
    }

    /* 复杂选择器 6 */
    nav ul li:hover > ul {
        display: block;
    }

    /* 复杂选择器 7 */
    section article:nth-of-type(2n) {
        background-color: #f4f4f4;
    }

    /* 复杂选择器 8 */
    header + main > aside {
        padding: 10px;
    }

    /* 复杂选择器 9 */
    footer ~ .back-to-top {
        display: inline-block;
    }

    /* 复杂选择器 10 */
    table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    """

    # 检测
    css_list = extract_css_features(html_content) + css_rules_listing(css_content)
    count, selectors = extract(css_list)
    print(f"Complex Selectors Found count = {count}:", selectors)
