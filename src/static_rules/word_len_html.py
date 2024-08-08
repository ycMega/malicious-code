from src.static_rules import *


class TestRule(Rule):
    def __init__(self, feature_dict):
        super().__init__(feature_dict, name="TestRule")
        self.description = "the ratio of word count to char count in html"

    def analyze(self):
        info_dict = self.feature_dict["html"]["WordCount"]
        res_dict = {}
        if not isinstance(info_dict, dict):
            print("Error: invalid html info in features.json-html-WordCount")
            return None
        for filename, info in info_dict.items():
            html_word_count = info["count"]
            html_char_count = self.feature_dict["html"]["CharCount"][filename]["count"]
            ratio = html_char_count / html_word_count
            normal_ratio = 4
            score = (
                min(100, (1 - normal_ratio / ratio) * 100 + 20)
                if ratio > normal_ratio
                else 0
            )
            res_dict[filename] = {
                "score": score,
                "additional_info": {"description": self.description},
            }

        return AnalysisResult(self.name, res_dict)

    def add_sub_rule(self, rule: "Rule"):
        """添加子规则"""
        self.sub_rules.append(rule)
