from src.static_rules import *


class WordLenCSS(Rule):
    def __init__(self, feature_dict):
        super().__init__(feature_dict, name="WordLenCSS")
        self.description = "the ratio of word count to char count in css"

    def analyze(self):
        css_word_count = self.feature_dict["css"]["WordCountCSS"]["Count"]
        css_char_count = self.feature_dict["css"]["WordCountCSS"]["AdditionalInfo"][
            "CharCount"
        ]
        ratio = css_char_count / css_word_count
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
