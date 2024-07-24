def calculate_score(js_content: str) -> int:
    score = js_content.count("document.write(") + js_content.count("document.writeln(")
    return score
