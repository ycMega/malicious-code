from src.static_features.js import *


class DynamicCSSJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DynamicCSSJS",
            "others",
            "部分dynamic CSS patterns的出现次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_list:
            start_time = time.time()
            res, dynamic_css = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": dynamic_css,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content):
    dynamic_css_patterns = [
        r"document\.styleSheets",  # 访问当前文档的样式表
        r"element\.style",  # 修改元素的 style 属性
        r'setAttribute\(\s*["\']style["\']',  # 设置元素的 style 属性
        r'createElement\(\s*["\']style["\']',  # 创建 <style> 标签
        r"appendChild\(\s*document\.head",  # 将样式表添加到文档头部
        r"insertRule\(",  # 插入新规则到样式表
        r"addRule\(",  # 旧版方法，向样式表添加规则
        r'cssText\s*=\s*["\'].*?["\']',  # 修改样式表的 cssText
        r'querySelector\(\s*["\'].*?["\']\)\.style',  # 使用选择器修改样式
        r"getComputedStyle\(",  # 获取计算后的样式
        r"removeChild\(\s*document\.head",  # 移除样式表
        r'@import\s*["\'].*?["\']',  # 动态导入样式
        r"new\s+CSSStyleSheet",  # 创建新的 CSSStyleSheet 实例
        r"sheet\.insertRule",  # 向样式表插入规则
        r'element\.setAttribute\(\s*["\']class["\']',  # 动态设置类名
    ]
    dynamic_css = []

    for pattern in dynamic_css_patterns:
        # res = re.search(pattern, js_content)
        for match in re.finditer(pattern, js_content):
            dynamic_css.append(match.group())

    return len(dynamic_css), dynamic_css


if __name__ == "__main__":
    # 测试 JavaScript 内容
    js_test_content = """
    document.getElementById("myDiv").style.color = "blue";
    var style = document.createElement("style");
    style.innerHTML = ".hidden { display: none; }";
    document.head.appendChild(style);
    var sheets = document.styleSheets;
    sheets[0].insertRule("body { background-color: red; }", sheets[0].cssRules.length);
    """

    # 运行检测
    count, dynamic_css = extract(js_test_content)
    print(f"Dynamic CSS features: {dynamic_css}")
