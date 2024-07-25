from bs4 import BeautifulSoup

# todo: 真正的ActiveX控件列表
# Suspicious objects are object elements that are included in the document and
# whose classid is contained in a list of ActiveX controls known to be exploitable.
# 定义已知的可疑 ActiveX 控件列表
SUSPICIOUS_CLASSIDS = [
    "clsid:12345678-1234-1234-1234-123456789012",  # 示例 classid
    "clsid:87654321-4321-4321-4321-210987654321",  # 示例 classid
    # 添加更多已知的可疑 classid
]


def calculate_score(html_content: str) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    suspicious_count = 0
    suspicious_objects = []

    # 查找所有 object 元素
    for tag in soup.find_all("object"):
        classid = tag.get("classid")
        if classid in SUSPICIOUS_CLASSIDS:
            suspicious_count += 1
            suspicious_objects.append(classid)

    return suspicious_count, suspicious_objects


if __name__ == "__main__":
    # 测试示例
    html_content = """
    <object classid="clsid:12345678-1234-1234-1234-123456789012"></object>
    <object classid="clsid:87654321-4321-4321-4321-210987654321"></object>
    <object classid="clsid:00000000-0000-0000-0000-000000000000"></object>
    <div>Some other content</div>
    """
    count, suspicious_objects = calculate_score(html_content)
    print(f"Number of suspicious objects: {count}")
    for obj in suspicious_objects:
        print(f"Detected suspicious object with classid: {obj}")
