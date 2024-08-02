import re
from collections import Counter

# 在网页的 DOM（文档对象模型）中，身份和关键字通常与用户交互和安全性相关。
# 例如，身份可能表示用户角色或登录信息，而关键字则可能与表单字段、输入要求或用户认证相关。


def calculate_score(js_content: str) -> dict:
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

    sum_count, features = calculate_score(js_example)
    print(f"DOM identites and keywords: {features}")
