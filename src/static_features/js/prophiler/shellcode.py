from src.static_features.js import *


class ShellcodeJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "ShellcodeJS",
            "prophiler",
            "对每个字符串统计以下特征：不可打印字符（ASCII[32,126]外）占比、十六进制字符占比、重复字符的规律性。取所有字符串中的最大评分",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, max_string = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": max_string,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 被称为“shellcode”是因为它经常用于打开攻击者与受害者系统之间的命令行界面（即“shell”）。Shellcode的危害包括但不限于：


# 远程执行代码：攻击者可以远程执行任意代码，控制受害者的计算机。
# 数据泄露：攻击者可以利用shellcode窃取或删除重要数据。
# 拒绝服务：通过消耗系统资源，shellcode可以使受害者的系统变得不稳定，甚至崩溃。
# 传播恶意软件：shellcode可以用来下载并安装更多的恶意软件，如勒索软件或后门程序。

# todo：从分数到score的映射。以及intervals检测函数还有很大优化空间


def is_hexadecimal(s):
    return all(c in "0123456789abcdefABCDEF" for c in s)


# 计算重复字符的规律性：检查字符串中的字符是否以某种规律间隔重复，并计算重复模式的覆盖范围。
# 返回概率评分：基于重复模式的强度和覆盖范围，返回一个介于0到1之间的概率评分。
# 目前没有好的实现，且时间复杂度过大


def has_regular_intervals(s):
    min_pattern_length = 3
    max_pattern_length = 6  # 不可过大
    total_score = 0
    patterns_found = 0

    for pattern_length in range(min_pattern_length, max_pattern_length + 1):
        pattern_to_positions = {}
        for i in range(len(s) - pattern_length + 1):
            pattern = s[i : i + pattern_length]
            if pattern in pattern_to_positions:
                pattern_to_positions[pattern].append(i)
            else:
                pattern_to_positions[pattern] = [i]

        for pattern, positions in pattern_to_positions.items():
            if len(positions) > 1:
                intervals = [
                    positions[i] - positions[i - 1] for i in range(1, len(positions))
                ]
                if len(set(intervals)) == 1:
                    total_score += 1
                else:
                    # 为间隔不完全一致的模式分配得分，得分基于间隔的变异程度
                    interval_consistency = 1 / len(set(intervals))
                    total_score += interval_consistency
                patterns_found += 1

    if patterns_found > 0:
        return total_score / patterns_found
    else:
        return 0


def extract(js_content: str):
    # strings = re.findall(r'"([^"]*)"', js_content) + re.findall(
    #     r"'([^']*)'", js_content
    # )
    string_pattern = r"""
    "(?:\\.|[^"\\\n])*"         |  # 双引号字符串，支持换行
    '(?:\\.|[^'\\\n])*'         |  # 单引号字符串，支持换行
    `(?:\\.|[^`\\\n])*`         # 模板字符串，支持换行
"""
    # pattern = r"(['\"]{1,3})(.*?)(\1)"
    strings = re.findall(
        string_pattern, js_content, re.VERBOSE | re.DOTALL
    )  # 允许在正则表达式中使用空格和注释；使 . 匹配所有字符，包括换行符（允许跨多行的匹配）
    probabilities = []

    for s in strings:
        if len(s) == 0:  # 避免除以0
            continue

        non_printable = sum(not (32 <= ord(c) <= 126) for c in s)
        prob_non_printable = non_printable / len(s)

        prob_hexadecimal = len(s) if is_hexadecimal(s) else 0
        prob_hexadecimal /= len(s)

        prob_regular_intervals = 1 if has_regular_intervals(s) else 0

        # 综合考虑三种方法的评分
        # score = (
        #     prob_non_printable * 0.4
        #     + prob_hexadecimal * 0.4
        #     + prob_regular_intervals * 0.2
        # )
        # print(
        #     f"prob_non_printable:{prob_non_printable}, prob_hexadecimal:{prob_hexadecimal}, prob_regular_intervals:{prob_regular_intervals}"
        # )
        score = max(prob_non_printable, prob_hexadecimal, prob_regular_intervals)
        probabilities.append((score, s))

    max_score = max(probabilities, key=lambda x: x[0])[0] if probabilities else 0
    max_string = max(probabilities, key=lambda x: x[0])[1] if probabilities else ""

    return max_score, max_string


# 示例用法
if __name__ == "__main__":
    # 测试示例
    js_content = """
    var shell = "48656c6c6f"; // Hexadecimal shellcode
    var shellcode = "4c8bdc4981ec88000000488b8424900000004833c448898424800000004889442410";
    var nonPrintable = "This is a test string with non-printable \x01\x02\x03 characters.";
    var normalString = "Just a normal string.";
    """
    probability = extract(js_content)
    print(f"Shellcode presence probability: {probability}")


# def has_regular_intervals(s):
#     n = len(s)
#     if n < 2:
#         return 0.0  # 字符串过短

#     max_length = 5  # 最大重复字符数
#     pattern_count = {}

#     # 查找字符模式
#     for length in range(1, max_length + 1):
#         for i in range(n - length + 1):
#             substring = s[i:i + length]
#             if substring not in pattern_count:
#                 pattern_count[substring] = []
#             pattern_count[substring].append(i)

#     max_strength = 0
#     total_coverage = 0

#     # 计算强度和覆盖范围
#     for substring, indices in pattern_count.items():
#         if len(indices) < 2:
#             continue

#         intervals = [indices[i] - indices[i - 1] for i in range(1, len(indices))]
#         min_interval = min(intervals)
#         strength = len(indices) / (n / min_interval)

#         coverage = (indices[-1] - indices[0] + len(substring)) / n

#         max_strength = max(max_strength, strength)
#         total_coverage += coverage

#     # 计算评分
#     if max_strength == 0:
#         return 0.0

#     score = (total_coverage / len(pattern_count)) * (max_strength / n)
#     return min(max(score, 0), 1)


# def has_regular_intervals(s, min_interval=5, max_interval=20):
#     if len(s) < min_interval:
#         return 0  # 字符串太短，无法形成有意义的间隔

#     interval_scores = []

#     for interval in range(min_interval, min(max_interval, len(s) // 2) + 1):
#         repeat_pattern_score = 0
#         total_checks = 0

#         for start in range(interval):
#             pattern = s[start::interval]
#             most_common_char = max(set(pattern), key=pattern.count)
#             common_char_count = pattern.count(most_common_char)

#             # 计算当前间隔下，最常见字符的比例
#             if len(pattern) > 0:
#                 repeat_pattern_score += common_char_count / len(pattern)
#                 total_checks += 1

#         if total_checks > 0:
#             # 计算当前间隔的平均得分，并加入到间隔得分列表中
#             interval_scores.append(repeat_pattern_score / total_checks)

#     if interval_scores:
#         # 返回所有间隔得分的最大值作为最终得分
#         return max(interval_scores)
#     else:
#         return 0
