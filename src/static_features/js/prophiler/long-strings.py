import deprecated

from src.static_features.js import *


class LongStringJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "LongStringJS",
            "prophiler",
            "检测长度达到阈值（比如30）字符的字符串数量，包含直接用“+”连接的情况",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, long_strings = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": long_strings,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content: str):
    # 使用正则表达式提取单行和多行字符串
    string_pattern = r"""
    "(?:\\.|[^"\\\n])*"         |  # 双引号字符串，支持换行
    '(?:\\.|[^'\\\n])*'         |  # 单引号字符串，支持换行
    `(?:\\.|[^`\\\n])*`         |# 模板字符串，支持换行
    \+
"""
    # 找到所有字符串
    threshold = 30
    found_strings = re.findall(string_pattern, js_content, re.VERBOSE | re.DOTALL)

    complete_strings = []  # 完整的字符串
    current_string = ""
    prev_joint = True  # 前一个字符是否是加号
    for item in found_strings:
        item = item.strip()
        if not prev_joint:  # 之前不是加号，如果出现字符串就重置
            if item and item != "+":
                complete_strings.append(current_string)
                current_string = item
            elif item == "+":
                prev_joint = True
                continue
        else:  # 之前是加号
            if item and item != "+":
                current_string += item
                prev_joint = False
                continue
    complete_strings.append(current_string)  # 最后一个字符串
    # 检查长度
    long_strings = [s for s in complete_strings if len(s) > threshold]

    return len(long_strings), long_strings


if __name__ == "__main__":
    # 测试示例
    js_content = """
    const testStrings = [
    // 双引号字符串，包含转义字符和换行
    "This is a long string with a newline character:\nAnd it continues here.",
    
    // 单引号字符串，包含转义字符
    'Another long string with a tab character:\tAnd more text.',
    
    // 模板字符串，包含换行
    `This is a long template string
    that spans multiple lines
    and includes variables like ${variable}.`,

    // 含有 JavaScript 表达式
    "A string with an expression: " + (1 + 2) + " is the result.",

    // 复杂的转义字符
    "A string with an escaped quote: \" and a backslash: \\.",

    // 超长字符串，超过阈值
    "A very long string that , " +
    "and this part continues" +
    "to ensure we have a ."
];
    """
    count, long_strings = extract(js_content)
    print(f"Number of long strings: {count}")
    for string in long_strings:
        print(f"Detected long string: {string}")
# import re

# threshold: int = 40
# # This threshold is learned during the training phase by examining the length of strings in both known benign and known malicious pages (40 characters in our experiments).


# def merge_list(*lists: list) -> list:
#     result = []
#     seen = set()
#     for l in lists:
#         for i in l:
#             if i not in seen:
#                 result.append(i)
#                 seen.add(i)
#     return result


# def extract(code_content: str) -> int:
#     # 使用正则表达式匹配所有字符串（包括单引号、双引号和多行字符串）
#     string_patterns = [
#         r"\'(.*?)\'",  # 匹配单行单引号字符串
#         r"\"(.*?)\"",  # 匹配单行双引号字符串
#         r"\'\'\'(.*?)\'\'\'",  # 匹配多行单引号字符串
#         r"\"\"\"(.*?)\"\"\"",  # 匹配多行双引号字符串
#     ]
#     long_strings_count = 0
#     strings = []
#     for pattern in string_patterns:
#         new_strings = re.findall(pattern, code_content, re.DOTALL)
#         strings = merge_list(strings, new_strings)  # 避免多个规则匹配到同一字符串
#     print(f"strings:{strings}")
#     long_strings_count += sum(1 for s in strings if len(s) > threshold)
#     return long_strings_count


# # 示例代码
# code_content = """
# var longString = "This is a very long string which is definitely longer than 40 characters";
# var shortString = "Short string";
# var multiLineString = \"\"\"This is a multi-line string
# that spans across multiple lines
# and is definitely longer than 40 characters\"\"\";
# """

# # 计算并打印长字符串的数量
# long_strings_count = extract(code_content)
# print(f"Number of long strings: {long_strings_count}")
