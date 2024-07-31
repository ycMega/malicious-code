import re
from collections import Counter


def calculate_score(js_content: str) -> tuple:
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

    return sum(activex_frequency.values()), dict(activex_frequency)


# 示例调用
js_example = """
var fs = new ActiveXObject("Scripting.FileSystemObject");
var shell = new ActiveXObject("WScript.Shell");
var stream = new ActiveXObject("Adodb.Stream");
"""

sum_count, frequency_dict = calculate_score(js_example)
print(f"activeX: {frequency_dict}")
