from src.static_features.js import *


class WordCountJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "WordCountJS",
            "others",
            "js文件单词数和可见字符数",
            "1.0",
        )

    def calculate_score(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_list = self.web_data.content["js"]
        js_content = "\n".join(d["content"] for d in js_list)

        char_count = len(re.sub(r"\s+", "", js_content))
        words = re.findall(r"\b\w+\b", js_content)
        res = len(words)
        addition = {"CharCount": char_count}
        return FeatureExtractionResult(
            self.meta.filetype, self.meta.name, res, time.time() - start_time, addition
        )
