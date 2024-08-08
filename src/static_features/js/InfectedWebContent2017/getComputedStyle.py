import re


def extract(js_content: str):
    # 定义正则表达式来匹配getComputedStyle的使用
    pattern = re.compile(r"\bgetComputedStyle\b")

    # 使用正则表达式找到所有匹配项
    matches = pattern.findall(js_content)

    # 返回匹配项的数量，即getComputedStyle的使用次数
    return len(matches)


# 示例使用
if __name__ == "__main__":
    js_content = """
    var links = document.links;
    for (var i = 0; i < links.length; ++i)
    { var link = links[i];
    if (getComputedStyle(link, "").color
    == "rgb(0, 0, 128)") {
    // we know link.href has not been visited
    }
    else{
    // we know link.href has been visited
    }
    }
    """
    usage_count = extract(js_content)
    print(f"getComputedStyle usage count: {usage_count}")
