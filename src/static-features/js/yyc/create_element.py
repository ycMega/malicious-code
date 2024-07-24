def calculate_score(js_content: str) -> int:
    score = js_content.count("document.createElement(")
    return score
