def calculate_score(js_content: str, js_path: str = "") -> int:
    score = js_content.count("eval(")
    return score
