from bs4 import BeautifulSoup

# longer than a certain threshold (128 characters) and contains less than 5% of whitespace characters.
# in this case, we prioritize performance over precision.
# 定义可疑内容的阈值
CONTENT_LENGTH_THRESHOLD = 128
WHITESPACE_RATIO_THRESHOLD = 0.05
from src.static_features.html import *


class SuspiciousContentElements(HTMLExtractor):
    def __init__(self, web_data):
        super().__init__(web_data)
        self.meta = ExtractorMeta(
            "html",
            "SuspiciousContentElements",
            "prophiler",
            "tag.get_text longer than a certain threshold (128 characters) and contains less than 5% of whitespace characters",
            "1.0",
        )

    def extract(self) -> FeatureExtractionResult:
        htmls = self.web_data.content["html"]
        info_dict = {}
        for h in htmls:
            start_time = time.time()
            res, suspicious_elements = extract(h["content"])
            info_dict[h["filename"]] = {
                "count": res,
                "time": time.time() - start_time,
                "additional_info": suspicious_elements,
            }
        return FeatureExtractionResult(self.meta.filetype, self.meta.name, info_dict)


def extract(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    suspicious_count = 0
    suspicious_elements = []

    # 查找所有元素
    for tag in soup.find_all(True):  # True 表示查找所有标签
        content = tag.get_text(strip=True)  # 获取元素的文本内容
        # print(f"tag:{tag.name},content:{content}")
        # 检查内容长度和空白字符比例
        if len(content) > CONTENT_LENGTH_THRESHOLD:
            whitespace_count = sum(1 for char in content if char.isspace())
            if whitespace_count / len(content) < WHITESPACE_RATIO_THRESHOLD:
                suspicious_count += 1
                suspicious_elements.append((tag.name, content))

    return suspicious_count, suspicious_elements


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <div>This is some valid content.</div>
    <script>var shellcode = "alert(\'x\'); // suspicious code here"</script>
    <div>12345678901234567890 1234567890123456789012345678901234567890 123456789012345678901234567890 12345678901234567890
    12345678901234567890 123456789012345678901234567890 1234567890123456789012345678901234567890</div>
    <div>1234567890123456789012345678901234567890</div>
    <div>Short content.</div>
    """
    count, suspicious_elements = extract(html_content)
    print(f"Number of elements containing suspicious content: {count}")
    for element in suspicious_elements:
        print(f"Detected suspicious element: {element[0]} - Content: {element[1]}")
