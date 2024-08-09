from src.static_features.html import *


# the frame tag is one of the tags that is susceptible to malicious attacks.
# Frameset tag is used to hold the number of frame tags
class FrameSetHTML(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "FrameSetHTML",
            "InfectedWebContent2017",
            "其中一个<frame>的尺寸被设置为100%，而其他<frame>的尺寸没有被明确指定（通常使用*表示）",
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
    # 初始化可疑frameset特征计数
    suspicious_frameset_count = 0

    # 查找所有frameset标签
    framesets = soup.find_all("frameset")
    for frameset in framesets:
        # 获取rows和cols属性
        rows = frameset.get("rows", "")
        cols = frameset.get("cols", "")

        # 检查rows和cols属性是否符合可疑条件：其中一个<frame>的尺寸被设置为100%，而其他<frame>的尺寸没有被明确指定（通常使用*表示）
        if ("100%" in rows.split(",") and "*" in rows.split(",")) or (
            "100%" in cols.split(",") and "*" in cols.split(",")
        ):
            suspicious_frameset_count += 1
    return suspicious_frameset_count


if __name__ == "__main__":
    # 示例HTML内容
    html_content = """
    <frameset rows="100%,*" frameborder="no" border="0" framespacing="0">
        <frame src="frame_a.htm">
        <frame src="frame_b.htm">
    </frameset>
    """
    print(f"Found {extract(html_content)} suspicious frameset(s).")
