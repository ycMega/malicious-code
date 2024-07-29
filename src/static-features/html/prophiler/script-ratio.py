from bs4 import BeautifulSoup

# the percentage of scripting content in a page


def calculate_score(html_content: str) -> float:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 获取整个页面的字符数
    total_chars = len(html_content)

    # 查找所有 <script> 标签并统计其内容的字符数
    script_content_length = sum(
        len(script.string) if script.string else 0 for script in soup.find_all("script")
    )

    # 计算脚本内容的百分比
    if total_chars == 0:
        return 0.0

    percentage = (script_content_length / total_chars) * 100

    return percentage


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

    percentage = calculate_score(sample_html)
    print(f"Percentage of scripting content: {percentage:.2f}%")
