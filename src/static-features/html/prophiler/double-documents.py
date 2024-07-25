from bs4 import BeautifulSoup


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")

    # 计数器
    double_document_count = {"html": 0, "head": 0, "title": 0, "body": 0}

    # 计数。可以这样遍历dict？
    for tag in double_document_count:
        double_document_count[tag] = len(soup.find_all(tag))

    # 检测是否存在多个元素
    presence_of_double_documents = {
        k: v for k, v in double_document_count.items() if v > 1
    }

    return presence_of_double_documents


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
        <head>
            <title>Another Title</title>
        </head>
        <body>
            <p>Another body content.</p>
        </body>
    </html>
    """
    double_documents = calculate_score(html_content)
    if double_documents:
        print("Presence of double documents:")
        for element, count in double_documents.items():
            print(f"{element}: {count}")
    else:
        print("No double documents found.")
