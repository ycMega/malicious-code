from pyjsparser import parse


def calculate_score(js_code):
    ast = parse(js_code)
    count = [0]  # 使用列表来避免在递归函数中处理不可变的整数

    def traverse(node, path=[]):
        if isinstance(node, dict):
            if node.get("type") == "Literal" and isinstance(node.get("value"), str):
                identifier = path[-1] if path else "unknown"
                print(f'{identifier} = "{node.get("value")}"')
                count[0] += 1
            elif node.get("type") == "AssignmentExpression" and isinstance(
                node.get("right", {}).get("value"), str
            ):
                left_hand_side = reconstruct_expression(node["left"])
                print(f'{left_hand_side} = "{node.get("right", {}).get("value")}"')
                count[0] += 1
            elif node.get("type") == "Property" and isinstance(
                node.get("value", {}).get("value"), str
            ):
                property_name = node.get("key", {}).get("name", "unknown")
                print(f'{property_name} = "{node.get("value", {}).get("value")}"')
                count[0] += 1
            # 这里在init节点已经遍历过了？如果再次遍历会导致重复计数？

            # elif node.get("type") == "ConditionalExpression":
            #     identifier = path[-1] if path else "unknown"
            #     consequent = node.get("consequent", {})
            #     alternate = node.get("alternate", {})
            #     if isinstance(consequent.get("value"), str):
            #         print(f'{identifier} = "{consequent.get("value")}"')
            #         count[0] += 1
            #     if isinstance(alternate.get("value"), str):
            #         print(f'{identifier} = "{alternate.get("value")}"')
            #         count[0] += 1

            # 递归遍历子节点，同时传递当前节点作为父节点
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    traverse(value, path + [key])
        elif isinstance(node, list):
            for item in node:
                traverse(item, path)

    def reconstruct_expression(expression):
        """
        根据AST节点重构表达式。
        这里只处理了一些简单的情况，需要根据实际情况扩展。
        """
        if expression.get("type") == "Identifier":
            return expression.get("name")
        # 可以根据需要添加更多的AST节点类型处理
        return "unknown_expression"

    traverse(ast)
    return count[0]


# 示例JavaScript代码
if __name__ == "__main__":
    js_code = """
    var shellcode = "4c8bdc4981ec88000000488b8424900000004833c448898424800000004889442410";
    var normalString = "This is a normal string for testing.";
    var condition = true;
    var result = condition ? "string1" : "string2";
    var arr = ["string1", "string2"];
    """
    print(f"Number of direct string assignments: {calculate_score(js_code)}")
