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
    ("sound", "src"),
    ("source", "src"),
    ("style", "src"),
    ("audio", "src"),
    ("track", "src"),
    ("input", "src"),
    ("bgsound", "src"),
    ("applet", "code"),
    ("link", "href"),
    ("a", "href"),
    ("base", "href"),
    ("area", "href"),
    ("meta", "content"),  # The value of URL in content attribute. 如何提取？
    ("body", "background"),
    # 添加更多标签和属性对应关系
]


def merge_dicts_add_values(*dicts: dict) -> dict:
    """
    合并任意数量的字典。如果字典中有相同的键，则将它们的值相加。
    :param dicts: 任意数量的字典
    :return: 合并后的字典
    """
    result: dict = {}
    for dictionary in dicts:
        for key, value in dictionary.items():
            # 如果键已存在于结果字典中，则添加值，否则设置键的值
            result[key] = result.get(key, 0) + value
    return result
