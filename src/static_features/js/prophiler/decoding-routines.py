# from pyesprima.pyesprima import parse
# from slimit import ast
# from slimit.parser import Parser
# from slimit.visitors import nodevisitor
# import json
# import subprocess
# from pyjsparser import parse

# todo: 由于不支持循环嵌套，本特征暂未实现
import deprecated
import escodegen
import esprima
from attr import has

from src.static_features.js import *
from src.utils.utils import parse_js_code

# deprecated 因为只是统计字符串数量，重复了


# 增强递归：在遍历时，可以将检测逻辑进一步抽象化，以便在任何节点上都能轻松调用。
# 配置化字符串长度阈值：可以考虑将字符串长度阈值作为参数传递，以便更灵活地调整。
# 记录字符串位置：除了检测字符串外，还可以记录字符串的位置，以便后续分析使用。


# class LoopLongStringJS(JSExtractor):
#     def __init__(self, web_data):
#         super().__init__(web_data)
#         self.meta = ExtractorMeta(
#             "js",
#             "LoopLongStringJS",
#             "prophiler",
#             "检测循环中长度达到30字符的字符串数量",
#             "1.0",
#         )

#     def extract(self) -> FeatureExtractionResult:
#         start_time = time.time()
#         js_content_list = self.web_data.content["js"]
#         info_dict = {}
#         for h in js_content_list:
#             start_time = time.time()
#             res = extract(h["content"])
#             info_dict[h["filename"]] = {
#                 "count": res,
#                 "time": time.time() - start_time,
#                 "additional_info": {},
#             }
#         return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def is_long_string(string, length_threshold=10):
    """判断字符串是否为长字符串."""
    return len(string) > length_threshold


def extract_long_strings(node, routine_code):
    """递归提取长字符串."""
    if not hasattr(node, "type"):
        return
    # Q：万一node不存在type属性呢？——但是目前找不到判断的方法
    # print(f"Current node: {escodegen.generate(node)}.")  # 输出当前遍历到的节点代码
    if node.type == "Literal" and isinstance(node.value, str):
        if is_long_string(node.value):
            routine_code.append(node)

    elif node.type == "TemplateLiteral":
        for elem in node.expressions:
            extract_long_strings(elem, routine_code)
        for quasis in node.quasis:
            # print(f"quasis value:{quasis.value}")
            routine_code.append(quasis.value)
            # quasis.value是raw+cooked形式，不是type+xx，无法被escodegen生成代码
            # extract_long_strings(quasis.value, routine_code)

    elif node.type in ["ArrayExpression", "ObjectExpression"]:
        for elem in (
            node.elements if node.type == "ArrayExpression" else node.properties
        ):
            extract_long_strings(
                elem.value if node.type == "ObjectExpression" else elem, routine_code
            )

    # 检查其他控制结构
    if node.type == "SwitchStatement":
        for case in node.cases:
            extract_long_strings(case.test, routine_code)
            for consequent in case.consequent:
                extract_long_strings(consequent, routine_code)

    # 检查函数和方法
    if node.type in [
        "FunctionDeclaration",  # Q：循环内部还能有函数定义吗
        "FunctionExpression",
        "ArrowFunctionExpression",
    ]:
        for param in node.params:
            extract_long_strings(param, routine_code)
        if node.body:
            extract_long_strings(node.body, routine_code)
    # 函数调用参数。和上面的不重复？
    if hasattr(node, "arguments") and node.arguments:
        for arg in node.arguments:
            extract_long_strings(arg, routine_code)
    if hasattr(node, "body") and node.body is not None:
        for inner_node in node.body:
            extract_long_strings(inner_node, routine_code)

    # 检查赋值和表达式
    if node.type == "VariableDeclaration":
        for decl in node.declarations:
            if decl.init:
                extract_long_strings(decl.init, routine_code)
    elif node.type == "AssignmentExpression":
        if node.right:
            extract_long_strings(node.right, routine_code)

    elif node.type == "ExpressionStatement":  # 关键！
        if hasattr(node, "expression"):
            extract_long_strings(node.expression, routine_code)

    elif node.type == "IfStatement":
        if node.test:
            extract_long_strings(node.test, routine_code)
        if node.consequent:
            extract_long_strings(node.consequent, routine_code)
        if node.alternate:
            extract_long_strings(node.alternate, routine_code)


@deprecated.deprecated(
    reason="This function is deprecated due to unstable performance of parsing the ast."
)
def extract_decoding_routines(ast):
    """提取可能的解码例程并统计数量."""
    routines = []

    for node in ast.body:
        if node.type in ["ForStatement", "WhileStatement", "DoWhileStatement"]:
            routine_code = []
            for inner_node in node.body.body:
                extract_long_strings(inner_node, routine_code)

            if routine_code:
                routines.append(routine_code)

    return routines


def extract(js_content: str) -> int:
    # 匹配循环结构，包含更多种类
    loop_pattern = r"\b(for|while|do\s*while)\s*\(.*?\)\s*{(.*?)}"

    # 查找所有循环
    loops = re.findall(loop_pattern, js_content, re.DOTALL)

    string_pattern = r"""
    "(?:\\.|[^"\\\n])*"         |  # 双引号字符串，支持换行
    '(?:\\.|[^'\\\n])*'         |  # 单引号字符串，支持换行
    `(?:\\.|[^`\\\n])*`         # 模板字符串，支持换行
"""

    long_strings_found = []
    start = 0
    threshold = 10
    while True:
        # 查找下一个循环或条件结构
        match = re.search(loop_pattern, js_content[start:], re.DOTALL)
        if not match:
            break

        start += match.start() + len(match.group(0))

        # 查找匹配的结束括号
        brace_count = 1
        while brace_count > 0:
            if js_content[start] == "{":
                brace_count += 1
            elif js_content[start] == "}":
                brace_count -= 1
            start += 1

        # 获取结构内部的代码
        body = js_content[match.end() : start - 1]

        # 查找长字符串
        long_strings = re.findall(string_pattern, body, re.VERBOSE)
        long_strings_found.extend(s for s in long_strings if len(s) > threshold)

    return len(long_strings_found), long_strings_found
    # pattern = r'\'(.*?)\'|"([^"]*?)"|\'\'\'(.*?)\'\'\'|"""(.*?)"""'
    # ast, error = parse_js_code(js_content)
    # if error:
    #     print(f"Error parsing code: {error}")
    #     # return -1
    # # print(ast)
    # decoding_routines = extract_decoding_routines(ast)
    # # print("Decoding routines:", decoding_routines)
    # return sum(len(routine) for routine in decoding_routines), decoding_routines


# except Exception as e:
#     print(f"Error calculating score: {str(e)}")
#     return 0


# 示例JavaScript代码
if __name__ == "__main__":
    # filename = "webpages\\bilibili\\jquery1.7.2.min.js"
    # print("Detected decoding routines:", extract("", filename))
    js_code = """
    for (var i = 0; i < encodedStr.length; i++) {
        var longString = "This is a very long string...";
        var a = b = "looooooooong string";
          
        if (longString.includes("long")) {
            b = a = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
            console.log(`Logging a long string...`);
        }
        var obj = { key: "Another long string" };
        decodedStr += String.fromCharCode(encodedStr.charCodeAt(i) ^ 0x30);
    }
    """
    count, long_strings = extract(js_code)
    print(f"long strings count:{count}\nlong strings:{long_strings}")
    # count, decoding_routines = extract(js_code)
    # print("Detected decoding routines:", count)
    # for routine in decoding_routines:
    #     for code in routine:
    #         try:
    #             print(f"Routine code: {escodegen.generate(code)}")
    #         except Exception as e:
    #             print(f"Error generating code: {str(e)}, code: {code}")


# def find_decoding_routines(ast):
#     long_string_threshold = 10  # 定义“长”字符串的长度阈值
#     decoding_routines = []

#     def visit(node, inside_loop=False):
#         if isinstance(node, dict):
#             if node["type"] in ["ForStatement", "WhileStatement", "DoWhileStatement"]:
#                 # 当进入循环时，设置inside_loop为True
#                 inside_loop = True
#             elif (
#                 node["type"] == "Literal"
#                 and isinstance(node["value"], str)
#                 and len(node["value"]) > long_string_threshold
#             ):
#                 # 如果在循环内找到“长”字符串，记录为解码例程
#                 if inside_loop:
#                     decoding_routines.append(node)
#                     return  # 找到后返回，避免重复记录
#             # 递归遍历子节点
#             for key in node:
#                 if isinstance(node[key], (dict, list)):
#                     visit(node[key], inside_loop)

#         elif isinstance(node, list):
#             for item in node:
#                 visit(item, inside_loop)

#     visit(ast)  # 从根节点开始遍历AST
#     return decoding_routines


# def extract(js_file_path: str) -> int:
#     result = subprocess.run(
#         ["node", "parse.js", js_file_path], capture_output=True, text=True
#     )
#     output = json.loads(result.stdout)
#     return output["count"]


# 使用示例
# count = extract("your_js_file.js")
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
