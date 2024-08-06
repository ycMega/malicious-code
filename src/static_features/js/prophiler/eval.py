import re


def calculate_score(js_content: str) -> int:
    # 使用正则表达式匹配 eval() 函数调用
    pattern = r"\beval\s*\(.*?\)"
    matches = re.findall(pattern, js_content)
    return len(matches)


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    function test() {
        eval('console.log("Hello World");');
        var x = eval('2 + 2');
        eval("alert('Test');");
    }
    eval('console.log("Outside");');
    // This is not eval() function
    var y = evalSomething('notEval()');
    """

    count = calculate_score(sample_js)
    print(f"Number of occurrences of eval(): {count}")
