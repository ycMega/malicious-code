from src.static_rules import *


class TestRule(Rule):
    def __init__(self, feature_dict):
        super().__init__(feature_dict, name="TestRule")
        self.description = "the ratio of word count to char count in html"

    def analyze(self):
        html_word_count = self.feature_dict["html"]["WordCount"]["Count"]
        html_char_count = self.feature_dict["html"]["CharCount"]["Count"]
        ratio = html_char_count / html_word_count
        normal_ratio = 4
        score = (
            min(100, (1 - normal_ratio / ratio) * 100 + 20)
            if ratio > normal_ratio
            else 0
        )

        return AnalysisResult(
            self.name,
            score,
            {"description": self.description},
        )

    def add_sub_rule(self, rule: "Rule"):
        """添加子规则"""
        self.sub_rules.append(rule)
