import re

from bs4 import BeautifulSoup

# encode--obfuscate


def calculate_score(html_content: str) -> int:
    reserved_html_encodings = [
        "&lt;",
        "&gt;",
        "&amp;",
        "&quot;",
        "&apos;",
        "&nbsp;",
        "&times;",
        "&divide;",
    ]
    encoded_string_count = 0
    encoded_html_count = 0

    # 查找所有文本节点
    # text_nodes = soup.find_all(string=True)
    strings = html_content.split()
    for text in strings:
        # print(f"text:{text}")
        # 检查“&#+数字;”模式出现的次数
        if len(re.findall(r"&#[0-9]+;", text)) >= 2:
            encoded_string_count += 1

        # 检查是否包含HTML保留字符的编码形式
        if any(
            reserved_encoding in text for reserved_encoding in reserved_html_encodings
        ):
            encoded_html_count += 1

    return encoded_string_count + encoded_html_count


if __name__ == "__main__":
    # 示例HTML内容
    html_content = """
    &lt;iframe src=&quot; Evil.com &quot; width=0 height=0&gt;&lt;/iframe&gt;
    """
    # 调用函数并打印结果
    res = calculate_score(html_content)
    print(f"encoded count:{res}")
