import bisect
import csv
import json
import os
from typing import Dict, List, Tuple

import deprecated

from src.io.async_logger import GLOBAL_LOGGER
from src.utils.utils import make_serializable


class Rule:
    def __init__(self, feature_dict: dict, name: str, version: str = "1.0"):
        self.feature_dict = feature_dict  # 特征字典
        self.name = name  # 规则名称
        self.time = None  # 记录检测时间
        self.sub_rules: List["Rule"] = []  # 子规则集合
        self.version = version
        self.description = ""  # 规则描述

    def analyze(self):
        """
        根据特征结果分析得分和接下来的规则。
        :param feature_result: 特征提取结果的字典
        :return: 得分和下一个规则
        """
        raise NotImplementedError("子类必须实现这个方法。")

    def add_sub_rule(self, rule: "Rule"):
        """添加子规则"""
        self.sub_rules.append(rule)


class AnalysisResult:
    def __init__(self, rule_name: str, res_dict: Dict[str, Dict] = None):
        self.rule_name = rule_name  # 规则名称
        self.res_dict = (
            res_dict or {}
        )  # 结果字典，key为filename，value为dict，字段包含score(float)和additional_info(dict)

    def __repr__(self):
        return (
            f"AnalysisResult(rule_name={self.rule_name}, result dict={self.res_dict})"
        )


class OverallAnalysisResult:
    def __init__(self, path: str):
        self.dir_path = path  # 文件路径
        self.results: list[AnalysisResult] = []  # 存储各个规则的分析结果

    def add_result(self, analysis_result: AnalysisResult):
        """添加单个分析结果并更新总得分和总用时"""
        self.results.append(analysis_result)

    def save_to_csv(self):
        filename = os.path.join(self.dir_path, "analysis_result.csv")
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # 写入表头
            writer.writerow(["Rule", "Filename", "Score"])

            # 写入数据
            try:
                for res in self.results:
                    for filename, info in res.res_dict.items():
                        writer.writerow([res.rule_name, filename, info["score"]])
            except Exception as e:
                print(f"Error saving to CSV: {str(e)}")
                GLOBAL_LOGGER.error(f"Error saving to CSV: {str(e)}")

    def save_to_json(self):
        filename = os.path.join(self.dir_path, "analysis_result.json")
        try:
            with open(filename, mode="w", encoding="utf-8") as file:
                res_dict: dict = {}
                for res in self.results:
                    try:
                        serialized_res = make_serializable(res.res_dict)
                        res_dict[res.rule_name] = serialized_res
                    except Exception as e:
                        GLOBAL_LOGGER.error(
                            f"Error serializing result of {res.rule_name}: {str(e)}. Ignoring it."
                        )
                file.write(json.dumps(res_dict, indent=4))
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
            GLOBAL_LOGGER.error(f"Error saving to JSON: {str(e)}")

    def do_summary(self):
        self.save_to_csv()
        self.save_to_json()

    def judge(self) -> Dict[str, float]:
        """判断是否通过,从0到100越大越恶意"""
        max_scores = {}
        for res in self.results:
            for filename, info in res.res_dict.items():
                score = info["score"]
                if filename not in max_scores:
                    max_scores[filename] = 0
                max_scores[filename] = max(max_scores[filename], score)
        return max_scores


# 用于动态指定区间和对应的规则列表，可以用于记录“子规则”，构建规则树
class SuccRule:
    def __init__(self):
        self.boundaries: List[float] = [0, 100]  # 存储分界点
        self.rules: List[List[Rule]] = [[]]  # 存储对应的规则列表

    def add_segment(self, start: float, end: float, new_rules: List[Rule]) -> None:
        """新增一段区间"""
        if start >= end:
            raise ValueError("Start must be less than end.")

        # 找到插入位置
        max_index = len(self.boundaries)
        right_bound = self.boundaries[-1]

        left_index = bisect.bisect_left(self.boundaries, start)
        right_index = bisect.bisect_right(
            self.boundaries, end
        )  # 返回值在有序列表中值的右侧位置。
        old_right_rule = self.rules[right_index - 1] if right_index > 0 else None
        print(
            f"boundaries:{self.boundaries}, start={start}, end={end}, left_index={left_index}, right_index={right_index}"
        )

        # 记录被删除的区间
        deleted_segments = []
        if left_index < right_index:
            for index in range(left_index, right_index):
                deleted_segments.append(
                    (self.boundaries[index], self.boundaries[index + 1])
                )

            # 删除内部分界点和规则
            del self.rules[left_index:right_index]
            self.boundaries[left_index:right_index] = []  # 删除对应的分界点

        # 插入新的分界点和规则
        self.boundaries.insert(left_index, start)
        self.boundaries.insert(left_index + 1, end)
        self.rules.insert(left_index, new_rules)

        if right_index < max_index and end < right_bound:

            self.rules.insert(left_index + 1, old_right_rule)

        print(
            f"Added segment: [{start}, {end}), with rules: {[rule.name for rule in new_rules]}"
        )
        return deleted_segments

    def remove_segment(self, index: int) -> None:
        """删除指定区间"""
        max_idx = len(self.rules)
        if index < 0 or index >= max_idx:
            raise IndexError("Invalid index for removal.")

        # 找到对应的分界点
        start = self.boundaries[index]
        end = self.boundaries[index + 1]
        if 0 < index < max_idx - 1:  # 删除中间区间，两侧区间各占一半
            self.boundaries[index + 1] = (start + end) / 2
        elif index == 0:
            self.boundaries[index + 1] = start
        self.boundaries.pop(index)
        del self.rules[index]
        print(f"removed segment: [{start}, {end})")

    @deprecated.deprecated(version="1.0", reason="not supported yet")
    def modify_segment(self, index: int, new_start: float, new_end: float) -> None:
        """修改区间范围"""
        if not 0 <= index < len(self.rules):
            raise IndexError(f"Index {index} out of bounds.")
        if new_start >= new_end:
            raise ValueError("New start must be less than new end.")

        existing_rules = self.rules[index]  # 获取原有规则
        self.remove_segment(index)  # 删除原有区间
        self.add_segment(new_start, new_end, existing_rules)  # 使用原有规则添加新区间

    def display(self) -> None:
        """友好的输出区间和规则信息"""
        if not self.boundaries:
            print("No segments available.")
            return

        for i in range(len(self.rules)):
            print(
                f"boundaries:{self.boundaries}. Segment {i}: Range: [{self.boundaries[i]}, {self.boundaries[i + 1]}), Rules: {[rule.name for rule in self.rules[i]]}"
            )


if __name__ == "__main__":
    # 测试示例
    rule1 = SuccRule()
    sub_rule1 = Rule({}, "Rule1")
    sub_rule2 = Rule({}, "Rule2")

    rule1.add_segment(0, 30, [sub_rule1])
    rule1.display()
    rule1.add_segment(30, 60, [sub_rule2])
    rule1.display()

    rule1.add_segment(20, 40, [Rule({}, "Rule4")])
    # 修改区间
    # rule1.modify_segment(0, 10, 50)
    rule1.display()

    # 删除区间
    rule1.remove_segment(1)
    rule1.display()
    rule1.add_segment(10, 60, [Rule({}, "Rule3")])
    rule1.display()
    rule1.remove_segment(2)
    rule1.display()
