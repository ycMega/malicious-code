import re

xss_detection_rules = [
    (["img"], ["src", "lowsrc", "dynsrc", "style"], 0),
    (
        [
            "frame",
            "iframe",
            "embed",
            "video",
            "sound",
            "source",
            "input",
            "bgsound",
            "script",
        ],
        ["src", "style"],
        0,
    ),
    (["object"], ["data", "style"], 0),
    (["applet"], ["code", "style"], 0),
    (["link", "a", "base", "area"], ["href", "style"], 0),
    (
        ["style"],
        [],
        0,
    ),  # inner HTML of tag，检查的不是某个attribute而是全部？可以这样理解吗
    (["meta"], ["content"], 0),
    (
        ["table", "td"],
        [
            "background",
            "style",
        ],
        0,
    ),
    (
        [
            "frame",
            "iframe",
            "embed",
            "applet",
            "link",
            "a",
            "base",
            "Object",
            "img",
            "video",
            "Button",
            "sound",
            "input",
            "form",
            "source",
            "body",
        ],
        [
            "event",
            "style",
        ],  # value of events (complete list of event attributes and style attributes
        3,
    ),
    (["style"], [], 1),
    (["meta"], ["content"], 3),
    (
        [
            "frame",
            "iframe",
            "applet",
            "embed",
            "video",
            "sound",
            "input",
            "bgsound",
            "link",
            "a",
            "style",
            "meta",
            "source",
            "table",
            "base",
            "body",
            "img",
        ],
        [],  # in body of the tag (after “<” and before “>”)
        2,
    ),
    (["img"], ["src", "lowsrc", "dynsrc", "style"], 3),
    (["object"], ["data"], 3),
    (["applet"], ["code"], 3),
    (["link", "a", "base", "area"], ["href"], 3),
    (
        [
            "frame",
            "iframe",
            "embed",
            "video",
            "sound",
            "source",
            "input",
            "bgsound",
            "Script",
        ],
        ["src", "style"],
        3,
    ),
]
regex_malfunc = r"\b(link|number|exec|eval|escape|fromCharCode|setinterval|settimeout|js_content\.write|createElement|ubound| \
    global|alert|unscape|decodeURIComponent|decodeURL|encodeURL|encodeURLComponent|parseInt|parseFloat| \
    String\.(?:fromCharCode|raw|charAt|charCodeAt|concat|endsWith|includes|indexOf|lastIndexOf|localeCompare|match|matchAll|normalize|\
        padEnd|padStart|repeat|replace|replaceAll|search|slice|split|startsWith|substring|toLocaleLowerCase|toLocaleUpperCase|\
            toLowerCase|toString|toUpperCase|trim|trimEnd|trimStart|valueOf))\b"
regex_location = (
    r"\b(location\.\w+)"  # \w+会确保匹配结束于单词字符，自然形成了单词的边界。
)

regex_string = r"(exe|files|.{151,})"
combined_patterns = "|".join([regex_malfunc, regex_location, regex_string])
suspicious_malicious_structures = re.compile(combined_patterns, re.IGNORECASE)
patterns: list[re.Pattern] = [
    re.compile(
        r"(javascript:|<script|vbscript:|livescript:|exe|.{151,})", re.IGNORECASE
    ),  # 长度>150是一个充分条件。不是必要条件？
    re.compile(r"@import", re.IGNORECASE),
    re.compile(r"#.*"),
    suspicious_malicious_structures,
]


# 检测逻辑（伪代码）
def calculate_score(js_content: str, js_path: str = "") -> int:
    count = 0
    for tag_list, cases_list, condition in xss_detection_rules:
        for tag in tag_list:
            # \s+：匹配一个或多个空白字符（如空格、制表符）。这确保了在<img之后至少有一个空格，之后才是标签的属性。
            # [^>]*：匹配除了>之外的任何字符任意次。这部分用于匹配<img>标签内的所有属性，直到遇到关闭的>。
            tag_pattern = re.compile(rf"<{tag}\s+[^>]*>", re.IGNORECASE)
            # 。*？匹配标签内的任何字符，?使得匹配尽可能少的字符，这是为了防止在有多个<style>标签时跨过中间的标签。
            # (.*?)：这是一个捕获组，用于捕获开始标签和结束标签之间的内容。同样使用?来进行非贪婪匹配
            # re.DOTALL：这个标志允许.匹配包括换行符在内的任何字符。
            tag_body_pattern = re.compile(
                rf"<{tag}.*?>(.*?)</{tag}>", re.IGNORECASE | re.DOTALL
            )
            matches = tag_pattern.findall(js_content) + tag_body_pattern.findall(
                js_content
            )
            # 这样一来， inner HTML和 body of the tag 是否就没区别了？
            # if len(matches) > 0:
            #     print(f"tag:{tag}, matches:", matches)
            for match in matches:
                attribute_matches = [match]
                if len(cases_list) > 0:  # 否则，则整段内容都视作match？
                    attribute_matches = []
                    for case in cases_list:
                        attribute_pattern = re.compile(
                            f"{case}=(\".*?\"|'.*?')", re.IGNORECASE
                        )
                        attribute_matches += attribute_pattern.findall(match)
                # if len(attribute_matches) > 0:
                #     print(
                #         f"attribute matches:{attribute_matches}, condition={condition}"
                #     )
                for attribute in attribute_matches:
                    suspicious_list = patterns[condition].findall(attribute)
                    count += len(suspicious_list)

    return count


if __name__ == "__main__":
    # 示例HTML代码
    html_content = """
    <style>
        body {background: url("javascript:alert('XSS')");}
    </style>
    <img src="javascript:alert(\'XSS\')" onload="alert(\'XSS\')">
    <div>
        <script>alert('XSS')</script>
    </div>
    """
    res = calculate_score(html_content)
    print("suspicious XSS count:", res)


# # 示例HTML代码
# html_content = "<img src=\"javascript:alert('XSS')\" onload=\"alert('XSS')\">"

# # 步骤1: 匹配完整的HTML标签
# tag_pattern = re.compile(r"<img\s+[^>]*>", re.IGNORECASE)
# matches = tag_pattern.findall(html_content)

# # 步骤2: 对匹配到的标签进行分析
# for tag in matches:
#     # 检测特定属性（如src）
#     src_pattern = re.compile(r'src=["\'](.*?)["\']', re.IGNORECASE)
#     src_matches = src_pattern.findall(tag)
#     for src in src_matches:
#         if "javascript:" in src:
#             print("检测到潜在的XSS攻击：", src)

#     # 检测标签体内的内容（如onload事件）
#     onload_pattern = re.compile(r'onload=["\'](.*?)["\']', re.IGNORECASE)
#     onload_matches = onload_pattern.findall(tag)
#     for onload in onload_matches:
#         if "alert" in onload:
#             print("检测到潜在的XSS攻击：", onload)
