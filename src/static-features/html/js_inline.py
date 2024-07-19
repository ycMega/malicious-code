from bs4 import BeautifulSoup

from constants import RULES_PATH_JS
from score import calculate_total_scores


# inline JS funcs
# e.g. eval 似乎应该提取出来然后应用js规则？
def calculate_score(soup: BeautifulSoup):
    total_js_score = 0
    inline_js = ""
    # 查找所有的 <script> 标签
    script_tags = soup.find_all("script")

    for script in script_tags:
        # 确保 <script> 标签没有 src 属性（即，它是内联的）
        if not script.get("src"):
            # 提取内联 JavaScript 代码
            inline_js += script.string
    if inline_js != "":
        # 将 JavaScript 代码传入分数统计函数
        js_score = calculate_total_scores(inline_js, RULES_PATH_JS)
        total_js_score = js_score["total_score"]

    return total_js_score
    # scripts = soup.find_all("script")
    # score = sum(1 for script in scripts if "eval(" in script.text)  # * 10
    # return score
