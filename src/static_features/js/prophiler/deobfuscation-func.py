import re

from src.static_features.js import *


class DeobfuscationFuncJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DeobfuscationFuncJS",
            "prophiler",
            "JS代码中的解混淆函数的使用情况",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, deobfuscation_functions = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": deobfuscation_functions,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 不考虑其他规则已经考虑过的函数？
deobfuscation_functions = [
    # "eval",
    "Function",  # 动态创建函数
    # "setTimeout",  # 延时执行代码
    # "setInterval",
    "decodeURIComponent",  # 解码 URI 组件或字符串
    "unescape",
    "atob",  # 解码一个已经被base-64编码的字符串
    "btoa",
    "parseInt",
    "parseFloat",  # 将字符串转换为浮点数
    "String.fromCharCode",  # 根据 Unicode 值生成字符串
    "String.prototype.charCodeAt",  # 获取字符的 Unicode 值
    "String.prototype.split",  # 将字符串分割为数组
    "String.prototype.replace",  # 替换字符串中的部分内容
    # "JSON.parse",  # 处理 JSON 数据的解析和序列化
    # "JSON.stringify",
    "Object.keys",  # 操作对象的键值对
    "Object.values",
    "Object.entries",
]


def extract(js_content: str) -> tuple:
    # 常见解混淆内置函数列表

    counts = {}

    for func in deobfuscation_functions:
        pattern = rf"\b{func}\s*\(.*?\)"
        matches = re.findall(pattern, js_content)
        counts[func] = len(matches)

    return sum(counts.values()), {k: v for k, v in counts.items() if v > 0}


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    function test() {
        eval('console.log("Hello");');
        var x = Function('return 1')();
        setTimeout(() => { console.log("Timeout"); }, 1000);
        var y = decodeURIComponent('%20');
        var z = unescape('%20');
        var a = atob('SGVsbG8=');
        var b = btoa('Hello');
        var c = parseInt('10');
        var d = parseFloat('10.5');
    }
    """

    counts = extract(sample_js)
    for func, count in counts.items():
        print(f"Number of occurrences of {func}: {count}")
