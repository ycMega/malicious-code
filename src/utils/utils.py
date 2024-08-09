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


def make_serializable(obj):
    """检查对象是否可 JSON 序列化，如果不可序列化则转换为可序列化形式"""
    try:
        json.dumps(obj)  # 尝试序列化
        return obj  # 如果可序列化，返回原对象
    except (TypeError, OverflowError) as exc:
        # 处理不可序列化的情况
        if isinstance(obj, set):
            return list(obj)  # 将 set 转换为 list
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}  # 递归处理字典
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]  # 递归处理列表
        else:
            raise ValueError(
                f"对象类型 {type(obj)} 无法序列化"
            ) from exc  # 保留原始异常信息


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


def extract_urls(text: str) -> list:
    # 正则表达式匹配URL
    # 没有明确的边界符 ^ 和 $，这意味着它可能匹配字符串中的URL，即使URL不是字符串的开头或结尾
    # url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    # 协议部分：^(https?|ftp):\/\/：匹配以 http://, https://, 或 ftp:// 开头的 URL。
    # 其他协议: |^[a-zA-Z][a-zA-Z\d+\-.]*:\/\/：匹配以其他协议（如 mailto: 或自定义协议）开头的 URL。
    # 邮箱格式: |^[a-zA-Z0-9\-._~%!$&'()*+,;=]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+：匹配邮箱格式的字符串。
    # 无协议 URL: |^(www\.)[^\s/$.?#].[^\s]*：匹配以 www. 开头的 URL。
    # 通用部分: [^\s/$.?#].[^\s]*：匹配 URL 的主体部分，确保不包含空白字符和某些特殊字符。

    url_pattern = r'(?:(?:https?|ftp):\/\/|\/\/|www\.)[^\s<>,;\'"(){}]+(?:\.[^\s<>,;\'"(){}]+)+[^\s<>,;\'"(){}]*'
    urls = re.findall(url_pattern, text)
    return urls


def parse_js_code(js_code: str, js_path: str = ""):
    # 8.6：经常遇到无法正确解析JS的情况，随后遍历AST会出错，因此放弃遍历AST
    try:
        ast = esprima.parseScript(js_code, tolerant=True)  # 使用 tolerant 选项
        return ast, None  # 返回 AST 和无错误
    except esprima.Error as e:
        error_info = str(e)
        return ast, error_info  # 返回无 AST 和错误信息

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
    #         print(f"JSON decode error: {str(e)}")


# def parse_js_code_python(js_code: str):
#     lines = js_code.split("\n")
#     for line in lines:
#         try:
#             ast = parse(line)
#         except Exception as e:
#             print(f"Error in line: {line}")
#             print(f"Error: {str(e)}")
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
#         print(f"Failed to parse JavaScript code: {str(e)}")
#         return None
#     return ast
