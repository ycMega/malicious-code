import difflib


# todo：不同文件间的比较——时间特征
def compare_versions(old_html, new_html):
    old_lines = old_html.splitlines()
    new_lines = new_html.splitlines()
    diff = difflib.unified_diff(old_lines, new_lines, lineterm="")
    return list(diff)


# 假设 old_html 和 new_html 是两个版本的 HTML 文档
old_html = "<html><body><a href='link1'>Link 1</a></body></html>"
new_html = "<html><body><a href='link1'>Link 1</a><p>New paragraph</p></body></html>"

changes = compare_versions(old_html, new_html)
print("版本变化:", changes)
