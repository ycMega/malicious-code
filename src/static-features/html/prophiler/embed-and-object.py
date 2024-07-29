from bs4 import BeautifulSoup


def calculate_score(html_content: str) -> int:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 统计 <embed> 和 <object> 标签的数量
    embed_count = len(
        soup.find_all("embed")
    )  # 递归地统计<embed> tag（findall方法返回的就是tags）。recursive=False就是不嵌套
    object_count = len(soup.find_all("object"))

    # 返回总数量
    return embed_count + object_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <embed src="https://example.com/media" />
        <object data="https://example.com/object" type="application/pdf"></object>
        <embed src="https://example.com/media2" />
        <p>This is a paragraph.</p>
        <object data="https://example.com/object2" type="application/pdf"></object>
    </body>
    </html>
    """

    score = calculate_score(sample_html)
    print(f"Number of <embed> and <object> tags: {score}")
