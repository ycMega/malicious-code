import re

from src.static_features.js import *


class GetComputedStyleJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "GetComputedStyleJS",
            "InfectedWebContent2017",
            "getComputedStyle()的使用次数",
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


def extract(js_content: str):
    # 定义正则表达式来匹配getComputedStyle的使用
    pattern = re.compile(r"\bgetComputedStyle\s*\(\b")

    # 使用正则表达式找到所有匹配项
    matches = pattern.findall(js_content)

    # 返回匹配项的数量，即getComputedStyle的使用次数
    return len(matches)


# 示例使用
if __name__ == "__main__":
    js_content = """
    var links = document.links;
    for (var i = 0; i < links.length; ++i)
    { var link = links[i];
    if (getComputedStyle(link, "").color
    == "rgb(0, 0, 128)") {
    // we know link.href has not been visited
    }
    else{
    // we know link.href has been visited
    }
    }
    """
    usage_count = extract(js_content)
    print(f"getComputedStyle usage count: {usage_count}")
