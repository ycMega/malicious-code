# from pyesprima.pyesprima import parse
# from slimit import ast
# from slimit.parser import Parser
# from slimit.visitors import nodevisitor
# import json
# import subprocess
from pyjsparser import parse


# 识别包含“长”字符串使用的循环，这可以帮助识别用于解码混淆脚本的例程
def parse_js_code(js_code: str):
    try:
        ast = parse(js_code)
        return ast
    except Exception as e:
        print(f"Error parsing JavaScript code: {e}")
        return None


def find_decoding_routines(ast):
    long_string_threshold = 10  # 定义“长”字符串的长度阈值
    decoding_routines = []

    def visit(node, inside_loop=False):
        if isinstance(node, dict):
            if node["type"] in ["ForStatement", "WhileStatement", "DoWhileStatement"]:
                # 当进入循环时，设置inside_loop为True
                inside_loop = True
            elif (
                node["type"] == "Literal"
                and isinstance(node["value"], str)
                and len(node["value"]) > long_string_threshold
            ):
                # 如果在循环内找到“长”字符串，记录为解码例程
                if inside_loop:
                    decoding_routines.append(node)
                    return  # 找到后返回，避免重复记录
            # 递归遍历子节点
            for key in node:
                if isinstance(node[key], (dict, list)):
                    visit(node[key], inside_loop)

        elif isinstance(node, list):
            for item in node:
                visit(item, inside_loop)

    visit(ast)  # 从根节点开始遍历AST
    return decoding_routines


def calculate_score(js_content: str) -> int:
    # try:
    ast = parse_js_code(js_content)
    decoding_routines = find_decoding_routines(ast)
    print("Decoding routines:", decoding_routines)
    return len(decoding_routines)


# except Exception as e:
#     print(f"Error calculating score: {e}")
#     return 0


# 示例JavaScript代码
if __name__ == "__main__":
    js_code = """
    var encodedStr = "aGVsbG8gd29ybGQ=";
    var decodedStr = "";
    for (var i = 0; i < encodedStr.length; i++) {
        var longString = "This is a very long string...";
        decodedStr += String.fromCharCode(encodedStr.charCodeAt(i) ^ 0x30);
    }
    """
    print("Detected decoding routines:", calculate_score(js_code))


# def calculate_score(js_file_path: str) -> int:
#     result = subprocess.run(
#         ["node", "parse.js", js_file_path], capture_output=True, text=True
#     )
#     output = json.loads(result.stdout)
#     return output["count"]


# 使用示例
# count = calculate_score("your_js_file.js")
# print(f"Detected decoding routines: {count}")
# 定义“长”字符串的最小长度
# LONG_STRING_MIN_LENGTH = 10


# def find_decoding_routines(js_code):
#     """
#     检测JavaScript代码中是否包含解码例程。
#     """
#     count = 0
#     parser = Parser()
#     tree = parser.parse(js_code)

#     for node in nodevisitor.visit(tree):
#         # 检查节点是否为循环结构
#         if isinstance(node, (ast.ForStatement, ast.WhileStatement)):
#             # 检查循环体内是否使用了长字符串
#             for child in nodevisitor.visit(node):
#                 if (
#                     isinstance(child, ast.String)
#                     and len(child.value) > LONG_STRING_MIN_LENGTH
#                 ):
#                     print("发现可能的解码例程")
#                     count += 1
#                     # break
#     return count


# 示例JavaScript代码
# js_code = """
# var longString = "这是一个非常非常长的字符串...";
# for (var i = 0; i < longString.length; i++) {
#     // 解码逻辑
# }
# """
# # 调用函数检测示例代码
# res = find_decoding_routines(js_code)
# print("find decoding routines:", res)

# cannot import name 'Syntax' from partially initialized module 'pyesprima' (most likely due to a circular import)

# detecting routines used to decode obfuscated scripts.
#  the AST of the JavaScript segment is analyzed to identify loops in which a “long” string is used
# 示例JavaScript代码


# def find_decoding_routines(node, parent=None):
#     """
#     递归遍历AST节点，寻找解码例程的特征。
#     """
#     count = 0
#     # 检查节点是否为循环结构
#     if isinstance(node, dict) and node.get("type") in [
#         "ForStatement",
#         "WhileStatement",
#     ]:
#         # 检查循环体内是否使用了长字符串
#         body = node.get("body", {})
#         if body.get("type") == "BlockStatement":
#             for statement in body.get("body", []):
#                 count += find_decoding_routines(statement, node)
#     elif isinstance(node, dict) and node.get("type") == "VariableDeclaration":
#         # 检查变量声明中是否包含长字符串
#         for declaration in node.get("declarations", []):
#             if (
#                 declaration.get("init", {}).get("type") == "Literal"
#                 and isinstance(declaration["init"].get("value", ""), str)
#                 and len(declaration["init"]["value"]) >= LONG_STRING_MIN_LENGTH
#             ):
#                 # print("发现可能的解码例程：", pyesprima.stringify(parent))
#                 count += 1
#     elif isinstance(node, dict):
#         for key, value in node.items():
#             if isinstance(value, dict):
#                 count += find_decoding_routines(value, node)
#             elif isinstance(value, list):
#                 for item in value:
#                     count += find_decoding_routines(item, node)
#     return count


# # 开始遍历AST


# # 解析JavaScript代码为AST
# ast = pyesprima.parse(js_code)
# res = find_decoding_routines(ast)
