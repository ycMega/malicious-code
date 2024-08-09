from collections import defaultdict

from src.static_features.js import *


class HTML_5_EventsJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "HTML_5_EventsJS",
            "InfectedWebContent2017",
            "一些HTML5 events的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 定义HTML5事件列表
html5_events = [
    "onforminput",
    "onformchange",
    "onfocus",
    "ondrag",
    "ondrop",
    "onplay",
    "onpause",
    "onerror",
    "onload",
    "onresize",
    "onscroll",
    "onsearch",
    "oninput",
    "oninvalid",
]


def extract(js_content: str) -> int:
    # 使用defaultdict初始化事件计数器
    event_counts = defaultdict(int)

    # 对于每个事件，使用正则表达式在HTML内容中查找匹配项
    for event in html5_events:
        # 正则表达式匹配事件，考虑大小写
        pattern = re.compile(rf"\b{event}\b", re.IGNORECASE)
        matches = pattern.findall(js_content)
        event_counts[event] = len(matches)

    return sum(event_counts.values())  # 暂且只统计总和


if __name__ == "__main__":
    # 示例HTML内容
    js_content = """
    <form id=test onforminput=alert(1)>
    <input> </form>
    <button form=test onformchange=alert(2)>X</button>
    <input type=text value= onfocus=alert('Injected value') autofocus>
    """

    # 计算并打印事件使用次数
    event_usage = extract(js_content)
    print("html5 Event usage:", event_usage)
