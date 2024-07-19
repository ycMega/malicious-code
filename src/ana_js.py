from constants import RULES_PATH_JS
from score import calculate_total_scores


def analyze_js(js_file_path: str) -> dict:
    with open(js_file_path, "r", encoding="utf-8") as file:
        js_content = file.read()

    total_scores = calculate_total_scores(js_content, RULES_PATH_JS)

    return total_scores


# 考虑用PyExecJS等工具进一步执行JS？
