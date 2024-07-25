import re
from collections import defaultdict

# 定义VBScript函数列表
vbscript_functions = [
    # 日期/时间函数。用于生成时间戳或进行时间计算，可能用于触发定时攻击。
    "Date",
    "Time",
    "Now",
    "DateAdd",
    "DateDiff",
    "DatePart",
    "DateSerial",
    "DateValue",
    "Day",
    "Hour",
    "Minute",
    "Month",
    "MonthName",
    "Second",
    "Weekday",
    "WeekdayName",
    "Year",
    # 转换函数。用于数据类型转换，可能用于格式化恶意数据或绕过类型检查
    "CBool",
    "CByte",
    "CCur",
    "CDate",
    "CDbl",
    "Chr",
    "CInt",
    "CLng",
    "CSng",
    "CStr",
    "Hex",
    "Oct",
    # 格式化函数。用于修改数据的显示方式，可能用于掩饰恶意数据
    "FormatCurrency",
    "FormatDateTime",
    "FormatNumber",
    "FormatPercent",
    # 数学函数。用于执行数学计算，可能用于算法攻击或生成特定的攻击向量。
    "Abs",
    "Atn",
    "Cos",
    "Exp",
    "Fix",
    "Int",
    "Log",
    "Rnd",
    "Round",
    "Sgn",
    "Sin",
    "Sqr",
    "Tan",
    # 数组函数。用于操作数组，可能用于构造复杂的数据结构以绕过安全检查。
    "Array",
    "IsArray",
    "Join",
    "LBound",
    "UBound",
    "Split",
    "Filter",
    # 字符串函数。用于处理字符串，常用于数据隐藏、代码混淆或构造特定的攻击载荷。
    "InStr",
    "InStrRev",
    "LCase",
    "Left",
    "Len",
    "LTrim",
    "Mid",
    "Replace",
    "Right",
    "RTrim",
    "Space",
    "StrComp",
    "StrReverse",
    "Trim",
    "UCase",
    # 文件和网络I/O函数。用于读写文件或网络通信，可能用于数据窃取或恶意软件分发。
    "CreateObject",
    "GetObject",
    # 其他常用函数
    "Eval",
    "Execute",
    "ExecuteGlobal",
    "VarType",
    "TypeName",
    "IsEmpty",
    "IsNull",
    "IsNumeric",
    "IsDate",
    # 错误处理
    "Err",  # 可能不是函数，而是被用到的变量？比如Err.Number
    "OnError",
    # 环境函数
    "Environ",
    "WScript",
    # 原文列出的和第一次生成的
    "split",
    "ubound",
    "eval",
    "CreateElement",
    "SetAttribute",
    # "CreateObject",
    "Document.write",
    # "Err.clear",
]


def calculate_score(vbscript_code: str) -> dict:
    # 使用defaultdict初始化函数计数器
    function_counts = defaultdict(int)

    # 对于每个函数，使用正则表达式在VBScript代码中查找匹配项
    for function in vbscript_functions:
        # 正则表达式匹配函数，考虑大小写
        pattern = re.compile(rf"\b{function}\b", re.IGNORECASE)
        matches = pattern.findall(vbscript_code)
        function_counts[function] = len(matches)

    return sum(function_counts.values())  # 暂且只统计总和


if __name__ == "__main__":
    # 示例VBScript代码
    vbscript_code = """
    <Script Language=VBScript>
    On Error Resume Next
    Set Ob = Document.CreateElement("object")
    Ob.SetAttribute "classid", "clsid:BD96C556-65A3-11D0-983A-00C04FC29E36"
    Set Pop = Ob.Createobject("Adodb.Stream","")
    If Not Err.Number = 0 then Err.clear
    Document.write("<embed src=flash.swf></embed>")
    Document.write ("<iFrame src=real.htm width=0 height=0></ifrAme>")
    Document.write ("<iFrame src=new.htm width=0 height=0></ifrAme>") Else
    Document.write ("<iFrame src=help.htm width=0 height=0></ifrAme>")
    End If</Script>
    """

    # 计算并打印函数使用次数
    function_usage = calculate_score(vbscript_code)
    print("VBScript Function usage:", function_usage)
