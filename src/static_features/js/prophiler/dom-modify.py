from src.static_features.js import *


class DomModifyJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DomModifyJS",
            "prophiler",
            "常见DOM修改函数的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 常见的 DOM 修改函数列表
DOM_MODIFYING_FUNCTIONS = {
    "appendChild",
    "removeChild",
    "replaceChild",
    "insertBefore",
    "insertAdjacentElement",
    "insertAdjacentHTML",
    "setAttribute",
    "removeAttribute",
    "clearAttributes",
    "createElement",
    "createTextNode",
    "setInnerHTML",
    "document.write",
    "document.writeln",
    "replaceNode",
    # 这俩似乎是某个AI自己添加的？
    "innerHTML",
    "outerHTML",
}


def extract(js_content: str):
    # 查找所有函数调用
    function_calls = re.findall(r"(\w+)\s*\(", js_content)
    dom_modifying_count = 0

    for func in function_calls:
        if func in DOM_MODIFYING_FUNCTIONS:
            dom_modifying_count += 1

    return dom_modifying_count


if __name__ == "__main__":
    # 测试示例
    js_content = """
    document.body.appendChild(document.createElement('div'));
    var elem = document.getElementById('myId');
    elem.setAttribute('data-test', 'value');
    elem.removeChild(document.getElementById('child'));
    clearAttributes(); // IE specific
    """
    count = extract(js_content)
    print(f"Number of DOM-modifying functions: {count}")

# from pyjsparser import parse

# # 定义常见的 DOM 修改函数
# DOM_MODIFYING_FUNCTIONS = {
#     "appendChild",
#     "removeChild",
#     "replaceChild",
#     "insertBefore",
#     "insertAdjacentHTML",
#     "insertAdjacentElement",
#     "createElement",
#     "createTextNode",
#     "setAttribute",
#     "removeAttribute",
#     "clearAttributes",
#     "replaceNode",
#     "innerHTML",
#     "outerHTML",
# }


# def is_dom_modifying_function(node):
#     if isinstance(node, dict):
#         if (
#             node.get("type") == "CallExpression"
#             and isinstance(node["callee"], dict)
#             and node["callee"].get("type") == "MemberExpression"
#         ):
#             function_name = node["callee"]["property"]["name"]
#             return function_name in DOM_MODIFYING_FUNCTIONS
#     return False


# def extract(node):
#     count = 0
#     if isinstance(node, dict):
#         if is_dom_modifying_function(node):
#             count += 1

#         for value in node.values():
#             if isinstance(value, (dict, list)):
#                 count += extract(value)

#     elif isinstance(node, list):
#         for item in node:
#             count += extract(item)
#     return count


# def extract(js_content: str, js_path: str="") -> int:
#     ast = parse(js_content)
#     total_dom_modifying_functions = extract(ast)
#     return total_dom_modifying_functions


# js_content = """
# document.createElement('div');
# document.body.appendChild(document.createTextNode('Hello'));
# var elem = document.getElementById('test');
# elem.innerHTML = '<p>Test</p>';
# """
# print("dom modifying functions:", extract(js_content))
