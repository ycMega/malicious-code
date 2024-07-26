def calculate_score(js_content: str, js_path: str = "") -> int:
    score = js_content.count("document.write(") + js_content.count("document.writeln(")
    return score
