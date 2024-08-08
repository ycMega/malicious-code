from re import S

from bs4 import BeautifulSoup

from src.static_features.html import *

# records the number of elements of type div, iframe, or object,
# whose dimension is less then a certain threshold (30 square pixels for the area, or 2 pixels for each side)
# 定义小面积的阈值
AREA_THRESHOLD = 30
SIDE_THRESHOLD = 2


class SmallAreaElements(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "SmallAreaElements",
            "prophiler",
            "高度/宽度/面积过小的div, iframe, 和 object元素的数量",
            "1.0",
        )

    def calculate_score(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, small_elements = calculate_score(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": small_elements,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    small_area_count = 0
    small_area_elements = []

    # 查找所有 div, iframe, 和 object 元素
    for tag in soup.find_all(["div", "iframe", "object"]):
        width = tag.get("width")
        height = tag.get("height")

        # 解析宽度和高度
        if width and height:
            try:
                width = int(width)
                height = int(height)
                area = width * height
                if (
                    width < SIDE_THRESHOLD
                    or height < SIDE_THRESHOLD
                    or area < AREA_THRESHOLD
                ):
                    small_area_count += 1
                    small_area_elements.append((tag.name, width, height, area))
            except ValueError:
                continue

    return small_area_count, small_area_elements


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <div style="width: 5px; height: 5px;"></div>
    <iframe width="10" height="10"></iframe>
    <object width="2" height="2"></object>
    <div style="width: 100px; height: 100px;"></div>
    """
    count, small_elements = calculate_score(html_content)
    print(f"Number of elements with small area: {count}")
    for element in small_elements:
        print(
            f"Detected small area element: {element[0]} - Width: {element[1]}px, Height: {element[2]}px, Area: {element[3]}px²"
        )
