# 可以通过计算这两个特征的比率（例如，字符数与词数的比率）来评估网页的正常性。
# 通常，正常网页的词数和字符数比率相对稳定，而恶意代码可能会导致字符数显著增加
def calculate_score(html_content: str) -> int:
    # 去除 HTML 标签
    import re

    text_content = re.sub(r"<[^>]+>", "", html_content)

    # 计算字符数和词数
    char_count = len(text_content)
    word_count = len(text_content.split())

    # 防止除零错误
    if word_count == 0:
        return 0

    # 计算评分：字符数与词数的比率
    score = char_count / word_count

    # 返回评分，阈值可根据实际情况调整
    return int(score)


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
    <h1>Hello World</h1>
    <p>This is a sample paragraph for testing.</p>
    </body>
    </html>
    """

    score = calculate_score(sample_html)
    print("the ratio of characters to words is:", score)
