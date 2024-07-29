from bs4 import BeautifulSoup

# the number of script elements (both included via the src attribute, and inline)


def calculate_score(html_content: str) -> int:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "lxml")

    # 查找所有 <script> 标签
    script_tags = soup.find_all("script")

    # 统计 <script> 标签的数量
    script_count = len(script_tags)

    return script_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://example.com/script.js"></script>
        <script>
            console.log('Inline script');
        </script>
    </head>
    <body>
        <p>This is a sample page.</p>
        <script src="/internal/script.js"></script>
    </body>
    </html>
    """

    score = calculate_score(sample_html)
    print(f"Number of <script> elements: {score}")
