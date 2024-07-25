from pyjsparser import parse

# 定义感兴趣的事件和可以attach的函数
# 似乎重要的是事件？函数只是筛选范围？
EVENTS = {"onerror", "onload", "onbeforeunload", "onunload"}
EVENT_ATTACHMENT_FUNCTIONS = {
    "addEventListener",
    "attachEvent",
    "dispatchEvent",
    "fireEvent",
}


def is_event_attachment(node):
    if isinstance(node, dict):
        if node.get("type") == "CallExpression":
            callee = node["callee"]
            if isinstance(callee, dict):
                if callee.get("type") == "MemberExpression":
                    function_name = callee["property"]["name"]
                    if function_name in EVENT_ATTACHMENT_FUNCTIONS:
                        # 检查事件名
                        args = node.get("arguments", [])
                        if (
                            args
                            and isinstance(args[0], dict)
                            and args[0].get("type") == "Literal"
                        ):
                            event_name = args[0]["value"]
                            if event_name in EVENTS:
                                print(
                                    f"Detected event attachment: {function_name} for event: {event_name}"
                                )
                                return True
    return False


def count_event_attachments(node):
    count = 0

    if isinstance(node, dict):
        if is_event_attachment(node):
            count += 1

        for value in node.values():
            if isinstance(value, (dict, list)):
                count += count_event_attachments(value)

    elif isinstance(node, list):
        for item in node:
            count += count_event_attachments(item)

    return count


# def count_event_attachments(ast):
#     count = 0
#     if isinstance(ast, dict):
#         # 检查是否是函数调用
#         if (
#             ast.get("type") == "CallExpression"
#             and ast.get("callee", {}).get("name") in EVENT_ATTACHMENT_FUNCTIONS
#         ):
#             # 检查第一个参数是否是我们感兴趣的事件
#             if ast.get("arguments", [{}])[0].get("value") in EVENTS:
#                 count += 1
#         # 递归遍历子节点
#         for key, value in ast.items():
#             if isinstance(value, (dict, list)):
#                 count += count_event_attachments(value)
#     elif isinstance(ast, list):
#         for item in ast:
#             count += count_event_attachments(item)
#     return count


def calculate_score(js_code: str) -> int:
    ast = parse(js_code)
    total_event_attachments = count_event_attachments(ast)
    return total_event_attachments


if __name__ == "__main__":
    # 测试示例
    js_code = """
    window.addEventListener('onload', function() {
    console.log('Page loaded');
    });
    document.attachEvent('onerror', function() {
        console.log('Error occurred');
    });
    window.onload = function() { console.log('Loaded'); };
    window.addEventListener('error', function() { console.log('Error'); });
    document.attachEvent('onbeforeunload', function() { console.log('Before unload'); });
    """
    score = calculate_score(js_code)
    print(f"Total event attachments: {score}")
