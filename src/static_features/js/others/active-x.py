from collections import Counter

from src.static_features.js import *


class ActiveX(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "ActiveX",
            "others",
            "document.+特定property的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_list:
            start_time = time.time()
            res, frequency_dict = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": frequency_dict,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content: str) -> tuple:
    # 定义 ActiveX 对象列表
    activex_objects = [
        "Scripting.FileSystemObject",
        "WScript.Shell",
        "Adodb.Stream",
        "Scripting.Dictionary",
        "MSXML2.ServerXMLHTTP",
        "MSXML2.DOMDocument",
        "WScript.Network",
        "Scripting.RegExp",
        "Microsoft.XMLHTTP",
        "WScript.Shell.Application",
    ]

    # 统计 ActiveX 对象的频率
    activex_frequency = Counter()

    for obj in activex_objects:
        count = len(re.findall(r"\b" + re.escape(obj) + r"\b", js_content))
        activex_frequency[obj] = count

    return sum(activex_frequency.values()), {
        k: v for k, v in activex_frequency.items() if v > 0
    }


if __name__ == "__main__":
    # 示例调用
    js_example = """
    var fs = new ActiveXObject("Scripting.FileSystemObject");
    var shell = new ActiveXObject("WScript.Shell");
    var stream = new ActiveXObject("Adodb.Stream");
    """

    sum_count, frequency_dict = extract(js_example)
    print(f"activeX: {frequency_dict}")
