from collections import Counter

from src.static_features.css import *
from src.utils.css import css_rules_listing, extract_css_features


class PerformanceDegradationCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "PerformanceDegradationCSS",
            "others",
            "深层嵌套、通配符和（资源相关？）的属性",
            "1.0",
        )

    # 似乎不能执行typechecked？会导致在模块加载阶段（而不是执行）报错，因为sys.modules中还没有对应的key
    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"]
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            input_list = css_rules_listing(css["content"])
            res, rule_usage = extract(input_list)
            info_dict[css["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": rule_usage,
            }

        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 大尺寸元素：如宽度和高度过大。
# 复杂的选择器：如过于复杂的嵌套选择器。
# 过多的动画和过渡：如频繁使用 animation 和 transition。
# **使用 @import**：在 CSS 中使用 @import 会增加额外的 HTTP 请求。
# **使用 !important**：频繁使用 !important 可能导致样式计算复杂化。


# 如果CSS规则导致页面渲染性能显著下降，这可能是攻击者故意使用资源密集型的CSS规则来拖慢页面响应，作为DoS攻击的一种形式
def extract(css_list: list):
    # 初始化计数器
    rule_usage = Counter()
    css_content = " ".join(css_list)
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
        "width",
        "height",
        "position",
        "top",
        "left",
        "right",
        "bottom",
        "margin",
        "padding",
        "border",
        "font-size",
        "line-height",
        "z-index",
        "display",
        "float",
        "clear",
        "overflow",
        "visibility",
        "opacity",
        "background",
        "background-color",
        "color",
        "text-align",
        "text-decoration",
        "text-transform",
        "letter-spacing",
        "word-spacing",
        "white-space",
        "vertical-align",
        "list-style",
        "list-style-type",
        "list-style-position",
        "list-style-image",
        "animation",
        "transition",
        "@import",
        "!important",
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
    html_test_content = """
    <!DOCTYPE html>
    <html lang="zh-cn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>性能退化测试</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
            }
            .large-image {
                width: 5000px;
                height: 3000px;
            }
            .absolute-position {
                position: absolute;
                top: 0;
                left: 0;
            }
            .fixed-position {
                position: fixed;
                bottom: 0;
                right: 0;
            }
            .complex-animation {
                animation: fadeIn 2s, move 3s;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes move {
                from { transform: translateX(0); }
                to { transform: translateX(100px); }
            }
            @import url('styles.css');
        </style>
    </head>
    <body>
        <h1>性能退化测试页面</h1>
        <div class="large-image">大图像</div>
        <div class="absolute-position">绝对定位元素</div>
        <div class="fixed-position">固定定位元素</div>
        <div class="complex-animation">复杂动画元素</div>
    </body>
    </html>
    """
    css_test_list = extract_css_features(html_test_content) + css_rules_listing(
        css_test_content
    )
    # 运行检测
    count, usage = extract(css_test_list)
    print(f"Performance Degradation Rules Detected count = {count}:", usage)
