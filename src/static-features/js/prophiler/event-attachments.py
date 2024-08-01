# from pyjsparser import parse
import re

from src.utils.utils import parse_js_code

# 定义感兴趣的事件和可以attach的函数
# 似乎重要的是事件？函数只是筛选范围？
EVENTS = {"onerror", "onload", "onbeforeunload", "onunload"}
EVENT_ATTACHMENT_FUNCTIONS = {
    "addEventListener",
    "attachEvent",
    "dispatchEvent",
    "fireEvent",
}


def count_event_attachments(node, event_counts):
    """递归遍历 AST，统计事件附件数量."""
    print(f"Current node: {node}.")  # 输出当前遍历到的节点代码
    if isinstance(node, list):
        for item in node:
            count_event_attachments(item, event_counts)
        return

    if hasattr(node, "type"):
        if node.type == "CallExpression":
            # 检查函数名称
            callee_name = getattr(node.callee, "name", None)
            if callee_name in EVENT_ATTACHMENT_FUNCTIONS:
                # 检查参数中是否包含感兴趣的事件
                if node.arguments and len(node.arguments) > 1:
                    event_arg = node.arguments[0]
                    if event_arg.type == "Literal" and event_arg.value in EVENTS:
                        event_counts[0] += 1  # 统计事件附件数量
                        event_counts[1].append(event_arg.value)  # 记录事件类型

        # 根据节点类型处理子节点
        if node.type in ["Program", "BlockStatement"]:
            for stmt in node.body:
                count_event_attachments(stmt, event_counts)

        elif node.type == "FunctionDeclaration" or node.type == "FunctionExpression":
            for param in node.params:
                count_event_attachments(param, event_counts)
            count_event_attachments(node.body, event_counts)

        elif node.type in [
            "IfStatement",
            "ForStatement",
            "WhileStatement",
            "DoWhileStatement",
        ]:
            count_event_attachments(node.test, event_counts)
            count_event_attachments(node.body, event_counts)
            if hasattr(node, "alternate"):
                count_event_attachments(node.alternate, event_counts)

        elif node.type == "ExpressionStatement":
            count_event_attachments(node.expression, event_counts)

        elif node.type == "ReturnStatement":
            if node.argument:
                count_event_attachments(node.argument, event_counts)

        # 其他类型的处理
        elif node.type == "AssignmentExpression":
            count_event_attachments(node.left, event_counts)
            count_event_attachments(node.right, event_counts)

        elif node.type == "VariableDeclaration":
            for decl in node.declarations:
                count_event_attachments(decl, event_counts)

        elif node.type == "VariableDeclarator":
            count_event_attachments(node.init, event_counts)


# 主调用函数
def analyze_events(ast):
    event_counts = [0, []]  # [事件附件数量, 事件类型列表]
    count_event_attachments(ast, event_counts)
    return event_counts[0], event_counts[1]


# 使用示例
# ast = esprima.parseScript(your_javascript_code)
# analyze_events(ast)


def calculate_score(js_content: str) -> int:
    # print("event-attachments.py: calculate_score")
    # ast, error = parse_js_code(js_content)
    # if error:
    #     print(f"Error parsing code: {error}")
    #     return -1
    # count, total_event_attachments = analyze_events(ast)
    # return count, total_event_attachments
    pattern = (
        r"\b("
        + "|".join(EVENT_ATTACHMENT_FUNCTIONS)
        + r")\s*\(\s*\'?("  # \s*匹配函数名、左括号后可能存在的空白字符；匹配零个或一个单引号 '，允许事件名称前有可选的引号
        + "|".join(EVENTS)
        + r")\'?\s*,"  # 逗号表示函数调用参数的结束
    )
    matches = re.findall(pattern, js_content)
    event_counts = len(matches)  # 事件附件总数
    matched_events = [match[1] for match in matches]  # 记录匹配的事件
    return event_counts, matched_events


if __name__ == "__main__":
    # 测试示例
    js_content = """
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
    # document.attachEvent('onerror', function() {
    #     console.log('Error occurred');
    # });
    # window.onload = function() { console.log('Loaded'); };
    # window.addEventListener('error', function() { console.log('Error'); });
    # document.attachEvent('onbeforeunload', function() { console.log('Before unload'); });
    count, total_event_attachments = calculate_score(js_content)
    print(f"Number of event attachments: {count}")
    print("Events attached:")
    for event in set(total_event_attachments):  # 去重事件类型
        print(event)
