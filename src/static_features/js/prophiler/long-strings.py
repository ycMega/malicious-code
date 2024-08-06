import re

# 定义长字符串的长度阈值
LONG_STRING_THRESHOLD = 40


def calculate_score(js_content: str):
    # 使用正则表达式提取单行和多行字符串
    long_strings = re.findall(
        r'"""(.*?)"""|\'\'\'(.*?)\'\'\'|\'([^\']{40,})\'|\"([^"]{40,})\"',
        js_content,
        re.DOTALL,
    )

    # 提取符合条件的长字符串
    detected_strings = [
        s
        for group in long_strings
        for s in group
        if s and len(s) >= LONG_STRING_THRESHOLD
    ]

    return len(detected_strings), detected_strings


if __name__ == "__main__":
    # 测试示例
    js_content = """
    var normalString = "This is a short string.";
    var longString = \"""This is a very long string that exceeds 
    ooh?
    the threshold of forty characters.\"""
    var anotherLongString = "Another long string that is definitely longer than the limit set.";
    """
    count, long_strings = calculate_score(js_content)
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


# def calculate_score(code_content: str) -> int:
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
# long_strings_count = calculate_score(code_content)
# print(f"Number of long strings: {long_strings_count}")
