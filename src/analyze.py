import re

from bs4 import BeautifulSoup
from pandas import merge

from score import calculate_total_scores
from utils import RULES_PATH_HTML, RULES_PATH_JS, RULES_PATH_URL, merge_dicts_add_values


def extract_urls(text: str) -> list:
    # 正则表达式匹配URL
    # 没有明确的边界符 ^ 和 $，这意味着它可能匹配字符串中的URL，即使URL不是字符串的开头或结尾
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    urls = re.findall(url_pattern, text)
    return urls


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
