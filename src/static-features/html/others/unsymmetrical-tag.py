import re

from bs4 import BeautifulSoup


def calculate_score(html_content: str) -> dict:
    # 匹配所有开始标签和结束标签
    soup = BeautifulSoup(html_content, "lxml")
    tags = soup.find_all()
    tags = re.findall(r"(</?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>", html_content)
    # print("tags:", tags)
    array = []
    asymmetrical_tags = {}
    self_closing_tags = {
        "br",
        "hr",
        "img",
        "input",
        "meta",
        "link",
        "base",
        "area",
        "col",
        "embed",
        "source",
        "track",
        "wbr",
    }

    for tag_type, tag_name in tags:
        if tag_name not in self_closing_tags:  # 不是自闭合标签
            if tag_type == "<":  # 是开始标签
                array.append(tag_name)
            else:  # 是结束标签
                # print(f"array={array}, tag={tag_name}")
                is_matched = False
                # 匹配上的元素未必在栈顶，因为栈顶可能就是一个unsymmetrical tag
                for i, name in enumerate(reversed(array)):
                    if name == tag_name:
                        del array[len(array) - 1 - i]
                        is_matched = True
                        break
                if not is_matched:
                    if tag_name in asymmetrical_tags:
                        asymmetrical_tags[tag_name] += 1
                    else:
                        asymmetrical_tags[tag_name] = 1

    # 剩余的栈中元素是未闭合的开始标签
    for tag in array:
        if tag in asymmetrical_tags:
            asymmetrical_tags[tag] += 1
        else:
            asymmetrical_tags[tag] = 1
    # asymmetrical_tags.extend(array)

    return sum(asymmetrical_tags.values()), asymmetrical_tags


if __name__ == "__main__":
    # 示例调用
    html_example = """
    <html>
    <head>
        <script src="https://example.com/script.js"></script>
    </head>
    <body>
        <div><img src="image.jpg"></div>
        <div>Content without closing tag
        <p>Paragraph without closing
    </body>
    </html>
    """

    sum_score, scores = calculate_score(html_example)
    print("Unsymmetrical tags:", scores)
