from bs4 import BeautifulSoup


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    malicious_pattern_count = 0

    # 检查特定的 meta 标签
    for meta in soup.find_all("meta"):
        if meta.get("http-equiv") == "refresh":
            content = meta.get("content")
            if "index.php?spl=" in content:
                malicious_pattern_count += 1

    return malicious_pattern_count


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=index.php?spl=malicious">
            <meta http-equiv="refresh" content="5; url=another_page.html">
        </head>
        <body>
            <h1>Safe Content</h1>
        </body>
    </html>
    """
    count = calculate_score(html_content)
    print(f"Number of known malicious patterns: {count}")
