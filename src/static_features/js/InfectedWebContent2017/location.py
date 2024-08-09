from src.static_features.js import *


class LocationJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "LocationJS",
            "InfectedWebContent2017",
            "location对象的部分属性和函数出现次数",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
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


# The properties of a location object可能被读取，也可能成为initial sources of taint values


def extract(js_content: str):
    # 定义需要统计的location对象的属性和函数
    features = [
        "location.pathname",
        "location.port",
        "location.hostname",
        "location.host",
        "location.hash",
        "location.protocol",
        "location.search",
        "location.assign",
        "location.reload",
        "location.replace",
    ]

    # 初始化一个字典来存储每个特征的使用次数
    feature_counts = {feature: 0 for feature in features}

    # 对每个特征使用正则表达式进行匹配，并计算使用次数
    for feature in features:
        pattern = re.compile(re.escape(feature))
        matches = pattern.findall(js_content)
        feature_counts[feature] = len(matches)

    return sum(feature_counts.values())


if __name__ == "__main__":
    # 示例使用
    js_content = """
    window.onload = function() {
        console.log(location.pathname);
        location.assign('http://example.com');
        location.reload();
        location.replace('http://example.com/newPage');
    };
    """
    feature_counts = extract(js_content)
    print(f"location features count: {feature_counts}")
    # for feature, count in feature_counts.items():
    #     print(f"{feature}: {count}")
