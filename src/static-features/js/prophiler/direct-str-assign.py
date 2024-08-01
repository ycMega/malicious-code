# from pyjsparser import PyJsParser
import escodegen

from src.utils.utils import parse_js_code

# 个人认为，direct assign几乎等价于字符串字面量出现次数。前者因为嵌套而很难统计。

# 直接赋值：例如 var str = "example";
# 属性设置：例如 obj.key = "value";
# 直接字符串声明：例如 const str = "example";
# 条件运算符中的字符串：例如 let result = condition ? "true" : "false";
# 数组中的字符串：例如 let arr = ["string1", "string2"];


def count_string_assignments(node, assignments):
    """递归提取长字符串."""
    # print(f"Current node: {escodegen.generate(node)}.")  # 输出当前遍历到的节点代码
    if node.type == "Literal" and isinstance(node.value, str):
        assignments.append(node)

    elif node.type == "TemplateLiteral":
        for elem in node.expressions:
            count_string_assignments(elem, assignments)
        for quasis in node.quasis:
            # print(f"quasis value:{quasis.value}")
            assignments.append(quasis.value)
            # quasis.value是raw+cooked形式，不是type+xx，无法被escodegen生成代码
            # count_string_assignments(quasis.value, assignments)

    elif node.type in ["ArrayExpression", "ObjectExpression"]:
        for elem in (
            node.elements if node.type == "ArrayExpression" else node.properties
        ):
            count_string_assignments(
                elem.value if node.type == "ObjectExpression" else elem, assignments
            )

    # 检查其他控制结构
    if node.type == "SwitchStatement":
        for case in node.cases:
            count_string_assignments(case.test, assignments)
            for consequent in case.consequent:
                count_string_assignments(consequent, assignments)

    # 检查函数和方法
    if node.type in [
        "FunctionDeclaration",  # Q：循环内部还能有函数定义吗
        "FunctionExpression",
        "ArrowFunctionExpression",
    ]:
        for param in node.params:
            count_string_assignments(param, assignments)
        if node.body:
            count_string_assignments(node.body, assignments)
    # 函数调用参数。和上面的不重复？
    if hasattr(node, "arguments") and node.arguments:
        for arg in node.arguments:
            count_string_assignments(arg, assignments)
    if hasattr(node, "body") and node.body is not None:
        for inner_node in node.body:
            count_string_assignments(inner_node, assignments)

    # 检查赋值和表达式
    if node.type == "VariableDeclaration":
        for decl in node.declarations:
            if decl.init:
                count_string_assignments(decl.init, assignments)
    elif node.type == "AssignmentExpression":
        if node.right:
            count_string_assignments(node.right, assignments)

    elif node.type == "ExpressionStatement":  # 关键！
        if hasattr(node, "expression"):
            count_string_assignments(node.expression, assignments)

    elif node.type == "IfStatement":
        if node.test:
            count_string_assignments(node.test, assignments)
        if node.consequent:
            count_string_assignments(node.consequent, assignments)
        if node.alternate:
            count_string_assignments(node.alternate, assignments)


def calculate_score(js_content: str):
    # print("direct-str-assign.py: calculate_score")
    ast, error = parse_js_code(js_content)
    if error:
        print(f"Error parsing code: {error}")
        return -1
    assignments = []  # 用于存储所有字符串赋值表达式
    for node in ast.body:
        count_string_assignments(node, assignments)  # 记录字符串赋值

    return len(assignments), assignments


# 示例JavaScript代码
if __name__ == "__main__":
    js_content = """

    var sh = shellcode = "4c8bdc4981ec88000000488b8424900000004833c448898424800000004889442410";
    var [x, y] = ["string1", "string2"];
    obj.prop = "string";
    x = shellcode = "This is a normal string for testing.";
    var condition = true;
    var result = condition ? "string1" : "string2";
    var arr = ["string1", "string2"];
    """
    # var sh = shellcode = "4c8bdc4981ec88000000488b8424900000004833c448898424800000004889442410";
    # var [x, y] = ["string1", "string2"];
    # obj.prop = "string";
    # x = shellcode = "This is a normal string for testing.";
    # var condition = true;
    # var result = condition ? "string1" : "string2";
    # var arr = ["string1", "string2"];
    count, assignments = calculate_score(js_content)
    print(f"Number of direct string assignments: {count}")
    for assignment in assignments:
        print(assignment)

# def count_string_assignments(node, assignments):
#     """记录字符串赋值表达式."""
#     print(f"Current node: {escodegen.generate(node)}.")  # 输出当前遍历到的节点代码
#     # print(f"Current node: {node}.")
#     # 如果是列表，递归处理每个项
#     if isinstance(node, list):
#         for item in node:
#             count_string_assignments(item, assignments)
#         return

#     # 处理单个节点
#     if hasattr(node, "type"):
#         if node.type == "ExpressionStatement":
#             count_string_assignments(node.expression, assignments)

#         elif node.type == "AssignmentExpression":
#             if node.right.type == "Literal" and isinstance(node.right.value, str):
#                 assignments.append(escodegen.generate(node))  # 记录赋值表达式
#             elif node.right.type == "TemplateLiteral":
#                 for elem in node.right.expressions:
#                     count_string_assignments(elem, assignments)
#                 for quasis in node.right.quasis:
#                     assignments.append(quasis.value.raw)  # 记录模板字符串
#             # elif node.right.type in [
#             #     "ArrayExpression",
#             #     "ObjectExpression",
#             #     "ConditionalExpression",
#             #     "AssignmentExpression",
#             # ]:
#             else:  # 对于其他所有情况都要遍历？
#                 count_string_assignments(node.right, assignments)

#         elif node.type == "VariableDeclaration":
#             for decl in node.declarations:
#                 if decl.init:
#                     if decl.init.type == "Literal" and isinstance(decl.init.value, str):
#                         assignments.append(
#                             escodegen.generate(node)
#                         )  # 记录变量初始化中的字符串
#                     elif decl.init.type == "TemplateLiteral":
#                         # 不考虑动态部分？
#                         # for elem in decl.init.expressions:
#                         #     count_string_assignments(elem, assignments)
#                         for quasis in decl.init.quasis:
#                             assignments.append(quasis.value.raw)
#                     # elif node.init and node.init.type in [
#                     #     "ArrayExpression",
#                     #     "ObjectExpression",
#                     #     "ConditionalExpression",
#                     #     "AssignmentExpression",
#                     # ]:
#                     else:
#                         count_string_assignments(decl.init, assignments)

#         elif node.type == "ArrayExpression":
#             for elem in node.elements:
#                 count_string_assignments(elem, assignments)

#         elif node.type == "ObjectExpression":
#             for prop in node.properties:
#                 count_string_assignments(prop, assignments)

#         elif node.type == "ConditionalExpression":
#             count_string_assignments(node.consequent, assignments)
#             count_string_assignments(node.alternate, assignments)

# def traverse(node, path=[]):
#     if isinstance(node, dict):
#         if node.get("type") == "Literal" and isinstance(node.get("value"), str):
#             identifier = path[-1] if path else "unknown"
#             # print(f'{identifier} = "{node.get("value")}"')
#             count[0] += 1
#         elif node.get("type") == "AssignmentExpression" and isinstance(
#             node.get("right", {}).get("value"), str
#         ):
#             left_hand_side = reconstruct_expression(node["left"])
#             # print(f'{left_hand_side} = "{node.get("right", {}).get("value")}"')
#             count[0] += 1
#         elif node.get("type") == "Property" and isinstance(
#             node.get("value", {}).get("value"), str
#         ):
#             property_name = node.get("key", {}).get("name", "unknown")
#             # print(f'{property_name} = "{node.get("value", {}).get("value")}"')
#             count[0] += 1
#         # 这里在init节点已经遍历过了？如果再次遍历会导致重复计数？

#         # elif node.get("type") == "ConditionalExpression":
#         #     identifier = path[-1] if path else "unknown"
#         #     consequent = node.get("consequent", {})
#         #     alternate = node.get("alternate", {})
#         #     if isinstance(consequent.get("value"), str):
#         #         print(f'{identifier} = "{consequent.get("value")}"')
#         #         count[0] += 1
#         #     if isinstance(alternate.get("value"), str):
#         #         print(f'{identifier} = "{alternate.get("value")}"')
#         #         count[0] += 1

#         # 递归遍历子节点，同时传递当前节点作为父节点
#         for key, value in node.items():
#             if isinstance(value, (dict, list)):
#                 traverse(value, path + [key])
#     elif isinstance(node, list):
#         for item in node:
#             traverse(item, path)

# def reconstruct_expression(expression):
#     """
#     根据AST节点重构表达式。
#     这里只处理了一些简单的情况，需要根据实际情况扩展。
#     """
#     if expression.get("type") == "Identifier":
#         return expression.get("name")
#     # 可以根据需要添加更多的AST节点类型处理
#     return "unknown_expression"
