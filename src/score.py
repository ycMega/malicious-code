import importlib.util
import os

from bs4 import BeautifulSoup

from src.utils.utils import merge_dicts_add_values


# 假设你有多个规则文件（例如rule1.py, rule2.py等），每个文件中都有一个名为calculate_score的函数
def load_rule_module(rule_path):
    spec = importlib.util.spec_from_file_location("rule_module", rule_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 能同时应用于html和JS吗
def calculate_total_scores(
    content: str, rules_path: str, content_path: str = ""
) -> dict:
    scores = {}  # 初始化一个空字典来存储每个特征的分数
    total_score = 0
    for rule_file in os.listdir(rules_path):
        if rule_file in ("__init__.py", "__pycache__"):
            continue
        if rule_file.endswith(".py"):
            rule_path = os.path.join(rules_path, rule_file)
            rule_module = load_rule_module(rule_path)
            # try:
            if hasattr(rule_module, "calculate_score"):
                score = (
                    rule_module.calculate_score(content, content_path)
                    if content_path != ""
                    else rule_module.calculate_score(content)  # for HTML
                )
                if isinstance(score, tuple):
                    score = score[0]  # 如果返回的是元组，则取第一个元素
                if score > -1:  # 表示此特征有效
                    total_score += score
                    feature_name = rule_file[:-3]  # 移除.py后缀来获取特征名称
                    scores[feature_name] = score  # 将特征名称和对应分数存储在字典中
                else:
                    print(f"Failed to calculate score for {rule_file}")
            # except Exception as e:
            #     print(f"Error calculating score for {rule_file}: {e}")
        else:
            item_path = os.path.join(rules_path, rule_file)
            if os.path.isdir(item_path):
                folder_scores = calculate_total_scores(content, item_path, content_path)
                total_score += folder_scores["total_score"]
                scores = merge_dicts_add_values(scores, folder_scores)

    scores["total_score"] = total_score  # 将总分也存储在字典中
    return scores


# def calculate_total_js_scores(js_str: str, js_rule_path: str) -> dict:
#     scores = {}
#     js_content_all = ""  # 目前的实现是把所有JS文件拼在一起，共同统计特征
#     for js_file in os.listdir(js_dir):
#         if js_file.endswith(".js"):
#             file_path = os.path.join(js_dir, js_file)
#             with open(file_path, "r", encoding="utf-8") as file:
#                 js_content_all += file.read() + "\n"

#     return scores
