from collections import Counter

# 混合模式影响元素之间的视觉交互和颜色合成，通常用于重叠元素
from src.static_features.css import *


class BlendModeCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "BlendModeCSS",
            "others",
            "可疑的混合模式mix-blend-mode的使用次数",
            "1.0",
        )

    # 似乎不能执行typechecked？会导致在模块加载阶段（而不是执行）报错，因为sys.modules中还没有对应的key
    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"]
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            input_list = css_rules_listing(css["content"])
            res, blend_mode_usage = extract(input_list)
            info_dict[css["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": blend_mode_usage,
            }

        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(css_list: list):
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
    count, blend_modes = extract(css_list)
    print(f"Blend Mode Usage Detected count = {count}:", blend_modes)
