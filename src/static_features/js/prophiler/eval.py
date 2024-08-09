from src.static_features.js import *


class EvalJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "EvalJS",
            "prophiler",
            "eval()函数的使用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content: str) -> int:
    # 使用正则表达式匹配 eval() 函数调用
    pattern = r"\beval\s*\(.*?\)"
    matches = re.findall(pattern, js_content)
    return len(matches)


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    function test() {
        eval('console.log("Hello World");');
        var x = eval('2 + 2');
        eval("alert('Test');");
    }
    eval('console.log("Outside");');
    // This is not eval() function
    var y = evalSomething('notEval()');
    """

    count = extract(sample_js)
    print(f"Number of occurrences of eval(): {count}")
