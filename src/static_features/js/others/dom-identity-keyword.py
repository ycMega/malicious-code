from collections import Counter

from src.static_features.js import *


class DomIdentityKeywordJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "DomIdentityKeywordJS",
            "others",
            "部分identity和keyword的出现次数（包括在字符串中出现）",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        js_list = self.web_data.content["js"]
        info_dict = {}
        for h in js_list:
            start_time = time.time()
            res, features = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": features,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


# 在网页的 DOM（文档对象模型）中，身份和关键字通常与用户交互和安全性相关。
# 例如，身份可能表示用户角色或登录信息，而关键字则可能与表单字段、输入要求或用户认证相关。


def extract(js_content: str) -> dict:
    features = {
        "identities_count": 0,
        "identities": [],
        "keywords_count": 0,
        "keywords": [],
    }

    # 定义更完整的身份和关键字
    identities = [
        "admin",
        "user",
        "guest",
        "member",
        "superuser",
        "administrator",
        "root",
        "client",
        "customer",
    ]

    keywords = [
        "username",
        "password",
        "email",
        "login",
        "submit",
        "register",
        "confirm",
        "access",
        "credentials",
        "authentication",
    ]

    # 查找身份
    for identity in identities:
        id_count = len(
            re.findall(r"\b" + re.escape(identity) + r"\b", js_content, re.IGNORECASE)
        )
        features["identities_count"] += id_count
        if id_count > 0:
            features["identities"].append(identity)

    # 统计关键字出现次数
    # 目前的统计也包括字符串里出现的单词
    for keyword in keywords:
        key_count = len(
            re.findall(r"\b" + re.escape(keyword) + r"\b", js_content, re.IGNORECASE)
        )
        features["keywords_count"] += key_count
        if key_count > 0:
            features["keywords"].append(keyword)

    return features["identities_count"] + features["keywords_count"], features


if __name__ == "__main__":
    # 示例调用
    js_example = """
    var username = "testUser";
    var password = "123456";
    document.getElementById("login").innerHTML = "Please enter your username and password.";
    """

    sum_count, features = extract(js_example)
    print(f"DOM identites and keywords: {features}")
