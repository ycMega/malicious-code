import re
from collections import defaultdict

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


def calculate_score(js_content: str) -> int:
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
    event_usage = calculate_score(js_content)
    print("html5 Event usage:", event_usage)
