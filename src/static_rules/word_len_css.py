from src.static_rules import *


class WordLenCSS(Rule):
    def __init__(self, feature_dict):
        super().__init__(feature_dict, name="WordLenCSS")
        self.description = "the ratio of word count to char count in css"

    def analyze(self):
        info_dict = self.feature_dict["css"]["WordCountCSS"]
        res_dict = {}
        if not isinstance(info_dict, dict):
            print("Error: invalid css info in features.json-css-WordCountCSS")
            return None
        for filename, info in info_dict.items():
            css_word_count = info["count"]
            css_char_count = info["additional_info"]["CharCount"]
            ratio = css_char_count / css_word_count
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
