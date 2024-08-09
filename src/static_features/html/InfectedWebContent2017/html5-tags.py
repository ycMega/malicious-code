import html

from src.static_features.html import *


# some HTML5 tags are capable of loading files in themselves
class HTML5_TagsHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "HTML5_TagsHTML",
            "InfectedWebContent2017",
            "检查特定tags中是否有外部或过长（超过150字符）的src属性，以及是否隐藏",
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


def extract(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "lxml")
    tags_to_check = ["embed", "video", "audio", "track", "source"]
    external_or_long_src_count = 0
    hidden_tags_count = 0

    for tag_name in tags_to_check:
        for tag in soup.find_all(tag_name):
            # 检查src属性
            src = tag.get("src", "")
            if src.startswith(("http://", "https://")) or len(src) > 150:
                external_or_long_src_count += 1

            # 检查是否隐藏
            if tag_name in ["video", "audio"] and (
                tag.get("width") == "0" or tag.get("height") == "0"
            ):
                hidden_tags_count += 1
            elif tag_name in ["embed", "track", "source"] and tag.find_parent(
                "video", {"width": "0", "height": "0"}
            ):
                hidden_tags_count += 1

    return external_or_long_src_count + hidden_tags_count


if __name__ == "__main__":
    # 示例HTML内容
    html_content = """
    <video width="0" height="0" controls>
    <source src="www.evil.com/malicious.mp4" type="video/mp4"></video>
    """

    res = extract(html_content)
    print(f"html5-tags count:{res}")
