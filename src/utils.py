RULES_PATH_HTML = "src/static-features/html"
RULES_PATH_JS = "src/static-features/js"
RULES_PATH_URL = "src/static-features/url"

# The number of encoded URLs and The number of IP address in elements sources
ENCODED_URLS_AND_IPS = [
    ("img", "src"),
    ("img", "lowsrc"),
    ("img", "dynsrc"),
    ("object", "data"),
    ("frame", "src"),
    ("iframe", "src"),
    ("embed", "src"),
    ("script", "src"),
    ("video", "src"),
    ("audio", "src"),
    ("source", "src"),
    ("img", "srcset"),
    ("a", "href"),
    ("a", "ping"),  # 示例：同一个标签的不同属性
    ("link", "href"),
    ("applet", "code"),
    ("meta", "content"),
    ("body", "background"),
    # 添加更多标签和属性对应关系
]


def merge_dicts_add_values(dict1: dict, dict2: dict) -> dict:
    # 创建一个新字典来存储结果
    result = dict1.copy()  # 先将dict1的内容复制到结果字典中

    # 遍历dict2的每个键值对
    for key, value in dict2.items():
        if key in result:
            # 如果键在结果字典中已存在，则将值相加
            result[key] += value
        else:
            # 如果键不存在，则直接添加到结果字典中
            result[key] = value

    return result
