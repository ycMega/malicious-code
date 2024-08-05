import json
import re
import subprocess

import esprima

# from pyjsparser import parse
METADATA_FILE = "metadata.yaml"
HAR_FILE = "network.har"

RULES_PATH_HTML = "src/static-features/html"
RULES_PATH_JS = "src/static-features/js"
RULES_PATH_URL = "src/static-features/url"
RULES_PATH_CSS = "src/static-features/css"
FILE_TYPES = ["html", "css", "js", "url", "har"]

# The number of encoded URLs and The number of IP address in elements sources
ENCODED_URLS_AND_IPS = [
    ("img", "src"),
    ("img", "lowsrc"),
    ("img", "dynsrc"),
    ("object", "data"),
    ("frame", "src"),
    ("iframe", "src"),
    ("embed", "src"),
    ("script", "src"),
    ("video", "src"),
    ("sound", "src"),
    ("source", "src"),
    ("style", "src"),
    ("audio", "src"),
    ("track", "src"),
    ("input", "src"),
    ("bgsound", "src"),
    ("applet", "code"),
    ("link", "href"),
    ("a", "href"),
    ("base", "href"),
    ("area", "href"),
    ("meta", "content"),  # The value of URL in content attribute. 如何提取？
    ("body", "background"),
    # 添加更多标签和属性对应关系
]


def merge_dicts_add_values(*dicts: dict) -> dict:
    """
    合并任意数量的字典。如果字典中有相同的键，则将它们的值相加。
    :param dicts: 任意数量的字典
    :return: 合并后的字典
    """
    result: dict = {}
    for dictionary in dicts:
        for key, value in dictionary.items():
            # 如果键已存在于结果字典中，则添加值，否则设置键的值
            result[key] = result.get(key, 0) + value
    return result


def parse_js_code(js_code: str, js_path: str = ""):
    try:
        ast = esprima.parseScript(js_code, tolerant=True)  # 使用 tolerant 选项
        return ast, None  # 返回 AST 和无错误
    except esprima.Error as e:
        return None, str(e)  # 返回无 AST 和错误信息

    # if js_path == "":
    #     print("ERROR:JS path should not be empty.")
    #     return None
    # result = subprocess.run(
    #     ["node", "src/utils/parse.js", js_path],
    #     text=True,
    #     check=True,
    #     capture_output=True,
    #     encoding="utf-8",
    # )
    # if result.returncode != 0:
    #     print(f"Error: {result.stderr}")
    # else:
    #     # print(f"stdout: {result.stdout}")  # 输出调试信息
    #     print(f"stderr: {result.stderr}")  # 输出调试信息

    #     # 解析输出的 AST
    #     try:
    #         ast = json.loads(result.stdout)  # 解析最后一行的 AST
    #         return ast
    #         # print(json.dumps(ast, indent=2))
    #     except json.JSONDecodeError as e:
    #         print(f"JSON decode error: {e}")


# def parse_js_code_python(js_code: str):
#     lines = js_code.split("\n")
#     for line in lines:
#         try:
#             ast = parse(line)
#         except Exception as e:
#             print(f"Error in line: {line}")
#             print(f"Error: {e}")
#             break
#     try:
#         # 匹配正则表达式的模式
#         # 匹配正则表达式的模式，确保不匹配字符串中的正则表达式
#         regex_pattern = r'(?<!["\'])/(.*?)/(?![*/])([gimuy]*)'
#         # regex_pattern = r"/(.*?)/([gimuy]*)"
#         regex_pattern = r"/([^\/]+?)([gimuy]*)"

#         # 函数用于替换正则表达式
#         def replace_regex(match):
#             regex_body = match.group(0)
#             # 转义斜杠
#             escaped_regex = regex_body.replace("/", r"\/")
#             return f"'{escaped_regex}'"  # 转为字符串

#         # 替换正则表达式中的特殊字符
#         # def replace_regex(match):
#         #     pattern = match.group(1).replace("\\", "\\\\").replace("/", "\\/")
#         #     flags = match.group(2)
#         #     return f"/{pattern}/{flags}"

#         # 使用正则表达式替换函数
#         regex_escaped_code = re.sub(regex_pattern, replace_regex, js_code)
#         fin_code = re.sub(
#             r"(?<=\d)_(?=\d)", "", regex_escaped_code
#         )  # 确保下划线前后都是数字
#         # js_code = js_code.replace("_", "") # 赋值_ = xxx会出错
#         ast = parse(fin_code)
#     except Exception as e:
#         print(f"Failed to parse JavaScript code: {e}")
#         return None
#     return ast
