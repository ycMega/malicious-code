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

    def extract(self) -> FeatureExtractionResult:
        js_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_list:
            start_time = time.time()
            js_content = h["content"]
            char_count = len(re.sub(r"\s+", "", js_content))
            words = re.findall(r"\b\w+\b", js_content)
            res = len(words)
            addition = {"CharCount": char_count}
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": addition,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)
