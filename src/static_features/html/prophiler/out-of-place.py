from bs4 import BeautifulSoup

# detect web pages that have become malicious as the result of a stored XSS or SQL injection attack.
from src.static_features.html import *


class OutOfPlace(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "OutOfPlace",
            "prophiler",
            "位置不正确的tag",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, out_of_place_elements = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": out_of_place_elements,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    out_of_place_count = 0
    out_of_place_elements = []

    # 定义允许的位置
    allowed_positions = {
        "script": ["head", "body"],
        "iframe": ["body"],
        "frame": ["frameset"],
        "form": ["body"],
        "object": ["body"],
        "embed": ["body"],
    }

    # 检查每种元素
    # they are checked according to the allowed positioning, as defined by the HTML DTD specifications
    for tag in soup.find_all(["script", "iframe", "frame", "form", "object", "embed"]):
        parent_tag = tag.parent.name
        if parent_tag not in allowed_positions.get(tag.name, []):
            out_of_place_count += 1
            out_of_place_elements.append((tag.name, str(tag)))

    return out_of_place_count, out_of_place_elements


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <html>
        <head>
            <title>Test Page</title>
            <script src="valid_script.js"></script>
            <script>console.log('Valid script');</script>
        </head>
        <body>
            <h1>Welcome</h1>
            <iframe src="https://example.com"></iframe>
            <form action="submit.php"></form>
        </body>
            <!-- Out of place elements -->
            <script>console.log('Out of place script');</script>
            
            <title>Another Title</title>
            
            <object data="object_data"></object>
            
            <embed src="embed_data.swf"></embed>
        
    </html>
    """
    count, elements = extract(html_content)
    print(f"Number of out of place elements: {count}")
    for element in elements:
        print(f"Detected out of place element: {element[0]} - {element[1]}")
