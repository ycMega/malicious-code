import os
import re

from pyjsparser import PyJsParser


def preprocess_js_code(js_code):
    # 匹配正则表达式的正则模式
    regex_pattern = r"/([^\/]+?)([gimuy]*)"

    # 替换正则表达式
    def replace_regex(match):
        regex_body = match.group(0)
        # 转义斜杠和特殊字符

        escaped_regex = regex_body.replace(
            "/", r"\/"
        )  # .replace(":", r"\:").replace("?", r"\?")
        escaped_regex = regex_body
        return f"{escaped_regex}"  # 转为字符串

    # 替换代码中的正则表达式
    processed_code = re.sub(regex_pattern, replace_regex, js_code)
    processed_code = re.sub(r"(?<=\d)_(?=\d)", "", processed_code)
    return processed_code


if __name__ == "__main__":
    # 示例 JavaScript 代码
    js_code = """
    bJ = /^(?:GET|HEAD)$/,
    bM = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,"""
    import json
    import subprocess

    filename = "webpages\\bilibili\\jquery1.7.2.min.js"
    # 调用 Node.js 脚本
    result = subprocess.run(
        ["node", "src/utils/parse.js", filename],
        text=True,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )

    # 检查返回码
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        # print(f"stdout: {result.stdout}")  # 输出调试信息
        print(f"stderr: {result.stderr}")  # 输出调试信息

        # 解析输出的 AST
        try:
            ast = json.loads(result.stdout)  # 解析最后一行的 AST
            # print(json.dumps(ast, indent=2))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

    # 打印生成的 AST
    # print(json.dumps(ast, indent=2))
    # # 预处理代码
    # processed_code = preprocess_js_code(js_code)

    # # 解析处理后的代码
    # parser = PyJsParser()
    # lines = processed_code.split("\n")
    # origin_lines = js_code.split("\n")
    # print(f"original lines:{origin_lines}. lines:{lines}")
    # for idx, line in enumerate(lines):
    #     try:
    #         ast = parser.parse(line)
    #     except Exception as e:
    #         print(f"Original line:{origin_lines[idx]}")
    #         print(f"Error in line: {line}.Error: {e}")
    #         break
    # try:
    #     ast = parser.parse(processed_code)
    #     print(ast)
    # except Exception as e:
    #     print(f"Error: {e}")
