from urllib.parse import urlparse

from bs4 import BeautifulSoup


def calculate_score(html_content: str, base_url: str) -> int:
    # 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 获取当前页面的域名
    base_domain = urlparse(base_url).netloc

    # 统计外部域的元素数量
    external_count = 0

    # 检查所有的 <img>, <script>, 和 <a> 标签
    for tag in soup.find_all(["img", "script", "a"]):
        src = tag.get("src") or tag.get("href")
        if src:
            src_domain = urlparse(src).netloc
            if src_domain and src_domain != base_domain:
                external_count += 1

    return external_count


if __name__ == "__main__":
    # 测试代码
    sample_html = """
    <html>
    <head>
        <title>Test Page</title>
        <script src="https://external.com/script.js"></script>
        <script src="/internal/script.js"></script>
    </head>
    <body>
        <img src="https://external.com/image.png" />
        <img src="/internal/image.png" />
        <a href="https://external.com/page.html">External Link</a>
        <a href="/internal/page.html">Internal Link</a>
    </body>
    </html>
    """

    base_url = "https://example.com"
    score = calculate_score(sample_html, base_url)
    print(f"External source element count: {score}")
