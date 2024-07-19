from bs4 import BeautifulSoup

from constants import RULES_PATH_HTML
from score import calculate_total_scores


def analyze_html(html_file_path: str) -> dict:
    # 读取 HTML 文件内容
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # 解析 HTML 内容为 BeautifulSoup 对象
    soup = BeautifulSoup(html_content, "lxml")  # 或使用 'html.parser'
    total_scores = calculate_total_scores(soup, RULES_PATH_HTML)

    return total_scores


# 示例调用
# 注意：你需要提供实际的 HTML 文件路径
# total_scores = analyze_html('path/to/your/html_file.html')
# print(total_scores)
