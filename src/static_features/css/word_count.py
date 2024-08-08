from src.static_features.css import *


class WordCountCSS(CSSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "css",
            "WordCountCSS",
            "yyc",
            "统计CSS文件的单词数和可见字符数",
            "1.0",
        )

    # 似乎不能执行typechecked？会导致在模块加载阶段（而不是执行）报错，因为sys.modules中还没有对应的key
    def extract(self) -> FeatureExtractionResult:
        css_list = self.web_data.content["css"]
        info_dict = {}
        for css in css_list:
            start_time = time.time()
            content = css["content"]
            # 统计字符数（去掉空白字符和不可见字符）
            char_count = len(re.sub(r"\s+", "", content))

            # 统计单词数
            words = re.findall(r"\b\w+\b", content)
            word_count = len(words)
            info_dict[css["filename"]] = {
                "count": word_count,
                "time": time.time() - start_time,
                "additional_info": {"CharCount": char_count},
            }

        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)
