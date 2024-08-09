import os

from src.static_features.html import *
from src.utils.utils import ENCODED_URLS_AND_IPS


# use the IP address to escape the black list of security filters
class IPExistHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "IPExistHTML",
            "InfectedWebContent2017",
            "检查特定tag-attribute组合中是否存在IPv4/v6地址",
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
    # 定义IP地址的正则表达式
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    ip6_pattern = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")

    # 初始化IP地址的计数器
    ip_count = 0

    # 解析HTML内容
    soup = BeautifulSoup(html_content, "html.parser")

    # 遍历定义的标签和属性
    for tag, attribute in ENCODED_URLS_AND_IPS:
        for element in soup.find_all(tag):
            # 提取属性值
            attr_value = element.get(attribute)
            if attr_value and (
                ip_pattern.search(attr_value) or ip6_pattern.search(attr_value)
            ):
                ip_count += 1

    return ip_count


if __name__ == "__main__":
    html_contents = """
    <iframe src="187.202.16.2" width=0 height=0></iframe>
    """
    res = extract(html_contents)
    print(f"IP count:{res}")

# def add_init_py(root_dir):
#     for dir_name, subdirs, files in os.walk(root_dir):
#         init_path = os.path.join(dir_name, "__init__.py")
#         if not os.path.exists(init_path):
#             open(init_path, "a").close()
#             print(f"Added __init__.py in {dir_name}")


# # 替换这里的路径为你的项目根目录路径
# project_root_dir = "src"
# add_init_py(project_root_dir)
