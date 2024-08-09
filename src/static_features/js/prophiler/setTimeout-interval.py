from src.static_features.js import *


class SetTimeoutIntervalJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "SetTimeoutIntervalJS",
            "prophiler",
            "setTimeout和setInterval函数调用次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        start_time = time.time()
        js_content_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_content_list:
            start_time = time.time()
            res, func_counts = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": func_counts,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(js_content: str) -> int:
    # 使用正则表达式匹配 setTimeout() 和 setInterval() 函数调用
    timeout_pattern = r"\bsetTimeout\s*\(.*?\)"
    interval_pattern = r"\bsetInterval\s*\(.*?\)"

    timeout_matches = re.findall(timeout_pattern, js_content)
    interval_matches = re.findall(interval_pattern, js_content)

    return len(timeout_matches) + len(interval_matches), {
        "setTimeout_count": len(timeout_matches),
        "setInterval_count": len(interval_matches),
    }


if __name__ == "__main__":
    # 测试代码
    sample_js = """
    function test() {
        setTimeout(() => { console.log("Timeout 1"); }, 1000);
        var x = setInterval(() => { console.log("Interval 1"); }, 2000);
        setTimeout('console.log("Timeout 2");', 500);
        // Not a setTimeout call
        setTimeoutSomething('notSetTimeout()');
    }
    setInterval(() => { console.log("Interval 2"); }, 3000);
    """

    _, counts = extract(sample_js)
    print(f"Number of occurrences of setTimeout(): {counts['setTimeout_count']}")
    print(f"Number of occurrences of setInterval(): {counts['setInterval_count']}")
