import sys

from src.static_features.css import *


class AbnormalAttributeCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "AbnormalAttributeCSS",
            "others",
            "异常模式的出现次数",
            "1.0",
        )

    # 似乎不能执行typechecked？会导致在模块加载阶段（而不是执行）报错，因为sys.modules中还没有对应的key
    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"]
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            input_list = css_rules_listing(css["content"])
            res, abnormal_styles = extract(input_list)
            info_dict[css["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": abnormal_styles,
            }

        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


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
    matches = []
    for pattern in abnormal_patterns:
        matches.extend(re.findall(pattern, style, re.IGNORECASE))
    return matches


def extract(css_list: list):
    abnormal_styles = []
    for style in css_list:
        matches = is_abnormal_css_usage(style)
        abnormal_styles.extend(matches)
    return len(abnormal_styles), abnormal_styles

    # soup = BeautifulSoup(html_content, "html.parser")

    # 检查内联样式
    # for element in soup.find_all(True):
    #     style = element.get("style", "")
    #     if style and is_abnormal_css_usage(style):
    #         abnormal_styles.append((element.name, style))

    # # 检查 <style> 标签中的 CSS
    # for style_tag in soup.find_all("style"):
    #     css_content = style_tag.string or ""
    #     rules = re.findall(
    #         r"([^{]+)\{([^}]+)\}", css_content
    #     )  # 匹配选择器部分和属性部分。比如.hidden{opacity:0;}
    #     for selector, style in rules:
    #         if is_abnormal_css_usage(style):
    #             abnormal_styles.append((selector.strip(), style.strip()))

    # return len(abnormal_styles), abnormal_styles


if __name__ == "__main__":
    # 示例 HTML
    html_content = """
    # <style>
    #     .hidden {
    #         opacity: 0;
    #         position: absolute;
    #     }
    #     .redirect {
    #         transform: translate(0, 0);
    #     }
    # </style>
    # <div style="opacity: 0; position: fixed;">Invisible</div>
    # <div style="transform: translate(0, 0);">Hidden Content</div>
    """
    css_content = """
    .navbar a {
        color: white;
        padding: 10px;
    }

    .navbar a:hover {
        background-color: #555;
    }

    /* 异常模式 1. 注意，这里检查不涉及到危险函数，所以没有查出 */
    .abnormal-pattern-1 {
        color: red;
        font-size: 100px;
        background-image: url("javascript:alert('XSS')");
    }

    /* 异常模式 2 */
    .abnormal-pattern-2 {
        position: absolute;
        top: -9999px;
        left: -9999px;
    }
    /* 异常模式 3 */
    .abnormal-pattern-3 {
        display: none;
        visibility: hidden;
    }
    """
    # 检测
    css_list = extract_css_features(html_content) + css_rules_listing(css_content)
    count, abnormal_styles = extract(css_list)
    print(f"Abnormal CSS Usage count={count}: ", abnormal_styles)
