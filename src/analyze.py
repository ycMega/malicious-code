import os
import re

from bs4 import BeautifulSoup
from deprecated import deprecated
from pandas import merge

from score import calculate_total_scores
from src.utils.utils import (
    RULES_PATH_HTML,
    RULES_PATH_JS,
    RULES_PATH_URL,
    merge_dicts_add_values,
)


def extract_urls(text: str) -> list:
    # 正则表达式匹配URL
    # 没有明确的边界符 ^ 和 $，这意味着它可能匹配字符串中的URL，即使URL不是字符串的开头或结尾
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    urls = re.findall(url_pattern, text)
    return urls


# from typing import List


def extract_inline_js(html_content: str) -> str:
    """
    从HTML内容中提取内联JavaScript代码。
    :param html_content: HTML文件的内容
    :return: 包含所有内联JavaScript代码的列表
    """
    # 匹配不包含src属性的<script>标签内的JavaScript代码
    # 注意：这个正则表达式假设<script>标签内没有使用额外的">"字符
    # 对于复杂情况，可能需要更复杂的解析器，如BeautifulSoup
    inline_js_pattern = r"<script[^>]*>(.*?)</script>"
    # 允许'.'匹配换行符，以确保可以匹配跨行的JavaScript代码
    matches = re.findall(inline_js_pattern, html_content, re.DOTALL | re.IGNORECASE)

    # 过滤掉包含src属性的<script>标签
    # 这些通常是外部JavaScript文件的引用，而不是内联代码
    inline_js_codes = "".join(match for match in matches if "src=" not in match.lower())
    # inline_js_codes = [match for match in matches if "src=" not in match.lower()]
    return inline_js_codes


def analyze_content(file_path: str, content_type: str) -> dict:
    """
    分析内容，无论是HTML还是JS。
    :param content: 要分析的内容
    :param content_type: 内容类型，'html' 或 'js'
    :return: 分数字典
    """
    js_path = file_path
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    if content_type == "html":
        # 对HTML内容进行处理，例如提取内联JS
        js_content = extract_inline_js(content)
        if js_content:
            # 生成新的文件名
            base_name = os.path.splitext(file_path)[0]
            js_path = f"{base_name}-inline.js"
            # 将内联JS代码写入新的文件
            with open(js_path, "w", encoding="utf-8") as js_file:
                js_file.write(js_content)
        else:
            js_path = ""
    elif content_type == "js":
        # 直接处理JS文件内容
        js_content = content
    else:
        raise ValueError("Invalid content type. Use 'html' or 'js'.")
    total_scores: dict = {}
    # html文件和JS文件都有可能包含对方的特征以及URL的特征
    # js content是JS文件或<script>包裹的JS代码，是content的子集，只在检测js特征的时候可以减少工作量
    total_html_scores = calculate_total_scores(content, RULES_PATH_HTML)
    # print(f"calling calculate js: js_path={js_path}")
    total_js_scores = (
        calculate_total_scores(js_content, RULES_PATH_JS, js_path)
        if js_path != ""
        else {}
    )
    urls: list[str] = extract_urls(content)
    total_url_scores: dict = {}
    for url in urls:
        url_scores = calculate_total_scores(url, RULES_PATH_URL)
        total_url_scores = merge_dicts_add_values(total_url_scores, url_scores)
    total_scores = merge_dicts_add_values(
        total_html_scores, total_js_scores, total_url_scores
    )
    # print(
    #     f"html_scores:{total_html_scores}, js_scores:{total_js_scores}, url_scores:{total_url_scores}"
    # )
    # total_scores["url"] = sum(total_url_scores.values())

    return total_scores


@deprecated
def analyze_html(html_file_path: str) -> dict:
    # 读取 HTML 文件内容
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # 解析 HTML 内容为 BeautifulSoup 对象
    # soup = BeautifulSoup(html_content, "lxml")  # 或使用 'html.parser'
    total_scores = calculate_total_scores(html_content, RULES_PATH_HTML)
    urls: list[str] = extract_urls(html_content)
    total_url_scores: dict = {}
    for url in urls:
        url_scores = calculate_total_scores(url, RULES_PATH_URL)
        total_url_scores = merge_dicts_add_values(total_url_scores, url_scores)
    # total_scores["url"] = total_url_scores
    total_scores["url"] = sum(
        total_url_scores.values()
    )  # 暂时只统计总和。否则需要调整csv存储格式
    return total_scores


@deprecated
def analyze_js(js_file_path: str) -> dict:
    with open(js_file_path, "r", encoding="utf-8") as file:
        js_content = file.read()

    total_scores = calculate_total_scores(js_content, RULES_PATH_JS)
    urls: list[str] = extract_urls(js_content)
    total_url_scores: dict = {}
    for url in urls:
        url_scores = calculate_total_scores(url, RULES_PATH_URL)
        total_url_scores = merge_dicts_add_values(total_url_scores, url_scores)
    # total_scores["url"] = total_url_scores
    total_scores["url"] = sum(total_url_scores.values())

    return total_scores


# 考虑用PyExecJS等工具进一步执行JS？

# 示例调用
# 注意：你需要提供实际的 HTML 文件路径
# total_scores = analyze_html('path/to/your/html_file.html')
# print(total_scores)
